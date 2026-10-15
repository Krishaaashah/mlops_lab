import io
import json
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageOps
from sklearn.datasets import load_digits

from app.main import app

DIGITS = load_digits()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def digit_bytes(index: int, size: int = 96, invert: bool = False, fmt: str = "PNG"):
    grey = np.rint(DIGITS.images[index] / 16 * 255).astype(np.uint8)
    img = Image.fromarray(grey).resize((size, size), Image.Resampling.BICUBIC)
    if invert:
        img = ImageOps.invert(img)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue(), int(DIGITS.target[index])


def accuracy(client, indices, **kwargs) -> float:
    hits = 0
    for i in indices:
        payload, label = digit_bytes(i, **kwargs)
        resp = client.post("/predict", files={"file": ("d.png", payload, "image/png")})
        assert resp.status_code == 200
        hits += resp.json()["prediction"] == str(label)
    return hits / len(indices)


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "model_loaded": True, "classes": 10}


def test_index_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Image Classifier" in resp.text


def test_info(client):
    body = client.get("/info").json()
    assert body["model"] == "MLPClassifier"
    assert body["classes"] == [str(i) for i in range(10)]


def test_predict_response_format(client):
    payload, _ = digit_bytes(0)
    body = client.post("/predict", files={"file": ("d.png", payload, "image/png")}).json()
    assert set(body) == {"filename", "prediction", "confidence", "probabilities"}
    assert len(body["probabilities"]) == 10
    assert sum(body["probabilities"].values()) == pytest.approx(1.0, abs=0.01)


def test_predict_accuracy_on_dataset_images(client):
    assert accuracy(client, range(0, len(DIGITS.target), 36)) >= 0.9


def test_predict_handles_inverted_images(client):
    assert accuracy(client, range(5, len(DIGITS.target), 90), invert=True) >= 0.85


def test_predict_accepts_jpeg(client):
    payload, label = digit_bytes(1, fmt="JPEG")
    resp = client.post("/predict", files={"file": ("d.jpg", payload, "image/jpeg")})
    assert resp.status_code == 200


def test_predict_rejects_non_image(client):
    resp = client.post("/predict", files={"file": ("x.txt", b"hello", "text/plain")})
    assert resp.status_code == 400


def test_predict_rejects_empty_file(client):
    resp = client.post("/predict", files={"file": ("x.png", b"", "image/png")})
    assert resp.status_code == 400


def test_predict_rejects_huge_file(client):
    big = b"\0" * (5 * 1024 * 1024 + 1)
    resp = client.post("/predict", files={"file": ("x.png", big, "image/png")})
    assert resp.status_code == 413


def test_pipeline_metrics_are_reasonable():
    metrics = json.loads(Path("metrics/metrics.json").read_text())
    assert metrics["accuracy"] >= 0.9
