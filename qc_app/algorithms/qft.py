"""Quantum Fourier Transform and inverse QFT built from primitive gates."""
import numpy as np
from qiskit import QuantumCircuit


def qft(qc, n_qubits, do_swaps=True):
    for j in range(n_qubits - 1, -1, -1):
        qc.h(j)
        for k in range(j - 1, -1, -1):
            angle = np.pi / (2 ** (j - k))
            qc.cp(angle, k, j)
    if do_swaps:
        for i in range(n_qubits // 2):
            qc.swap(i, n_qubits - i - 1)
    return qc


def inverse_qft(qc, n_qubits, do_swaps=True):
    if do_swaps:
        for i in range(n_qubits // 2):
            qc.swap(i, n_qubits - i - 1)
    for j in range(n_qubits):
        for k in range(j - 1, -1, -1):
            qc.cp(-np.pi / (2 ** (j - k)), k, j)
        qc.h(j)
    return qc


def build_circuit(input_value=1, n_qubits=3, inverse=False):
    qc = QuantumCircuit(n_qubits, n_qubits)
    bits = format(input_value, f"0{n_qubits}b")
    for i, bit in enumerate(reversed(bits)):
        if bit == "1":
            qc.x(i)
    if inverse:
        inverse_qft(qc, n_qubits)
    else:
        qft(qc, n_qubits)
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def run(input_value=1, n_qubits=3, shots=1024, seed=42, inverse=False):
    from qc_app.core.backends import run_counts, top_count

    counts = run_counts(build_circuit(input_value, n_qubits, inverse), shots, seed)
    return {
        "algorithm": "qft",
        "input_value": input_value,
        "mode": "inverse" if inverse else "forward",
        "top_outcome": top_count(counts),
        "counts": counts,
    }
