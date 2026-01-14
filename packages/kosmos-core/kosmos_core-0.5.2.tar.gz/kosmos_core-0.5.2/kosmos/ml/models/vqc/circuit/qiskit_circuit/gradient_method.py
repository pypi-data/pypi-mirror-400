import math
from abc import ABC, abstractmethod

import numpy as np
import torch
from qiskit import QuantumCircuit

from kosmos.ml.typing import TensorNpArray
from kosmos.utils.rng import RNG

DEVICE = "cpu"


class GradientMethod(ABC):
    r"""Abstract base class for quantum-circuit gradient methods.

    Implementations may follow analytic rules (e.g., parameter-shift) or stochastic
    gradient-free approaches (e.g., SPSA). All subclasses must implement the ``jacobian``
    method that computes d(outputs)/d(weights).

    Notes:
        This package provides two implementations:

        - ``ParameterShiftRule``: exact, low variance, but requires 2 evaluations per parameter.
        - ``SPSA``: stochastic, higher variance, but requires only 2 evaluations per sample
          independent of parameter count.

    """

    def __init__(self) -> None:
        """Initialize the gradient method."""
        self.parameterized_circuit = None

    def set_parameterized_circuit(
        self,
        parameterized_circuit: "QiskitParameterizedCircuit",  # noqa: F821
    ) -> None:
        """Assign the parameterized circuit to be used by the gradient method.

        This must be called before computing gradients.

        Args:
            parameterized_circuit (QiskitParameterizedCircuit): The Qiskit parameterized circuit.

        """
        self.parameterized_circuit = parameterized_circuit

    def validate_parameterized_circuit(self) -> None:
        """Validate that the parameterized circuit has been set."""
        if self.parameterized_circuit is None:
            msg = "The parameterized circuit has not been set for the gradient method."
            raise ValueError(msg)

    @abstractmethod
    def jacobian(self, x: TensorNpArray, weights: np.ndarray) -> torch.Tensor:
        """Compute d(outputs)/d(weights).

        Args:
            x (TensorNpArray): Input values, shape (len_x, input_dim).
            weights (np.ndarray): Weights values.

        Returns:
            torch.Tensor: Jacobian of shape (len_x, output_dim, followed by weights.shape).

        """


class ParameterShiftRule(GradientMethod):
    r"""Gradient computation using the parameter-shift rule.

    The parameter-shift rule is an analytic approach to computing gradients in variational quantum
    circuits. The gradient of an expectation value can be computed exactly using two circuit
    evaluations per parameter:

    .. math:: f'(\theta) = \frac{f(\theta + s) - f(\theta - s)}{2 \sin(s)}

    In the common case of Pauli rotations, the canonical shift is :math:`s = \pi/2`.

    Notes:
        - The method provides low-variance, unbiased gradients.
        - Computational cost scales linearly with the number of parameters (two evaluations per
          parameter).
        - Requires the circuit to be differentiable in the parameter of interest and the underlying
          generator to have a known spectrum.

    """

    def __init__(self, shift: float = np.pi / 2) -> None:
        """Initialize the parameter-shift rule.

        Args:
            shift (float): Shift magnitude. Defaults to π/2.

        """
        super().__init__()
        self.shift = shift

    def jacobian(self, x: TensorNpArray, weights: np.ndarray) -> torch.Tensor:
        """Compute d(outputs)/d(weights) via parameter-shift.

        Args:
            x (TensorNpArray): Input values, shape (len_x, input_dim).
            weights (np.ndarray): Weights values.

        Returns:
            torch.Tensor: Jacobian of shape (len_x, output_dim, followed by weights.shape).

        """
        self.validate_parameterized_circuit()

        x = x.detach().cpu().numpy() if isinstance(x, torch.Tensor) else x

        len_x = len(x)
        wshape = weights.shape
        indices = list(np.ndindex(wshape))

        qcs: list[QuantumCircuit] = []
        for idx in indices:
            for xb in x:
                for s in (self.shift, -self.shift):
                    w = weights.copy()
                    w[idx] += s
                    qcs.append(self.parameterized_circuit.circuit(w, xb))

        outputs = self.parameterized_circuit.execute_circuits(qcs)

        jac = np.zeros((len_x, self.parameterized_circuit.output_dim, *wshape), dtype=np.float32)
        for k, idx in enumerate(indices):
            for b in range(len_x):
                base = (k * len_x + b) * 2
                y_plus = np.atleast_2d(outputs[base])
                y_minus = np.atleast_2d(outputs[base + 1])
                jac[(b, slice(None), *idx)] = 0.5 * (y_plus - y_minus)

        return torch.from_numpy(jac).float().to(DEVICE)


