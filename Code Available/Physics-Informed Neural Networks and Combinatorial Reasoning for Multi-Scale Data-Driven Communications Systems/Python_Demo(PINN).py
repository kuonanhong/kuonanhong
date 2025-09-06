import numpy as np
import torch
import torch.nn as nn
from torch.autograd import grad
import matplotlib.pyplot as plt
import networkx as nx
# Only import PyG if GNN is enabled
# from torch_geometric.data import Data
# from torch_geometric.nn import GATConv
# import torch.nn.functional as F
import os
import time

# --- 0. Setup & Configuration ---
ENABLE_GNN = False # <<<--- SET TO False TO DISABLE GNN FOR DEBUGGING

SEED = 42
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Parameters
GRID_SIZE = 30
K_PARAM = 15.0
NUM_NODES_GNN = 50 # Keep for now, only used if ENABLE_GNN=True
NUM_EPOCHS = 1000 # Reduce epochs for faster testing initially
LR = 1e-3
ALPHA = 1.0
BETA = 0.1
GNN_CONSTRAINT_THRESHOLD = 0.6
GNN_NEIGHBOR_LIMIT = 2

# Create output directory for figures
output_dir = "simulation_figures"
os.makedirs(output_dir, exist_ok=True)

print("--- Configuration Loaded ---")

# --- 1. PDE Ground Truth Generation (Simplified Helmholtz) ---
def generate_helmholtz_ground_truth(grid_size, k):
    """Generates a simple numerical solution for Helmholtz on a grid."""
    print("Generating Helmholtz ground truth...")
    x = np.linspace(0, 1, grid_size)
    y = np.linspace(0, 1, grid_size)
    X, Y = np.meshgrid(x, y)

    m, n = 3, 4
    true_k_sq = (m * np.pi)**2 + (n * np.pi)**2
    print(f"Using analytical solution with m={m}, n={n}. Requires k^2={true_k_sq:.2f}. Provided k={k} (k^2={k**2:.2f}).")
    u_true = np.sin(m * np.pi * X) * np.sin(n * np.pi * Y)

    # Collocation points (interior)
    X_colloc = X[1:-1, 1:-1].flatten()[:, None]
    Y_colloc = Y[1:-1, 1:-1].flatten()[:, None]
    colloc_coords = np.hstack((X_colloc, Y_colloc))

    # Boundary points (Dirichlet BC: u=0)
    bc_coords_list = []
    bc_values_list = []
    # x=0
    bc_coords_list.append(np.hstack([np.zeros_like(y)[:,None], y[:,None]]))
    bc_values_list.append(np.zeros_like(y))
    # x=1
    bc_coords_list.append(np.hstack([np.ones_like(y)[:,None], y[:,None]]))
    bc_values_list.append(np.zeros_like(y))
    # y=0 (excluding corners)
    bc_coords_list.append(np.hstack([x[1:-1][:,None], np.zeros_like(x[1:-1])[:,None]]))
    bc_values_list.append(np.zeros_like(x[1:-1]))
     # y=1 (excluding corners)
    bc_coords_list.append(np.hstack([x[1:-1][:,None], np.ones_like(x[1:-1])[:,None]]))
    bc_values_list.append(np.zeros_like(x[1:-1]))

    bc_coords_np = np.vstack(bc_coords_list)
    bc_values_np = np.concatenate(bc_values_list)[:, None]

    # Convert to tensors
    colloc_coords_t = torch.tensor(colloc_coords, dtype=torch.float32).to(device)
    bc_coords_t = torch.tensor(bc_coords_np, dtype=torch.float32).to(device)
    bc_values_t = torch.tensor(bc_values_np, dtype=torch.float32).to(device)

    print(f"Generated data shapes: colloc={colloc_coords_t.shape}, bc_coords={bc_coords_t.shape}, bc_values={bc_values_t.shape}")
    print("Finished generating Helmholtz ground truth.")
    return colloc_coords_t, bc_coords_t, bc_values_t, X, Y, u_true

