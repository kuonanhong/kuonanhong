import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# -------------------------------
# Preprocess
# -------------------------------
def nonlinear_spring_force(x, k, alpha):
    return k * x + alpha * x**3

# Generate data
x = np.linspace(-10, 10, 500)  # Displacement range
k = 10      # Linear coefficient
alpha = 0.5 # Non-linear coefficient
F = nonlinear_spring_force(x, k, alpha)

# Add noise (noise level 5%)
np.random.seed(42)
noise = np.random.normal(0, F.max() * 0.05, x.shape)
F_noisy = F + noise

# Data
X = x.reshape(-1, 1)
y = F_noisy

# Split train/test data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# -------------------------------
# 1. Compare different Kernel's Performance
# -------------------------------
kernels = ['linear', 'poly', 'rbf', 'sigmoid']
results = {}
for kernel in kernels:
    if kernel == 'poly':
        # Polynomial kernel default degree=3
        svm = SVR(kernel=kernel, degree=3)
    else:
        svm = SVR(kernel=kernel)
    svm.fit(X_train, y_train)
    y_pred = svm.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    results[kernel] = {'MSE': mse, 'R2': r2}

labels = list(results.keys())
mses = [results[k]['MSE'] for k in labels]
r2s = [results[k]['R2'] for k in labels]
x_pos = np.arange(len(labels))
width = 0.35

# Bar plot (4 kernels) —— MSE and R^2
plt.figure(figsize=(12,8))
ax1 = plt.gca()

plt.xticks(x_pos, labels, fontsize=22)  # Increase font size for x-axis labels
plt.yticks(fontsize=18)

# Set left y-axis (MSE) to scientific notation
ax1.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
ax1.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))

# Plot MSE bar (left-axis)
bars_mse = ax1.bar(x_pos - width/2, mses, width, label='MSE', color='skyblue')
ax1.set_xlabel('Kernel Function', fontsize=22)
ax1.set_ylabel('MSE', fontsize=18)

# Use twin axes to plot R^2 bar (right-axis)
ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('$R^2$', color=color, fontsize=18)
bars_r2 = ax2.bar(x_pos + width/2, r2s, width, label='$R^2$', color=color)
ax2.tick_params(axis='y', labelcolor=color, labelsize=18)

# Add value notation (MSE use scientific notation)
for bar in bars_mse:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2e}', ha='center', va='bottom', fontsize=18)
for bar in bars_r2:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2f}', ha='center', va='bottom', fontsize=18)

# Legend and twin axes (upper left corner)
leg1 = ax1.legend(loc='upper left', bbox_to_anchor=(0, 1), fontsize=18)
leg2 = ax2.legend(loc='upper left', bbox_to_anchor=(0.2, 1), fontsize=18)
plt.tight_layout()
plt.savefig('polynomial_kernel_real_data.png')
plt.show()

# -------------------------------
# 2. Compare different Polynomial Kernel Degree's Performance
# -------------------------------
degrees = [2, 3, 4]
results_poly = {}
for deg in degrees:
    svm_poly = SVR(kernel='poly', degree=deg)
    svm_poly.fit(X_train, y_train)
    y_pred_poly = svm_poly.predict(X_test)
    mse_poly = mean_squared_error(y_test, y_pred_poly)
    r2_poly = r2_score(y_test, y_pred_poly)
    results_poly[deg] = {'MSE': mse_poly, 'R2': r2_poly}

labels_poly = [f'Degree {d}' for d in degrees]
mses_poly = [results_poly[d]['MSE'] for d in degrees]
r2s_poly = [results_poly[d]['R2'] for d in degrees]
x_pos_poly = np.arange(len(labels_poly))
width = 0.35

# Create figure, set appropriate size and font
fig, ax1_poly = plt.subplots(figsize=(10, 6))
plt.xticks(x_pos_poly, labels_poly, fontsize=22)  # Increase font size for x-axis labels
plt.yticks(fontsize=18)

# Set left y-axis (MSE) to scientific notation
ax1_poly.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
ax1_poly.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))

# Plot MSE bar (left-axis)
bars_mse_poly = ax1_poly.bar(x_pos_poly - width/2, mses_poly, width, label='MSE', color='lightgreen')
ax1_poly.set_xlabel('Polynomial Kernel Degree', fontsize=22)
ax1_poly.set_ylabel('MSE', fontsize=18)

# Create second y-axis and plot R^2 bars
ax2_poly = ax1_poly.twinx()
color = 'tab:purple'
ax2_poly.set_ylabel('$R^2$', color=color, fontsize=18)
bars_r2_poly = ax2_poly.bar(x_pos_poly + width/2, r2s_poly, width, label='$R^2$', color=color)
ax2_poly.tick_params(axis='y', labelcolor=color, labelsize=18)

# Add numerical annotations
for bar in bars_mse_poly:
    yval = bar.get_height()
    ax1_poly.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2e}', ha='center', va='bottom', fontsize=18)
for bar in bars_r2_poly:
    yval = bar.get_height()
    ax2_poly.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2f}', ha='center', va='bottom', fontsize=18)

plt.tight_layout()
plt.savefig('polynomial_of_different_degree.png')
plt.show()
