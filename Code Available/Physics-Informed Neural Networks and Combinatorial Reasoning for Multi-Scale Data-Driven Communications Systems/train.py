"""
python train.py --epochs 1200 --mps 1
"""
import torch, numpy as np
from data.synthetic_scenes import helmholtz_ground_truth, sample_points, random_graph
from models.pinn import PINN2D, helmholtz_residual
from models.gnn import SimpleGNN
from utils.plots import plot_training, plot_pinn_field
from solvers.wmmse_unroll import wmmse_unroll
import argparse

# Force float32 for MPS compatibility
torch.set_default_dtype(torch.float32)

def device_select(use_mps=True):
    if use_mps and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

def main(args):
    device = device_select(args.mps==1)
    # ===== PINN setup =====
    u_true, k = helmholtz_ground_truth(nx=3, ny=4)
    pinn = PINN2D(hidden=64, depth=4).to(device)
    opt_pinn = torch.optim.Adam(pinn.parameters(), lr=1e-3)
    x_int, x_bnd = sample_points(n_int=1024, n_bnd=256, device=device)

    curves = {"L_phys": [], "L_disc": [], "L_joint": []}

    # ===== GNN setup (toy allocation first) =====
    N = 50
    pos, A = random_graph(n=N, radius=0.2, device=device)
    A = A.to(device=device, dtype=torch.float32)
    # features: [x, y, uθ(x,y)]
    gnn = SimpleGNN(in_dim=3, hid=64).to(device)
    opt_gnn = torch.optim.Adam(gnn.parameters(), lr=1e-3)

    # toy labels for Fig.4-style (threshold=0.6 against ground-truth field)
    with torch.no_grad():
        u_gt_nodes = u_true(pos.to(dtype=torch.float32)).unsqueeze(-1)
    y = (u_gt_nodes > 0.6).float().to(device)

    epochs = args.epochs
    for ep in range(epochs):
        # ---- PINN step ----
        pinn.train(); opt_pinn.zero_grad()
        k_t = torch.tensor(float(k), device=device, dtype=torch.float32)
        r, u_int = helmholtz_residual(pinn, x_int.to(dtype=torch.float32), k_t)
        L_pde = (r**2).mean()
        # Dirichlet: u=0 on boundary for demo (fits our chosen eigenmode)
        u_b = pinn(x_bnd.to(dtype=torch.float32))
        L_bc = (u_b**2).mean()
        L_phys = L_pde + L_bc
        L_phys.backward(); opt_pinn.step()

        # ---- GNN step (toy classification) ----
        gnn.train(); opt_gnn.zero_grad()
        with torch.no_grad():
            u_nodes = pinn(pos.to(dtype=torch.float32)).detach()
        X = torch.cat([pos.to(dtype=torch.float32), u_nodes], dim=1) # (N,3)
        y_hat = gnn(A, X) # (N,1)
        bce = torch.nn.functional.binary_cross_entropy(y_hat, y)
        L_disc = bce
        L_disc.backward(); opt_gnn.step()

        curves["L_phys"].append(L_phys.item())
        curves["L_disc"].append(L_disc.item())
        curves["L_joint"].append(L_phys.item() + L_disc.item())

    # ===== plots for PINN =====
    # generate a grid for visualization
    M = 64
    xs = torch.linspace(0,1,M, device=device, dtype=torch.float32)
    X,Y = torch.meshgrid(xs,xs, indexing="ij")
    grid = torch.stack([X.flatten(),Y.flatten()], dim=-1)
    with torch.no_grad():
        U_t = u_true(grid).unsqueeze(-1)
        U_p = pinn(grid)
    plot_pinn_field(grid.cpu(), U_t.cpu(), U_p.cpu(), out="fig_pinn_field_error.png")

    # training curves
    plot_training(curves, out="fig_training_curves.png")

    # save a minimal checkpoint
    torch.save({"pinn": pinn.state_dict(), "gnn": gnn.state_dict()}, "ckpt.pt")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=1200)
    ap.add_argument("--mps", type=int, default=1)
    args = ap.parse_args()
    main(args)