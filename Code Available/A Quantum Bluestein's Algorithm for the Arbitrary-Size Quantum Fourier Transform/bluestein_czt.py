
"""
bluestein_czt.py
----------------
NumPy implementation of:
- Direct DFT (reference)
- Bluestein's algorithm for arbitrary-N DFT
- Generic Chirp-Z Transform (CZT)

Also includes a demo CLI:
  $ python bluestein_czt.py --demo
which will:
  1) If "czt_input_signal.csv" exists (columns: t, real, imag), it loads that as the input.
     Otherwise, it generates a multi-tone + narrowband zoom target signal and saves it to CSV.
  2) Runs DFT vs Bluestein and produces "zoom_fft_overview.png".
  3) Runs CZT to zoom into a selected band and produces "czt_zoom_zoomed.png".
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os

def dft_naive(x):
    N = len(x)
    n = np.arange(N)
    k = n.reshape((N,1))
    W = np.exp(-2j*np.pi*k*n/N)
    return W @ x

def next_pow2(n):
    m = 1
    while m < n:
        m <<= 1
    return m

def bluestein_dft(x):
    """
    Compute the exact DFT of x (length N, arbitrary) using Bluestein's algorithm.
    """
    x = np.asarray(x, dtype=complex)
    N = len(x)
    n = np.arange(N)
    a = x * np.exp(-1j*np.pi*(n**2)/N)        # chirp-in
    b = np.exp( 1j*np.pi*(n**2)/N)            # kernel

    # Choose M >= 2N-1 as power of 2 for fast conv
    M = next_pow2(2*N-1)

    # Zero-pad
    a_pad = np.zeros(M, dtype=complex); a_pad[:N] = a
    b_pad = np.zeros(M, dtype=complex); b_pad[:N] = b; b_pad[-(N-1):] = b[1:][::-1]  # circulant embedding

    # FFT-based convolution
    A = np.fft.fft(a_pad)
    B = np.fft.fft(b_pad)
    C = A*B
    c = np.fft.ifft(C)

    # Take the first N entries and de-chirp
    y = c[:N] * np.exp(-1j*np.pi*(n**2)/N)
    return y

def czt(x, M, W, A=1.0):
    """
    Generic Chirp-Z Transform.
      X[k] = sum_{n=0}^{N-1} x[n] * A^{-n} * W^{n k}, for k=0..M-1
    """
    x = np.asarray(x, dtype=complex)
    N = len(x)
    n = np.arange(N)
    k = np.arange(M)
    # Reduce to convolution form (Bluestein-like)
    y = x * (A**(-n)) * (W**(n**2/2))
    g = (W**(-k**2/2))
    # Convolution length
    L = next_pow2(N+M-1)
    Y = np.fft.fft(np.pad(y, (0, L-N)))
    G = np.fft.fft(np.pad(g, (0, L-M)))
    conv = np.fft.ifft(Y*G)
    X = conv[:M] * (W**(k**2/2))
    return X

def _gen_signal(N=1024, fs=1.0):
    t = np.arange(N)/fs
    # Multi-tone plus a close pair
    x = (0.8*np.exp(2j*np.pi*(0.05)*t) +
         0.6*np.exp(2j*np.pi*(0.0515)*t) +
         0.3*np.exp(2j*np.pi*(0.3)*t) +
         0.2*np.exp(2j*np.pi*(0.32)*t))
    # Add a bit of noise
    x += 0.03*(np.random.randn(N)+1j*np.random.randn(N))
    return t, x

def _plot_overview(x, title, fname):
    X_fft = np.fft.fft(x)
    f = np.fft.fftfreq(len(x), d=1.0)
    m = np.abs(X_fft)
    # one-sided plot (0..0.5)
    mask = (f>=0)&(f<=0.5)
    plt.figure(figsize=(7,4))
    plt.plot(f[mask], 20*np.log10(m[mask]+1e-12))
    plt.xlabel('Normalized frequency')
    plt.ylabel('Magnitude (dB)')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(fname, dpi=200)
    plt.close()

def _plot_czt_zoom(x, f_center=0.05, f_span=0.01, M=1024, fname='czt_zoom_zoomed.png'):
    # Map desired band to CZT parameters
    # Frequencies from f_start to f_end
    f_start = f_center - f_span/2
    f_end   = f_center + f_span/2
    # Chirp-Z parameters (normalized frequency -> angle 2πf)
    A = np.exp(1j*2*np.pi*f_start)
    W = np.exp(-1j*2*np.pi*(f_end-f_start)/M)
    Xz = czt(x, M=M, W=W, A=A)
    f_axis = np.linspace(f_start, f_end, M)
    plt.figure(figsize=(7,4))
    plt.plot(f_axis, 20*np.log10(np.abs(Xz)+1e-12))
    plt.xlabel('Normalized frequency')
    plt.ylabel('Magnitude (dB)')
    plt.title('CZT zoom')
    plt.tight_layout()
    plt.savefig(fname, dpi=200)
    plt.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--demo', action='store_true', help='Run demo and generate images.')
    parser.add_argument('--input_csv', type=str, default='czt_input_signal.csv',
                        help='Optional input CSV (columns: t, real, imag). If missing, a demo signal is created and saved here.')
    args = parser.parse_args()

    if args.demo:
        if os.path.exists(args.input_csv):
            df = pd.read_csv(args.input_csv)
            t = df['t'].to_numpy()
            x = df['real'].to_numpy() + 1j*df['imag'].to_numpy()
        else:
            t, x = _gen_signal(N=2048, fs=1.0)
            pd.DataFrame({'t':t, 'real':x.real, 'imag':x.imag}).to_csv(args.input_csv, index=False)

        # DFT vs Bluestein consistency check and overview figure
        X_ref = dft_naive(x[:1024])  # smaller slice for naive
        X_blu = bluestein_dft(x[:1024])
        err = np.linalg.norm(X_ref - X_blu)/np.linalg.norm(X_ref)
        print(f"[check] Bluestein relative error vs DFT on N=1024 slice: {err:.2e}")

        _plot_overview(x, 'FFT overview (one-sided)', 'zoom_fft_overview.png')
        _plot_czt_zoom(x, f_center=0.051, f_span=0.01, M=2048, fname='czt_zoom_zoomed.png')
        print("Generated: zoom_fft_overview.png, czt_zoom_zoomed.png")

if __name__ == '__main__':
    main()
