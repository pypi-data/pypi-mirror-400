import os
import json
import mlflow
from optiq.training.sphere_cnn_runner import train_sphere_cnn

# 1. Setup Configuration
# This config mimics what the Web UI produces
config = {
    "json_path": "extracted_jogging/jogging_anim.json",  # Path to your data
    "epochs": 5,
    "batch_size": 32,
    "lr": 1e-3,
    "hidden_dim": 64,
    "layers": 3,
    "metrics": ["MeanSquaredError", "MeanAbsoluteError"],
}

# 2. Setup MLflow (Optional but recommended for persistence)
# Point to your MLflow server (e.g., from Docker Compose) or local ./mlruns
mlflow.set_tracking_uri("http://localhost:5001")
mlflow.set_experiment("programmatic_training")

print("Starting training...")

# 3. Run Training wrapped in MLflow run
with mlflow.start_run() as run:
    print(f"MLflow Run ID: {run.info.run_id}")

    # Log parameters
    mlflow.log_params(config)

    # Execute Training
    # The runner handles the PyTorch Lightning loop
    metrics = train_sphere_cnn(
        json_path=config["json_path"],
        epochs=config["epochs"],
        batch_size=config["batch_size"],
        lr=config["lr"],
        hidden=config["hidden_dim"],
        layers=config["layers"],
        out_path="my_model.pt",
        metrics_list=config["metrics"],
        checkpoint_every=2,  # Save checkpoint every 2 epochs
    )

    # Log final model (best-effort, avoid crash if artifact store is read-only)
    mlflow.log_artifact("my_model.pt")

    print("Training Complete!")
    print("Final Metrics:", metrics)
