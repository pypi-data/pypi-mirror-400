# SPDX-FileCopyrightText: 2026 MetaMachines LLC
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import torch


def _require_cuda() -> None:
    if not torch.cuda.is_available():
        raise unittest.SkipTest("CUDA is not available")
    major, _minor = torch.cuda.get_device_capability()
    if major < 8:
        raise unittest.SkipTest("Compute capability >= 8.0 required")


def _error_metrics(tensor_a: torch.Tensor, tensor_b: torch.Tensor) -> tuple[float, float, float]:
    diff = tensor_a - tensor_b
    mse = torch.mean(diff * diff)
    rmse = torch.sqrt(mse).item()
    abs_error = diff.abs()
    max_abs_error = abs_error.max().item()
    mean_abs_error = abs_error.mean().item()
    return rmse, max_abs_error, mean_abs_error


class HyperSemiringGradientExampleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _require_cuda()
        torch.manual_seed(0)
        torch.cuda.manual_seed(0)

    def _assert_bounds(
        self,
        metrics: tuple[float, float, float],
        bounds: tuple[float, float, float],
        label: str,
    ) -> None:
        rmse, max_abs, mean_abs = metrics
        rmse_bound, max_bound, mean_bound = bounds
        self.assertLessEqual(rmse, rmse_bound, f"{label} rmse {rmse:.6e} > {rmse_bound:.6e}")
        self.assertLessEqual(max_abs, max_bound, f"{label} max {max_abs:.6e} > {max_bound:.6e}")
        self.assertLessEqual(mean_abs, mean_bound, f"{label} mean {mean_abs:.6e} > {mean_bound:.6e}")

    def test_hyper_semiring_gradient_example(self) -> None:
        try:
            import mm_kermac.hyper_semiring_gradient as hyper_semiring_gradient
            from mm_kermac.helpers import torch_einsum_L2_norm, torch_inefficient_p_norm
        except Exception as exc:
            raise unittest.SkipTest(f"mm_kermac import failed: {exc}")

        device = torch.device("cuda")
        M, N, O, K, L = 12, 8, 2, 32, 1

        tensor_A = torch.randn(L, K, M, device=device)  # grad_kernel_matrix
        tensor_B = torch.randn(L, N, K, device=device)  # x
        tensor_C = torch.randn(L, O, K, device=device)  # coefs
        tensor_D = torch.randn(L, N, M, device=device)  # z

        coefs = tensor_C
        grad_kernel_matrix = tensor_A
        x = tensor_B
        z = tensor_D

        epsilon = 1e-3
        bounds = (1e-4, 1e-3, 1e-4)

        # L1 grad
        norm_L1 = hyper_semiring_gradient.NormL1()
        kermac_out = norm_L1(
            x=x,
            z=z,
            coefs=coefs,
            grad_kernel_matrix=grad_kernel_matrix,
            debug=False,
        )
        torch_out = torch_inefficient_p_norm(
            x=x,
            z=z,
            coefs=coefs,
            grad_kernel_matrix=grad_kernel_matrix,
            p=1.0,
            eps=0.0,
        )
        self._assert_bounds(_error_metrics(kermac_out, torch_out), bounds, "Norm L1 Grad")

        # L2 grad
        norm_L2 = hyper_semiring_gradient.NormL2()
        kermac_out = norm_L2(
            x=x,
            z=z,
            coefs=coefs,
            grad_kernel_matrix=grad_kernel_matrix,
            debug=False,
        )
        torch_out = torch_inefficient_p_norm(
            x=x,
            z=z,
            coefs=coefs,
            grad_kernel_matrix=grad_kernel_matrix,
            p=2.0,
            eps=0.0,
        )
        einsum_out = torch_einsum_L2_norm(
            x=x,
            z=z,
            coefs=coefs,
            grad_kernel_matrix=grad_kernel_matrix,
        )
        self._assert_bounds(_error_metrics(kermac_out, torch_out), bounds, "Norm L2 Grad (inefficient)")
        self._assert_bounds(_error_metrics(kermac_out, einsum_out), bounds, "Norm L2 Grad (einsum)")

        # Lp grad
        p_power_grad = torch.tensor([1.3 - 1.0], dtype=torch.float32, device=device)
        norm_Lp = hyper_semiring_gradient.NormLp(epsilon=epsilon)
        kermac_out = norm_Lp(
            x=x,
            z=z,
            coefs=coefs,
            grad_kernel_matrix=grad_kernel_matrix,
            p_power_grad=p_power_grad,
            debug=False,
        )
        torch_out = torch_inefficient_p_norm(
            x=x,
            z=z,
            coefs=coefs,
            grad_kernel_matrix=grad_kernel_matrix,
            p=1.3,
            eps=epsilon,
        )
        self._assert_bounds(_error_metrics(kermac_out, torch_out), bounds, "Norm Lp Grad (p=1.3)")
