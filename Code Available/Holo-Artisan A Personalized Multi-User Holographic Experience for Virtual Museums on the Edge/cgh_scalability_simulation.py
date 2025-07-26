import numpy as np
import matplotlib.pyplot as plt

# --- Simulation Parameters ---
# Number of concurrent users to simulate
n_users = np.arange(1, 31)

# --- Performance Assumptions (in milliseconds) ---
# Estimated time to compute a single 1080p phase hologram on one GPU core/unit.
# This is a realistic estimate for an iterative algorithm like Gerchberg-Saxton.
T_CGH_PER_USER = 15.0  # ms

# Real-time interaction deadline (e.g., for 30 frames per second)
REAL_TIME_DEADLINE = 1000 / 30  # ms (approx 33.3 ms)

# --- Calculation ---
# In a perfectly parallel system (one processing unit per user), latency is constant.
# This represents the ideal hardware scenario (e.g., a powerful multi-core GPU).
latency_parallel = np.full_like(n_users, T_CGH_PER_USER)

# In a sequential system (one processing unit for all users), latency scales linearly.
# This represents the bottleneck on a single-threaded processor.
latency_sequential = n_users * T_CGH_PER_USER

# --- Plotting the Results ---
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(8, 5))

# Plot sequential processing load
ax.plot(n_users, latency_sequential, 's-', label='Total Sequential Compute Time', color='purple', linewidth=2)

# Plot the real-time deadline
ax.axhline(y=REAL_TIME_DEADLINE, color='blue', linestyle='--', linewidth=1.5, label=f'Real-time Deadline ({REAL_TIME_DEADLINE:.1f} ms)')

# Formatting the plot
ax.set_xlabel('Number of Concurrent Users', fontsize=12)
ax.set_ylabel('Required Compute Time (ms)', fontsize=12)
ax.set_title('CGH Computational Load Scalability', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.set_xlim(0, 30)
ax.set_ylim(0, max(latency_sequential) * 1.1)
ax.grid(True, which='both', linestyle='--', linewidth=0.5)

# Add text to explain the implication
ax.text(15, 200, 'Sequential processing fails\nto meet real-time demands\nfor >2 users.',
        verticalalignment='center', horizontalalignment='center',
        fontsize=10, bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))

ax.text(15, 50, 'Parallel hardware (e.g., GPU)\nis required to keep latency\nconstant at 15 ms per user.',
        verticalalignment='center', horizontalalignment='center',
        fontsize=10, bbox=dict(boxstyle='round,pad=0.5', fc='lightblue', alpha=0.5))


# Save the figure
plt.savefig('cgh_scalability.pdf', bbox_inches='tight')
print("CGH scalability plot saved to 'cgh_scalability.pdf'")

# Display the plot
plt.show()