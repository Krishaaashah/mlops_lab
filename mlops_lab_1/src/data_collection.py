from tensorflow.keras.datasets import fashion_mnist
import yaml

# Load parameters
with open("params.yaml", "r") as file:
    params = yaml.safe_load(file)

print("=" * 50)
print("Downloading Fashion-MNIST Dataset...")
print("=" * 50)

# Download dataset
(x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()

print("\nDataset downloaded successfully!\n")

print(f"Training Images : {x_train.shape}")
print(f"Training Labels : {y_train.shape}")

print(f"Testing Images  : {x_test.shape}")
print(f"Testing Labels  : {y_test.shape}")