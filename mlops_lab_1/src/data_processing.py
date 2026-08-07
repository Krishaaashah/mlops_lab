import os
import yaml
import numpy as np
from tensorflow.keras.datasets import fashion_mnist

# Load configuration
with open("params.yaml", "r") as file:
    params = yaml.safe_load(file)

processed_path = params["data"]["processed_data_path"]

os.makedirs(processed_path, exist_ok=True)

print("=" * 50)
print("Loading Fashion-MNIST Dataset...")
print("=" * 50)

# Load dataset
(x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()

print("Processing dataset...")

# Normalize pixel values (0-255 → 0-1)
x_train = x_train.astype("float32") / 255.0
x_test = x_test.astype("float32") / 255.0

# Reshape for CNN (add channel dimension)
x_train = x_train.reshape(-1, 28, 28, 1)
x_test = x_test.reshape(-1, 28, 28, 1)

# Save processed arrays
np.save(os.path.join(processed_path, "x_train.npy"), x_train)
np.save(os.path.join(processed_path, "y_train.npy"), y_train)
np.save(os.path.join(processed_path, "x_test.npy"), x_test)
np.save(os.path.join(processed_path, "y_test.npy"), y_test)

print("\n✅ Data Processing Completed Successfully!")

print(f"x_train shape : {x_train.shape}")
print(f"y_train shape : {y_train.shape}")
print(f"x_test shape  : {x_test.shape}")
print(f"y_test shape  : {y_test.shape}")