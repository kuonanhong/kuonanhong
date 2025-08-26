"""
Two options to make the noise section reviewer‑friendly:

(1) Pure NumPy density‑matrix + Kraus channels (depolarizing on 1q/2q gates)
(2) Qiskit Aer noise model version (if Qiskit is available)

Run as:
  python qba_noise_curve_qiskit_or_densitymatrix.py --mode=density  # option 1 (default)
  python qba_noise_curve_qiskit_or_densitymatrix.py --mode=qiskit   # option 2 (requires qiskit-aer)

Outputs:
  qba_noise_curve_dm.csv / qba_noise_curve_dm.png  (density mode)
  qba_noise_curve_aer.csv / qba_noise_curve_aer.png (qiskit mode)

Both compute average state fidelity vs per-gate depolarizing probability p for:
  - Direct 3-qubit QFT (no final bit-reversal)
  - QBA-like pipeline: QFT_8 -> 3 phase-diagonals -> QFT_8^(-1)

Note: The QBA-like here is structurally similar to the paper's toy model.
"""

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Utilities: matrices and gates
# -----------------------------
I2 = np.eye(2, dtype=complex)
X = np.array([[0,1],[1,0]], complex)
Y = np.array([[0,-1j],[1j,0]], complex)
Z = np.array([[1,0],[0,-1]], complex)
H = (1/np.sqrt(2))*np.array([[1,1],[1,-1]], complex)


def Rz(theta):
    return np.array([[np.exp(-1j*theta/2),0],[0,np.exp(1j*theta/2)]], complex)

def CR(phi):
    U = np.eye(4, dtype=complex)
    U[3,3] = np.exp(1j*phi)
    return U

# -----------------------------
# Density-matrix helpers
# -----------------------------

def pure_state_dm(psi):
    psi = psi.reshape(-1,1)
    return psi @ psi.conj().T


def apply_kraus(rho, Ks):
    out = np.zeros_like(rho)
    for K in Ks:
        out += K @ rho @ K.conj().T
    return out


def kron_n(*ops):
    out = np.array([[1]], dtype=complex)
    for O in ops:
        out = np.kron(out, O)
    return out


def embed_1q(U, target, n):
    ops = [I2]*n
    ops[target] = U
    return kron_n(*ops)


def embed_2q(U, q1, q2, n):
    # Ensure q1<q2 for layout
    if q1>q2:
        q1,q2 = q2,q1
    # Build by basis permutation if necessary
    # Simpler: construct full 2^n x 2^n by iterating computational basis
    dim = 2**n
    F = np.zeros((dim, dim), dtype=complex)
    for i in range(dim):
        for j in range(dim):
            # Map indices to bits
            ib = [(i>>k)&1 for k in range(n-1,-1,-1)]
            jb = [(j>>k)&1 for k in range(n-1,-1,-1)]
            # Extract the 2-qubit subindices
            i2 = (ib[q1]<<1) | ib[q2]
            j2 = (jb[q1]<<1) | jb[q2]
            # Other bits must match
            ok = True
            for k in range(n):
                if k!=q1 and k!=q2 and ib[k]!=jb[k]:
                    ok=False; break
            if ok:
                F[i,j] = U[i2,j2]
    return F

# Depolarizing channel Kraus (1-qubit)
#  E(ρ) = (1-p) ρ + p/3 (XρX + YρY + ZρZ)

def kraus_depolarizing_1q(p):
    return [np.sqrt(1-p)*I2, np.sqrt(p/3)*X, np.sqrt(p/3)*Y, np.sqrt(p/3)*Z]

# Two-qubit depolarizing (simple tensor of 1q channels on each qubit for illustration)

def kraus_depolarizing_2q(p):
    K1 = kraus_depolarizing_1q(p)
    K2 = kraus_depolarizing_1q(p)
    Ks=[]
    for A in K1:
        for B in K2:
            Ks.append(np.kron(A,B))
    return Ks

# -----------------------------
# Circuits
# -----------------------------

def circuit_qft3_layers():
    return [
        ('1q', 2, H),
        ('2q', (1,2), CR(np.pi/2)),
        ('2q', (0,2), CR(np.pi/4)),
        ('1q', 1, H),
        ('2q', (0,1), CR(np.pi/2)),
        ('1q', 0, H),
    ]


