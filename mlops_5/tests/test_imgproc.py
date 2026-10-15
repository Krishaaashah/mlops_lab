import io

import numpy as np
from PIL import Image, ImageDraw, ImageOps
from sklearn.datasets import load_digits

from src.imgproc import IMG_SIZE, MAX_PIXEL, preprocess_image

DIGITS = load_digits()


def digit_image(index: int, size: int = 64) -> Image.Image:
    grey = np.rint(DIGITS.images[index] / 16 * 255).astype(np.uint8)
    return Image.fromarray(grey).resize((size, size), Image.Resampling.BICUBIC)


def test_output_shape_and_range():
    vec = preprocess_image(digit_image(3))
    assert vec.shape == (IMG_SIZE * IMG_SIZE,)
    assert vec.dtype == np.float32
    assert vec.min() >= 0
    assert vec.max() <= MAX_PIXEL + 1e-3


def test_dark_on_light_matches_light_on_dark():
    img = digit_image(7)
    np.testing.assert_allclose(
        preprocess_image(img), preprocess_image(ImageOps.invert(img)), atol=1e-3
    )


def test_blank_image_gives_zeros():
    vec = preprocess_image(Image.new("L", (50, 50), 255))
    assert not vec.any()


def test_accepts_raw_bytes_and_transparent_png():
    img = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
    ImageDraw.Draw(img).rectangle((20, 10, 40, 50), fill=(0, 0, 0, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    vec = preprocess_image(buf.getvalue())
    assert vec.max() > 0  # black stroke on transparent background is detected
