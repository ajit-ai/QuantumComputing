"""HHL algorithm for 2x2 Hermitian linear systems Ax = b.

Demo-scale implementation: Hamiltonian simulation via exact matrix
exponential, 3-bit quantum phase estimation, eigenvalue-conditioned
rotation, and postselection on the ancilla.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import UnitaryGate
from scipy.linalg import expm

from qc_app.algorithms.qft import inverse_qft

DEFAULT_MATRIX = [[1.0, -1 / 3], [-1 / 3, 1.0]]
DEFAULT_B = [1.0, 0.0]
N_COUNTING = 3


def _validate(matrix, b):
    A = np.array(matrix, dtype=float)
    rhs = np.array(b, dtype=float)
    if A.shape != (2, 2):
        raise ValueError("matrix must be 2x2")
    if not np.allclose(A, A.T):
        raise ValueError("matrix must be symmetric")
    if rhs.shape != (2,):
        raise ValueError("b must have length 2")
    return A, rhs


def _align_evolution_time(eigenvalues):
    """Pick t placing both phases lambda*t/2pi near k/8 grid points."""
    best_t, best_score = None, -np.inf
    for t in np.linspace(0.05, 4.5, 4000):
        phases = np.mod(eigenvalues * t / (2 * np.pi), 1.0)
        score = -np.sum(np.abs(phases * 8 - np.round(phases * 8)) ** 2)
        if score > best_score:
            best_score, best_t = score, t
    return float(best_t)


def _rotation_matrix(angles):
    dim = len(angles)
    U = np.zeros((2 * dim, 2 * dim))
    for z, theta in enumerate(angles):
        c, s = np.cos(theta / 2), np.sin(theta / 2)
        U[z, z] = c
        U[z, z + dim] = -s
        U[z + dim, z] = s
        U[z + dim, z + dim] = c
    return U


def build_circuit(matrix=None, b=None):
    A, rhs = _validate(matrix or DEFAULT_MATRIX, b or DEFAULT_B)
    eigenvalues, eigenvectors = np.linalg.eigh(A)
    t = _align_evolution_time(eigenvalues)
    lam_min = float(np.min(np.abs(eigenvalues)))
    C = 0.9 * lam_min

    unitary = UnitaryGate(expm(1j * A * t), label="e^{iAt}")
    qc = QuantumCircuit(1 + N_COUNTING + 1, 1 + N_COUNTING)
    out, counting, ancilla = 0, range(1, 1 + N_COUNTING), 1 + N_COUNTING

    b_norm = rhs / np.linalg.norm(rhs)
    qc.prepare_state(b_norm, [out])
    qc.h(counting)
    for k in range(N_COUNTING):
        qc.append(unitary.power(2 ** k).control(1), [1 + k, out])
    inverse_qft(qc, N_COUNTING, qubits=list(counting))

    lambdas = 2 * np.pi * np.arange(1, 2 ** N_COUNTING) / (2 ** N_COUNTING * t)
    angles = [0.0] + [2 * float(np.arcsin(min(1.0, C / lam))) for lam in lambdas]
    qc.unitary(_rotation_matrix(angles), [*counting, ancilla])

    from qc_app.algorithms.qft import qft

    qft(qc, N_COUNTING, qubits=list(counting))
    for k in reversed(range(N_COUNTING)):
        qc.append(unitary.power(2 ** k).control(1).inverse(), [1 + k, out])
    qc.h(counting)

    qc.measure(ancilla, 0)
    qc.measure(counting, range(1, 1 + N_COUNTING))
    return qc, A, rhs, eigenvalues, eigenvectors, t


def run(matrix=None, b=None):
    qc, A, rhs, eigenvalues, _, t = build_circuit(matrix, b)
    state = qc.remove_final_measurements(inplace=False)
    from qiskit.quantum_info import Statevector

    probs = np.abs(Statevector(state).data) ** 2

    classical = np.linalg.solve(A, rhs)
    target = classical / np.linalg.norm(classical)

    estimate = np.zeros(2)
    success_mass = 0.0
    for idx, p in enumerate(probs):
        out = idx & 1
        counting_val = (idx >> 1) & (2 ** N_COUNTING - 1)
        ancilla = idx >> (1 + N_COUNTING)
        if ancilla == 1 and counting_val == 0:
            estimate[out] += p
            success_mass += p
    if success_mass > 0:
        estimate /= estimate.sum()
    amplitudes = np.sqrt(estimate)

    sign = np.sign(np.dot(amplitudes, target)) or 1.0
    error = float(np.linalg.norm(sign * amplitudes - target))
    return {
        "algorithm": "hhl",
        "matrix": A.tolist(),
        "b": rhs.tolist(),
        "classical_solution": classical.tolist(),
        "quantum_solution_normalized": (sign * amplitudes).tolist(),
        "target_normalized": target.tolist(),
        "solution_error": error,
        "success_probability": float(success_mass),
        "evolution_time": t,
    }