class SPSA(GradientMethod):
    r"""Gradient computation using Simultaneous Perturbation Stochastic Approximation (SPSA).

    SPSA is a gradient-free method that estimates all partial derivatives using only two circuit
    evaluations per random perturbation, independent of the number of parameters. A random
    perturbation vector :math:`\Delta` is drawn from a symmetric Bernoulli distribution
    :math:`\{-1, +1\}`, which is optimal in the sense of minimizing estimator variance
    (Sadegh & Spall, 1998).

    The gradient estimate for parameter :math:`i` is:

    .. math::
           \hat{g}_i \approx \frac{f(\theta + \epsilon \Delta) - f(\theta - \epsilon \Delta)}
           {2\epsilon \Delta_i}

    Multiple samples are averaged to reduce variance.

    Notes:
        - Cost is :math:`O(\mathrm{num\_samples})` compared to :math:`O(\mathrm{num\_parameters})`
          of the parameter-shift rule.
        - Produces an unbiased gradient estimator under mild regularity.
        - Typically more robust to noise than analytic gradient methods such as parameter-shift.
        - Only gradient estimation is implemented here; the optimizer gain sequences :math:`a_k`
          and :math:`c_k` are not part of this component.
        - This implementation follows standard formulations used in quantum optimization, such as
          PennyLane's ``SPSAOptimizer``
          (https://docs.pennylane.ai/en/stable/_modules/pennylane/optimize/spsa.html#SPSAOptimizer.compute_grad).

    """

    def __init__(self, epsilon: float = 0.01, num_samples: int = 3) -> None:
        """Initialize the SPSA gradient method.

        Args:
            epsilon (float): Perturbation magnitude. Defaults to 0.01.
            num_samples (int): Number of random perturbation samples to average over.
                Defaults to 3.

        """
        super().__init__()

        if epsilon <= 0 or not math.isfinite(epsilon):
            msg = "epsilon must be > 0 and finite."
            raise ValueError(msg)
        if num_samples <= 0 or not math.isfinite(num_samples):
            msg = "num_samples must be > 0 and finite."
            raise ValueError(msg)

        self.epsilon = epsilon
        self.num_samples = num_samples
        self.np_rng = RNG.np_generator()

    def jacobian(self, x: TensorNpArray, weights: np.ndarray) -> torch.Tensor:
        """Compute d(outputs)/d(weights) via SPSA.

        Args:
            x (TensorNpArray): Input values, shape (len_x, input_dim).
            weights (np.ndarray): Weights values.

        Returns:
            torch.Tensor: Jacobian of shape (len_x, output_dim, followed by weights.shape).

        """
        self.validate_parameterized_circuit()

        x = x.detach().cpu().numpy() if isinstance(x, torch.Tensor) else x

        len_x = len(x)
        wshape = weights.shape
        output_dim = self.parameterized_circuit.output_dim

        jac_avg = np.zeros((len_x, output_dim, *wshape), dtype=np.float32)

        deltas: list[np.ndarray] = []
        qcs: list[QuantumCircuit] = []
        for _ in range(self.num_samples):
            delta = self.np_rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=wshape)
            deltas.append(delta)
            w_plus = weights + self.epsilon * delta
            w_minus = weights - self.epsilon * delta

            for xb in x:
                qcs.append(self.parameterized_circuit.circuit(w_plus, xb))
                qcs.append(self.parameterized_circuit.circuit(w_minus, xb))

        outputs = self.parameterized_circuit.execute_circuits(qcs)

        scale = 1.0 / (2 * self.epsilon)
        for s_idx, delta in enumerate(deltas):
            for b in range(len_x):
                base = (s_idx * len_x + b) * 2
                y_plus = np.asarray(outputs[base])
                y_minus = np.asarray(outputs[base + 1])
                diff = scale * (y_plus - y_minus)

                for out_idx in range(output_dim):
                    jac_avg[b, out_idx] += diff[out_idx] * delta

        jac_avg /= self.num_samples

        return torch.from_numpy(jac_avg).float().to(DEVICE)
