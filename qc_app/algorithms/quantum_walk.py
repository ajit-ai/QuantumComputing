"""Discrete-time quantum walk on a cycle graph with a Hadamard coin."""
import numpy as np
from qiskit import QuantumCircuit

from qc_app.core.backends import run_counts


def _append_shift(qc, coin, pos_qubits, direction):
    n = len(pos_qubits)
    ops = [(list(pos_qubits[:i]), pos_qubits[i]) for i in range(n - 1, 0, -1)]
    ops.append((None, pos_qubits[0]))
    seq = ops if direction == "up" else list(reversed(ops))
    for controls, target in seq:
        if controls is None:
            qc.cx(coin, target)
        else:
            qc.mcx([coin] + controls, target)


def _step(qc, coin, pos_qubits):
    qc.h(coin)
    qc.x(coin)
    _append_shift(qc, coin, pos_qubits, "down")
    qc.x(coin)
    _append_shift(qc, coin, pos_qubits, "up")


def build_circuit(steps=1, n_position=3):
    qc = QuantumCircuit(n_position + 1, n_position)
    coin = n_position
    pos = range(n_position)
    for _ in range(steps):
        _step(qc, coin, pos)
    qc.measure(pos, range(n_position))
    return qc


def position_probabilities(steps=1, n_position=3):
    """Exact distribution via statevector (no measurement)."""
    from qiskit.quantum_info import Statevector

    qc = build_circuit(steps, n_position).remove_final_measurements(inplace=False)
    probs = np.abs(Statevector(qc).data) ** 2
    dist = {}
    for idx, p in enumerate(probs):
        node = idx & (2 ** n_position - 1)
        dist[node] = dist.get(node, 0.0) + float(p)
    return dist


def run(steps=1, n_position=3, shots=2048, seed=42):
    counts = run_counts(build_circuit(steps, n_position), shots, seed)
    total = sum(counts.values())
    distribution = {
        int(bitstring.replace(" ", ""), 2): count / total
        for bitstring, count in counts.items()
    }
    top_node = max(distribution, key=distribution.get)
    return {
        "algorithm": "quantum_walk",
        "graph": f"cycle(2^{n_position})",
        "steps": steps,
        "top_node": top_node,
        "distribution": {format(k, f"0{n_position}b"): round(v, 4)
                         for k, v in sorted(distribution.items())},
        "counts": counts,
    }
