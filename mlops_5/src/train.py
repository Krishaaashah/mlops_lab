"""Stage 3 - train the classifier and save it as a single joblib bundle."""
from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import sklearn
import yaml
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.imgproc import IMG_SIZE


def main(data_path: str, out_path: str) -> None:
    with open("params.yaml") as fh:
        params = yaml.safe_load(fh)["train"]

    data = np.load(data_path)
    X, y = data["X"], data["y"]

    model = Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "mlp",
                MLPClassifier(
                    hidden_layer_sizes=tuple(params["hidden_layers"]),
                    alpha=params["alpha"],
                    max_iter=params["max_iter"],
                    random_state=params["seed"],
                ),
            ),
        ]
    )
    model.fit(X, y)
    print(f"training accuracy: {model.score(X, y):.4f}")

    bundle = {
        "model": model,
        "classes": [str(c) for c in model.classes_],
        "img_size": IMG_SIZE,
        "sklearn_version": sklearn.__version__,
    }
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, out)
    print(f"model saved to {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data/processed/train.npz")
    parser.add_argument("--out", default="models/model.joblib")
    args = parser.parse_args()
    main(args.data, args.out)
