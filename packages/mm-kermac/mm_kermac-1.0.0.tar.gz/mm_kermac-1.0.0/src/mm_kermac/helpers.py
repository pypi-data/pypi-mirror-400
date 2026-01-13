# SPDX-FileCopyrightText: 2026 MetaMachines LLC
#
# SPDX-License-Identifier: MIT

import torch

def compare_tensors(
    tensor_a,
    tensor_b
):
    diff = tensor_a - tensor_b
    squared_diff = diff ** 2
    mse = torch.mean(squared_diff)
    rmse = torch.sqrt(mse).item()

    abs_error = torch.abs(diff)
    max_abs_error = torch.max(abs_error).item()
    mean_abs_error = torch.mean(abs_error).item()

    print(f"\tRoot Mean Squared Error:     {rmse:.6e}")
    print(f"\tMax Absolute Error:          {max_abs_error:.6e}")
    print(f"\tMean Absolute Error:         {mean_abs_error:.6e}")

def torch_einsum_L2_norm(
    x: torch.Tensor,
    z: torch.Tensor,
    coefs: torch.Tensor,
    grad_kernel_matrix: torch.Tensor
):
    torch_out = torch.einsum('bli,bij,bjd->bljd', coefs, grad_kernel_matrix, z.permute(0,2,1)) - torch.einsum('bli,bij,bid->bljd', coefs, grad_kernel_matrix, x.permute(0,2,1))
    return torch_out.permute(0,1,3,2)

def torch_inefficient_p_norm(
    x: torch.Tensor,                    # (B, D, I)   == tensor_mini_B
    z: torch.Tensor,                    # (B, D, J)   == tensor_mini_D
    coefs: torch.Tensor,                # (B, L, I)   == tensor_mini_C
    grad_kernel_matrix: torch.Tensor,   # (B, I, J)   == tensor_mini_A
    p: float,
    eps: float = 0.0  
):
    """
    Computes the batched version of:
        out[o, n, m] = sum_k c[o,k] * a[k,m] * sign(d[n,m] - b[n,k]) * |d[n,m] - b[n,k]|^(p-1)

    Batched shapes:
      a: (B, I, J)   -> K=I, M=J
      b: (B, D, I)   -> N=D, K=I
      c: (B, L, I)   -> O=L, K=I
      d: (B, D, J)   -> N=D, M=J
      returns: (B, L, D, J)
    """
    # diff[b, n, m, k] = d[b, n, m] - b[b, n, k]
    diff = z[:, :, :, None] - x[:, :, None, :]      # (B, D, J, I)

    if p == 2.0 and eps == 0.0:
        # sign(x)*|x|^(p-1) == x when p=2
        g = diff                                     # (B, D, J, I)
    else:
        g = torch.sign(diff) * diff.abs().clamp_min(eps).pow(p - 1.0)  # (B, D, J, I)

    # out[b, o, n, m] = sum_k c[b,o,k] * a[b,k,m] * g[b,n,m,k]
    # c: (B, L, I), a: (B, I, J), g: (B, D, J, I)  -> einsum over k=I
    out = torch.einsum('bli,bij,bdji->bldj', coefs, grad_kernel_matrix, g)  # (B, L, D, J)
    return out
