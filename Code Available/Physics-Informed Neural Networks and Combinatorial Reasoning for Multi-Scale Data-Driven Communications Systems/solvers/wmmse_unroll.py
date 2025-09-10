import torch

def wmmse_unroll(H_diag, p_init, iters=5, noise=1e-2):
    """
    Minimal unrolled WMMSE for single-cell interference channel.
    H_diag: (K,) effective channel gains per user (diagonal approx)
    p_init: (K,) initial powers
    """
    p = p_init.clone()
    K = H_diag.numel()
    for _ in range(iters):
        # receiver gain
        i_plus_n = (H_diag * p).sum() - H_diag * p + noise
        g = (H_diag * p) / (i_plus_n + noise)
        # mmse weight
        e = 1 - g * H_diag * p / (i_plus_n + noise)
        w = 1 / (e + 1e-8)
        # transmit update (project to [0,Pmax])
        num = w * g * H_diag
        den = w * (g**2) * (H_diag + 1e-8)
        p = torch.clamp(num / (den + 1e-8), 0.0, 1.0)
    return p
