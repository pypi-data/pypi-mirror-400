# SPDX-FileCopyrightText: 2026 MetaMachines LLC
#
# SPDX-License-Identifier: MIT

import argparse
import torch

from mm_kermac.helpers import compare_tensors
import mm_kermac.hyper_semiring as hyper_semiring

def parse_args():
    """Parse command-line arguments for matrix dimensions, p-norm, and flags."""
    parser = argparse.ArgumentParser(description="Run kermac.cdist_t with configurable parameters")
    parser.add_argument('-m','--M', type=int, default=10000, help='Number of rows in output matrix (default: 10000)')
    parser.add_argument('-n','--N', type=int, default=10000, help='Number of columns in output matrix (default: 10000)')
    parser.add_argument('-k','--K', type=int, default=1024, help='Inner dimension of input matrices (default: 1024)')
    parser.add_argument('-a','--try_align', default=False, action='store_true', help='Specialize kernel if tensors are 4 element aligned')
    parser.add_argument('-d','--debug', default=False, action='store_true', help='Enable debug output (default: True)')
    return parser.parse_args()

def main():
    args = parse_args()
    M, N, K = args.M, args.N, args.K
    try_to_align = args.try_align
    debug = args.debug

    device = torch.device('cuda')
    x = torch.randn(M,K,device=device)
    z = torch.randn(N,K,device=device)
    out = torch.zeros(3,M,N,device=device)

    gemm = hyper_semiring.Gemm()
    print('Running MMA')
    gemm(
        x=x, 
        z=z, 
        out=out,
        try_to_align=try_to_align,
        debug=debug
    )
    torch_out = x @ z.T
    compare_tensors(out, torch_out)

    norm_L2 = hyper_semiring.NormL2()
    print('Running Norm L2')
    norm_L2(
        x=x, 
        z=z, 
        out=out,
        try_to_align=try_to_align,
        debug=debug
    )
    torch_out = torch.cdist(x, z, p=2.0)
    compare_tensors(out, torch_out)

    norm_L1 = hyper_semiring.NormL1()
    print('Running Norm L1')
    norm_L1(
        x=x, 
        z=z, 
        out=out,
        try_to_align=try_to_align,
        debug=debug
    )
    torch_out = torch.cdist(x, z, p=1.0)
    compare_tensors(out, torch_out)

    p_inner = torch.tensor([1.3, 1.4, 1.5], dtype=torch.float32, device=device)
    p_outer = torch.tensor([1.0 / 1.3, 1.0 / 1.4, 1.0 / 1.5], dtype=torch.float32, device=device)
    epsilon = 1e-3

    norm_Lp = hyper_semiring.NormLp(epsilon)
    print('Running Norm P=1.3, P=1.4, P=1.5 Batched')
    norm_Lp(
        x=x, 
        z=z,
        p_inner=p_inner,
        p_outer=p_outer, 
        out=out,
        try_to_align=try_to_align,
        debug=debug
    )

    print('Comparing Norm P=1.3')
    torch_out = torch.cdist(x, z, p=1.3)
    compare_tensors(out[0], torch_out)

    print('Comparing Norm P=1.4')
    torch_out = torch.cdist(x, z, p=1.4)
    compare_tensors(out[1], torch_out)

    print('Comparing Norm P=1.5')
    torch_out = torch.cdist(x, z, p=1.5)
    compare_tensors(out[2], torch_out)

if __name__ == '__main__':
    main()
