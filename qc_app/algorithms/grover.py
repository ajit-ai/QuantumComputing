"""Grover's search algorithm."""
import math

from qiskit import QuantumCircuit

from qc_app.core.backends import run_counts, top_count


def _multi_controlled_z(qc, n):
    qc.h(n - 1)
    if n == 1:
        qc.z(0)
    else:
        qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)


def _oracle(qc, marked):
    n = len(marked)
    zero_positions = [i for i, bit in enumerate(reversed(marked)) if bit == "0"]
    if zero_positions:
        qc.x(zero_positions)
    _multi_controlled_z(qc, n)
    if zero_positions:
        qc.x(zero_positions)


def _diffuser(qc, n):
    qc.h(range(n))
    qc.x(range(n))
    _multi_controlled_z(qc, n)
    qc.x(range(n))
    qc.h(range(n))


def optimal_iterations(n_qubits):
    return max(1, int(math.floor(math.pi / 4 * math.sqrt(2 ** n_qubits))))


def build_circuit(marked="11", iterations=None):
    n = len(marked)
    if iterations is None:
        iterations = optimal_iterations(n)
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    for _ in range(iterations):
        _oracle(qc, marked)
        _diffuser(qc, n)
    qc.measure(range(n), range(n))
    return qc


def run(marked="11", shots=1024, seed=42, iterations=None):
    counts = run_counts(build_circuit(marked, iterations), shots, seed)
    total = sum(counts.values())
    return {
        "algorithm": "grover",
        "marked_state": marked,
        "answer": top_count(counts),
        "success_probability": counts.get(marked, 0) / total,
        "iterations": iterations or optimal_iterations(len(marked)),
        "counts": counts,
    }
