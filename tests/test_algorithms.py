import math

from qc_app.algorithms import deutsch_jozsa, grover, qaoa, qft, qpe, shors, simon


def test_deutsch_jozsa_constant():
    result = deutsch_jozsa.run(oracle_type="constant")
    assert result["verdict"] == "constant"
    assert result["correct"] is True


def test_deutsch_jozsa_balanced():
    result = deutsch_jozsa.run(oracle_type="balanced")
    assert result["verdict"] == "balanced"
    assert result["correct"] is True


def test_grover_finds_marked_state():
    for marked in ("00", "01", "10", "11"):
        result = grover.run(marked=marked)
        assert result["answer"] == marked
        assert result["success_probability"] > 0.95


def test_grover_optimal_iterations_formula():
    assert grover.optimal_iterations(4) == max(
        1, int(math.floor(math.pi / 4 * math.sqrt(16)))
    )


def test_simon_recovers_secret():
    result = simon.run(secret="101", shots=128)
    assert result["matches_expected"] is True
    assert result["constraints_consistent"] is True


def test_qft_uniform_on_zero():
    counts = qft.run(input_value=0, n_qubits=3, shots=4096)["counts"]
    expected = 4096 / 8
    for outcome, count in counts.items():
        assert abs(count - expected) < expected * 0.25


def test_qft_inverse_roundtrip():
    import numpy as np
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector

    from qc_app.algorithms.qft import inverse_qft, qft

    qc = QuantumCircuit(3)
    qc.x(0)
    qc.x(2)
    forward = qc.compose(QuantumCircuit(3))
    qft(forward, 3)
    backward = forward.compose(QuantumCircuit(3))
    inverse_qft(backward, 3)
    final = Statevector(backward).data
    expected = Statevector(qc).data
    assert np.allclose(final, expected)


def test_qpe_exact_phase():
    result = qpe.run(n_counting=3)
    assert result["exact"] is True
    assert result["measured_phase"] == 0.125


def test_shors_factors_15():
    result = shors.run(n=15)
    assert result["factors"] == [3, 5]
    assert result["product_check"] is True


def test_vqe_converges_near_exact():
    from qc_app.algorithms import vqe

    out = vqe.run(max_iter=120)
    assert out["error"] < 0.1
    assert out["energy"] < -1.7


def test_qaoa_maxcut_triangle():
    result = qaoa.run()
    assert result["brute_force_optimum"] == 2
    assert result["approximation_ratio"] > 0.9
