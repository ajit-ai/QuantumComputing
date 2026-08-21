"""Algorithm registry: single entry point for all implemented algorithms."""
from qc_app.algorithms import deutsch_jozsa, grover, qaoa, qft, qpe, shors, simon, vqe

REGISTRY = {
    "deutsch_jozsa": {
        "description": "Decide if a function is constant or balanced (one query).",
        "run": deutsch_jozsa.run,
    },
    "grovers": {
        "description": "Quadratic-speedup unstructured search.",
        "run": grover.run,
    },
    "simon": {
        "description": "Find hidden XOR mask with exponential speedup.",
        "run": simon.run,
    },
    "shors": {
        "description": "Integer factorization via quantum period finding.",
        "run": shors.run,
    },
    "qft": {
        "description": "Quantum Fourier Transform / inverse QFT.",
        "run": qft.run,
    },
    "qpe": {
        "description": "Quantum Phase Estimation (T-gate demo).",
        "run": qpe.run,
    },
    "vqe": {
        "description": "Variational Quantum Eigensolver on H2.",
        "run": vqe.run,
    },
    "qaoa": {
        "description": "QAOA for MaxCut combinatorial optimization.",
        "run": qaoa.run,
    },
}


def list_algorithms():
    return {name: meta["description"] for name, meta in REGISTRY.items()}


def run_algorithm(name, **params):
    if name not in REGISTRY:
        raise KeyError(f"Unknown algorithm '{name}'. Available: {sorted(REGISTRY)}")
    return REGISTRY[name]["run"](**params)
