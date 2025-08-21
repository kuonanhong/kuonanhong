# qba_noise_curve: generate qba_noise_curve.csv and qba_noise_curve.png
# (3-qubit toy model; direct QFT vs QBA-like)
# Outputs stored under /mnt/data in this run.
# ref: 1.1 https://chatgpt.com/c/68a42b62-a480-8330-a243-85f2ef96da8b
#     1.2 https://chatgpt.com/share/68a42d9f-388c-8003-8fb3-9bedaeec4491
import numpy as np, pandas as pd, matplotlib.pyplot as plt

np.random.seed(3)

H = (1/np.sqrt(2))*np.array([[1,1],[1,-1]], dtype=complex)
def Rz(theta):
    return np.array([[np.exp(-1j*theta/2),0],[0,np.exp(1j*theta/2)]], dtype=complex)
def CR(phi):
    U = np.eye(4, dtype=complex); U[3,3] = np.exp(1j*phi); return U

def apply_gate_vec(psi, U_small, qubits, n_qubits):
    qubits = tuple(qubits); k=len(qubits)
    all_idx = list(range(n_qubits))
    rest = [q for q in all_idx if q not in qubits]
    perm = rest + list(qubits)
    dim = 2**n_qubits
    P = np.zeros((dim, dim), dtype=complex)
    for i in range(dim):
        bits = [(i >> (n_qubits-1-b)) & 1 for b in range(n_qubits)]
        pb   = [bits[p] for p in perm]
        j=0
        for b in pb: j=(j<<1)|b
        P[j,i]=1
    psi_p = P @ psi
    Uext  = np.kron(np.eye(2**(n_qubits-k), dtype=complex), U_small)
    psi_q = Uext @ psi_p
    psi_o = P.conj().T @ psi_q
    return psi_o

def depolarize_single(psi, p, target, n_qubits):
    X = np.array([[0,1],[1,0]], complex)
    Y = np.array([[0,-1j],[1j,0]], complex)
    Z = np.array([[1,0],[0,-1]], complex)
    mixed = (1-p)*psi
    for U in (X,Y,Z):
        mixed += (p/3)*apply_gate_vec(psi, U, (target,), n_qubits)
    return mixed

def circuit_qft3():
    return [
        ('H', (2,), H),
        ('CR',(1,2), CR(np.pi/2)),
        ('CR',(0,2), CR(np.pi/4)),
        ('H', (1,), H),
        ('CR',(0,1), CR(np.pi/2)),
        ('H', (0,), H),
    ]

def circuit_qba_like3():
    layers = [
        ('H', (2,), H),
        ('CR',(1,2), CR(np.pi/2)),
        ('CR',(0,2), CR(np.pi/4)),
        ('H', (1,), H),
        ('CR',(0,1), CR(np.pi/2)),
        ('H', (0,), H),
        ('Rz',(0,), Rz(0.3)),
        ('Rz',(1,), Rz(-0.5)),
        ('Rz',(2,), Rz(0.7)),
        ('H', (0,), H),
        ('CR',(0,1), CR(-np.pi/2)),
        ('H', (1,), H),
        ('CR',(0,2), CR(-np.pi/4)),
        ('CR',(1,2), CR(-np.pi/2)),
        ('H', (2,), H),
    ]
    return layers

def run_circuit(layers, n_qubits, p):
    psi0 = np.random.randn(2**n_qubits) + 1j*np.random.randn(2**n_qubits)
    psi0 /= np.linalg.norm(psi0)
    psi_id = psi0.copy()
    for _,qs,U in layers:
        psi_id = apply_gate_vec(psi_id, U, qs, n_qubits)
    psi = psi0.copy()
    for _,qs,U in layers:
        psi = apply_gate_vec(psi, U, qs, n_qubits)
        if len(qs)==1:
            psi = depolarize_single(psi, p, qs[0], n_qubits)
        else:
            psi = depolarize_single(psi, p, qs[0], n_qubits)
            psi = depolarize_single(psi, p, qs[1], n_qubits)
    F = float(np.abs(np.vdot(psi_id, psi))**2)
    return F

layers_qft = circuit_qft3()
layers_qba = circuit_qba_like3()

noise_grid = np.linspace(0.0, 0.03, 16)
rows=[]
for p in noise_grid:
    F_qft = np.mean([run_circuit(layers_qft, 3, p) for _ in range(60)])
    F_qba = np.mean([run_circuit(layers_qba, 3, p) for _ in range(60)])
    rows.append({'p_depol':p, 'F_QFT':F_qft, 'F_QBA_like':F_qba})

df_noise = pd.DataFrame(rows)
df_noise.to_csv('qba_noise_curve.csv', index=False)

plt.figure(figsize=(6,4))
plt.plot(df_noise['p_depol'], df_noise['F_QFT'], marker='o', label='Direct QFT (3q)')
plt.plot(df_noise['p_depol'], df_noise['F_QBA_like'], marker='s', label='QBA-like (3q)')
plt.xlabel('Per-gate depolarizing probability $p$')
plt.ylabel('Average state fidelity')
plt.legend(); plt.tight_layout()
plt.savefig('qba_noise_curve.png', dpi=200)
