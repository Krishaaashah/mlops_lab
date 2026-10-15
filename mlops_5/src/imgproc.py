"""Image pre-processing shared by the DVC pipeline and the web application.

The very same function is used when the training data is prepared and when a
user uploads a picture to the API, so the model always sees identically
processed inputs (no train/serve skew).
"""
from __future__ import annotations

import io
from pathlib import Path
from typing import BinaryIO, Union

import numpy as np
from PIL import Image

IMG_SIZE = 8            # model input is IMG_SIZE x IMG_SIZE pixels
MAX_PIXEL = 16.0        # pixel range used by the digits dataset (0..16)
DEFAULT_MARGIN = 0.15   # empty border kept around the digit (fraction of its size)
INK_THRESHOLD = 0.2     # fraction of the intensity range that counts as "ink"

ImageSource = Union[str, Path, bytes, BinaryIO, Image.Image]


def _open(source: ImageSource) -> Image.Image:
    if isinstance(source, Image.Image):
        return source
    if isinstance(source, (bytes, bytearray)):
        source = io.BytesIO(source)
    return Image.open(source)


def _to_grayscale(img: Image.Image) -> np.ndarray:
    """Greyscale float array; transparent areas are treated as white paper."""
    if img.mode in ("RGBA", "LA", "PA") or "transparency" in img.info:
        rgba = img.convert("RGBA")
        paper = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        img = Image.alpha_composite(paper, rgba)
    return np.asarray(img.convert("L"), dtype=np.float32)


def preprocess_image(
    source: ImageSource,
    size: int = IMG_SIZE,
    margin: float = DEFAULT_MARGIN,
) -> np.ndarray:
    """Convert any picture into the flat feature vector expected by the model.

    Steps: greyscale -> make the object bright on a dark background -> scale to
    0..1 -> crop to the object -> pad to a square with a margin -> resize to
    ``size`` x ``size`` -> scale to 0..MAX_PIXEL.
    """
    gray = _to_grayscale(_open(source))

    # The background colour is estimated from the image border.
    border = np.concatenate([gray[0, :], gray[-1, :], gray[:, 0], gray[:, -1]])
    if border.mean() > 127.5:
        gray = 255.0 - gray

    low, high = float(gray.min()), float(gray.max())
    if high - low < 1e-6:  # blank image
        return np.zeros(size * size, dtype=np.float32)
    gray = (gray - low) / (high - low)

    ys, xs = np.where(gray > INK_THRESHOLD)
    crop = gray[ys.min(): ys.max() + 1, xs.min(): xs.max() + 1]

    h, w = crop.shape
    side = max(h, w)
    pad = int(round(side * margin))
    canvas = np.zeros((side + 2 * pad, side + 2 * pad), dtype=np.float32)
    top = pad + (side - h) // 2
    left = pad + (side - w) // 2
    canvas[top: top + h, left: left + w] = crop

    small = Image.fromarray((canvas * 255).astype(np.uint8)).resize(
        (size, size), Image.Resampling.LANCZOS
    )
    return (np.asarray(small, dtype=np.float32) / 255.0 * MAX_PIXEL).reshape(-1)
