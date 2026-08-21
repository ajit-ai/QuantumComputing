"""FastAPI service exposing algorithms and the quantum captcha demo."""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from qc_app.algorithms import list_algorithms, run_algorithm
from qc_app.apps.captcha import QuantumCaptcha, entanglement_challenge, to_png_bytes

app = FastAPI(
    title="QuantumComputing Demo API",
    description="SDK-agnostic quantum algorithms and QRNG captcha service.",
    version="0.1.0",
)

STATIC_DIR = Path(__file__).parent / "static"


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


class AlgorithmRequest(BaseModel):
    params: dict = Field(default_factory=dict)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/algorithms")
def algorithms():
    return list_algorithms()


@app.post("/algorithms/{name}/run")
def run(name: str, request: AlgorithmRequest):
    try:
        return run_algorithm(name, **request.params)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TypeError as exc:
        raise HTTPException(status_code=400, detail=f"Bad parameters: {exc}") from exc


@app.get("/captcha", responses={200: {"content": {"image/png": {}}}})
def captcha(length: int = 6, seed: int | None = None):
    result = QuantumCaptcha(length=length, seed=seed).generate()
    return Response(
        content=to_png_bytes(result["image"]), media_type="image/png"
    )


@app.get("/captcha/challenge")
def captcha_challenge(seed: int | None = None):
    return entanglement_challenge(seed=seed)
