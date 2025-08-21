# qft_entropy_layers: generate CSV and PNG (3-qubit QFT without bit-reversal)
# Outputs:
#   /mnt/data/qft_entropy_layers.csv
#   /mnt/data/qft_entropy_layers.png
# (程式已在上方執行完成並輸出檔案)
# ref: 1.1 https://chatgpt.com/c/68a42b62-a480-8330-a243-85f2ef96da8b
#     1.2 https://chatgpt.com/share/68a42d9f-388c-8003-8fb3-9bedaeec4491
import numpy as np, pandas as pd, matplotlib.pyplot as plt
np.random.seed(7)

I2 = np.eye(2, dtype=complex)
H  = (1/np.sqrt(2))*np.array([[1,1],[1,-1]], dtype=complex)

def CR(phi):
    U = np.eye(4, dtype=complex); U[3,3] = np.exp(1j*phi); return U

def apply_gate_vec(psi, U_small, qubits, n_qubits=3):
    qubits = tuple(qubits); k = len(qubits)
    all_idx = list(range(n_qubits))
    rest = [q for q in all_idx if q not in qubits]
    perm = rest + list(qubits)
    dim = 2**n_qubits
    P = np.zeros((dim, dim), dtype=complex)
    for i in range(dim):
        bits = [(i >> (n_qubits-1-b)) & 1 for b in range(n_qubits)]
        pb   = [bits[p] for p in perm]
        j=0
        for b in pb: j = (j<<1)|b
        P[j,i]=1
    psi_p = P @ psi
    Uext  = np.kron(np.eye(2**(n_qubits-k), dtype=complex), U_small)
    psi_q = Uext @ psi_p
    psi_o = P.conj().T @ psi_q
    return psi_o

def entropy_vn_from_state(psi, keep, n_qubits):
    sys = list(range(n_qubits)); trace = [q for q in sys if q not in keep]
    perm = keep + trace
    dim_keep = 2**len(keep); dim_tr = 2**len(trace)
    dim = 2**n_qubits
    P = np.zeros((dim, dim), dtype=complex)
    for i in range(dim):
        bits = [(i >> (n_qubits-1-b)) & 1 for b in range(n_qubits)]
        pb   = [bits[p] for p in perm]
        j=0
        for b in pb: j=(j<<1)|b
        P[j,i]=1
    psi_p  = P @ psi
    psi_m  = psi_p.reshape((dim_keep, dim_tr))
    rhoA   = psi_m @ psi_m.conj().T
    evals  = np.linalg.eigvalsh((rhoA + rhoA.conj().T)/2)
    evals  = np.clip(evals.real, 0, 1); evals = evals[evals>1e-15]
    return float(-np.sum(evals*np.log2(evals)))

# Canonical 3q QFT layers (no final bit-reversal), qubits: 0(MSB),1,2(LSB)
layers = [
    ('H', (2,), H),
    ('CR',(1,2), CR(np.pi/2)),
    ('CR',(0,2), CR(np.pi/4)),
    ('H', (1,), H),
    ('CR',(0,1), CR(np.pi/2)),
    ('H', (0,), H),
]

# random generic superposition input
psi = np.random.randn(8) + 1j*np.random.randn(8); psi/=np.linalg.norm(psi)

records=[]
def record(li, psi):
    for cut, keep in [('q0 | q1q2',[0]), ('q1 | q2q0',[1])]:
        S = entropy_vn_from_state(psi, keep, 3)
        records.append({'layer':li, 'cut':cut, 'entropy':S})

record(0, psi.copy())
psi_t = psi.copy()
for i,(name,qs,U) in enumerate(layers, start=1):
    psi_t = apply_gate_vec(psi_t, U, qs, 3)
    record(i, psi_t.copy())

df = pd.DataFrame(records).sort_values(['cut','layer'])
df.to_csv('qft_entropy_layers.csv', index=False)

plt.figure(figsize=(6,4))
for cut, sub in df.groupby('cut'):
    plt.plot(sub['layer'], sub['entropy'], marker='o', label=cut)
plt.xlabel('Layer index'); plt.ylabel('Entropy $S$'); plt.legend(); plt.tight_layout()
plt.savefig('qft_entropy_layers.png', dpi=200)
