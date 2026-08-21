import math

import numpy as np

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


def test_hhl_solves_default_system():
    from qc_app.algorithms import hhl

    result = hhl.run()
    assert result["solution_error"] < 0.02
    assert result["success_probability"] > 0.2
    classical = np.array(result["classical_solution"])
    assert abs(classical[0] / classical[1] - 3.0) < 1e-9


def test_hhl_rejects_non_symmetric():
    from qc_app.algorithms import hhl

    try:
        hhl.run(matrix=[[1, 2], [0, 1]], b=[1, 0])
        raised = False
    except ValueError:
        raised = True
    assert raised is True


def test_quantum_walk_single_step():
    from qc_app.algorithms import quantum_walk

    dist = quantum_walk.position_probabilities(steps=1, n_position=3)
    support = {node for node, p in dist.items() if p > 1e-9}
    assert support == {1, 7}
    assert abs(dist[1] - 0.5) < 1e-9
    assert abs(dist[7] - 0.5) < 1e-9


def test_quantum_walk_two_step_support_and_symmetry():
    from qc_app.algorithms import quantum_walk

    dist = quantum_walk.position_probabilities(steps=2, n_position=3)
    support = {node for node, p in dist.items() if p > 1e-9}
    assert support == {6, 0, 2}
    for node in range(8):
        assert abs(dist.get(node, 0) - dist.get((-node) % 8, 0)) < 1e-9


def test_quantum_walk_three_step_normalization_and_support():
    from qc_app.algorithms import quantum_walk

    dist = quantum_walk.position_probabilities(steps=3, n_position=3)
    total = sum(dist.values())
    assert abs(total - 1.0) < 1e-9
    support = {node for node, p in dist.items() if p > 1e-9}
    assert support <= {1, 3, 5, 7}
