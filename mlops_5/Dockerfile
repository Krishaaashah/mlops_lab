# Image Classification service - FastAPI + scikit-learn model trained by the DVC pipeline.
# The model (models/model.joblib) must exist before building: run `dvc repro` or `dvc pull`.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install dependencies first so this layer is cached between code changes
COPY requirements.txt .
RUN pip install -r requirements.txt

# Application code, shared pre-processing, trained model and its metrics
COPY src/__init__.py src/imgproc.py ./src/
COPY app/ ./app/
COPY models/model.joblib ./models/model.joblib
COPY metrics/metrics.json ./metrics/metrics.json

# Run as a non-root user
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
