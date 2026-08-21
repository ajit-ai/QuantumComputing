import numpy as np

from qc_app.apps.captcha import QuantumCaptcha, entanglement_challenge, to_png_bytes


def test_captcha_text_length_and_charset():
    captcha = QuantumCaptcha(length=6, seed=7)
    text = captcha.generate_text()
    assert len(text) == 6
    assert all(ch in "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" for ch in text)


def test_captcha_reproducible_with_seed():
    first = QuantumCaptcha(length=6, seed=11).generate_text()
    second = QuantumCaptcha(length=6, seed=11).generate_text()
    assert first == second


def test_captcha_image_rendering():
    result = QuantumCaptcha(length=5, seed=3).generate()
    image = result["image"]
    assert image.size == (280, 100)
    png = to_png_bytes(image)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"


def test_entanglement_challenge_consistent():
    result = entanglement_challenge(seed=5)
    assert result["correct"] is True


def test_quantum_random_bytes_distribution():
    qc_bytes = QuantumCaptcha(seed=9)._quantum_random_bytes(64)
    assert len(qc_bytes) == 64
    assert np.std(list(qc_bytes)) > 10
