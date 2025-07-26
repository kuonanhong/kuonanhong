import numpy as np
import matplotlib.pyplot as plt

# --- Simulation Parameters ---
# Number of users to simulate
n_users = np.arange(1, 51)

# --- Edge Architecture Parameters (in milliseconds) ---
# Constant time for local perception and AI inference on an edge device.
# This is low and does not depend on the number of other users.
T_LOCAL_PROC = 35

# --- Cloud Architecture Parameters (in milliseconds) ---
# Average network round-trip time (RTT) to a remote cloud server.
T_NETWORK_RTT = 100
# Base time for the server to render a scene for one user.
T_RENDER_BASE = 50
# Additional processing/rendering time for each concurrent user.
# This models the increasing load on the central server GPU.
T_RENDER_PER_USER = 5

# --- Latency Calculation ---
# Edge latency is constant as processing is local.
latency_edge = np.full_like(n_users, T_LOCAL_PROC, dtype=float)

# Cloud processing time increases linearly with the number of users.
t_cloud_proc = T_RENDER_BASE + (n_users * T_RENDER_PER_USER)
# Total cloud latency is the sum of network RTT and processing time.
latency_cloud = T_NETWORK_RTT + t_cloud_proc

# --- Plotting the Results ---
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(n_users, latency_edge, 'o-', label='Holo-Artisan (Edge-based)', color='green', linewidth=2)
ax.plot(n_users, latency_cloud, 's-', label='Traditional Cloud-based', color='red', linewidth=2)

# Add a horizontal line for the real-time interaction threshold
ax.axhline(y=50, color='blue', linestyle='--', linewidth=1.5, label='Real-time Threshold (50 ms)')

# Formatting the plot
ax.set_xlabel('Number of Concurrent Users', fontsize=12)
ax.set_ylabel('End-to-End Latency (ms)', fontsize=12)
ax.set_title('Simulated Latency Comparison: Edge vs. Cloud Architecture', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.set_xlim(0, 50)
ax.set_ylim(0, max(latency_cloud) * 1.1)
ax.grid(True, which='both', linestyle='--', linewidth=0.5)

# Save the figure to be included in the LaTeX document
plt.savefig('latency_simulation.pdf', bbox_inches='tight')

# Display the plot
plt.show()