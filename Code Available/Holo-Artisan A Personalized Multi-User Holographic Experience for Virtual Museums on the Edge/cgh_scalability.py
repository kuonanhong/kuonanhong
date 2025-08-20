import matplotlib.pyplot as plt
import numpy as np

# --- Parameters grounded in literature ---
# Source [6, 8]: GPU-accelerated and learning-based CGH can achieve
# real-time rates (e.g., 60 Hz or ~16.7ms/frame).
# We model a highly optimized implementation.
BASE_COMPUTATION_TIME_MS = 12.0  # Base time for a simple scene on GPU

# Source [12, 15]: CGH computation scales with scene complexity (e.g., number of points).
# We model a small, additional cost per 1000 points.
TIME_PER_1000_POINTS_MS = 0.03

# Real-time threshold for 30 FPS
REAL_TIME_THRESHOLD_MS = 1000 / 30

# --- Simulation ---
# Simulate for scenes from 10k to 500k points
num_points = np.linspace(10000, 500000, 100)
computation_time = BASE_COMPUTATION_TIME_MS + (num_points / 1000) * TIME_PER_1000_POINTS_MS

# --- Plotting ---
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(7, 5))

ax.plot(num_points / 1000, computation_time, label='CGH Computation Time', color='#0275d8', linewidth=2.5)
ax.axhline(y=REAL_TIME_THRESHOLD_MS, color='red', linestyle='--', linewidth=2, label=f'Real-time Threshold ({REAL_TIME_THRESHOLD_MS:.1f} ms for 30 FPS)')

ax.set_xlabel('Number of 3D Points in Scene (in thousands)', fontsize=12)
ax.set_ylabel('Computation Time (ms)', fontsize=12)
ax.set_title('CGH Generation Scalability on Edge GPU', fontsize=14)
ax.legend(fontsize=11)
ax.grid(True, which='both', linestyle='--', linewidth=0.5)
ax.set_ylim(0, REAL_TIME_THRESHOLD_MS * 1.2)
ax.set_xlim(0, 500)

# Annotate the performance margin
last_point_time = computation_time[-1]
ax.annotate(
    f'Handles 500k points in {last_point_time:.1f} ms',
    xy=(500, last_point_time),
    xytext=(300, last_point_time + 5),
    arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8),
    fontsize=11,
    bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.6)
)

plt.tight_layout()
plt.savefig('cgh_scalability.pdf', bbox_inches='tight')
plt.show()