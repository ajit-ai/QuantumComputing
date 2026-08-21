"""Shared helpers for running circuits on local simulators."""
from qiskit import transpile
from qiskit_aer import AerSimulator


def get_simulator(seed=None):
    return AerSimulator(seed_simulator=seed)


def run_counts(circuit, shots=1024, seed=None):
    sim = get_simulator(seed)
    compiled = transpile(circuit, sim)
    return sim.run(compiled, shots=shots).result().get_counts()


def top_count(counts):
    return max(counts, key=counts.get)
