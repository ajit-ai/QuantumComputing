"""Shor's algorithm: quantum period finding + classical post-processing.

Supports small semiprimes (N <= 21) by building the modular multiplication
unitary U_a: |x> -> |a*x mod N> as an explicit permutation matrix.
"""
import math
import random
from fractions import Fraction

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import UnitaryGate

from qc_app.algorithms.qft import inverse_qft
from qc_app.core.backends import run_counts


def _multiplication_permutation(a, n):
    dim = 2 ** n
    perm = np.zeros((dim, dim))
    for x in range(dim):
        if x < n and math.gcd(x, n) == 1:
            y = (a * x) % n
        else:
            y = x
        perm[y, x] = 1.0
    return perm


def period_finding_circuit(a, n, n_counting=None):
    if n_counting is None:
        n_counting = 2 * n
    target_reg = max(n.bit_length(), 2)
    unitary = UnitaryGate(_multiplication_permutation(a, n), label=f"{a}x mod {n}")
    qc = QuantumCircuit(n_counting + target_reg, n_counting)
    qc.h(range(n_counting))
    qc.x(n_counting)
    for k in range(n_counting):
        controlled = unitary.power(2 ** k).control(1)
        qc.append(controlled, [k] + list(range(n_counting, n_counting + target_reg)))
    inverse_qft(qc, n_counting)
    qc.measure(range(n_counting), range(n_counting))
    return qc


def find_period(a, n, shots=32, seed=42):
    """Estimate the multiplicative order r of a mod n via phase estimation."""
    n_counting = 2 * n.bit_length() + 3
    counts = run_counts(period_finding_circuit(a, n, n_counting), shots, seed)
    candidates = {}
    for bitstring, count in counts.items():
        value = int(bitstring.replace(" ", ""), 2)
        if value == 0:
            continue
        frac = Fraction(value, 2 ** n_counting).limit_denominator(n)
        r = frac.denominator
        if r > 1 and pow(a, r, n) == 1 % n:
            candidates[r] = candidates.get(r, 0) + count
    if not candidates:
        return None
    return max(candidates, key=candidates.get)


def factor(n, max_attempts=8, seed=42):
    """Factor odd composite n using Shor's reduction. Returns set of factors."""
    rng = random.Random(seed)
    attempts = []
    if n % 2 == 0:
        return {2, n // 2}
    for attempt in range(max_attempts):
        a = rng.randrange(2, n - 1)
        g = math.gcd(a, n)
        if 1 < g < n:
            return {g, n // g}
        r = find_period(a, n, seed=seed + attempt)
        attempts.append({"a": a, "r": r})
        if r and r % 2 == 0:
            candidate = pow(a, r // 2, n)
            if candidate != n - 1:
                f1 = math.gcd(candidate - 1, n)
                f2 = math.gcd(candidate + 1, n)
                if 1 < f1 < n:
                    return {f1, n // f1}
                if 1 < f2 < n:
                    return {f2, n // f2}
    raise ValueError(f"Failed to factor {n}; attempts={attempts}")


def run(n=15, seed=42):
    factors = factor(n, seed=seed)
    return {
        "algorithm": "shors",
        "input": n,
        "factors": sorted(factors),
        "product_check": math.prod(factors) == n,
    }