# --- 2. PINN Definition ---
class SimplePINN(nn.Module):
    def __init__(self):
        super().__init__()
        print("Initializing PINN model...")
        self.net = nn.Sequential(
            nn.Linear(2, 64), nn.Tanh(),
            nn.Linear(64, 64), nn.Tanh(),
            nn.Linear(64, 64), nn.Tanh(),
            nn.Linear(64, 1)
        )
        self.net.apply(self.init_weights)
        print("PINN model initialized.")

    def init_weights(self, m):
        if isinstance(m, nn.Linear):
            torch.nn.init.xavier_uniform_(m.weight)
            m.bias.data.fill_(0.01)

    def forward(self, x):
        return self.net(x)

def pinn_loss(model, colloc_coords, bc_coords, bc_values, k):
    """Calculates PINN loss (PDE residual + BC loss)."""
    # Ensure inputs are on the correct device
    colloc_coords = colloc_coords.to(model.net[0].weight.device)
    bc_coords = bc_coords.to(model.net[0].weight.device)
    bc_values = bc_values.to(model.net[0].weight.device)

    # PDE Residual Loss
    colloc_coords.requires_grad_(True)
    u_colloc = model(colloc_coords)

    # Check for NaNs in model output
    if torch.isnan(u_colloc).any():
        print("NaN detected in PINN output (u_colloc)!")
        return torch.tensor(float('nan')), torch.tensor(float('nan'))

    # Calculate gradients safely
    try:
        grads = grad(u_colloc, colloc_coords, grad_outputs=torch.ones_like(u_colloc), create_graph=True, allow_unused=False)[0]
        u_x = grads[:, 0:1]
        u_y = grads[:, 1:2]

        u_xx = grad(u_x, colloc_coords, grad_outputs=torch.ones_like(u_x), create_graph=True, allow_unused=False)[0][:, 0:1]
        u_yy = grad(u_y, colloc_coords, grad_outputs=torch.ones_like(u_y), create_graph=True, allow_unused=False)[0][:, 1:2]
    except RuntimeError as e:
         print(f"Error during gradient calculation: {e}")
         # Print shapes and check requires_grad status
         print(f"u_colloc shape: {u_colloc.shape}, requires_grad: {u_colloc.requires_grad}")
         print(f"colloc_coords shape: {colloc_coords.shape}, requires_grad: {colloc_coords.requires_grad}")
         if 'grads' in locals():
             print(f"grads shape: {grads.shape}, requires_grad: {grads.requires_grad}")
             print(f"u_x shape: {u_x.shape}, requires_grad: {u_x.requires_grad}")
             print(f"u_y shape: {u_y.shape}, requires_grad: {u_y.requires_grad}")
         return torch.tensor(float('inf')), torch.tensor(float('inf')) # Return high loss on error


    # Check for NaNs in gradients
    if torch.isnan(u_xx).any() or torch.isnan(u_yy).any():
        print("NaN detected in second derivatives (u_xx or u_yy)!")
        return torch.tensor(float('nan')), torch.tensor(float('nan'))


    pde_residual = u_xx + u_yy + k**2 * u_colloc
    loss_pde = torch.mean(pde_residual**2)

    # Boundary Condition Loss
    u_bc_pred = model(bc_coords)
    loss_bc = torch.mean((u_bc_pred - bc_values)**2)

    # Detach coordinates after use (though requires_grad_(False) should be sufficient)
    colloc_coords = colloc_coords.detach()

    if torch.isnan(loss_pde) or torch.isnan(loss_bc):
        print("NaN detected in loss components!")

    return loss_pde, loss_bc * 10.0

