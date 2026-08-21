"""Deutsch-Jozsa algorithm: decide constant vs balanced with one query."""
from qiskit import QuantumCircuit

from qc_app.core.backends import run_counts, top_count


def build_circuit(oracle_type="constant", n_qubits=3):
    qc = QuantumCircuit(n_qubits + 1, n_qubits)
    ancilla = n_qubits
    qc.x(ancilla)
    qc.h(range(n_qubits + 1))
    qc.barrier()
    if oracle_type == "balanced":
        for i in range(n_qubits):
            qc.cx(i, ancilla)
    elif oracle_type != "constant":
        raise ValueError("oracle_type must be 'constant' or 'balanced'")
    qc.barrier()
    qc.h(range(n_qubits))
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def run(oracle_type="constant", n_qubits=3, shots=256, seed=42):
    counts = run_counts(build_circuit(oracle_type, n_qubits), shots, seed)
    outcome = top_count(counts)
    is_constant = set(outcome) == {"0"}
    return {
        "algorithm": "deutsch_jozsa",
        "oracle_type": oracle_type,
        "outcome": outcome,
        "verdict": "constant" if is_constant else "balanced",
        "correct": is_constant == (oracle_type == "constant"),
        "counts": counts,
    }
