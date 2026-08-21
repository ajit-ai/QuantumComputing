# QuantumComputing

A quantum computing demo application: SDK-agnostic algorithm library, a
quantum-randomness CAPTCHA service, and a FastAPI layer - plus the original
vendor reference notebooks.

## Repository Layout

```
qc_app/                     THE APPLICATION (SDK-agnostic)
├── core/                   Backend helpers (AerSimulator, counts)
├── algorithms/             8 algorithms behind one registry interface
│   ├── deutsch_jozsa.py    Constant vs balanced, one query
│   ├── grover.py           Unstructured search (quadratic speedup)
│   ├── simon.py            Hidden XOR mask (exponential speedup)
│   ├── shors.py            Factoring via quantum period finding
│   ├── qft.py              QFT / inverse QFT from primitive gates
│   ├── qpe.py              Quantum Phase Estimation (T-gate demo)
│   ├── vqe.py              VQE on H2 with built-in SPSA optimizer
│   └── qaoa.py             QAOA for MaxCut optimization
├── apps/
│   └── captcha.py          QuantumCaptcha: QRNG text + entanglement challenge
└── api/
    └── main.py             FastAPI service

notebooks/                  VENDOR REFERENCE MATERIAL (original notebooks)
├── ibm/QisKit_BaseCircuit.ipynb        Qiskit fundamentals (50 cells)
├── google/Cirq/simple_demo.ipynb       Cirq basics
├── pennylane/                          PennyLane QNodes & workflows
├── basics/                             Microquantum, classical ML baseline
├── algorithms_*.ipynb                  Original algorithm notebooks
└── demos/QuantumCaptcha.ipynb          Original captcha notebook

tests/                      pytest suite (algorithms, captcha, API)
```

## Quickstart

```bash
pip install -r requirements.txt

# Run any algorithm from Python
python -c "from qc_app.algorithms import run_algorithm; print(run_algorithm('shors', n=15))"

# Start the API + web UI
uvicorn qc_app.api.main:app --reload
# open http://localhost:8000 for the demo dashboard
```

## Docker

```bash
docker build -t quantumcomputing-demo .
docker run -p 8000:8000 quantumcomputing-demo
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/algorithms` | List registered algorithms |
| POST | `/algorithms/{name}/run` | Run an algorithm with JSON params |
| GET | `/captcha?length=6` | PNG captcha image (quantum RNG) |
| GET | `/captcha/challenge` | Bell-state entanglement challenge |

Example:

```bash
curl -X POST localhost:8000/algorithms/grovers/run \
     -H "Content-Type: application/json" \
     -d '{"params": {"marked": "101"}}'
```

## Algorithm Catalog

1. **Shor's** - factorization, O((log N)^3) vs classical exponential
2. **Grover's** - search, O(sqrt(N)) queries
3. **QFT** - periodicity detection, O((log N)^2) gates
4. **QPE** - eigenphase estimation; core of Shor's
5. **Deutsch-Jozsa** - constant/balanced in one query
6. **Simon's** - hidden XOR structure, O(n) queries
7. **VQE** - H2 ground state energy (NISQ-friendly hybrid)
8. **QAOA** - MaxCut combinatorial optimization (NISQ-friendly hybrid)

Roadmap additions: HHL, Quantum Walks, real-hardware backends (IBM Quantum),
Streamlit UI, Docker packaging.

## Development

```bash
pytest -v          # run test suite
flake8 qc_app tests
```

CI runs on every push/PR to `main` via GitHub Actions.
