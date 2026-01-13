import json
from typing import Dict, Iterable, List, Tuple, Optional, Callable
import torch
from torch.utils.data import DataLoader
import pytorch_lightning as pl
from pytorch_lightning.loggers import MLFlowLogger

from optiq.io.conditional_motion import (
    ConditionalAutoregDataset,
    build_conditional_sequences,
)
from optiq.lightning_modules import ConditionalAutoregLightning
from optiq.callbacks import ProgressCallback, MLflowCheckpointCallback


def train_conditional_autoreg(
    pairs: Iterable[Tuple[str, str]],
    window: int = 10,
    stride: int = 1,
    epochs: int = 30,
    batch_size: int = 32,
    lr: float = 1e-3,
    hidden_size: int = 128,
    num_layers: int = 2,
    dropout: float = 0.1,
    export_pred: str = None,
    rollout_steps: int = 60,
    device: str = None,
    output_path: str = None,
    metrics_list: Optional[List[str]] = None,
    progress_callback: Optional[Callable[[int, Optional[Dict]], None]] = None,
    checkpoint_every: int = 0,
) -> Dict[str, float]:

    sequences, joint_names = build_conditional_sequences(pairs)
    dataset = ConditionalAutoregDataset(sequences, window=window, stride=stride)
    if len(dataset) == 0:
        raise ValueError("Dataset is empty.")

    train_loader = DataLoader(
        dataset, batch_size=batch_size, shuffle=True, num_workers=0
    )
    num_classes = len(set(cls_id for _, cls_id in sequences))

    model = ConditionalAutoregLightning(
        joints=len(joint_names),
        num_classes=num_classes,
        hidden_size=hidden_size,
        num_layers=num_layers,
        dropout=dropout,
        lr=lr,
        metrics=metrics_list,
    )

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
            run_id = mlflow.active_run().info.run_id
            tracking_uri = mlflow.get_tracking_uri()
            logger = MLFlowLogger(run_id=run_id, tracking_uri=tracking_uri)
    except ImportError:
        pass

    trainer = pl.Trainer(
        max_epochs=epochs,
        accelerator="auto",
        devices=1,
        enable_checkpointing=False,
        logger=logger,
        callbacks=callbacks,
    )

    trainer.fit(model, train_dataloaders=train_loader)

    if output_path:
        torch.save(model.model.state_dict(), output_path)
        print(f"Saved model to {output_path}")

    if export_pred:
        first_seq, first_label = sequences[0]
        seed = torch.from_numpy(first_seq[:window])
        # Generate on CPU or same device
        model.eval()
        rollout = model.generate(
            seed=seed, class_id=first_label, steps=rollout_steps, device=model.device
        )

        export_data: Dict[str, List[Dict]] = {
            "fps": 30.0,
            "frames": rollout_steps,
            "bones": {},
        }
        for j, name in enumerate(joint_names):
            export_data["bones"][name] = [
                {"position": rollout[t, j].tolist(), "step": int(t)}
                for t in range(rollout_steps)
            ]
        with open(export_pred, "w") as f:
            json.dump(export_data, f, indent=2)
        print(f"Exported rollout to {export_pred}")

    return {"train_loss": trainer.callback_metrics.get("train_loss", 0.0).item()}
