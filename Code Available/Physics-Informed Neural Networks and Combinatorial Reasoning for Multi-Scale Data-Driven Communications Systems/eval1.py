import torch, numpy as np
from data.synthetic_scenes import random_graph
from models.pinn import PINN2D
from models.gnn import SimpleGNN
from utils.plots import plot_alloc_overlay
from solvers.wmmse_unroll import wmmse_unroll

def device_select():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

def main():
    device = device_select()
    # load models
    ckpt = torch.load("ckpt.pt", map_location=device)
    pinn = PINN2D(hidden=64, depth=4).to(device); pinn.load_state_dict(ckpt["pinn"]); pinn.eval()
    gnn  = SimpleGNN(in_dim=3, hid=64).to(device); gnn.load_state_dict(ckpt["gnn"]); gnn.eval()

    # test graph
    pos, A = random_graph(n=50, radius=0.2, device=device)
    with torch.no_grad():
        u_nodes = pinn(pos)
    X = torch.cat([pos, u_nodes], dim=1)
    with torch.no_grad():
        alloc_prob = gnn(A, X)  # (N,1)
    plot_alloc_overlay(pos.cpu().numpy(), alloc_prob, out="fig_gnn_alloc_overlay.png")

    # demonstration of WMMSE unroll on diagonal gains from PINN
    gains = torch.relu(u_nodes.squeeze()) + 1e-3
    p0 = torch.full_like(gains, 0.5)
    p_opt = wmmse_unroll(gains, p0, iters=10)
    print("Mean optimized power:", float(p_opt.mean()))

if __name__ == "__main__":
    main()
