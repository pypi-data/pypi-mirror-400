import os
from optiq.training.sphere_cnn_runner import train_sphere_cnn


def main():
    print("Running local training without external MLflow server...")

    # Simple config
    json_path = "extracted_jogging/jogging_anim.json"

    # Check if data exists
    if not os.path.exists(json_path):
        print(
            f"Warning: {json_path} not found. Using dummy path (will fail if not present)."
        )

    # Run training directly
    # This will use TensorBoardLogger by default (saving to lightning_logs/)
    # and save the model to 'local_model.pt'
    metrics = train_sphere_cnn(
        json_path=json_path,
        epochs=3,
        batch_size=32,
        lr=1e-3,
        hidden=64,
        layers=3,
        out_path="local_model.pt",
        metrics_list=["MeanSquaredError"],
        # Checkpoints will be saved locally in CWD as epoch_X_checkpoint.pt
        # and NOT deleted because no MLflow run is active to upload them to.
        checkpoint_every=1,
    )

    print("Training finished!")
    print(f"Metrics: {metrics}")
    print("Model saved to: local_model.pt")
    print("Checkpoints saved in current directory.")
    print("Logs available in 'lightning_logs/'")


if __name__ == "__main__":
    main()
