from fastapi.testclient import TestClient

from qc_app.api.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_index_serves_ui():
    response = client.get("/")
    assert response.status_code == 200
    assert "QuantumComputing Demo" in response.text


def test_list_algorithms():
    response = client.get("/algorithms")
    assert response.status_code == 200
    names = set(response.json())
    assert {"deutsch_jozsa", "grovers", "shors", "vqe", "qaoa"} <= names


def test_run_deutsch_jozsa_via_api():
    response = client.post(
        "/algorithms/deutsch_jozsa/run", json={"params": {"oracle_type": "balanced"}}
    )
    assert response.status_code == 200
    assert response.json()["verdict"] == "balanced"


def test_unknown_algorithm_returns_404():
    response = client.post("/algorithms/nope/run", json={"params": {}})
    assert response.status_code == 404


def test_captcha_endpoint_returns_png():
    response = client.get("/captcha?length=6&seed=42")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_captcha_challenge_endpoint():
    response = client.get("/captcha/challenge?seed=1")
    assert response.status_code == 200
    body = response.json()
    assert body["correct"] is True