def circuit_qba_like3_layers():
    layers = [
        ('1q', 2, H),
        ('2q', (1,2), CR(np.pi/2)),
        ('2q', (0,2), CR(np.pi/4)),
        ('1q', 1, H),
        ('2q', (0,1), CR(np.pi/2)),
        ('1q', 0, H),
        # three diagonal chirp-ish phases (unitary phases only, minimal)
        ('1q', 0, Rz(0.3)),
        ('1q', 1, Rz(-0.5)),
        ('1q', 2, Rz(0.7)),
        # inverse QFT_3 (not exact inverse of the above toy, but mirrors structure)
        ('1q', 0, H),
        ('2q', (0,1), CR(-np.pi/2)),
        ('1q', 1, H),
        ('2q', (0,2), CR(-np.pi/4)),
        ('2q', (1,2), CR(-np.pi/2)),
        ('1q', 2, H),
    ]
    return layers

# -----------------------------
# Density-matrix simulation
# -----------------------------

def run_dm_avg_fidelity(layers, p, n_qubits=3, n_trials=60, seed=3):
    rng = np.random.default_rng(seed)
    fid = []
    # Precompute Kraus sets
    K1 = kraus_depolarizing_1q(p)
    K2 = kraus_depolarizing_2q(p)

    for _ in range(n_trials):
        # Random pure input
        psi0 = rng.normal(size=2**n_qubits) + 1j*rng.normal(size=2**n_qubits)
        psi0 /= np.linalg.norm(psi0)
        rho0 = pure_state_dm(psi0)

        # Ideal evolution (no noise)
        rho_id = rho0.copy()
        for kind, q, U in layers:
            if kind=='1q':
                Ue = embed_1q(U, q, n_qubits)
            else:
                Ue = embed_2q(U, q[0], q[1], n_qubits)
            rho_id = Ue @ rho_id @ Ue.conj().T

        # Noisy evolution
        rho = rho0.copy()
        for kind, q, U in layers:
            if kind=='1q':
                Ue = embed_1q(U, q, n_qubits)
                rho = Ue @ rho @ Ue.conj().T
                # apply 1q depolarizing on that target
                Ks_local = [embed_1q(K, q, n_qubits) for K in K1]
                rho = apply_kraus(rho, Ks_local)
            else:
                Ue = embed_2q(U, q[0], q[1], n_qubits)
                rho = Ue @ rho @ Ue.conj().T
                # apply 2q depolarizing on those two targets
                Ks_local = [embed_2q(K, q[0], q[1], n_qubits) for K in K2]
                rho = apply_kraus(rho, Ks_local)

        # Fidelity between rho and rho_id (Uhlmann for pure vs mixed reduces to <psi_id|rho|psi_id>)
        # Extract pure state from rho_id
        w, v = np.linalg.eigh(rho_id)
        idx = np.argmax(w)
        psi_id = v[:, idx]
        F = np.real(np.vdot(psi_id, rho @ psi_id))
        fid.append(F)

    return float(np.mean(fid))

