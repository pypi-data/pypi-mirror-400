# SPDX-FileCopyrightText: 2026 MetaMachines LLC
#
# SPDX-License-Identifier: MIT

import argparse
import mm_kermac
import torch

from mm_kermac.helpers import (
    compare_tensors,
    torch_einsum_L2_norm,
    torch_inefficient_p_norm
)
from mm_kermac.stack_ptx_types import Stack, PtxInstruction

import mm_kermac.hyper_semiring_gradient as hyper_semiring_gradient

def parse_args():
    """Parse command-line arguments for matrix dimensions, p-norm, and flags."""
    parser = argparse.ArgumentParser(description="Run kermac.cdist_t with configurable parameters")
    parser.add_argument('-m','--M', type=int, default=20, help='Number of rows in data_z (default: 20)')
    parser.add_argument('-n','--N', type=int, default=16, help='Number of columns in data (default: 16)')
    parser.add_argument('-o','--O', type=int, default=3, help='Number of channels in coefficents (default: 3)')
    parser.add_argument('-k','--K', type=int, default=100, help='Number of rows in data_x (default: 100)')
    parser.add_argument('-l','--L', type=int, default=2, help='Number of batches in each dimension (default: 2)')
    parser.add_argument('-d','--debug', default=False, action='store_true', help='Enable debug output (default: True)')
    return parser.parse_args()

def main():
    args = parse_args()
    M, N, O, K, L = args.M, args.N, args.O, args.K, args.L
    debug = args.debug

    device = torch.device('cuda')
    timer = mm_kermac.CudaTimer()

    size_M = M
    size_D = N
    size_C = O
    size_N = K
    size_L = L

    tensor_A = torch.randn(size_L,size_N,size_M,device=device) # M-major # M-major 
    tensor_B = torch.randn(size_L,size_D,size_N,device=device) # N-major # K-major
    tensor_C = torch.randn(size_L,size_C,size_N,device=device) # N-major # K-major
    tensor_D = torch.randn(size_L,size_D,size_M,device=device) # M-major # M-Major

    coefs =         tensor_C
    grad_kernel_matrix = tensor_A
    x =             tensor_B
    z =             tensor_D

    torch.cuda.synchronize()

    epsilon = 1e-3

    print('Running Norm L1 Grad')
    norm_L1 = hyper_semiring_gradient.NormL1()
    kermac_out = \
        norm_L1(
            x=x,
            z=z,
            coefs=coefs,
            grad_kernel_matrix=grad_kernel_matrix,
            debug = debug
        )
    
    torch_out = \
        torch_inefficient_p_norm(
            x=x,
            z=z,
            coefs=coefs,
            grad_kernel_matrix=grad_kernel_matrix,
            p=1.0,
            eps=0.0,
        )
    compare_tensors(kermac_out, torch_out)

    print('Running Norm L2 Grad')
    norm_L2 = hyper_semiring_gradient.NormL2()
    kermac_out = \
        norm_L2(
            x=x,
            z=z,
            coefs=coefs,
            grad_kernel_matrix=grad_kernel_matrix,
            debug = debug
        )
    
    torch_out = \
        torch_inefficient_p_norm(
            x=x,
            z=z,
            coefs=coefs,
            grad_kernel_matrix=grad_kernel_matrix,
            p=2.0,
            eps=0.0,
        )
    einsum_out = \
        torch_einsum_L2_norm(
            x=x,
            z=z,
            coefs=coefs,
            grad_kernel_matrix=grad_kernel_matrix
        )
    print("   Against Inefficient P-norm")
    compare_tensors(kermac_out, torch_out)
    print("   Against Torch Einsum L2-norm")
    compare_tensors(kermac_out, einsum_out)

    p_power_grad = torch.tensor([1.3 - 1.0], dtype=torch.float32, device=device)

    print('Running Norm P=1.3 Grad')
    norm_Lp = \
        hyper_semiring_gradient.NormLp(
            epsilon=epsilon,
        )
    kermac_out = \
        norm_Lp(
            x=x,
            z=z,
            coefs=coefs,
            grad_kernel_matrix=grad_kernel_matrix,
            p_power_grad=p_power_grad,
            debug = debug
        )
    
    torch_out = \
        torch_inefficient_p_norm(
            x=x,
            z=z,
            coefs=coefs,
            grad_kernel_matrix=grad_kernel_matrix,
            p=1.3,
            eps=epsilon,
        )
    compare_tensors(kermac_out, torch_out)

if __name__ == '__main__':
    main()
