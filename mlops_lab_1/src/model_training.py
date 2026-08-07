import os
import yaml
import numpy as np

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Conv2D,
    MaxPooling2D,
    Flatten,
    Dense,
    Dropout
)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ----------------------------
# Load Parameters
# ----------------------------

with open("params.yaml", "r") as file:
    params = yaml.safe_load(file)

processed_path = params["data"]["processed_data_path"]

model_path = params["output"]["model_path"]

batch_size = params["model"]["batch_size"]
epochs = params["model"]["epochs"]
learning_rate = params["model"]["learning_rate"]
dropout_rate = params["model"]["dropout_rate"]

# ----------------------------
# Load Data
# ----------------------------

print("=" * 50)
print("Loading Feature Data...")
print("=" * 50)


data = np.load("data/features/feature_data.npz")

x_train = data["x_train"]
y_train = data["y_train"]

x_test = data["x_test"]
y_test = data["y_test"]

# ----------------------------
# Data Augmentation
# ----------------------------

datagen = ImageDataGenerator(
    rotation_range=10,
    zoom_range=0.1
)

datagen.fit(x_train)

# ----------------------------
# CNN Model
# ----------------------------

model = Sequential([

    Conv2D(32, (3,3), activation="relu", input_shape=(28,28,1)),
    MaxPooling2D(),

    Conv2D(64, (3,3), activation="relu"),
    MaxPooling2D(),

    Flatten(),

    Dense(128, activation="relu"),

    Dropout(dropout_rate),

    Dense(10, activation="softmax")

])

# ----------------------------
# Compile
# ----------------------------

model.compile(
    optimizer=Adam(learning_rate=learning_rate),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# ----------------------------
# Train
# ----------------------------

history = model.fit(
    datagen.flow(x_train, y_train, batch_size=batch_size),
    epochs=epochs,
    validation_data=(x_test, y_test)
)

# ----------------------------
# Save Model
# ----------------------------

os.makedirs("models", exist_ok=True)

model.save(model_path)

np.save(
    "models/history.npy",
    history.history
)

print("\nTraining Completed Successfully!")

print(f"Model Saved At : {model_path}")