"""QuantumCaptcha - visual CAPTCHAs powered by true quantum randomness.

Extracted from notebooks/demos/QuantumCaptcha.ipynb.
"""
import io
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from qiskit import QuantumCircuit

from qc_app.core.backends import run_counts

CHAR_POOL = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


class QuantumCaptcha:
    """Generates secure visual CAPTCHAs using quantum random bits."""

    def __init__(self, length=6, seed=None):
        self.length = length
        self.seed = seed

    def _quantum_random_bytes(self, num_bytes):
        qc = QuantumCircuit(8)
        qc.h(range(8))
        qc.measure_all()
        counts = run_counts(qc, shots=num_bytes, seed=self.seed)
        stream = []
        for bitstring, count in counts.items():
            bits = bitstring.replace(" ", "")
            for _ in range(count):
                stream.append(int(bits, 2))
        while len(stream) < num_bytes:
            stream.append(0)
        return bytes(stream[:num_bytes])

    def generate_text(self):
        rng = random.Random(sum(self._quantum_random_bytes(4)))
        return "".join(rng.choice(CHAR_POOL) for _ in range(self.length))

    def render(self, text, width=280, height=100):
        image = Image.new("RGB", (width, height), (245, 247, 250))
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("arial.ttf", 44)
        except OSError:
            font = ImageFont.load_default()
        for i, char in enumerate(text):
            x = 18 + i * (width - 36) // self.length
            y = random.Random(f"{text}{i}").randint(18, height - 60)
            color = (
                random.Random(i).randint(20, 120),
                random.Random(i + 9).randint(20, 120),
                random.Random(i + 17).randint(20, 120),
            )
            draw.text((x, y), char, font=font, fill=color)
        for _ in range(6):
            x1, y1 = random.Random(f"l{_}{text}").randint(0, width), random.Random(
                f"m{_}{text}"
            ).randint(0, height)
            x2, y2 = random.Random(f"n{_}{text}").randint(0, width), random.Random(
                f"o{_}{text}"
            ).randint(0, height)
            draw.line((x1, y1, x2, y2), fill=(150, 160, 175), width=2)
        return image.filter(ImageFilter.GaussianBlur(0.6))

    def generate(self):
        text = self.generate_text()
        image = self.render(text)
        return {"text": text, "image": image}

    def save(self, path):
        result = self.generate()
        result["image"].save(path)
        return path


def to_png_bytes(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def entanglement_challenge(seed=None):
    """Bell-state challenge: does the hidden X gate make outcomes opposite?"""
    inject_x = bool(random.getrandbits(1))
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    if inject_x:
        qc.x(1)
    qc.measure([0, 1], [0, 1])
    counts = run_counts(qc, shots=64, seed=seed)
    top = max(counts, key=counts.get)
    relation = "opposite" if set(top) == {"0", "1"} else "identical"
    return {
        "expected_relation": "opposite" if inject_x else "identical",
        "sample_outcome": top,
        "measured_relation": relation,
        "correct": relation == ("opposite" if inject_x else "identical"),
    }
