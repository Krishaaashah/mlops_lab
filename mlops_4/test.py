"""Test suite for the image classification project.

These tests validate the model architecture, preprocessing pipeline, and
inference path using synthetic data so the CI pipeline runs quickly and
does not depend on downloading the full MNIST dataset on every run.
"""
import numpy as np
import pytest

from src.model import build_model
from src.preprocess import preprocess_images


@pytest.fixture(scope="module")
def model():
    return build_model()


def test_model_builds(model):
    """The model should build without errors and contain layers."""
    assert model is not None
    assert len(model.layers) > 0


def test_model_input_output_shape(model):
    """The model should accept 28x28x1 images and output 10 class scores."""
    assert model.input_shape == (None, 28, 28, 1)
    assert model.output_shape == (None, 10)


def test_preprocess_normalizes_pixel_values():
    """Pixel values should be scaled into the [0, 1] range."""
    raw_images = np.random.randint(0, 256, size=(4, 28, 28), dtype=np.uint8)
    processed = preprocess_images(raw_images)
    assert processed.min() >= 0.0
    assert processed.max() <= 1.0


def test_preprocess_adds_channel_dimension():
    """A batch of grayscale images should gain a trailing channel dimension."""
    raw_images = np.random.randint(0, 256, size=(4, 28, 28), dtype=np.uint8)
    processed = preprocess_images(raw_images)
    assert processed.shape == (4, 28, 28, 1)


def test_model_predicts_on_batch(model):
    """The model should produce a valid probability distribution per image."""
    dummy_batch = np.random.rand(8, 28, 28, 1).astype("float32")
    predictions = model.predict(dummy_batch, verbose=0)
    assert predictions.shape == (8, 10)
    np.testing.assert_allclose(predictions.sum(axis=1), np.ones(8), atol=1e-4)


def test_model_predictions_are_valid_classes(model):
    """Predicted class indices should fall within the 10 digit classes."""
    dummy_batch = np.random.rand(5, 28, 28, 1).astype("float32")
    predictions = model.predict(dummy_batch, verbose=0)
    predicted_classes = np.argmax(predictions, axis=1)
    assert predicted_classes.min() >= 0
    assert predicted_classes.max() <= 9
