"""Stage 4 - evaluate the model on the held-out test set.

Writes metrics/metrics.json (tracked as a DVC metric) and a confusion-matrix
plot (tracked as a DVC plot).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.metrics import (  # noqa: E402
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    f1_score,
)


def main(model_path: str, data_path: str, out_dir: str) -> None:
    bundle = joblib.load(model_path)
    data = np.load(data_path)
    X, y = data["X"], data["y"]
    pred = bundle["model"].predict(X)

    metrics = {
        "accuracy": round(float(accuracy_score(y, pred)), 4),
        "f1_macro": round(float(f1_score(y, pred, average="macro")), 4),
        "test_samples": int(len(y)),
    }

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")

    print(classification_report(y, pred, digits=3))

    fig, ax = plt.subplots(figsize=(6, 6))
    ConfusionMatrixDisplay.from_predictions(
        y, pred, ax=ax, cmap="Blues", colorbar=False
    )
    ax.set_title(f"Confusion matrix (accuracy {metrics['accuracy']:.1%})")
    fig.tight_layout()
    fig.savefig(out / "confusion_matrix.png", dpi=150)
    plt.close(fig)

    print(metrics)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="models/model.joblib")
    parser.add_argument("--data", default="data/processed/test.npz")
    parser.add_argument("--out", default="metrics")
    args = parser.parse_args()
    main(args.model, args.data, args.out)
