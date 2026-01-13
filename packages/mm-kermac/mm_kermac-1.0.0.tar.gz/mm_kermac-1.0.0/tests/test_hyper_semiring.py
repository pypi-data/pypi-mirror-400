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


class HyperSemiringExampleTest(unittest.TestCase):
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

    def test_hyper_semiring_example(self) -> None:
        try:
            import mm_kermac.hyper_semiring as hyper_semiring
        except Exception as exc:
            raise unittest.SkipTest(f"mm_kermac import failed: {exc}")

        device = torch.device("cuda")
        M, N, K = 128, 128, 64
        x = torch.randn(M, K, device=device)
        z = torch.randn(N, K, device=device)

        # GEMM
        out = torch.zeros(3, M, N, device=device)
        gemm = hyper_semiring.Gemm()
        kermac_out = gemm(x=x, z=z, out=out, try_to_align=False, debug=False)
        torch_out = x @ z.T
        self._assert_bounds(_error_metrics(kermac_out, torch_out), (1e-5, 1e-4, 1e-5), "Gemm")

        # L2 norm
        out = torch.zeros(3, M, N, device=device)
        norm_L2 = hyper_semiring.NormL2()
        kermac_out = norm_L2(x=x, z=z, out=out, try_to_align=False, debug=False)
        torch_out = torch.cdist(x, z, p=2.0)
        self._assert_bounds(_error_metrics(kermac_out, torch_out), (1e-4, 5e-4, 1e-4), "Norm L2")

        # L1 norm
        out = torch.zeros(3, M, N, device=device)
        norm_L1 = hyper_semiring.NormL1()
        kermac_out = norm_L1(x=x, z=z, out=out, try_to_align=False, debug=False)
        torch_out = torch.cdist(x, z, p=1.0)
        self._assert_bounds(_error_metrics(kermac_out, torch_out), (2e-3, 1e-2, 2e-3), "Norm L1")

        # Lp norms (batched)
        out = torch.zeros(3, M, N, device=device)
        p_inner = torch.tensor([1.3, 1.4, 1.5], dtype=torch.float32, device=device)
        p_outer = torch.tensor([1.0 / 1.3, 1.0 / 1.4, 1.0 / 1.5], dtype=torch.float32, device=device)
        epsilon = 1e-3

        norm_Lp = hyper_semiring.NormLp(epsilon)
        kermac_out = norm_Lp(
            x=x,
            z=z,
            p_inner=p_inner,
            p_outer=p_outer,
            out=out,
            try_to_align=False,
            debug=False,
        )

        lp_bounds = (5e-4, 2e-3, 5e-4)
        for idx, p in enumerate((1.3, 1.4, 1.5)):
            torch_out = torch.cdist(x, z, p=p)
            self._assert_bounds(_error_metrics(kermac_out[idx], torch_out), lp_bounds, f"Norm Lp p={p}")
