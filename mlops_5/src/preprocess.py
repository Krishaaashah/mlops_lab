"""Stage 2 - pre-process the raw PNG images and create train/test splits."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import yaml
from sklearn.model_selection import train_test_split

from src.imgproc import preprocess_image


def load_images(raw_dir: str) -> tuple[np.ndarray, np.ndarray]:
    features, labels = [], []
    class_dirs = sorted(p for p in Path(raw_dir).iterdir() if p.is_dir())
    for class_dir in class_dirs:
        for img_path in sorted(class_dir.glob("*.png")):
            features.append(preprocess_image(img_path))
            labels.append(int(class_dir.name))
    return np.stack(features), np.array(labels)


def main(raw_dir: str, out_dir: str) -> None:
    with open("params.yaml") as fh:
        params = yaml.safe_load(fh)["preprocess"]

    X, y = load_images(raw_dir)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=params["test_size"],
        random_state=params["seed"],
        stratify=y,
    )

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out / "train.npz", X=X_train, y=y_train)
    np.savez_compressed(out / "test.npz", X=X_test, y=y_test)
    print(f"train: {X_train.shape}  test: {X_test.shape}  -> {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", default="data/raw")
    parser.add_argument("--out", default="data/processed")
    args = parser.parse_args()
    main(args.raw, args.out)
