import os
import yaml
import numpy as np

# Load parameters
with open("params.yaml", "r") as file:
    params = yaml.safe_load(file)

processed_path = params["data"]["processed_data_path"]

print("=" * 50)
print("Loading Processed Data...")
print("=" * 50)

x_train = np.load(os.path.join(processed_path, "x_train.npy"))
y_train = np.load(os.path.join(processed_path, "y_train.npy"))

x_test = np.load(os.path.join(processed_path, "x_test.npy"))
y_test = np.load(os.path.join(processed_path, "y_test.npy"))

print("Processed data loaded successfully!")


features_path = "data/features"
os.makedirs(features_path, exist_ok=True)

np.savez(
    os.path.join(features_path, "feature_data.npz"),
    x_train=x_train,
    y_train=y_train,
    x_test=x_test,
    y_test=y_test
)

print("\nFeature Selection Completed Successfully!")

print(f"x_train : {x_train.shape}")
print(f"x_test  : {x_test.shape}")