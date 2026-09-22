"""CNN model architecture for MNIST digit classification."""
from tensorflow.keras import layers, models


def build_model(input_shape=(28, 28, 1), num_classes=10):
    """Build and compile a small CNN for image classification.

    Args:
        input_shape: Shape of a single input image (H, W, C).
        num_classes: Number of output classes.

    Returns:
        A compiled tf.keras.Model.
    """
    model = models.Sequential([
        layers.Input(shape=input_shape),
        layers.Conv2D(32, (3, 3), activation="relu"),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation="relu"),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dense(64, activation="relu"),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation="softmax"),
    ])

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model
