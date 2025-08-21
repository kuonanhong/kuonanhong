# (a) T-count estimate for chirp diagonal synthesis (epsilon=1e-6)
# ref: 1.1 https://chatgpt.com/c/68a42b62-a480-8330-a243-85f2ef96da8b
#     1.2 https://chatgpt.com/share/68a42d9f-388c-8003-8fb3-9bedaeec4491
import numpy as np, pandas as pd, matplotlib.pyplot as plt

def chirp_term_counts(m):
    singles = m                       # self terms
    pairs   = m*(m-1)//2              # pairwise terms
    return singles, pairs

def tcount_estimate(m, eps=1e-6, alpha=1.5):
    singles, pairs = chirp_term_counts(m)
    total_angles   = singles + pairs
    return total_angles * alpha * np.log2(1/eps)

rows=[]
for m in range(3, 13):
    s,p = chirp_term_counts(m)
    rows.append({'m':m, 'singles':s, 'pairs':p, 'Tcount_est_eps1e-6':tcount_estimate(m)})

df_t = pd.DataFrame(rows)
df_t.to_csv('tcount_chirp.csv', index=False)

plt.figure(figsize=(6,4))
plt.plot(df_t['m'], df_t['Tcount_est_eps1e-6'], marker='o')
plt.xlabel('Qubits $m$'); plt.ylabel('Estimated $T$-count ($\\varepsilon=10^{-6}$)')
plt.tight_layout(); plt.savefig('tcount_chirp.png', dpi=200)

# (b) LNN vs all-to-all QFT depth toy model
def depth_qft_all_to_all(n): return int(n*(n+1)/2)
def depth_qft_lnn(n):
    base = depth_qft_all_to_all(n)
    swap_overhead = 0
    for s in range(n):
        for j in range(s+1, n):
            swap_overhead += 2*(j-s-1)
    swap_overhead += n//2
    return base + swap_overhead

rows=[]
for n in range(3, 13):
    rows.append({'n_qubits':n, 'QFT_all_to_all_depth':depth_qft_all_to_all(n), 'QFT_LNN_depth_est':depth_qft_lnn(n)})
df_l = pd.DataFrame(rows)
df_l.to_csv('lnn_depth.csv', index=False)

plt.figure(figsize=(6,4))
plt.plot(df_l['n_qubits'], df_l['QFT_all_to_all_depth'], marker='o', label='All-to-all (model)')
plt.plot(df_l['n_qubits'], df_l['QFT_LNN_depth_est'], marker='s', label='LNN (routing model)')
plt.xlabel('Number of qubits $n$'); plt.ylabel('Depth (arbitrary layers)')
plt.legend(); plt.tight_layout(); plt.savefig('lnn_depth.png', dpi=200)