# --- 3. GNN Definition & Graph Generation (DISABLED IF ENABLE_GNN=False) ---
if ENABLE_GNN:
    # Only import if needed
    from torch_geometric.data import Data
    from torch_geometric.nn import GATConv
    import torch.nn.functional as F

    def generate_graph_data(num_nodes, pinn_model, X_domain, Y_domain, u_true_domain, k):
        # ... (Keep the function definition as before) ...
        pass # Replace pass with the original function body

    class SimpleGNN(torch.nn.Module):
        # ... (Keep the class definition as before) ...
        pass # Replace pass with the original class body

    def calculate_constraint_violation(predicted_alloc_probs, adj, neighbor_limit):
         # ... (Keep the function definition as before) ...
        # Let's simplify for debugging: return 0 penalty initially
        return 0.0
        # pass # Replace pass with the original function body

    def gnn_loss(gnn_output_logits, gnn_data, adj, neighbor_limit):
        # ... (Keep the function definition as before) ...
        pass # Replace pass with the original function body

# --- 4. Training ---
pinn_model = SimplePINN().to(device)

if ENABLE_GNN:
     print("Initializing GNN...")
     gnn_model = SimpleGNN(num_node_features=3, num_classes=1).to(device)
     optimizer = torch.optim.Adam(
         list(pinn_model.parameters()) + list(gnn_model.parameters()),
         lr=LR
     )
     print("GNN Initialized. Using joint optimizer.")
else:
     optimizer = torch.optim.Adam(pinn_model.parameters(), lr=LR)
     print("GNN Disabled. Using optimizer for PINN only.")


print("Preparing training data...")
colloc_coords_t, bc_coords_t, bc_values_t, X_grid, Y_grid, u_true_grid = generate_helmholtz_ground_truth(GRID_SIZE, K_PARAM)

if ENABLE_GNN:
    print("Generating initial graph data...")
    # Pass dummy values if pinn_model isn't fully ready? Or ensure pinn is somewhat trained first?
    # Let's assume pinn_model is initialized, predictions might be random initially.
    gnn_data_template, graph_adj = generate_graph_data(NUM_NODES_GNN, pinn_model, X_grid, Y_grid, u_true_grid, K_PARAM)
    print("Graph data generated.")


# Training Loop
losses_physics = []
losses_bc = []
losses_pde = [] # Added separate pde loss tracking
losses_joint = []
if ENABLE_GNN:
    losses_comb = []
    losses_alloc = []
    losses_penalty = []


print("Starting training loop...")
start_time = time.time()

