"""QAOA for MaxCut on small graphs with deterministic grid-search tuning."""
import itertools

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


def _maxcut_cost(bitstring, edges):
    bits = [int(b) for b in reversed(bitstring)]
    return sum(1 for u, v in edges if bits[u] != bits[v])


def cost_unitary(qc, gamma, edges):
    for u, v in edges:
        qc.cx(u, v)
        qc.rz(2 * gamma, v)
        qc.cx(u, v)


def mixer_unitary(qc, beta, n_qubits):
    for i in range(n_qubits):
        qc.rx(2 * beta, i)


def build_circuit(gamma, beta, edges, n_qubits, p=1):
    qc = QuantumCircuit(n_qubits)
    qc.h(range(n_qubits))
    for g, b in zip(np.atleast_1d(gamma), np.atleast_1d(beta)):
        cost_unitary(qc, g, edges)
        mixer_unitary(qc, b, n_qubits)
    return qc


def state_probabilities(gamma, beta, edges, n_qubits, p=1):
    sv = Statevector(build_circuit(gamma, beta, edges, n_qubits, p))
    probs = np.abs(sv.data) ** 2
    return {format(i, f"0{n_qubits}b"): probs[i] for i in range(len(probs))}


def expected_cut(gamma, beta, edges, n_qubits, p=1):
    probs = state_probabilities(gamma, beta, edges, n_qubits, p)
    return sum(prob * _maxcut_cost(bs, edges) for bs, prob in probs.items())


def optimize(edges, n_qubits, steps=25):
    best = None
    for gamma, beta in itertools.product(
        np.linspace(0.05, np.pi / 2, steps), np.linspace(0.05, np.pi / 4, steps)
    ):
        score = expected_cut(gamma, beta, edges, n_qubits)
        if best is None or score > best[0]:
            best = (score, gamma, beta)
    return {"expected_cut": best[0], "gamma": best[1], "beta": best[2]}


def brute_force_optimum(edges, n_qubits):
    return max(
        _maxcut_cost(format(i, f"0{n_qubits}b"), edges) for i in range(2 ** n_qubits)
    )


def run(edges=None, n_qubits=None, steps=20):
    if edges is None:
        n_qubits = 3
        edges = [(0, 1), (1, 2), (2, 0)]
    result = optimize(edges, n_qubits, steps)
    optimum = brute_force_optimum(edges, n_qubits)
    probs = state_probabilities(result["gamma"], result["beta"], edges, n_qubits)
    best_bitstring = max(probs, key=lambda b: (_maxcut_cost(b, edges), probs[b]))
    return {
        "algorithm": "qaoa",
        "edges": edges,
        "n_qubits": n_qubits,
        "expected_cut": result["expected_cut"],
        "brute_force_optimum": optimum,
        "approximation_ratio": result["expected_cut"] / optimum,
        "best_bitstring": best_bitstring,
        "params": {k: result[k] for k in ("gamma", "beta")},
    }
