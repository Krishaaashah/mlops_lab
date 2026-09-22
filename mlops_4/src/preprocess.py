"""Data loading and preprocessing utilities for MNIST digit classification."""
import numpy as np
from tensorflow.keras.datasets import mnist


def load_raw_data():
    """Load the raw MNIST dataset (uint8 pixels, unprocessed).

    Returns:
        (x_train, y_train), (x_test, y_test)
    """
    return mnist.load_data()


def preprocess_images(images):
    """Normalize and reshape a batch of grayscale images.

    Args:
        images: numpy array of shape (N, H, W) with pixel values 0-255.

    Returns:
        numpy array of shape (N, H, W, 1) with pixel values in [0, 1].
    """
    images = images.astype("float32") / 255.0
    if images.ndim == 3:
        images = np.expand_dims(images, axis=-1)
    return images


def load_data():
    """Load and fully preprocess the MNIST dataset for training/evaluation.

    Returns:
        (x_train, y_train), (x_test, y_test) with images normalized to
        [0, 1] and reshaped to (N, 28, 28, 1).
    """
    (x_train, y_train), (x_test, y_test) = load_raw_data()
    return (preprocess_images(x_train), y_train), (preprocess_images(x_test), y_test)
