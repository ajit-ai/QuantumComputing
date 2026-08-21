"""Variational Quantum Eigensolver with a built-in SPSA optimizer.

Demo system: H2 molecule at equilibrium bond length (STO-3G, parity-mapped,
2-qubit reduction). Ground state energy ~ -1.857 Ha.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector

H2_HAMILTONIAN_COEFFS = {
    "II": -1.052373245772859,
    "IZ": 0.39793742484318045,
    "ZI": -0.39793742484318045,
    "ZZ": -0.01128010425623538,
    "XX": 0.18093119978423156,
}


def h2_hamiltonian():
    return SparsePauliOp.from_list(list(H2_HAMILTONIAN_COEFFS.items()))


def ansatz_circuit(params):
    sector, theta = params[0], params[1]
    qc = QuantumCircuit(2)
    if abs(sector) > 0.5:
        qc.x(0)
    qc.ry(theta, 1)
    qc.cx(1, 0)
    return qc


def energy(params, hamiltonian=None):
    if hamiltonian is None:
        hamiltonian = h2_hamiltonian()
    state = Statevector(ansatz_circuit(params))
    return float(np.real(state.expectation_value(hamiltonian)))


def spsa(func, x0, max_iter=200, a=1.0, c=0.3, seed=42):
    rng = np.random.default_rng(seed)
    x = np.array(x0, dtype=float)
    for k in range(max_iter):
        a_k = a / (k + 1) ** 0.602
        c_k = c / (k + 1) ** 0.101
        delta = rng.choice([-1.0, 1.0], size=x.size)
        plus = func(x + c_k * delta)
        minus = func(x - c_k * delta)
        gradient = (plus - minus) / (2 * c_k) * delta
        x = x - a_k * gradient
    return x


def run(max_iter=250, seed=42):
    hamiltonian = h2_hamiltonian()
    optimal_params = spsa(
        lambda p: energy(p, hamiltonian), [0.0, 0.0], max_iter, seed=seed
    )
    final_energy = energy(optimal_params, hamiltonian)
    exact = float(np.min(np.linalg.eigvalsh(hamiltonian.to_matrix())))
    return {
        "algorithm": "vqe",
        "optimal_params": optimal_params.tolist(),
        "energy": final_energy,
        "exact_energy": exact,
        "error": abs(final_energy - exact),
        "iterations": max_iter,
    }
