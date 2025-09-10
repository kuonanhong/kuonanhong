import torch
import torch.nn as nn

class PINN2D(nn.Module):
    def __init__(self, in_dim=2, hidden=64, depth=4, out_dim=1, act="tanh"):
        super().__init__()
        acts = {"tanh": nn.Tanh(), "relu": nn.ReLU(), "sine": None}
        self.actname = act
        layers = []
        dims = [in_dim] + [hidden]*depth + [out_dim]
        for i in range(len(dims)-2):
            lin = nn.Linear(dims[i], dims[i+1])
            nn.init.xavier_uniform_(lin.weight)
            layers += [lin, acts["tanh"] if act!="sine" else nn.Tanh()]
        lin = nn.Linear(dims[-2], dims[-1])
        nn.init.xavier_uniform_(lin.weight)
        layers.append(lin)
        self.net = nn.Sequential(*layers)

    def forward(self, x):  # x: (...,2)
        return self.net(x)

def helmholtz_residual(u_theta, x, k):
    # r = Δu + k^2 u
    x.requires_grad_(True)
    u = u_theta(x)  # (...,1)
    grads = torch.autograd.grad(u, x, torch.ones_like(u), create_graph=True)[0]  # (...,2)
    u_x = grads[...,0:1]; u_y = grads[...,1:2]
    u_xx = torch.autograd.grad(u_x, x, torch.ones_like(u_x), create_graph=True)[0][...,0:1]
    u_yy = torch.autograd.grad(u_y, x, torch.ones_like(u_y), create_graph=True)[0][...,1:2]
    lap = u_xx + u_yy
    r = lap + (k**2) * u
    return r, u
