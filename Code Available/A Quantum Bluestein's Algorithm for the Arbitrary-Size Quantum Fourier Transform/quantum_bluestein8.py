import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT, Diagonal
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt

# Parameters
N = 5
m = int(np.ceil(np.log2(2*N - 1)))
M = 2**m  # workspace size >= 2N-1
alpha = None

# Random complex input (normalized for quantum state)
x = np.random.randn(N) + 1j*np.random.randn(N)
x = x / np.linalg.norm(x)  # ensure input state is normalized

# Build the quantum circuit: m qubits for data, 1 ancilla qubit
qc = QuantumCircuit(m+1)
main_qubits = list(range(m))      # indices 0..m-1 for main register
anc = m                           # last qubit as ancilla

# 1) Input chirp: diag(e^{-iπ j^2/N})
diag_chirp = np.exp(-1j * np.pi * (np.arange(M)**2) / N)
qc.append(Diagonal(diag_chirp), main_qubits)

# 2) Forward QFT on main qubits (normalized)
qc.append(QFT(num_qubits=m, do_swaps=True, inverse=False), main_qubits)

# 3) Block-encoded convolution: build unitary on m+1 qubits
#    Compute FFT of chirp kernel b_j = exp(iπ j^2/N), extended symmetrically
b = np.zeros(M, dtype=complex)
b[:N] = np.exp(+1j * np.pi * (np.arange(N)**2) / N)
for k in range(1, N):
    b[M-k] = b[k]
B = np.fft.fft(b)               # length-M FFT of b
alpha = np.max(np.abs(B))      # normalization factor
# Construct 2M x 2M unitary U for ancilla block-encoding
U = np.zeros((2*M, 2*M), dtype=complex)
for k in range(M):
    c = B[k] / alpha
    # ensure |c| <= 1 numerically
    if abs(c) > 1: c = c/abs(c)  # clip any tiny overshoot
    d = np.sqrt(max(0, 1 - abs(c)**2))
    # Map |k>|0> -> c|k>|0> + d|k>|1>, and complete to a 2x2 block:
    U[k, k] = c
    U[k+M, k] = d
    U[k, k+M] = -np.conj(d)
    U[k+M, k+M] = np.conj(c)
# Apply the unitary to (main,anc) with main-qubits as bits [0..m-1] and ancilla bit as m
from qiskit.circuit.library import UnitaryGate
qc.append(UnitaryGate(U), main_qubits + [anc])

# 4) Inverse QFT on main register
qc.append(QFT(num_qubits=m, do_swaps=True, inverse=True), main_qubits)

# 5) Output de-chirp: diag(e^{-iπ k^2/N})
diag_dechirp = np.exp(-1j * np.pi * (np.arange(M)**2) / N)
qc.append(Diagonal(diag_dechirp), main_qubits)

# Prepare initial state |psi_in>: embed x into state |0> ancilla, register of size M
# Use Statevector to initialize main register; ancilla starts in |0>
psi0 = np.zeros(2**(m+1), dtype=complex)
# main index j corresponds to state |j> on first m bits (ancilla=0)
# Build statevector: ancilla is LSB or MSB? (we appended ancilla as last qubit,
# so ordering is [q0,...,q_{m-1}, ancilla] with ancilla as MSB).
for j in range(N):
    idx = j  # since j < M and ancilla=0, index = j in little-endian ordering
    psi0[idx] = x[j]
# Normalize (should already be normalized from x)
psi0 = psi0 / np.linalg.norm(psi0)

# Simulate the circuit to get final statevector
final_state = Statevector(psi0).evolve(qc)

# Extract amplitudes where ancilla=0 (indices 0..M-1)
psi_main = final_state.data[:M]
# Postselect ancilla=0 branch and renormalize
psi_main = psi_main / np.linalg.norm(psi_main)
# Apply global scaling alpha and remove global phase
psi_main = psi_main * alpha
# Align global phase to classical DFT: match index-0 phase
classical = np.fft.fft(x)    # classical DFT (unnormalized amplitudes)
# Compute phase difference using first nonzero element
k0 = 0
if abs(psi_main[k0]) > 1e-8 and abs(classical[k0]) > 1e-8:
    phase = np.angle(classical[k0] / psi_main[k0])
else:
    phase = 0
psi_main *= np.exp(1j * phase)

# Compute errors and prepare plots
X_QBA = psi_main[:N]
X_DFT = classical
error = np.abs(X_QBA - X_DFT)

indices = np.arange(N)
plt.figure(figsize=(8, 6))
plt.subplot(3,1,1)
plt.stem(indices, np.abs(X_DFT), linefmt='C0-', markerfmt='C0o', label='Classical |FFT|')
plt.stem(indices, np.abs(X_QBA), linefmt='C1--', markerfmt='C1x', label='QBA |output|')
plt.ylabel('Magnitude')
plt.legend()

plt.subplot(3,1,2)
plt.stem(indices, np.angle(X_DFT), linefmt='C0-', markerfmt='C0o', label='Classical ∠FFT')
plt.stem(indices, np.angle(X_QBA), linefmt='C1--', markerfmt='C1x', label='QBA ∠output')
plt.ylabel('Phase (rad)')
plt.legend()

plt.subplot(3,1,3)
plt.stem(indices, error, linefmt='C2-', markerfmt='C2s')
plt.xlabel('Index $k$')
plt.ylabel('Absolute Error')
plt.tight_layout()
plt.savefig("block-encoded convolution(an ancilla qubit).png")
plt.show()