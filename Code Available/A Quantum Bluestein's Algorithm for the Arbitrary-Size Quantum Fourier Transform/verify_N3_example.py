import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT, Diagonal
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt

# Parameters
# N=3 is the target DFT size from the paper's pedagogical example
N = 3
# m = ceil(log2(2N-1)) = ceil(log2(5)) = 3 qubits
m = int(np.ceil(np.log2(2*N - 1)))
# M = 2^m = 8. This is the power-of-two workspace size.
M = 2**m  # workspace size >= 2N-1
alpha = None # Normalization factor for block-encoding

# --- Input State from Appendix A.1.1 ---
# The paper specifies the input state:
# |psi_in> = (1/sqrt(2))|1> + (1/sqrt(2))|2>
# This corresponds to the vector x = [0, 1/sqrt(2), 1/sqrt(2)]
x = np.array([0, 1/np.sqrt(2), 1/np.sqrt(2)], dtype=complex)
# Note: The input state is already normalized.
# x = x / np.linalg.norm(x) # This line is not needed

# --- Build the Quantum Circuit ---
# We need m data qubits (0...m-1) and 1 ancilla qubit (m)
qc = QuantumCircuit(m+1)
main_qubits = list(range(m))      # indices 0..m-1 for main register: Qubits [0, 1, 2]
anc = m                           # last qubit as ancilla: Qubit [3]

# --- Step 1: Input Chirp ---
# Apply diag(e^{-i*pi*j^2/N}) for j in [0, ..., M-1]
diag_chirp = np.exp(-1j * np.pi * (np.arange(M)**2) / N)
qc.append(Diagonal(diag_chirp), main_qubits)
qc.barrier()

# --- Step 2: Forward QFT ---
# Apply QFT_M (M=8) on the main register
qc.append(QFT(num_qubits=m, do_swaps=True, inverse=False), main_qubits)
qc.barrier()

# --- Step 3: Block-Encoded Convolution ---
# This is the core of the algorithm.
# We must implement U_conv = diag(FFT_M(b)) unitarily.

# 1. Define the classical kernel b_j = exp(i*pi*j^2/N)
# It must be padded correctly for a linear convolution (M >= 2N-1)
b = np.zeros(M, dtype=complex)

# Positive indices: 0, 1, ..., N-1
b[:N] = np.exp(+1j * np.pi * (np.arange(N)**2) / N)
# Negative indices (for circular convolution): M-k maps to -k
for k in range(1, N):
    b[M-k] = b[k] # Symmetrical part for Bluestein

# 2. Compute the Fourier-domain filter B = FFT_M(b)
B = np.fft.fft(b)               # length-M FFT of b

# 3. Find normalization factor alpha = max(|B_k|)
alpha = np.max(np.abs(B))

# 4. Construct the (m+1)-qubit unitary U for block-encoding
# This matrix will be 2M x 2M
U = np.zeros((2*M, 2*M), dtype=complex)
for k in range(M):
    # c is the amplitude we want to apply
    c = B[k] / alpha
    # Ensure |c| <= 1 (it should be, but guard against precision errors)
    if abs(c) > 1: c = c/abs(c)

    # d is the amplitude that goes to the ancilla |1> state
    d = np.sqrt(max(0, 1 - abs(c)**2)) # max(0,...) for numerical stability

    # This 2x2 block implements the mapping:
    # |k>|0> -> c|k>|0> + d|k>|1>
    # |k>|1> -> -d*|k>|0> + c*|k>|1> (example completion)
    # Mapping to the full (2M x 2M) matrix U:
    # U[row, col]
    U[k, k] = c     # c * |k><k| (ancilla 0 -> 0)
    U[k+M, k] = d   # d * |k+M><k| (ancilla 0 -> 1)
    U[k, k+M] = -np.conj(d)   # -d* * |k><k+M| (ancilla 1 -> 0)
    U[k+M, k+M] = np.conj(c)  # c* * |k+M><k+M| (ancilla 1 -> 1)

# 5. Apply the custom unitary to the circuit
from qiskit.circuit.library import UnitaryGate
qc.append(UnitaryGate(U), main_qubits + [anc])
qc.barrier()

# --- Step 4: Inverse QFT ---
# Apply QFT_M^{-1} (M=8) on the main register
qc.append(QFT(num_qubits=m, do_swaps=True, inverse=True), main_qubits)
qc.barrier()

# --- Step 5: Output De-chirp ---
# Apply diag(e^{-i*pi*k^2/N}) for k in [0, ..., M-1]
diag_dechirp = np.exp(-1j * np.pi * (np.arange(M)**2) / N)
qc.append(Diagonal(diag_dechirp), main_qubits)

