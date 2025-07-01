import numpy as np
from pymatgen.ext.matproj import MPRester
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

#################################
# 1. Read copper (Cu) entries from Materials Project
#################################
API_KEY = "Your API Key"

with MPRester(API_KEY) as m:
    # Search for materials containing Cu; this returns a list of dictionaries
    data = m.summary.search(elements=["Cu"])

#################################
# 2. Extract band gap and density, and filter the data
#################################
band_gaps = []
densities = []

for mat in data:
    bg = mat.get('band_gap')  # use dict access
    dens = mat.get('density')

    # Collect data where band_gap > 0 and density is not None
    if (bg is not None and bg > 0) and (dens is not None):
        band_gaps.append(bg)
        densities.append(dens)

band_gaps = np.array(band_gaps)
densities = np.array(densities)

print("Number of valid band_gap entries =", len(band_gaps))
print("Number of valid density entries =", len(densities))

#################################
# 3. Create a synthetic target: define a smooth sigma = f(band_gap, density)
#################################
# Demonstration function: sigma = exp(-band_gap) * sqrt(density)
targets = np.exp(-band_gaps) * np.sqrt(densities)

# Use [band_gap, density] as features (could include additional features for testing)
X = np.column_stack([band_gaps, densities])
y = targets

#################################
# 4. Split data into training and testing sets and standardize them
#################################
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

scaler_X = StandardScaler()
scaler_y = StandardScaler()

X_train_scaled = scaler_X.fit_transform(X_train)
X_test_scaled = scaler_X.transform(X_test)

y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).ravel()
y_test_scaled = scaler_y.transform(y_test.reshape(-1, 1)).ravel()

#################################
# 5. Train SVR with four different kernels and compare MSE, R2
#################################
kernels = ['rbf', 'linear', 'poly', 'sigmoid']
mse_scores = {}
r2_scores = {}

for kernel in kernels:
    if kernel == 'poly':
        model = SVR(kernel=kernel, degree=3, C=100, gamma='scale')
    else:
        model = SVR(kernel=kernel, C=100, gamma='scale')

    model.fit(X_train_scaled, y_train_scaled)
    y_pred_scaled = model.predict(X_test_scaled)

    # Inverse transform to the original scale for evaluation
    y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).ravel()

    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    mse_scores[kernel] = mse
    r2_scores[kernel] = r2

    print(f"[{kernel}] MSE = {mse:.4f},  R2 = {r2:.4f}")

#################################
# 6. Plot: Two bar charts (MSE and R2), using dual y-axis for Sigmoid
#################################
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# (a) Left chart: MSE for rbf, linear, poly, and sigmoid (dual y-axis for sigmoid)
kernels_left = ['rbf', 'linear', 'poly']
mse_left = [mse_scores[k] for k in kernels_left]
bars_mse = ax1.bar(kernels_left, mse_left, color='b', width=0.7)
ax1.set_ylabel('MSE', color='b', fontsize=16)
ax1.tick_params(axis='y', labelcolor='b')

for bar in bars_mse:
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width() / 2, h, f"{h:.2f}",
             ha='center', va='bottom', color='black', fontsize=12)

# Right twin axis for sigmoid's MSE
ax1_sig = ax1.twinx()
mse_sigmoid = mse_scores['sigmoid']
bar_sig = ax1_sig.bar(['sigmoid'], [mse_sigmoid], color='r', width=0.5)
ax1_sig.set_ylabel("MSE (Sigmoid)", color='r', fontsize=20)
ax1_sig.tick_params(axis='y', labelcolor='r')

for bar in bar_sig:
    h = bar.get_height()
    ax1_sig.text(bar.get_x() + bar.get_width() / 2, h, f"{h:.2f}",
                 ha='center', va='bottom', color='black', fontsize=20)

#ax1.set_title("Mean Squared Error (MSE) for SVM Kernels", fontsize=18)

# (b) Right chart: R² for rbf, linear, poly, and sigmoid (dual y-axis for sigmoid)
r2_left = [r2_scores[k] for k in kernels_left]
bars_r2 = ax2.bar(kernels_left, r2_left, color='b', width=0.7)
ax2.set_ylabel('R²', color='b', fontsize=20)
ax2.tick_params(axis='y', labelcolor='b')

for bar in bars_r2:
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width() / 2, h, f"{h:.2f}",
             ha='center', va='bottom', color='black', fontsize=20)

ax2_sig = ax2.twinx()
r2_sigmoid = r2_scores['sigmoid']
bar_sig_r2 = ax2_sig.bar(['sigmoid'], [r2_sigmoid], color='r', width=0.5)
ax2_sig.set_ylabel("R² (Sigmoid)", color='r', fontsize=20)
ax2_sig.tick_params(axis='y', labelcolor='r')

for bar in bar_sig_r2:
    h = bar.get_height()
    ax2_sig.text(bar.get_x() + bar.get_width() / 2, h, f"{h:.2f}",
                 ha='center', va='bottom', color='black', fontsize=20)

#ax2.set_title("R² Score for SVM Kernels", fontsize=18)

for ax in (ax1, ax2, ax1_sig, ax2_sig):
    ax.tick_params(axis='x')

plt.tight_layout()
plt.savefig("svm_kernel_performance.png")
plt.show()
