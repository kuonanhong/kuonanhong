import matplotlib.pyplot as plt
import numpy as np
import torch

def plot_training(curves, out="fig_training_curves.png"):
    plt.figure()
    for k,v in curves.items():
        plt.plot(v, label=k)
    plt.yscale("log")
    plt.legend(); plt.xlabel("epoch"); plt.ylabel("loss")
    plt.tight_layout(); plt.savefig(out, dpi=200)

def plot_pinn_field(x_grid, u_true, u_pred, out="fig_pinn_field_error.png"):
    # x_grid: (M,2), u_*: (M,1)
    M = int(np.sqrt(x_grid.shape[0]))
    U_t = u_true.reshape(M,M).detach().cpu().numpy()
    U_p = u_pred.reshape(M,M).detach().cpu().numpy()
    E = np.abs(U_t - U_p)

    plt.figure(figsize=(12,3.6))
    for i,(Z,title) in enumerate([(U_t,"Ground Truth"),(U_p,"PINN Pred"),(E,"Abs Error")],1):
        plt.subplot(1,3,i); plt.imshow(Z, origin="lower"); plt.title(title); plt.colorbar()
    plt.tight_layout(); plt.savefig(out, dpi=200)

def plot_alloc_overlay(pos, alloc_prob, u_bg=None, out="fig_gnn_alloc_overlay.png"):
    plt.figure()
    if u_bg is not None:
        # simple background: interpolate by nearest neighbor on a grid if required
        pass
    ap = alloc_prob.detach().cpu().numpy().flatten()
    plt.scatter(pos[:,0], pos[:,1], c=(ap>0.5), cmap="coolwarm", s=40, edgecolors="k")
    plt.title("GNN Allocation (prob>0.5 in red)")
    plt.tight_layout(); plt.savefig(out, dpi=200)
