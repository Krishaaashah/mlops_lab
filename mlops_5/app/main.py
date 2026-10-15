"""FastAPI service that serves the trained image classifier.

Endpoints
    GET  /         web page: draw a digit or upload a picture
    POST /predict  multipart upload (field "file") -> prediction + probabilities
    GET  /health   liveness / readiness probe (used by Docker and CI)
    GET  /info     model details and test-set metrics
    GET  /docs     interactive Swagger UI
"""
from __future__ import annotations

import json
import logging
import os
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path

import joblib
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

from src.imgproc import preprocess_image

logger = logging.getLogger("uvicorn.error")

MODEL_PATH = Path(os.getenv("MODEL_PATH", "models/model.joblib"))
METRICS_PATH = Path(os.getenv("METRICS_PATH", "metrics/metrics.json"))
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB


@lru_cache(maxsize=1)
def load_bundle() -> dict:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


@asynccontextmanager
async def lifespan(_: FastAPI):
    load_bundle()  # fail fast when the model file is missing
    logger.info("Model loaded from %s", MODEL_PATH)
    yield


app = FastAPI(
    title="Image Classification API",
    version="1.0.0",
    description="Handwritten-digit classifier trained with a DVC pipeline.",
    lifespan=lifespan,
)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index() -> str:
    return INDEX_HTML


@app.get("/health")
def health() -> dict:
    try:
        bundle = load_bundle()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=f"Model not available: {exc}")
    return {"status": "ok", "model_loaded": True, "classes": len(bundle["classes"])}


@app.get("/info")
def info() -> dict:
    bundle = load_bundle()
    metrics = json.loads(METRICS_PATH.read_text()) if METRICS_PATH.exists() else None
    size = bundle["img_size"]
    return {
        "model": type(bundle["model"].steps[-1][1]).__name__,
        "classes": bundle["classes"],
        "input_size": f"{size}x{size}",
        "sklearn_version": bundle["sklearn_version"],
        "metrics": metrics,
    }


@app.post("/predict")
def predict(file: UploadFile = File(...)) -> dict:
    data = file.file.read(MAX_UPLOAD_BYTES + 1)
    if not data:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image is larger than 5 MB.")

    try:
        features = preprocess_image(data)
    except Exception:  # noqa: BLE001
        logger.warning("Could not decode upload %r", file.filename)
        raise HTTPException(
            status_code=400,
            detail="Could not read the file as an image (use PNG or JPEG).",
        )

    bundle = load_bundle()
    proba = bundle["model"].predict_proba(features.reshape(1, -1))[0]
    best = int(proba.argmax())
    return {
        "filename": file.filename,
        "prediction": bundle["classes"][best],
        "confidence": round(float(proba[best]), 4),
        "probabilities": {
            label: round(float(p), 4) for label, p in zip(bundle["classes"], proba)
        },
    }


INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Image Classifier</title>
<style>
  :root { --bg:#f6f7fb; --card:#fff; --ink:#1c2230; --muted:#6b7385; --accent:#3b5bdb; --line:#e3e6ef; }
  * { box-sizing: border-box; }
  body { margin:0; font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; background:var(--bg); color:var(--ink); }
  main { max-width: 880px; margin: 0 auto; padding: 32px 16px 48px; }
  h1 { margin: 0 0 4px; font-size: 1.6rem; }
  p.sub { margin: 0 0 24px; color: var(--muted); }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  @media (max-width: 720px) { .grid { grid-template-columns: 1fr; } }
  .card { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 20px; }
  h2 { margin: 0 0 12px; font-size: 1.05rem; }
  canvas { width: 100%; max-width: 280px; aspect-ratio: 1; background: #000; border-radius: 8px; touch-action: none; cursor: crosshair; display: block; }
  .actions { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
  button, label.btn { font: inherit; padding: 8px 14px; border-radius: 8px; border: 1px solid var(--accent); background: var(--accent); color: #fff; cursor: pointer; }
  button.ghost { background: transparent; color: var(--accent); }
  input[type=file] { display: none; }
  #preview { max-width: 100%; max-height: 200px; border-radius: 8px; margin-top: 12px; display: none; border: 1px solid var(--line); }
  .hint { color: var(--muted); font-size: .9rem; margin: 0 0 12px; }
  #result { margin-top: 16px; min-height: 40px; }
  .headline { display: flex; align-items: baseline; gap: 12px; margin-bottom: 12px; }
  .digit { font-size: 3rem; font-weight: 700; color: var(--accent); line-height: 1; }
  .conf { color: var(--muted); }
  .row { display: grid; grid-template-columns: 1.5rem 1fr 3.5rem; align-items: center; gap: 8px; font-size: .9rem; margin: 4px 0; }
  .track { height: 8px; background: var(--line); border-radius: 4px; overflow: hidden; }
  .fill { height: 100%; background: var(--accent); }
  .row span:last-child { text-align: right; color: var(--muted); }
  footer { margin-top: 24px; color: var(--muted); font-size: .85rem; }
  footer a { color: var(--accent); }
</style>
</head>
<body>
<main>
  <h1>Image Classifier</h1>
  <p class="sub">Handwritten digit recognition (0-9) &middot; DVC &middot; Docker &middot; GitHub Actions &middot; AWS</p>

  <div style="background:#eef2ff; border:1px solid #c7d2fe; border-radius:10px; padding:12px 16px; margin: 0 0 20px; font-size:0.92rem; color:#3730a3; display:flex; flex-wrap:wrap; gap:16px; justify-content:space-between; align-items:center;">
    <div><strong>Student:</strong> Krisha Shah &middot; <strong>PRN:</strong> 24070126512</div>
    <div style="display:flex; gap:12px; flex-wrap:wrap;">
      <a href="https://github.com/Krishaaashah/mlops_lab/tree/main/mlops_5" target="_blank" style="color:#4338ca; font-weight:600; text-decoration:none;">&#128279; GitHub Repo</a>
      <a href="https://github.com/Krishaaashah/mlops_lab/actions" target="_blank" style="color:#4338ca; font-weight:600; text-decoration:none;">&#9989; CI/CD Runs</a>
      <a href="/docs" style="color:#4338ca; font-weight:600; text-decoration:none;">&#128218; Swagger API</a>
    </div>
  </div>

  <div class="grid">
    <section class="card">
      <h2>Draw a digit</h2>
      <p class="hint">Use your mouse or finger, then press Predict.</p>
      <canvas id="pad" width="280" height="280"></canvas>
      <div class="actions">
        <button id="predictDrawing">Predict</button>
        <button id="clear" class="ghost">Clear</button>
      </div>
    </section>

    <section class="card">
      <h2>Upload an image</h2>
      <p class="hint">PNG or JPEG of a single digit (dark on light or light on dark).</p>
      <label class="btn" for="file">Choose image</label>
      <input id="file" type="file" accept="image/*">
      <div><img id="preview" alt="Uploaded image preview"></div>
    </section>
  </div>

  <section class="card" style="margin-top:16px">
    <h2>Result</h2>
    <div id="result"><span class="hint">No prediction yet.</span></div>
  </section>

  <footer>
    <div>API docs: <a href="/docs">/docs</a> &middot; <a href="/health">/health</a> &middot; <a href="/info">/info</a></div>
    <div style="margin-top:6px; font-size:0.8rem; color:#6b7385;">
      Course Project: Handwritten Digit Recognition &middot; AWS EC2 Deployment &middot; DVC S3 Remote
    </div>
  </footer>
</main>

<script>
const pad = document.getElementById('pad');
const ctx = pad.getContext('2d');
const out = document.getElementById('result');
const preview = document.getElementById('preview');

function resetPad() {
  ctx.fillStyle = '#000';
  ctx.fillRect(0, 0, pad.width, pad.height);
  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 18;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
}
resetPad();

let drawing = false;
function point(e) {
  const r = pad.getBoundingClientRect();
  return [(e.clientX - r.left) * pad.width / r.width, (e.clientY - r.top) * pad.height / r.height];
}
pad.addEventListener('pointerdown', e => {
  drawing = true;
  pad.setPointerCapture(e.pointerId);
  const [x, y] = point(e);
  ctx.beginPath();
  ctx.moveTo(x, y);
  ctx.lineTo(x + 0.1, y + 0.1);
  ctx.stroke();
});
pad.addEventListener('pointermove', e => {
  if (!drawing) return;
  const [x, y] = point(e);
  ctx.lineTo(x, y);
  ctx.stroke();
});
['pointerup', 'pointercancel'].forEach(t => pad.addEventListener(t, () => { drawing = false; }));

document.getElementById('clear').onclick = () => {
  resetPad();
  show('No prediction yet.');
};
document.getElementById('predictDrawing').onclick = () => {
  pad.toBlob(blob => send(blob, 'drawing.png'), 'image/png');
};
document.getElementById('file').onchange = e => {
  const f = e.target.files[0];
  if (!f) return;
  preview.src = URL.createObjectURL(f);
  preview.style.display = 'block';
  send(f, f.name);
};

function show(text) { out.textContent = text; }

async function send(blob, name) {
  show('Predicting...');
  const fd = new FormData();
  fd.append('file', blob, name);
  try {
    const res = await fetch('/predict', { method: 'POST', body: fd });
    const data = await res.json();
    if (!res.ok) { show(data.detail || 'Request failed'); return; }
    render(data);
  } catch (err) {
    show('Network error: ' + err.message);
  }
}

function render(d) {
  out.textContent = '';
  const head = document.createElement('div');
  head.className = 'headline';
  const digit = document.createElement('span');
  digit.className = 'digit';
  digit.textContent = d.prediction;
  const conf = document.createElement('span');
  conf.className = 'conf';
  conf.textContent = (d.confidence * 100).toFixed(1) + '% confident';
  head.append(digit, conf);
  out.append(head);

  Object.entries(d.probabilities).forEach(([label, p]) => {
    const row = document.createElement('div');
    row.className = 'row';
    const l = document.createElement('span');
    l.textContent = label;
    const track = document.createElement('div');
    track.className = 'track';
    const fill = document.createElement('div');
    fill.className = 'fill';
    fill.style.width = (p * 100) + '%';
    track.append(fill);
    const v = document.createElement('span');
    v.textContent = (p * 100).toFixed(1) + '%';
    row.append(l, track, v);
    out.append(row);
  });
}
</script>
</body>
</html>
"""