# -----------------------------
# Qiskit Aer path (optional)
# -----------------------------
def run_qiskit_aer():
    try:
        from qiskit import QuantumCircuit
        from qiskit_aer import Aer
        from qiskit_aer.noise import NoiseModel, depolarizing_error
        from qiskit.quantum_info import Statevector, DensityMatrix
    except Exception as e:
        print("Qiskit Aer not available:", e)
        return None

    # --- Circuits without any save instructions ---
    def qft3_circ():
        qc = QuantumCircuit(3)
        qc.h(2)
        qc.cp(np.pi / 2, 1, 2)
        qc.cp(np.pi / 4, 0, 2)
        qc.h(1)
        qc.cp(np.pi / 2, 0, 1)
        qc.h(0)
        return qc

    def qba_like_circ():
        qc = qft3_circ()
        # three diagonal phases
        qc.rz(0.3, 0)
        qc.rz(-0.5, 1)
        qc.rz(0.7, 2)
        # inverse-QFT-like mirror
        qc.h(0)
        qc.cp(-np.pi / 2, 0, 1)
        qc.h(1)
        qc.cp(-np.pi / 4, 0, 2)
        qc.cp(-np.pi / 2, 1, 2)
        qc.h(2)
        return qc

    backend = Aer.get_backend('aer_simulator_density_matrix')

    ps = np.linspace(0.0, 0.03, 16)
    rows = []

    for p in ps:
        # Build a depolarizing noise model
        noise_model = NoiseModel()
        err1 = depolarizing_error(float(p), 1)
        err2 = depolarizing_error(float(p), 2)
        noise_model.add_all_qubit_quantum_error(err1, ["h", "rz"])  # single-qubit gates used
        noise_model.add_all_qubit_quantum_error(err2, ["cp"])  # two-qubit gates used

        # ----- Ideal (no-save) circuits for the reference pure states -----
        qc_qft_id = qft3_circ()
        qc_qba_id = qba_like_circ()

        psi0 = Statevector.from_int(0, 2 ** 3)  # |000> (simple fixed input)
        psi_id_qft = psi0.evolve(qc_qft_id)
        psi_id_qba = psi0.evolve(qc_qba_id)

        # Convert to DensityMatrix objects just in case we need .data later
        rho_id_qft = DensityMatrix(psi_id_qft)
        rho_id_qba = DensityMatrix(psi_id_qba)

        # ----- Noisy runs (with save_density_matrix) -----
        qc_qft_noisy = qft3_circ()
        qc_qba_noisy = qba_like_circ()
        qc_qft_noisy.save_density_matrix()
        qc_qba_noisy.save_density_matrix()

        res_qft = backend.run(qc_qft_noisy, noise_model=noise_model).result()
        res_qba = backend.run(qc_qba_noisy, noise_model=noise_model).result()

        rho_noisy_qft = DensityMatrix(res_qft.data(0)['density_matrix']).data
        rho_noisy_qba = DensityMatrix(res_qba.data(0)['density_matrix']).data

        # Fidelity for pure |psi_id> vs mixed rho_noisy: <psi_id| rho_noisy |psi_id>
        F_qft = float(np.real(psi_id_qft.data.conj().T @ rho_noisy_qft @ psi_id_qft.data))
        F_qba = float(np.real(psi_id_qba.data.conj().T @ rho_noisy_qba @ psi_id_qba.data))

        rows.append({'p_depol': float(p), 'F_QFT': F_qft, 'F_QBA_like': F_qba})

    df = pd.DataFrame(rows)
    df.to_csv('qba_noise_curve_aer.csv', index=False)

    plt.figure(figsize=(6, 4))
    plt.plot(df['p_depol'], df['F_QFT'], marker='o', label='Direct QFT (3q) — Aer')
    plt.plot(df['p_depol'], df['F_QBA_like'], marker='s', label='QBA-like (3q) — Aer')
    plt.xlabel('Per-gate depolarizing probability $p$')
    plt.ylabel('Average state fidelity')
    plt.legend();
    plt.tight_layout()
    plt.savefig('qba_noise_curve_aer.png', dpi=200)
    print('Saved qba_noise_curve_aer.csv/.png')
    return df

# -----------------------------
# Main
# -----------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['density','qiskit'], default='density')
    parser.add_argument('--trials', type=int, default=60)
    args = parser.parse_args()

    ps = np.linspace(0.0, 0.03, 16)

    if args.mode=='density':
        layers_qft = circuit_qft3_layers()
        layers_qba = circuit_qba_like3_layers()
        rows=[]
        for p in ps:
            F_qft = run_dm_avg_fidelity(layers_qft, float(p), n_qubits=3, n_trials=args.trials, seed=3)
            F_qba = run_dm_avg_fidelity(layers_qba, float(p), n_qubits=3, n_trials=args.trials, seed=3)
            rows.append({'p_depol':float(p), 'F_QFT':F_qft, 'F_QBA_like':F_qba})
        df = pd.DataFrame(rows)
        df.to_csv('qba_noise_curve_dm.csv', index=False)
        plt.figure(figsize=(6,4))
        plt.plot(df['p_depol'], df['F_QFT'], marker='o', label='Direct QFT (3q) — DM')
        plt.plot(df['p_depol'], df['F_QBA_like'], marker='s', label='QBA-like (3q) — DM')
        plt.xlabel('Per-gate depolarizing probability $p$')
        plt.ylabel('Average state fidelity')
        plt.legend(); plt.tight_layout()
        plt.savefig('qba_noise_curve_dm.png', dpi=200)
        print('Saved qba_noise_curve_dm.csv/.png')
    else:
        run_qiskit_aer()