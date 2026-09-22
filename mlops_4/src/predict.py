"""Run inference with a trained MNIST CNN model."""
import argparse

import numpy as np
from tensorflow.keras.models import load_model

from src.preprocess import preprocess_images


def predict(model_path, images):
    """Predict digit classes for a batch of raw images.

    Args:
        model_path: Path to a saved Keras model file.
        images: numpy array of raw (unnormalized) images, shape (N, 28, 28).

    Returns:
        numpy array of predicted class labels, shape (N,).
    """
    model = load_model(model_path)
    processed = preprocess_images(images)
    predictions = model.predict(processed, verbose=0)
    return np.argmax(predictions, axis=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict digits with a trained model")
    parser.add_argument("--model-path", type=str, default="saved_model/mnist_cnn.keras")
    parser.add_argument("--num-samples", type=int, default=5)
    args = parser.parse_args()

    from src.preprocess import load_raw_data

    (_, _), (x_test_raw, y_test) = load_raw_data()
    sample = x_test_raw[: args.num_samples]
    preds = predict(args.model_path, sample)
    print("Predicted:", preds)
    print("Actual:   ", y_test[: args.num_samples])
