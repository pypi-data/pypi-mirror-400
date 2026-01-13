# SPDX-FileCopyrightText: 2026 MetaMachines LLC
#
# SPDX-License-Identifier: MIT

import argparse

import torch

import mm_kermac.hyper_semiring as hyper_semiring


def _require_cuda() -> None:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available")
    major, _minor = torch.cuda.get_device_capability()
    if major < 8:
        raise RuntimeError("Compute capability >= 8.0 required")


def _time_cuda(fn, iters: int) -> float:
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    start.record()
    for _ in range(iters):
        fn()
    end.record()
    torch.cuda.synchronize()
    return start.elapsed_time(end) / iters


def _bench_case(name: str, kermac_fn, torch_fn, warmup: int, iters: int) -> None:
    for _ in range(warmup):
        kermac_fn()
    torch.cuda.synchronize()
    kermac_ms = _time_cuda(kermac_fn, iters)

    for _ in range(warmup):
        torch_fn()
    torch.cuda.synchronize()
    torch_ms = _time_cuda(torch_fn, iters)

    speedup = torch_ms / kermac_ms if kermac_ms > 0 else float("inf")
    print(f"{name:>8} | kermac {kermac_ms:8.3f} ms | torch {torch_ms:8.3f} ms | {speedup:6.2f}x")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark mm-kermac hyper_semiring vs torch.cdist"
    )
    parser.add_argument("--M", type=int, default=2048, help="Rows in x (default: 2048)")
    parser.add_argument("--N", type=int, default=2048, help="Rows in z (default: 2048)")
    parser.add_argument("--K", type=int, default=256, help="Columns in x/z (default: 256)")
    parser.add_argument("--iters", type=int, default=50, help="Timed iterations (default: 50)")
    parser.add_argument("--warmup", type=int, default=10, help="Warmup iterations (default: 10)")
    parser.add_argument("--p-frac", type=float, default=1.3, help="Fractional p for NormLp (default: 1.3)")
    parser.add_argument("--epsilon", type=float, default=0.0, help="Epsilon clamp for NormLp (default: 0.0)")
    parser.add_argument("--try-align", action="store_true", help="Enable alignment specialization")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.p_frac <= 0:
        raise ValueError("--p-frac must be > 0")
    _require_cuda()

    torch.manual_seed(0)
    torch.cuda.manual_seed(0)

    device = torch.device("cuda")
    x = torch.randn(args.M, args.K, device=device)
    z = torch.randn(args.N, args.K, device=device)
    out = torch.empty((args.M, args.N), device=device)

    norm_l1 = hyper_semiring.NormL1()
    norm_l2 = hyper_semiring.NormL2()
    norm_lp = hyper_semiring.NormLp(args.epsilon)

    p_inner = torch.tensor(args.p_frac, dtype=torch.float32, device=device)
    p_outer = torch.tensor(1.0 / args.p_frac, dtype=torch.float32, device=device)

    def kermac_l1():
        norm_l1(x=x, z=z, out=out, try_to_align=args.try_align, debug=False)

    def kermac_l2():
        norm_l2(x=x, z=z, out=out, try_to_align=args.try_align, debug=False)

    def kermac_lp():
        norm_lp(
            x=x,
            z=z,
            p_inner=p_inner,
            p_outer=p_outer,
            out=out,
            try_to_align=args.try_align,
            debug=False,
        )

    def torch_l1():
        torch.cdist(x, z, p=1.0)

    def torch_l2():
        torch.cdist(x, z, p=2.0)

    def torch_lp():
        torch.cdist(x, z, p=args.p_frac)

    torch.cuda.synchronize()
    print(f"Device: {torch.cuda.get_device_name(device)}")
    print(f"M={args.M} N={args.N} K={args.K} iters={args.iters} warmup={args.warmup}")
    print(f"Fractional p={args.p_frac} epsilon={args.epsilon} try_align={args.try_align}")
    print("   case |    kermac ms |     torch ms | speedup")

    with torch.no_grad():
        _bench_case("p=1.0", kermac_l1, torch_l1, args.warmup, args.iters)
        _bench_case("p=2.0", kermac_l2, torch_l2, args.warmup, args.iters)
        _bench_case(f"p={args.p_frac:g}", kermac_lp, torch_lp, args.warmup, args.iters)


if __name__ == "__main__":
    main()
