#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal, self-contained QBA verification script that:
  • Picks a non-power-of-two N (default 5) and creates a random complex vector x
  • Computes the reference (classical) DFT_N(x) exactly (unnormalized DFT)
  • Computes the same result via Bluestein's reduction using length-M FFT, with M = 2^m >= 2N-1
  • (Optional) Builds a Qiskit circuit with QFT_M, Diagonal phases (chirp-in / conv-phase / de-chirp)
    to demonstrate the gate-level structure. The numerical comparison/plots use the NumPy result,
    so the script works even when Qiskit is unavailable.
  • Saves a comparison figure and a CSV of per-index absolute errors for easy inclusion in a paper.

Outputs:
  qiskit_qba_minimal.png
  qiskit_qba_minimal_errors.csv

Run:
  python qiskit_qba_minimal.py

Notes:
  1) We use the standard (unnormalized) DFT definition X_k = sum_j x_j * exp(-2π i j k / N).
  2) The Bluestein implementation below (NumPy path) is algebraically exact up to floating-point error.
  3) If Qiskit is installed, we also construct a gate-level circuit (not used for the numeric plot),
     with a phase-only diagonal for the conv-phase block to keep the circuit unitary.
"""

import numpy as np
import matplotlib.pyplot as plt
import csv

# -----------------------------
# Utilities
# -----------------------------

def next_power_of_two(n: int) -> int:
    """Return the smallest power of two >= n."""
    m = 1
    while m < n:
        m <<= 1
    return m


def dft_matrix(N: int) -> np.ndarray:
    """Unnormalized DFT matrix: [W^{jk}] with W = exp(-2π i / N)."""
    j = np.arange(N).reshape(-1, 1)
    k = np.arange(N).reshape(1, -1)
    W = np.exp(-2j * np.pi * j * k / N)
    return W


def classical_dft(x: np.ndarray) -> np.ndarray:
    """Compute unnormalized DFT via matrix multiplication (exact reference up to fp error)."""
    N = x.shape[0]
    F = dft_matrix(N)
    return F @ x


def bluestein_dft_numpy(x: np.ndarray) -> np.ndarray:
    """Compute unnormalized DFT using Bluestein's algorithm via FFT-based convolution.

    This follows the identity:
        X_k = e^{-π i k^2 / N} * sum_j [ x_j * e^{-π i j^2 / N} * e^{+π i (k-j)^2 / N} ]
    Implemented as a linear convolution a * b, where
        a_j = x_j * e^{-π i j^2 / N}
        b_j = e^{+π i j^2 / N}
    and packed into a circular convolution of length M >= 2N-1.
    """
    N = x.shape[0]
    M = next_power_of_two(2 * N - 1)

    # Chirp-in (a)
    j = np.arange(N)
    a = x * np.exp(-1j * np.pi * (j ** 2) / N)

    # Build b (length-M) with symmetric packing so that circular conv = linear conv
    b = np.zeros(M, dtype=complex)
    b[:N] = np.exp(+1j * np.pi * (np.arange(N) ** 2) / N)
    # Mirror part for negative indices: b[-j] for j=1..N-1  → indices M-j
    for jj in range(1, N):
        b[M - jj] = b[jj]

    # Zero-pad a to length M
    a_pad = np.zeros(M, dtype=complex)
    a_pad[:N] = a

    # Convolution via FFT/IFFT (NumPy uses unnormalized FFT, IFFT divides by M)
    A = np.fft.fft(a_pad)
    B = np.fft.fft(b)
    y = np.fft.ifft(A * B)  # length-M circular convolution → first N entries match linear conv

    # De-chirp and take first N entries
    k = np.arange(N)
    X = np.exp(-1j * np.pi * (k ** 2) / N) * y[:N]
    return X


# -----------------------------
# Optional: Qiskit circuit build (for demonstration)
# -----------------------------

def build_qba_circuit_qiskit(N: int):
    """If Qiskit is available, build a gate-level circuit for QBA with M=2^m >= 2N-1.
    We use Diagonal gates for chirps (unit-modulus) and a phase-only conv-phase.
    Returns (circ, M). If Qiskit is not installed, returns (None, M).
    """
    try:
        from qiskit import QuantumCircuit
        from qiskit.circuit.library import QFT, Diagonal
    except Exception:
        return None, next_power_of_two(2 * N - 1)

    M = next_power_of_two(2 * N - 1)
    m = int(np.log2(M))

    circ = QuantumCircuit(m, name=f"QBA_N{N}_M{M}")

    # Diagonal 1: chirp-in  exp(-π i j^2 / N)
    diag1 = np.exp(-1j * np.pi * (np.arange(M) ** 2) / N)
    circ.append(Diagonal(diag1), range(m))

    # QFT_M
    circ.append(QFT(m, do_swaps=False), range(m))

    # Diagonal 2: conv-phase – to keep circuit strictly unitary, we take ONLY the phase of FFT(b)
    b = np.zeros(M, dtype=complex)
    b[:N] = np.exp(+1j * np.pi * (np.arange(N) ** 2) / N)
    for jj in range(1, N):
        b[M - jj] = b[jj]
    B = np.fft.fft(b)
    diag2 = np.exp(1j * np.angle(B))  # unit-modulus phase-only version
    circ.append(Diagonal(diag2), range(m))

    # iQFT_M
    circ.append(QFT(m, do_swaps=False).inverse(), range(m))

    # Diagonal 3: de-chirp  exp(-π i k^2 / N)
    diag3 = np.exp(-1j * np.pi * (np.arange(M) ** 2) / N)
    circ.append(Diagonal(diag3), range(m))

    return circ, M


# -----------------------------
# Main: compare DFT_N vs Bluestein (NumPy) and save plots/CSV
# -----------------------------
if __name__ == "__main__":
    np.random.seed(7)

    N = 5  # pick a non-power-of-two size to highlight the use-case
    # Random complex input
    x = np.random.randn(N) + 1j * np.random.randn(N)

    # Reference via exact matrix DFT (unnormalized)
    X_ref = classical_dft(x)

    # Bluestein via FFT-based convolution (NumPy) – algebraically exact up to fp error
    X_blu = bluestein_dft_numpy(x)

    # Absolute error per frequency bin
    err = np.abs(X_ref - X_blu)

    # Save CSV of errors
    csv_path = "qiskit_qba_minimal_errors.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["k", "abs_error", "|X_ref|", "|X_blu|"])
        for k in range(N):
            w.writerow([k, float(err[k]), float(np.abs(X_ref[k])), float(np.abs(X_blu[k]))])

    # Try to also build a Qiskit circuit (for demonstration)
    circ, M = build_qba_circuit_qiskit(N)
    if circ is not None:
        try:
            from qiskit.visualization import circuit_drawer
            # Save the circuit image (text or mpl backend depending on env)
            circuit_drawer(circ, output="mpl").savefig("qiskit_qba_minimal_circuit.png", dpi=200, bbox_inches="tight")
        except Exception:
            # Fallback: print to text file
            with open("qiskit_qba_minimal_circuit.txt", "w", encoding="utf-8") as f:
                f.write(str(circ))

    # Plot: magnitude comparison (left) and absolute error (right)
    k = np.arange(N)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Left: |X|
    axes[0].plot(k, np.abs(X_ref), marker="o", label="|DFT_N(x)| (ref)")
    axes[0].plot(k, np.abs(X_blu), marker="s", linestyle="--", label="|Bluestein(x)| (NumPy)")
    axes[0].set_xlabel("k")
    axes[0].set_ylabel("magnitude")
    axes[0].set_title(f"N={N} comparison (M={M})")
    axes[0].legend()

    # Right: per-bin absolute error
    axes[1].bar(k, err, width=0.6)
    axes[1].set_xlabel("k")
    axes[1].set_ylabel("|DFT - Bluestein|")
    axes[1].set_title("Absolute error per k")

    plt.tight_layout()
    fig.savefig("qiskit_qba_minimal.png", dpi=200)
    print("Saved figure: qiskit_qba_minimal.png")
    print("Saved errors: qiskit_qba_minimal_errors.csv")

    # Also print a quick numeric summary
    print(f"Max |DFT - Bluestein| = {np.max(err):.3e}")
    print(f"Mean |DFT - Bluestein| = {np.mean(err):.3e}")

    # Inform whether a Qiskit circuit was built
    if circ is None:
        print("Qiskit not found: ran NumPy verification only (plots still generated).")
    else:
        print("Qiskit circuit constructed and saved (see qiskit_qba_minimal_circuit.png or .txt).")
