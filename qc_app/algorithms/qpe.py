"""Quantum Phase Estimation on the T gate (phase = 1/8)."""
from qiskit import QuantumCircuit

from qc_app.algorithms.qft import inverse_qft
from qc_app.core.backends import run_counts, top_count


def build_circuit(unitary_gate, n_counting=3, eigenstate_prep=None):
    n_target = unitary_gate.num_qubits
    qc = QuantumCircuit(n_counting + n_target, n_counting)
    qc.h(range(n_counting))
    if eigenstate_prep:
        eigenstate_prep(qc, range(n_counting, n_counting + n_target))
    for k in range(n_counting):
        power = 2 ** k
        controlled = unitary_gate.power(power).control(1)
        qc.append(controlled, [k] + list(range(n_counting, n_counting + n_target)))
    inverse_qft(qc, n_counting)
    qc.measure(range(n_counting), range(n_counting))
    return qc


def _prepare_eigenstate(qc, targets):
    qc.x(list(targets))


def run(n_counting=3, shots=1024, seed=42):
    from qiskit.circuit.library import TGate

    t = TGate()
    counts = run_counts(build_circuit(t, n_counting, _prepare_eigenstate), shots, seed)
    top = top_count(counts)
    measured_phase = int(top, 2) / (2 ** n_counting)
    return {
        "algorithm": "qpe",
        "expected_phase": 0.125,
        "measured_phase": measured_phase,
        "top_outcome": top,
        "exact": abs(measured_phase - 0.125) < 1e-9,
        "counts": counts,
    }
