import json
from typing import Dict, List, Optional, Callable
import torch
from torch.utils.data import DataLoader, random_split
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.loggers import MLFlowLogger

from optiq.io.sphere_data import SphereSequenceDataset, load_sphere_positions
from optiq.lightning_modules import SphereCNNLightning
from optiq.callbacks import ProgressCallback, MLflowCheckpointCallback


def train_sphere_cnn(
    json_path: str,
    source: str = "bones",
    horizon: int = 1,
    epochs: int = 25,
    batch_size: int = 64,
    lr: float = 1e-3,
    val_split: float = 0.1,
    hidden: int = 64,
    layers: int = 3,
    kernel_size: int = 3,
    dropout: float = 0.0,
    model_type: str = "cnn",
    training_type: str = "next",
    noise_std: float = 0.1,
    out_path: str = "sphere_cnn.pt",
    export_pred: Optional[str] = None,
    metrics_list: Optional[List[str]] = None,
    progress_callback: Optional[Callable[[int, Optional[Dict]], None]] = None,
    checkpoint_every: int = 0,
) -> Dict[str, float]:
    """
    Train SphereMotionCNN using PyTorch Lightning.
    """
    # Data Loading
    positions, names, fps = load_sphere_positions(json_path, source=source)
    dataset = SphereSequenceDataset(positions, horizon=horizon)

    val_len = int(len(dataset) * val_split)
    train_len = max(len(dataset) - val_len, 1)
    train_set, val_set = random_split(dataset, [train_len, val_len])

    train_loader = DataLoader(
        train_set, batch_size=batch_size, shuffle=True, num_workers=0
    )
    val_loader = (
        DataLoader(val_set, batch_size=batch_size, shuffle=False, num_workers=0)
        if val_len > 0
        else None
    )

    # PL Module
    model = SphereCNNLightning(
        hidden=hidden,
        layers=layers,
        kernel_size=kernel_size,
        dropout=dropout,
        lr=lr,
        model_type=model_type,
        noise_std=noise_std,
        training_type=training_type,
        metrics=metrics_list,
    )

    # Trainer
    # We want to save state_dict to out_path at the end.
    # Lightning saves checkpoints. We can extract state_dict or just save manual.
    callbacks = []
    if progress_callback:
        callbacks.append(ProgressCallback(progress_callback))

    if checkpoint_every > 0:
        callbacks.append(MLflowCheckpointCallback(every_n_epochs=checkpoint_every))

    # Use MLFlowLogger if we are in an active run (worker handles start_run)
    logger = True  # Default
    try:
        import mlflow

        if mlflow.active_run():
            # If active run exists, MLFlowLogger can attach to it?
            # Actually MLFlowLogger needs run_id or creates new.
            # If we pass run_id=active_run.info.run_id, it should work.
            run_id = mlflow.active_run().info.run_id
            tracking_uri = mlflow.get_tracking_uri()
            logger = MLFlowLogger(run_id=run_id, tracking_uri=tracking_uri)
    except ImportError:
        pass

    trainer = pl.Trainer(
        max_epochs=epochs,
        devices=1,
        accelerator="auto",
        enable_checkpointing=False,  # We manage save manually for now to match interface
        logger=logger,
        enable_progress_bar=True,  # Worker captures stdout
        callbacks=callbacks,
    )

    trainer.fit(model, train_dataloaders=train_loader, val_dataloaders=val_loader)

    # Save final model state dict
    torch.save(model.model.state_dict(), out_path)

    # Export predictions if requested
    if export_pred:
        model.eval()
        device = model.device
        with torch.no_grad():
            frames_out = positions.shape[0] - horizon
            bones: Dict[str, List[Dict]] = {name: [] for name in names}
            for i in range(frames_out):
                x = torch.from_numpy(positions[i]).unsqueeze(0).to(device)
                pred = model(x)[0].cpu().numpy()
                for j, name in enumerate(names):
                    bones[name].append(
                        {
                            "position": pred[j].tolist(),
                            "step": i,
                        }
                    )
        export = {"fps": fps, "frames": frames_out, source: bones}
        with open(export_pred, "w") as f:
            json.dump(export, f, indent=2)

    # Return final metrics
    return {
        "train_loss": trainer.callback_metrics.get("train_loss", 0.0).item(),
        "val_loss": trainer.callback_metrics.get("val_loss", float("nan")).item(),
    }
