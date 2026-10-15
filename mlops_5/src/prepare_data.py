"""Stage 1 - export the handwritten-digits dataset as PNG images.

Output layout:  <out>/<class label>/<index>.png
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.datasets import load_digits

UPSCALE = 4  # 8x8 -> 32x32 so the files look like ordinary pictures


def main(out_dir: str) -> None:
    out = Path(out_dir)
    if out.exists():
        shutil.rmtree(out)

    digits = load_digits()
    for idx, (pixels, label) in enumerate(zip(digits.images, digits.target)):
        folder = out / str(label)
        folder.mkdir(parents=True, exist_ok=True)
        grey = np.rint(pixels / 16.0 * 255).astype(np.uint8)
        img = Image.fromarray(grey).resize(
            (8 * UPSCALE, 8 * UPSCALE), Image.Resampling.NEAREST
        )
        img.save(folder / f"{idx:04d}.png")

    print(f"Wrote {len(digits.target)} images to {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="data/raw")
    main(parser.parse_args().out)
