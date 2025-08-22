import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Helpers
# ----------------------------
def dft(x):
    N = len(x)
    k = np.arange(N)[:, None]
    n = np.arange(N)[None, :]
    W = np.exp(-2j * np.pi * k * n / N)
    return W @ x

def bluestein_slow(x):
    """O(N^2) 寫法：按定義做 a*b 的線性卷積，再去 chirp。"""
    N = len(x)
    j = np.arange(N)
    a = x * np.exp(-1j * np.pi * (j**2) / N)
    def b(t): return np.exp(1j * np.pi * (t**2) / N)

    y = np.zeros(N, dtype=complex)
    for k in range(N):
        s = 0j
        for jj in range(N):
            s += a[jj] * b(k - jj)  # 線性卷積
        y[k] = s
    c = np.exp(-1j * np.pi * (j**2) / N)
    return c * y

def bluestein_fast(x, M=16):
    """正確的 FFT 實作：用長度 M 的循環卷積來實現線性卷積（對稱嵌入核）。"""
    N = len(x)
    j = np.arange(N)

    # chirp-in
    a = x * np.exp(-1j * np.pi * (j**2) / N)

    # zero-pad a 到長度 M
    A = np.zeros(M, dtype=complex)
    A[:N] = a

    # 正確打包卷積核 b_t = exp(+i pi t^2 / N), t in [-(N-1)..(N-1)]
    B = np.zeros(M, dtype=complex)
    B[0] = 1.0
    for t in range(1, N):
        val = np.exp(1j * np.pi * (t**2) / N)
        B[t] = val
        B[M - t] = val

    # 循環卷積 (FFT-IFTT)
    Y = np.fft.ifft(np.fft.fft(A) * np.fft.fft(B))

    # 取前 N 點，de-chirp
    y = Y[:N]
    c = np.exp(-1j * np.pi * (j**2) / N)
    return c * y

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    np.random.seed(0)
    N, M = 6, 16
    # 隨機複數輸入
    x = np.random.randn(N) + 1j * np.random.randn(N)

    # 三條管線
    X_dft  = dft(x)
    X_slow = bluestein_slow(x)
    X_fast = bluestein_fast(x, M=M)

    # 誤差
    err_slow = np.abs(X_dft - X_slow)
    err_fast = np.abs(X_dft - X_fast)

    print("Max |DFT - Bluestein_slow| =", np.max(err_slow))
    print("Max |DFT - Bluestein_fast| =", np.max(err_fast))

    # 存 CSV（方便論文附檔）
    df = pd.DataFrame({
        "k": np.arange(N),
        "X_dft_real":  np.real(X_dft),
        "X_dft_imag":  np.imag(X_dft),
        "X_bslow_real": np.real(X_slow),
        "X_bslow_imag": np.imag(X_slow),
        "X_bfast_real": np.real(X_fast),
        "X_bfast_imag": np.imag(X_fast),
        "err_slow": err_slow,
        "err_fast": err_fast
    })
    df.to_csv("worked_example_n6_results.csv", index=False)

    # 1) 幅度對照圖
    k = np.arange(N)
    plt.figure(figsize=(6, 4))
    plt.plot(k, np.abs(X_dft),  "o-", label="DFT$_6$")
    plt.plot(k, np.abs(X_slow), "s--", label="Bluestein (slow, exact conv.)")
    plt.plot(k, np.abs(X_fast), "d-.", label="Bluestein (fast via FFT$_{16}$)")
    plt.xlabel("Index $k$")
    plt.ylabel("Magnitude")
    plt.legend()
    plt.tight_layout()
    plt.savefig("n6_consistency.png", dpi=200)

    # 2) 誤差莖狀圖（注意：新版 matplotlib 不要用 use_line_collection）
    plt.figure(figsize=(6, 4))
    markerline1, stemlines1, baseline1 = plt.stem(k, err_slow, label="|DFT - slow|")
    markerline2, stemlines2, baseline2 = plt.stem(k+0.03, err_fast, label="|DFT - fast|")  # 微移避免重疊
    plt.xlabel("Index $k$")
    plt.ylabel("Absolute error")
    plt.yscale("log")
    plt.legend()
    plt.tight_layout()
    plt.savefig("n6_error.png", dpi=200)
