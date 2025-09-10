import numpy as np
import torch

def helmholtz_ground_truth(nx=3, ny=4):
    # u(x,y)=sin(nxπx) sin(nyπy), choose k^2=(nx^2+ny^2)π^2 ⇒ Δu + k^2 u = 0
    k = np.pi * np.sqrt(nx**2 + ny**2)
    def u_true(xy):  # xy: (...,2)
        x, y = xy[...,0], xy[...,1]
        return torch.sin(nx*np.pi*x) * torch.sin(ny*np.pi*y)
    return u_true, k

def sample_points(n_int=900, n_bnd=160, device="cpu"):
    # Interior grid in (0,1)^2, boundary on square
    #xs = torch.linspace(0,1,int(np.sqrt(n_int))+2, device=device)
    xs = torch.linspace(0, 1, int(np.sqrt(n_int)) + 2, device=device, dtype=torch.float32)
    X, Y = torch.meshgrid(xs, xs, indexing="ij")
    pts = torch.stack([X.flatten(), Y.flatten()], dim=-1)
    # interior exclude boundary
    mask = (pts[:,0]>0) & (pts[:,0]<1) & (pts[:,1]>0) & (pts[:,1]<1)
    x_int = pts[mask][:n_int].clone().requires_grad_(True)

    # boundary sampling
    #xb = torch.rand(n_bnd//4, device=device)
    xb = torch.rand(n_bnd // 4, device=device, dtype=torch.float32)
    ones = torch.ones_like(xb); zeros = torch.zeros_like(xb)
    b1 = torch.stack([xb, zeros], -1)
    b2 = torch.stack([xb, ones], -1)
    b3 = torch.stack([zeros, xb], -1)
    b4 = torch.stack([ones, xb], -1)
    x_bnd = torch.cat([b1,b2,b3,b4],0).requires_grad_(True)
    return x_int, x_bnd

def random_graph(n=50, radius=0.2, device="cpu"):
    # Random node positions and radius graph
    #pos = torch.rand((n,2), device=device)
    pos = torch.rand((n, 2), device=device, dtype=torch.float32)
    # adjacency by radius
    dist = torch.cdist(pos, pos)
    A = (dist <= radius).float()
    # ensure self loops
    A.fill_diagonal_(1.0)
    return pos, A
