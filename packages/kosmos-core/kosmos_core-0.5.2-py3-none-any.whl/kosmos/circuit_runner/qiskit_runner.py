import numpy as np
from qiskit import QuantumCircuit, generate_preset_pass_manager
from qiskit.providers import BackendV2 as Backend
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime import RuntimeJobV2 as RuntimeJob
from qiskit_ibm_runtime.sampler import SamplerV2 as Sampler

from kosmos.circuit_runner.circuit_runner import CircuitRunner
from kosmos.circuit_runner.ibm_runtime_utils import qiskit_remote_backend
from kosmos.circuit_runner.qiskit_result import job_expectation_values
from kosmos.circuit_runner.typing import QuantumCircuitFramework
from kosmos.ml.models.vqc.circuit.qiskit_circuit.gradient_method import (
    GradientMethod,
    ParameterShiftRule,
)
from kosmos.utils.rng import RNG


class QiskitRunner(CircuitRunner):
    """General Qiskit circuit runner."""

    def __init__(
        self,
        backend: Backend,
        num_shots: int = 1024,
        gradient_method: GradientMethod | None = None,
    ) -> None:
        """Initialize the Qiskit runner.

        Args:
            backend (Backend): The backend to use.
            num_shots (int): Number of shots. Defaults to 1024.
            gradient_method (GradientMethod | None): The gradient method to use when running VQCs.
                Uses ParameterShiftRule() if None. Defaults to None.

        """
        self.backend = backend
        self.num_shots = num_shots
        self._gradient_method = gradient_method or ParameterShiftRule()

    @property
    def framework(self) -> QuantumCircuitFramework:
        """The framework used by the circuit runner."""
        return "qiskit"

    def run_sampler(self, circuits: list[QuantumCircuit]) -> RuntimeJob:
        """Run circuits using Sampler primitive.

        Args:
            circuits (list[QuantumCircuit]): The circuits to run.

        Returns:
            RuntimeJob: The submitted job.

        """
        pm = generate_preset_pass_manager(backend=self.backend, optimization_level=3)
        isa_circuits = pm.run(circuits)
        sampler = Sampler(self.backend)
        return sampler.run(isa_circuits, shots=self.num_shots)

    def expectation_values(self, circuits: list[QuantumCircuit]) -> list[np.ndarray]:
        """Compute Z-basis expectation values for the given circuits.

        Args:
            circuits: The circuits to run.

        Returns:
            list[np.ndarray]: A list of arrays, where each array contains the expectation
                values for one circuit in the job.

        """
        job = self.run_sampler(circuits)
        return job_expectation_values(job)

    def get_gradient_method(
        self,
        parameterized_circuit: "QiskitParameterizedCircuit",  # noqa: F821
    ) -> GradientMethod:
        """Get the gradient method instance.

        Args:
            parameterized_circuit (QiskitParameterizedCircuit): The Qiskit parameterized circuit.

        Returns:
            GradientMethod: The gradient method instance.

        """
        self._gradient_method.set_parameterized_circuit(parameterized_circuit)
        return self._gradient_method


class AerSimulatorRunner(QiskitRunner):
    """Qiskit circuit runner using the AerSimulator using density matrix simulation."""

    def __init__(
        self, num_shots: int = 1024, gradient_method: GradientMethod | None = None
    ) -> None:
        """Initialize the AerSimulator runner.

        Args:
            num_shots (int): Number of shots. Defaults to 1024.
            gradient_method (GradientMethod | None): The gradient method to use when running VQCs.
                Uses ParameterShiftRule() if None. Defaults to None.

        """
        noise_model = None
        aer_simulator = AerSimulator(
            method="density_matrix", noise_model=noise_model, seed_simulator=RNG.get_seed()
        )
        super().__init__(aer_simulator, num_shots, gradient_method)


class IBMRuntimeRunner(QiskitRunner):
    """Qiskit circuit runner using an IBM Runtime backend."""

    def __init__(
        self,
        qiskit_runtime_service: QiskitRuntimeService,
        backend_name: str | None = None,
        min_num_qubits: int | None = None,
        num_shots: int = 1024,
        gradient_method: GradientMethod | None = None,
    ) -> None:
        """Initialize the IBM Runtime runner.

        Args:
            qiskit_runtime_service (QiskitRuntimeService): The Qiskit Runtime service instance.
            backend_name (str | None): The name of the backend. Returns the least busy backend if
                None. Defaults to None.
            min_num_qubits (int | None): The minimum number of qubits. Defaults to None.
            num_shots (int): Number of shots. Defaults to 1024.
            gradient_method (GradientMethod | None): The gradient method to use when running VQCs.
                Uses ParameterShiftRule() if None. Defaults to None.

        """
        backend = qiskit_remote_backend(qiskit_runtime_service, backend_name, min_num_qubits)
        super().__init__(backend, num_shots, gradient_method)
