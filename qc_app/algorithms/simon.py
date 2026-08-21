"""Simon's algorithm with GF(2) post-processing.

Oracle: f(x) = min(x, x^secret) - exactly 2-to-1, implemented as an
explicit permutation unitary (practical for secrets up to ~4 bits).
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import UnitaryGate

from qc_app.core.backends import run_counts


def _simon_oracle_matrix(secret):
    n = len(secret)
    s = int(secret, 2)
    if s == 0:
        raise ValueError("secret must be nonzero")
    dim = 2 ** (2 * n)
    perm = np.zeros((dim, dim))
    for idx in range(dim):
        x = idx & (2 ** n - 1)
        y = (idx >> n) & (2 ** n - 1)
        new_idx = x | ((y ^ min(x, x ^ s)) << n)
        perm[new_idx, idx] = 1.0
    return perm


def build_circuit(secret="10"):
    n = len(secret)
    if n > 4:
        raise ValueError("demo oracle supports secrets up to 4 bits")
    qc = QuantumCircuit(2 * n, n)
    qc.h(range(n))
    qc.append(UnitaryGate(_simon_oracle_matrix(secret), label="Uf"), range(2 * n))
    qc.barrier()
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def solve_secret(outcomes, n_bits):
    """Return smallest nonzero s with z . s = 0 (mod 2) for all sampled z."""
    nonzero = {z for z in outcomes if z}
    if not nonzero:
        return None
    for candidate in range(1, 2 ** n_bits):
        if all(bin(z & candidate).count("1") % 2 == 0 for z in nonzero):
            return candidate
    return None


def run(secret="10", shots=128, seed=42):
    n = len(secret)
    counts = run_counts(build_circuit(secret), shots, seed)
    outcomes = [int(bitstring.replace(" ", ""), 2) for bitstring in counts]
    solved = solve_secret(outcomes, n)
    expected = int(secret, 2)
    consistent = solved is not None and all(
        bin(z & expected).count("1") % 2 == 0 for z in outcomes if z
    )
    return {
        "algorithm": "simon",
        "secret": secret,
        "solved_secret": format(solved, f"0{n}b") if solved is not None else None,
        "matches_expected": solved == expected,
        "constraints_consistent": consistent,
        "counts": counts,
    }
