from collections.abc import Callable
from typing import Protocol

import numpy as np
import torch
from torch.autograd.function import FunctionCtx


class AutogradCtx(Protocol):
    """Autograd context for the QiskitAutogradFunction."""

    saved_tensors: tuple[torch.Tensor, ...]
    gradient_fn: Callable[[torch.Tensor, np.ndarray], torch.Tensor]


class QiskitAutogradFunction(torch.autograd.Function):
    """Custom autograd bridge between PyTorch and Qiskit for variational quantum circuits."""

    @staticmethod
    def forward(
        ctx: FunctionCtx,
        x: torch.Tensor,
        weights: torch.Tensor,
        evaluator: Callable,
        gradient_fn: Callable,
    ) -> torch.Tensor:
        """Perform the forward pass by evaluating the quantum circuit via the provided evaluator.

        Args:
            ctx (FunctionCtx): Autograd context to save information for the backward pass.
            x (torch.Tensor): Input batch of shape (B, input_dim).
            weights (torch.Tensor): Trainable weights of the circuit.
            evaluator (Callable): Callable that evaluates the quantum circuit and returns
                the output values for the given inputs and weights.
            gradient_fn (Callable): Callable computing gradients of the circuit output with
                respect to its parameters, e.g., via the parameter-shift rule.

        Returns:
            torch.Tensor: Output batch of shape (B, output_dim).

        """
        ctx.save_for_backward(x, weights)
        ctx.gradient_fn = gradient_fn
        ctx.evaluator = evaluator

        return evaluator(x, weights.detach().cpu().numpy())

    @staticmethod
    def backward(
        ctx: AutogradCtx, *grad_outputs: torch.Tensor
    ) -> tuple[None, torch.Tensor, None, None]:
        """Compute gradients using the provided quantum gradient function.

        Args:
            ctx (AutogradCtx): Autograd context with saved tensors from the forward pass.
            *grad_outputs (torch.Tensor): Gradient of the loss with respect to
                the forward output, shape (B, output_dim).

        Returns:
            tuple[None, torch.Tensor, None, None]: Gradients for each forward input. Only the
                gradient with respect to `weights` is returned; gradients for `model` and `x`
                are None.

        """
        x, weights = ctx.saved_tensors
        (grad_output,) = grad_outputs

        # Compute dOutput/dWeights via parameter-shift
        jac = ctx.gradient_fn(x, weights.detach().cpu().numpy())
        jac_np = jac.detach().cpu().numpy()  # shape: (B, output_dim, *weights.shape)

        grad_out_np = grad_output.detach().cpu().numpy()  # shape: (B, output_dim)

        # Chain rule: dL/dW = sum(dL/dOut * dOut/dW)
        grad_w = np.tensordot(grad_out_np, jac_np, axes=([0, 1], [0, 1]))

        return None, torch.from_numpy(grad_w).float(), None, None