for epoch in range(NUM_EPOCHS):
    pinn_model.train()
    if ENABLE_GNN:
        gnn_model.train()

    optimizer.zero_grad()

    # --- PINN Loss Calculation ---
    try:
        loss_pde_val, loss_bc_val = pinn_loss(pinn_model, colloc_coords_t, bc_coords_t, bc_values_t, K_PARAM)

        # Check for NaN/Inf losses immediately
        if torch.isnan(loss_pde_val) or torch.isinf(loss_pde_val) or \
           torch.isnan(loss_bc_val) or torch.isinf(loss_bc_val):
            print(f"Epoch {epoch}: NaN or Inf detected in PINN losses. Stopping.")
            break

        loss_physics = loss_pde_val + loss_bc_val

    except Exception as e:
        print(f"Epoch {epoch}: Exception during PINN loss calculation: {e}")
        break # Stop training on error


    # --- GNN Data Preparation & Loss Calculation (Only if enabled) ---
    if ENABLE_GNN:
        loss_comb = torch.tensor(0.0).to(device) # Default value
        loss_alloc = torch.tensor(0.0).to(device)
        loss_penalty = torch.tensor(0.0).to(device)
        try:
            # Get updated PINN values at GNN node locations
            pinn_model.eval() # Use eval mode for stable predictions
            with torch.no_grad(): # No need for grads from PINN prediction to flow back TO PINN here
                 node_pinn_values_updated = pinn_model(gnn_data_template.pos.to(device))
            pinn_model.train() # Back to train mode

            gnn_data_updated = Data(
                x=torch.cat([gnn_data_template.pos.to(device), node_pinn_values_updated], dim=1),
                edge_index=gnn_data_template.edge_index.to(device),
                y=gnn_data_template.y.to(device),
                pos=gnn_data_template.pos.to(device)
            )

            gnn_output_logits = gnn_model(gnn_data_updated)
            loss_comb_val, loss_alloc_val, loss_penalty_val = gnn_loss(gnn_output_logits, gnn_data_updated, graph_adj, GNN_NEIGHBOR_LIMIT)

            # Check for NaN/Inf losses
            if torch.isnan(loss_comb_val) or torch.isinf(loss_comb_val):
                 print(f"Epoch {epoch}: NaN or Inf detected in GNN loss. Skipping GNN update.")
                 # Decide how to handle: skip GNN part of loss, or stop? Let's skip GNN loss for this epoch.
                 loss_comb = torch.tensor(0.0, requires_grad=True).to(device) # Use a zero loss that requires grad
            else:
                 loss_comb = loss_comb_val
                 loss_alloc = loss_alloc_val
                 loss_penalty = loss_penalty_val

        except Exception as e:
             print(f"Epoch {epoch}: Exception during GNN loss calculation: {e}")
             loss_comb = torch.tensor(0.0, requires_grad=True).to(device) # Assign zero loss on error


    # --- Joint Loss & Backpropagation ---
    if ENABLE_GNN:
        joint_loss = ALPHA * loss_physics + BETA * loss_comb
    else:
        joint_loss = loss_physics # Only PINN loss if GNN is disabled

    # Check loss before backward
    if torch.isnan(joint_loss) or torch.isinf(joint_loss):
         print(f"Epoch {epoch}: NaN or Inf detected in final joint_loss. Stopping.")
         break

    try:
        joint_loss.backward()
        # Optional: Gradient clipping if gradients explode
        # torch.nn.utils.clip_grad_norm_(pinn_model.parameters(), max_norm=1.0)
        # if ENABLE_GNN:
        #     torch.nn.utils.clip_grad_norm_(gnn_model.parameters(), max_norm=1.0)

        optimizer.step()
    except RuntimeError as e:
        print(f"Epoch {epoch}: RuntimeError during backward() or step(): {e}")
        # Often indicates issues with graph connectivity, NaN in grads, etc.
        break # Stop training


    # Logging
    losses_pde.append(loss_pde_val.item())
    losses_bc.append(loss_bc_val.item())
    losses_joint.append(joint_loss.item())
    if ENABLE_GNN:
        losses_comb.append(loss_comb.item())
        losses_alloc.append(loss_alloc.item())
        # Ensure penalty is a scalar number for logging
        losses_penalty.append(loss_penalty.item() if torch.is_tensor(loss_penalty) else loss_penalty)


    if epoch % 100 == 0 or epoch == NUM_EPOCHS - 1:
        log_msg = f"Epoch {epoch}/{NUM_EPOCHS} - Time: {time.time() - start_time:.2f}s"
        log_msg += f" - Joint Loss: {joint_loss.item():.4e}"
        log_msg += f" - PINN Loss (PDE={loss_pde_val.item():.4e}, BC={loss_bc_val.item():.4e})"
        if ENABLE_GNN:
             log_msg += f" - GNN Loss (Alloc={loss_alloc.item():.4e}, Penalty={losses_penalty[-1]:.4e})"
        print(log_msg)


end_time = time.time()
print(f"Training finished in {end_time - start_time:.2f} seconds.")

# --- 5. Evaluation and Plotting ---
print("Starting evaluation and plotting...")
pinn_model.eval()
if ENABLE_GNN:
    gnn_model.eval()

# 5.1 PINN Prediction Comparison (Always run this part)
print("Generating PINN comparison plot...")
grid_coords_np = np.hstack((X_grid.flatten()[:,None], Y_grid.flatten()[:,None]))
grid_coords_t = torch.tensor(grid_coords_np, dtype=torch.float32).to(device)

with torch.no_grad():
    u_pred_flat = pinn_model(grid_coords_t).cpu().numpy()
u_pred_grid = u_pred_flat.reshape(X_grid.shape)
pde_error = np.abs(u_true_grid - u_pred_grid)

# Check if prediction contains NaNs
if np.isnan(u_pred_grid).any():
    print("WARNING: NaN values found in PINN final prediction!")
    u_pred_grid = np.nan_to_num(u_pred_grid) # Replace NaNs for plotting
    pde_error = np.nan_to_num(pde_error)

