import pytorch_lightning as pl
from typing import Callable, Dict, Optional, Any
import torch
import mlflow
import os


class ProgressCallback(pl.Callback):
    def __init__(self, update_fn: Callable[[int, Optional[Dict[str, Any]]], None]):
        self.update_fn = update_fn

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        # trainer.num_training_batches is the total batches per epoch
        total_batches = trainer.num_training_batches
        current_epoch = trainer.current_epoch
        max_epochs = trainer.max_epochs

        # Total steps = max_epochs * total_batches
        # Current step = current_epoch * total_batches + batch_idx + 1

        progress = 0
        if total_batches > 0:
            total_steps = max_epochs * total_batches
            current_step = current_epoch * total_batches + batch_idx + 1
            progress = int((current_step / total_steps) * 100)

        # We generally don't want to spam metrics every batch unless needed
        # But we can update progress
        self.update_fn(progress, None)

    def on_train_epoch_end(self, trainer, pl_module):
        # Ensure we hit the epoch milestones cleanly
        progress = int(((trainer.current_epoch + 1) / trainer.max_epochs) * 100)

        # Collect metrics
        metrics = {}
        for k, v in trainer.callback_metrics.items():
            if isinstance(v, torch.Tensor):
                metrics[k] = v.item()
            else:
                metrics[k] = v

        # Add epoch info
        metrics["epoch"] = trainer.current_epoch + 1

        self.update_fn(progress, metrics)


class MLflowCheckpointCallback(pl.Callback):
    def __init__(self, every_n_epochs: int = 1, save_name: str = "checkpoint.pt"):
        self.every_n_epochs = every_n_epochs
        self.save_name = save_name

    def on_train_epoch_end(self, trainer, pl_module):
        epoch = trainer.current_epoch + 1
        if epoch % self.every_n_epochs == 0:
            # Save model
            # We access the underlying model from the lightning module
            if hasattr(pl_module, "model"):
                state_dict = pl_module.model.state_dict()

                # Save locally first
                filename = f"epoch_{epoch}_{self.save_name}"
                torch.save(state_dict, filename)

                # Log to MLflow (best-effort to avoid training failure on FS issues)
                uploaded = False
                if mlflow.active_run():
                    run_id = mlflow.active_run().info.run_id
                    print(f"Checkpoing: uploading {filename} to MLflow run {run_id}")
                    try:
                        mlflow.log_artifact(filename, artifact_path="checkpoints")
                        uploaded = True
                    except Exception as e:
                        # Do not crash training if artifact store is unavailable or read-only
                        print(f"Warning: failed to upload checkpoint to MLflow ({e})")

                # Cleanup local checkpoint ONLY if uploaded successfully
                # For local usage without MLflow active run, we keep the files.
                if uploaded and os.path.exists(filename):
                    os.remove(filename)
