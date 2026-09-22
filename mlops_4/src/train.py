"""Train the CNN on MNIST and save the resulting model."""
import argparse
import os

from src.model import build_model
from src.preprocess import load_data


def train(epochs=5, batch_size=128, model_path="saved_model/mnist_cnn.keras"):
    """Train a CNN digit classifier on MNIST and save it to disk.

    Args:
        epochs: Number of training epochs.
        batch_size: Training batch size.
        model_path: Where to save the trained model.

    Returns:
        The trained Keras model.
    """
    (x_train, y_train), (x_test, y_test) = load_data()

    model = build_model()
    model.fit(
        x_train, y_train,
        validation_split=0.1,
        epochs=epochs,
        batch_size=batch_size,
        verbose=2,
    )

    test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
    print(f"Test loss: {test_loss:.4f} | Test accuracy: {test_acc:.4f}")

    os.makedirs(os.path.dirname(model_path) or ".", exist_ok=True)
    model.save(model_path)
    print(f"Model saved to {model_path}")
    return model


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train MNIST CNN classifier")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--model-path", type=str, default="saved_model/mnist_cnn.keras")
    args = parser.parse_args()

    train(epochs=args.epochs, batch_size=args.batch_size, model_path=args.model_path)
