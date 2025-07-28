!pip install qiskit
!pip install qiskit qiskit-aer

from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
import math
from fractions import Fraction
import math

def find_factors(N, a, period):
    """Find factors of N using the period."""
    if period % 2 != 0:
        return None, None  # Period must be even
    factor1 = math.gcd(pow(a, period // 2) - 1, N)
    factor2 = math.gcd(pow(a, period // 2) + 1, N)
    # Check if factors are valid (non-trivial)
    if factor1 == 1 or factor1 == N or factor2 == 1 or factor2 == N:
        return None, None
    return factor1, factor2

def shor_period_finding(N, a):
    """Simplified quantum period finding for N=15, a=7."""
    n = math.ceil(math.log2(N))  # Number of qubits for counting
    qc = QuantumCircuit(2 * n, n)  # 2n qubits, n classical bits

    # Initialize counting qubits in superposition
    for q in range(n):
        qc.h(q)

    # Modular exponentiation (simplified for a=7, N=15)
    qc.x(n)  # Set target qubit to |1>
    # Simplified controlled modular multiplication (approximated)
    # For a=7, N=15, period=4, this is a placeholder
    for q in range(n):
        if q == 0:  # Simulate a^1 mod N
            qc.cx(q, n + 1)

    # Apply Quantum Fourier Transform (decomposed to basic gates)
    qc.append(QFT(n, do_swaps=True), range(n))

    # Measure counting qubits
    qc.measure(range(n), range(n))

    # Simulate
    simulator = AerSimulator(method='automatic')
    try:
        result = simulator.run(qc, shots=1024).result()
        counts = result.get_counts()
        if not counts:
            raise ValueError("Simulation failed to produce results.")
        max_count = max(counts, key=counts.get)
        s = int(max_count, 2) / 2**n  # Convert to fraction
        period = Fraction(s).limit_denominator(N).denominator
        return period
    except Exception as e:
        print(f"Simulation error: {e}")
        return None

# Example
N = 15
a = 7
QFT(n, do_swaps=True)
try:
    period = shor_period_finding(N, a)
    if period:
        print(f"Period: {period}")
        p, q = find_factors(N, a, period)
        if p and q:
            print(f"Factors of {N}: {p}, {q}")
        else:
            print("No non-trivial factors found.")
    else:
        print("Failed to find period.")
except Exception as e:
    print(f"Error: {e}")