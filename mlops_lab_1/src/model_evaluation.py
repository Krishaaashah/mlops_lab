import os
import yaml
import json
import numpy as np

from tensorflow.keras.models import load_model

# ----------------------------
# Load Parameters
# ----------------------------

with open("params.yaml", "r") as file:
    params = yaml.safe_load(file)

processed_path = params["data"]["processed_data_path"]
model_path = params["output"]["model_path"]

print("=" * 50)
print("Loading Model...")
print("=" * 50)

# Load model
model = load_model(model_path)

# Load processed test data
data = np.load("data/features/feature_data.npz")

x_test = data["x_test"]
y_test = data["y_test"]

# Evaluate
loss, accuracy = model.evaluate(x_test, y_test, verbose=1)

print("\nEvaluation Completed!")

print(f"Test Loss     : {loss:.4f}")
print(f"Test Accuracy : {accuracy:.4f}")

# Save metrics
os.makedirs("artifacts", exist_ok=True)

metrics = {
    "loss": float(loss),
    "accuracy": float(accuracy)
}

with open("artifacts/metrics.json", "w") as f:
    json.dump(metrics, f, indent=4)

print("\nMetrics saved to artifacts/metrics.json")