fig_pinn, axes = plt.subplots(1, 3, figsize=(18, 5))
vmin = np.nanmin(u_true_grid) # Use nanmin/nanmax
vmax = np.nanmax(u_true_grid)

try:
    im0 = axes[0].pcolormesh(X_grid, Y_grid, u_true_grid, cmap='viridis', vmin=vmin, vmax=vmax, shading='gouraud')
    axes[0].set_title("PDE Ground Truth (Analytical)")
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("y")
    fig_pinn.colorbar(im0, ax=axes[0])

    im1 = axes[1].pcolormesh(X_grid, Y_grid, u_pred_grid, cmap='viridis', vmin=vmin, vmax=vmax, shading='gouraud')
    axes[1].set_title("PINN Prediction")
    axes[1].set_xlabel("x")
    axes[1].set_ylabel("y")
    fig_pinn.colorbar(im1, ax=axes[1])

    # Determine error plot range, handle potential NaNs
    error_vmax = np.nanmax(pde_error)
    if error_vmax == 0: error_vmax = 1.0 # Avoid range issue if error is zero everywhere
    im2 = axes[2].pcolormesh(X_grid, Y_grid, pde_error, cmap='inferno', vmin=0, vmax=error_vmax, shading='gouraud')
    axes[2].set_title("Absolute Error |True - Pred|")
    axes[2].set_xlabel("x")
    axes[2].set_ylabel("y")
    fig_pinn.colorbar(im2, ax=axes[2])

    plt.tight_layout()
    fig_pinn_path = os.path.join(output_dir, "figure_pinn_comparison.png")
    plt.savefig(fig_pinn_path)
    print(f"Saved PINN comparison plot to {fig_pinn_path}")
except Exception as e:
    print(f"Error during PINN plotting: {e}")
finally:
    plt.close(fig_pinn)


# 5.2 GNN Allocation Result Visualization (Only if enabled and successful)
if ENABLE_GNN and 'gnn_data_template' in locals(): # Check if GNN part ran
    print("Generating GNN allocation plot...")
    # (Keep the GNN plotting code from the original script here)
    # Make sure to handle potential NaNs in gnn_pred_probs if necessary
    try:
        # Get final GNN predictions
        with torch.no_grad():
            node_pinn_values_final = pinn_model(gnn_data_template.pos.to(device))
            gnn_data_final = Data(
                x=torch.cat([gnn_data_template.pos.to(device), node_pinn_values_final], dim=1),
                edge_index=gnn_data_template.edge_index.to(device),
                y=gnn_data_template.y.to(device),
                pos=gnn_data_template.pos.to(device)
            )
            gnn_output_final_logits = gnn_model(gnn_data_final)
            gnn_pred_probs = torch.sigmoid(gnn_output_final_logits).cpu().numpy().flatten()
            gnn_pred_alloc = (gnn_pred_probs > 0.5).astype(int)

        target_alloc_np = gnn_data_template.y.cpu().numpy().flatten()
        node_coords_np = gnn_data_template.pos.cpu().numpy()

        # Check for NaNs
        if np.isnan(gnn_pred_probs).any():
             print("WARNING: NaN detected in final GNN probabilities!")
             gnn_pred_alloc = np.nan_to_num(gnn_pred_alloc > 0.5).astype(int) # Handle NaNs

        fig_gnn, ax = plt.subplots(1, 1, figsize=(8, 7))
        im_bg = ax.pcolormesh(X_grid, Y_grid, u_pred_grid, cmap='viridis', alpha=0.6, shading='gouraud', vmin=vmin, vmax=vmax)
        fig_gnn.colorbar(im_bg, ax=ax, label="PINN Predicted Value (u)")

        correct_true_pos = (gnn_pred_alloc == 1) & (target_alloc_np == 1)
        correct_true_neg = (gnn_pred_alloc == 0) & (target_alloc_np == 0)
        false_pos = (gnn_pred_alloc == 1) & (target_alloc_np == 0)
        false_neg = (gnn_pred_alloc == 0) & (target_alloc_np == 1)

        ax.scatter(node_coords_np[correct_true_pos, 0], node_coords_np[correct_true_pos, 1], c='green', marker='o', s=80, label='Correctly Allocated (TP)', edgecolors='k', alpha=0.8)
        ax.scatter(node_coords_np[correct_true_neg, 0], node_coords_np[correct_true_neg, 1], c='gray', marker='x', s=80, label='Correctly Not Allocated (TN)', alpha=0.8)
        ax.scatter(node_coords_np[false_pos, 0], node_coords_np[false_pos, 1], c='red', marker='o', s=80, label='Incorrectly Allocated (FP)', edgecolors='k', alpha=0.8)
        ax.scatter(node_coords_np[false_neg, 0], node_coords_np[false_neg, 1], c='orange', marker='x', s=80, label='Incorrectly Not Allocated (FN)', alpha=0.8)

        ax.set_title(f"GNN Allocation Results (N={NUM_NODES_GNN})")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.legend(fontsize=8, loc='upper right')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        plt.tight_layout()
        fig_gnn_path = os.path.join(output_dir, "figure_gnn_allocation.png")
        plt.savefig(fig_gnn_path)
        print(f"Saved GNN allocation plot to {fig_gnn_path}")
    except Exception as e:
         print(f"Error during GNN plotting: {e}")
    finally:
         plt.close(fig_gnn)