# --- State Preparation ---
# Create the M-dimensional initial state |psi_in>|0>
psi0 = np.zeros(2**(m+1), dtype=complex)
# The input state x lives in the j=0..N-1 subspace
# Qiskit's bit ordering is [q_m, ..., q_1, q_0]
# We built the circuit as [q_0, ..., q_{m-1}, anc]
# So, ancilla is the Most Significant Qubit (MSB).
# State |j>|0> corresponds to index j (since ancilla=0)
for j in range(N):
    idx = j  # Index for the |j>|0> state
    psi0[idx] = x[j]
    # psi0 is already normalized because x was.

# --- Simulation ---
# Evolve the initial state through the full QBA circuit
final_state = Statevector(psi0).evolve(qc)

# --- Post-Processing and Analysis ---
# 1. Post-select on the ancilla being |0>
# These are the first M amplitudes (indices 0 to M-1)
psi_main = final_state.data[:M]

# 2. Renormalize the post-selected state (required by projection)
norm = np.linalg.norm(psi_main)
if norm > 1e-9:
    psi_main = psi_main / norm
else:
    print("Warning: Post-selection probability is near zero.")

# 3. Rescale by alpha
# The block-encoding introduced a scaling factor of 1/alpha.
# To get the true DFT amplitudes, we must multiply by alpha.
psi_main = psi_main * alpha

# --- Define the Classical "Ground Truth" ---
# This is the key change to verify Appendix A.1
# Instead of np.fft.fft(x), we use the *theoretically derived*
# result from Appendix A.1.3 of the paper.
# F_3 * x = [1, -0.5, -0.5]
classical = np.array([1, -0.5, -0.5], dtype=complex)

# We also need the N=3 result from np.fft.fft(x) for phase alignment
# Note: np.fft.fft(x) is normalized differently than the paper's F_3
# Let's align to the paper's theoretical result directly.
X_DFT = classical
X_QBA = psi_main[:N] # Get the first N=3 amplitudes

# 4. Align Global Phase
# The QBA result and classical result may differ by a global phase e^{i*phi}.
# We align them to compare their relative amplitudes.
# We find the first non-zero element to align.
k0 = np.argmax(np.abs(X_DFT) > 1e-9) # Find first non-zero index (k0=0)
if abs(X_QBA[k0]) > 1e-9 and abs(X_DFT[k0]) > 1e-9:
    phase = np.angle(X_DFT[k0] / X_QBA[k0])
else:
    phase = 0
X_QBA *= np.exp(1j * phase)

# --- Plotting ---
error = np.abs(X_QBA - X_DFT)
indices = np.arange(N)

print(f"--- QBA Verification N={N}, M={M} ---")
print(f"Input state (x): {x}")
print(f"Theoretical DFT (X_DFT): {np.round(X_DFT, 8)}")
print(f"QBA Output (X_QBA):    {np.round(X_QBA, 8)}")
print(f"Absolute Error: {error}")
print(f"Max Error: {np.max(error)}")

plt.figure(figsize=(8, 6))
plt.suptitle(f"QBA Verification: N={N} (Paper Appendix A.1 Example)", fontsize=14)

# Plot 1: Magnitudes
plt.subplot(3,1,1)
plt.stem(indices, np.abs(X_DFT), linefmt='C0-', markerfmt='C0o', label='Theoretical |DFT| (from A.1.3)')
plt.stem(indices, np.abs(X_QBA), linefmt='C1--', markerfmt='C1x', label='QBA |output|')
plt.ylabel('Magnitude')
plt.legend()
plt.grid(True)

# Plot 2: Phases
plt.subplot(3,1,2)
plt.stem(indices, np.angle(X_DFT), linefmt='C0-', markerfmt='C0o', label='Theoretical ∠DFT (from A.1.3)')
plt.stem(indices, np.angle(X_QBA), linefmt='C1--', markerfmt='C1x', label='QBA ∠output')
plt.ylabel('Phase (rad)')
plt.legend()
plt.grid(True)

# Plot 3: Error
plt.subplot(3,1,3)
plt.stem(indices, error, linefmt='C2-', markerfmt='C2s')
plt.xlabel('Index $k$')
plt.ylabel('Absolute Error')
plt.yscale('log') # Use log scale to see tiny errors
plt.ylim(bottom=1e-18) # Set a floor for the log plot
plt.grid(True)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig("qba_verification_N3_example.png")
plt.show()