import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Define the phonon dispersion function (simulated)
def phonon_dispersion(k, k_max, omega_max):
    omega = omega_max * np.abs(np.sin(np.pi * k / k_max))
    return omega

# Generate wavevector data
k_max = 10  # Maximum wavevector
k = np.linspace(0, k_max, 500)
omega_max = 5  # Maximum frequency
omega = phonon_dispersion(k, k_max, omega_max)

# Add noise to simulate experimental data
np.random.seed(42)
noise = np.random.normal(0, omega_max * 0.05, k.shape)  # 5% noise level
omega_noisy = omega + noise

# Prepare the dataset
X = k.reshape(-1, 1)
y = omega_noisy

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Define the custom periodic kernel
def periodic_kernel(X, Y, l=1.0, p=10.0):
    pairwise_diff = np.subtract.outer(X[:,0], Y[:,0])
    K = np.exp(-2 * (np.sin(np.pi * pairwise_diff / p) ** 2) / l**2)
    return K

# Custom kernel SVR model
class CustomKernelSVR(SVR):
    def __init__(self, l=1.0, p=10.0, **kwargs):
        super().__init__(kernel='precomputed', **kwargs)
        self.l = l
        self.p = p
    def fit(self, X, y):
        self.X_train_ = X
        K = periodic_kernel(X, X, l=self.l, p=self.p)
        return super().fit(K, y)
    def predict(self, X):
        K = periodic_kernel(X, self.X_train_, l=self.l, p=self.p)
        return super().predict(K)

# List of standard kernels
kernels = ['linear', 'poly', 'rbf']
results = {}

# Train SVM models with standard kernels
for kernel in kernels:
    svm = SVR(kernel=kernel)
    svm.fit(X_train, y_train)
    y_pred = svm.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    results[kernel] = {'model': svm, 'MSE': mse, 'R^2': r2}

# Train the SVM model with the custom kernel
svm_custom = CustomKernelSVR(l=1.0, p=k_max)
svm_custom.fit(X_train, y_train)
y_pred_custom = svm_custom.predict(X_test)
mse_custom = mean_squared_error(y_test, y_pred_custom)
r2_custom = r2_score(y_test, y_pred_custom)
results['custom'] = {'model': svm_custom, 'MSE': mse_custom, 'R^2': r2_custom}

# Plot performance comparison
labels = list(results.keys())
mses = [results[k]['MSE'] for k in labels]
r2s = [results[k]['R^2'] for k in labels]

x_pos = np.arange(len(labels))
width = 0.35
color = 'tab:blue'
fig, ax1 = plt.subplots(figsize=(10, 6))

ax1.set_xlabel('Kernel Function')
ax1.set_ylabel('MSE', fontsize=24)
bars_mse = ax1.bar(x_pos - width/2, mses, width, label='MSE', color='tab:blue')
ax1.tick_params(axis='y', labelcolor=color, labelsize=18)
ax1.set_xticks(x_pos)
ax1.set_xticklabels(labels)

# Add text annotations for MSE
for bar in bars_mse:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2f}', ha='center', va='bottom', fontsize=18, color='black')

ax2 = ax1.twinx()
ax2.set_ylabel('$R^2$', fontsize=24)
bars_r2 = ax2.bar(x_pos + width/2, r2s, width, label='$R^2$', color='tab:red')
ax2.tick_params(axis='y', labelcolor=color, labelsize=18)
# Add text annotations for R^2, and handle negative values for linear and poly
for i, bar in enumerate(bars_r2):
    yval = bar.get_height()
    if yval < 0:  # Handle negative R^2 by placing it above the bar
        ax2.text(bar.get_x() + bar.get_width()/2, 0.02, f'{yval:.2f}', ha='center', va='bottom', fontsize=18, color='black')
    else:
        ax2.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2f}', ha='center', va='bottom', fontsize=18, color='black')

# Adjust legends to be side by side, non-overlapping
ax1_legend = ax1.legend(loc='upper left', bbox_to_anchor=(0, 1))
ax2_legend = ax2.legend(loc='upper left', bbox_to_anchor=(0.15, 1))

#plt.title('Performance Comparison of Different Kernels (Phonon Dispersion)')
plt.tight_layout()
plt.savefig("custom_kernel_real_data.png")
plt.show()