# 5.3 Training Loss Curves
print("Generating training loss plot...")
# Check if loss lists are populated
if not losses_joint:
     print("No loss data recorded, skipping loss plot.")
else:
    fig_loss, axes = plt.subplots(2, 2, figsize=(12, 10))
    epochs_ran = range(len(losses_joint)) # Use actual length in case of early stopping

    axes[0, 0].plot(epochs_ran, losses_joint, label='Joint Loss')
    axes[0, 0].set_yscale('log')
    axes[0, 0].set_title('Total Joint Loss (Log Scale)')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Loss')
    axes[0, 0].grid(True, which='both', linestyle='--', linewidth=0.5)
    axes[0, 0].legend()

    axes[0, 1].plot(epochs_ran, losses_pde, label='PDE Residual Loss')
    axes[0, 1].plot(epochs_ran, losses_bc, label='Boundary Condition Loss')
    axes[0, 1].set_yscale('log')
    axes[0, 1].set_title('PINN Losses (Log Scale)')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Loss')
    axes[0, 1].grid(True, which='both', linestyle='--', linewidth=0.5)
    axes[0, 1].legend()

    if ENABLE_GNN and losses_comb: # Only plot GNN losses if enabled and recorded
        axes[1, 0].plot(epochs_ran, losses_comb, label='Total GNN Loss')
        axes[1, 0].set_yscale('log')
        axes[1, 0].set_title('Total GNN/Combinatorial Loss (Log Scale)')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Loss')
        axes[1, 0].grid(True, which='both', linestyle='--', linewidth=0.5)
        axes[1, 0].legend()

        axes[1, 1].plot(epochs_ran, losses_alloc, label='GNN Allocation Loss (BCE)')
        axes[1, 1].plot(epochs_ran, losses_penalty, label='Constraint Penalty')
        # axes[1, 1].set_yscale('log') # Penalty might be zero often
        axes[1, 1].set_title('GNN Loss Components')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Loss / Penalty')
        axes[1, 1].grid(True, which='both', linestyle='--', linewidth=0.5)
        axes[1, 1].legend()
    else:
        # Clear unused GNN plots if GNN was disabled
        fig_loss.delaxes(axes[1,0])
        fig_loss.delaxes(axes[1,1])


    plt.suptitle("Training Loss Evolution")
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    fig_loss_path = os.path.join(output_dir, "figure_training_losses.png")
    plt.savefig(fig_loss_path)
    print(f"Saved training loss plot to {fig_loss_path}")
    plt.close(fig_loss)


print("--- Simulation Finished ---")