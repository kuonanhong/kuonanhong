import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# Define the photoelectric effect equation (low energy approximation)
def photoelectric_effect(nu, phi):
    h = 4.135667696e-15  # Planck's constant in eV·s
    E_kin = h * nu - phi
    E_kin[E_kin < 0] = 0  # Kinetic energy can't be negative
    return E_kin

# Generate frequency data for low-energy incident photons
nu = np.linspace(5e14, 7e14, 200)  # Smaller range for faster computation
phi = 2.0  # Work function in eV
E_kin = photoelectric_effect(nu, phi)

# Add noise to simulate experimental data
np.random.seed(42)
noise = np.random.normal(0, E_kin.max() * 0.02, E_kin.shape)  # Noise level set to 2% of max value
E_kin_noisy = E_kin + noise

# Prepare the dataset
X = nu.reshape(-1, 1)  # Reshape frequency into a 2D array for SVM input
y = E_kin_noisy  # Noisy kinetic energy as target

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train SVM model with linear kernel
svm_linear = SVR(kernel='linear')
svm_linear.fit(X_train, y_train)

# Predict using the linear kernel model
y_pred_linear = svm_linear.predict(X_test)

# Calculate performance metrics for the linear kernel
mse_linear = mean_squared_error(y_test, y_pred_linear)
r2_linear = r2_score(y_test, y_pred_linear)

# Train SVM models with other kernels and calculate performance metrics
kernels = ['rbf', 'poly', 'sigmoid']
results = {'linear': {'MSE': mse_linear, 'R2': r2_linear}}

for kernel in kernels:
    svm = SVR(kernel=kernel)
    svm.fit(X_train, y_train)
    y_pred = svm.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    results[kernel] = {'MSE': mse, 'R2': r2}

# Plot performance comparison of different kernels
labels = list(results.keys())
mses = [results[k]['MSE'] for k in labels]
r2s = [results[k]['R2'] for k in labels]

x = np.arange(len(labels))
width = 0.35

fig, ax1 = plt.subplots(figsize=(10, 6))

# Set x-axis labels
ax1.set_xticks(x)
ax1.set_xticklabels(labels, fontsize=24)  # 調大字體大小 2 倍以上

# Plot Mean Squared Error (MSE)
color = 'tab:blue'
ax1.set_xlabel('Kernel')
ax1.set_ylabel('MSE', color=color, fontsize=24)
bars_mse = ax1.bar(x - width/2, mses, width, label='MSE', color=color)
ax1.tick_params(axis='y', labelcolor=color, labelsize=18)
ax1.set_xticks(x)
ax1.set_xticklabels(labels)

# Add text annotations for MSE
for bar in bars_mse:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2e}', ha='center', va='bottom', fontsize=18, color='black')

# Plot R-squared (R^2)
ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('$R^2$', color=color ,fontsize=24)
bars_r2 = ax2.bar(x + width/2, r2s, width, label='$R^2$', color=color)
ax2.tick_params(axis='y', labelcolor=color, labelsize=18)

# Add text annotations for R^2
for bar in bars_r2:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2f}', ha='center', va='bottom', fontsize=18, color='black')

# Set legends to be unified and placed in the upper left without overlapping
ax1_legend = ax1.legend(loc='upper left', bbox_to_anchor=(0, 1))
ax2_legend = ax2.legend(loc='upper left', bbox_to_anchor=(0.2, 1))

#plt.title('Performance Comparison of Different SVM Kernels (Photoelectric Effect)', pad=20)  # Move title slightly down
plt.tight_layout()
plt.savefig("linear_kernel_real_data.png")
plt.show()