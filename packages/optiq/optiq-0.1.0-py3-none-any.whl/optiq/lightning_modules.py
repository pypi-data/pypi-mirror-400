"""
PyTorch Lightning modules for motion prediction training.

Includes specialized modules for:
- Basic next-step prediction
- Scheduled sampling (teacher forcing -> autoregressive)
- Multi-step prediction with accumulated loss

Loss functions:
- MSE: Standard mean squared error
- Chamfer: Chamfer distance between bone positions (robust to small misalignments)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F
import pytorch_lightning as pl


def chamfer_distance(
    pred: torch.Tensor,
    target: torch.Tensor,
    num_bones: int = 65,
    features_per_bone: int = 7,
) -> torch.Tensor:
    """
    Compute Chamfer distance between predicted and target bone positions.

    For motion data, we treat each bone's position as a point in 3D space.
    Chamfer distance finds the nearest neighbor for each point and averages.

    Args:
        pred: Predicted features (B, F) where F = num_bones * features_per_bone
        target: Target features (B, F)
        num_bones: Number of bones (default: 65 for Mixamo)
        features_per_bone: Features per bone (default: 7 = 3 pos + 4 quat)

    Returns:
        Chamfer distance (scalar tensor)
    """
    batch_size = pred.shape[0]

    # Extract positions only (first 3 features per bone)
    # Reshape to (B, num_bones, features_per_bone)
    pred_reshaped = pred.view(batch_size, num_bones, features_per_bone)
    target_reshaped = target.view(batch_size, num_bones, features_per_bone)

    # Get positions (B, num_bones, 3)
    pred_pos = pred_reshaped[:, :, :3]
    target_pos = target_reshaped[:, :, :3]

    # Compute pairwise distances (B, num_bones, num_bones)
    # dist[b, i, j] = ||pred_pos[b, i] - target_pos[b, j]||^2
    diff = pred_pos.unsqueeze(2) - target_pos.unsqueeze(1)  # (B, N, N, 3)
    dist_sq = (diff**2).sum(-1)  # (B, N, N)

    # For each predicted point, find nearest target point
    min_pred_to_target = dist_sq.min(dim=2)[0]  # (B, N)

    # For each target point, find nearest predicted point
    min_target_to_pred = dist_sq.min(dim=1)[0]  # (B, N)

    # Chamfer distance is the mean of both directions
    chamfer = (min_pred_to_target.mean() + min_target_to_pred.mean()) / 2

    return chamfer


def chamfer_with_quaternion_loss(
    pred: torch.Tensor,
    target: torch.Tensor,
    num_bones: int = 65,
    features_per_bone: int = 7,
    pos_weight: float = 1.0,
    quat_weight: float = 0.5,
) -> torch.Tensor:
    """
    Combined loss: Chamfer distance on positions + MSE on quaternions.

    Args:
        pred: Predicted features (B, F)
        target: Target features (B, F)
        num_bones: Number of bones
        features_per_bone: Features per bone (3 pos + 4 quat)
        pos_weight: Weight for position chamfer loss
        quat_weight: Weight for quaternion MSE loss

    Returns:
        Combined loss (scalar tensor)
    """
    batch_size = pred.shape[0]

    # Reshape to (B, num_bones, features_per_bone)
    pred_reshaped = pred.view(batch_size, num_bones, features_per_bone)
    target_reshaped = target.view(batch_size, num_bones, features_per_bone)

    # Position chamfer loss
    pred_pos = pred_reshaped[:, :, :3]
    target_pos = target_reshaped[:, :, :3]

    diff = pred_pos.unsqueeze(2) - target_pos.unsqueeze(1)
    dist_sq = (diff**2).sum(-1)
    min_pred_to_target = dist_sq.min(dim=2)[0]
    min_target_to_pred = dist_sq.min(dim=1)[0]
    pos_loss = (min_pred_to_target.mean() + min_target_to_pred.mean()) / 2

    # Quaternion MSE loss (with symmetry: q and -q represent same rotation)
    pred_quat = pred_reshaped[:, :, 3:7]
    target_quat = target_reshaped[:, :, 3:7]

    # Compute loss for both q and -q, take minimum
    quat_diff_pos = (pred_quat - target_quat) ** 2
    quat_diff_neg = (pred_quat + target_quat) ** 2
    quat_loss = torch.minimum(quat_diff_pos.sum(-1), quat_diff_neg.sum(-1)).mean()

    return pos_weight * pos_loss + quat_weight * quat_loss


class NextStepLitModule(pl.LightningModule):
    """Basic next-step prediction module."""

    def __init__(self, model: nn.Module, lr: float = 1e-3):
        super().__init__()
        self.model = model
        self.lr = lr

    def forward(self, x, condition=None):
        return self.model(x, condition=condition)

    def training_step(self, batch, batch_idx):
        x, y, cond = batch
        out = self(x, condition=cond)
        loss = F.mse_loss(out, y)
        self.log("train_loss", loss, prog_bar=True, on_step=True, on_epoch=True)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.lr)


class ScheduledSamplingLitModule(pl.LightningModule):
    """
    Training module with proper scheduled sampling for autoregressive stability.

    KEY INSIGHT: The model must be trained on its OWN predictions with gradients
    flowing through the entire rollout. This is computationally expensive but
    necessary for the model to learn error recovery.

    REQUIRES: RolloutDataset that provides sequences of targets.

    Training modes:
    1. "teacher_forcing": Always use ground truth (fast, but poor inference)
    2. "scheduled": Mix of teacher forcing and free-running (balanced)
    3. "free_running": Always use predictions with full gradient (slow, best inference)

    The scheduled mode transitions from teacher_forcing to free_running over training.
    """

    def __init__(
        self,
        model: nn.Module,
        lr: float = 1e-3,
        sampling_schedule: str = "linear",
        initial_teacher_ratio: float = 1.0,
        final_teacher_ratio: float = 0.0,
        decay_steps: int = 10000,
        rollout_steps: int = 10,
        noise_std: float = 0.005,
        loss_type: str = "mse",
        num_bones: int = 65,
        features_per_bone: int = 7,
        velocity_weight: float = 0.1,
        # New: control gradient flow
        gradient_steps: int = 5,  # How many steps to backprop through (memory vs quality)
    ):
        super().__init__()
        self.model = model
        self.lr = lr
        self.sampling_schedule = sampling_schedule
        self.initial_teacher_ratio = initial_teacher_ratio
        self.final_teacher_ratio = final_teacher_ratio
        self.decay_steps = decay_steps
        self.rollout_steps = rollout_steps
        self.noise_std = noise_std
        self.loss_type = loss_type
        self.num_bones = num_bones
        self.features_per_bone = features_per_bone
        self.velocity_weight = velocity_weight
        self.gradient_steps = gradient_steps

        self.save_hyperparameters(ignore=["model"])

    def forward(self, x, condition=None):
        return self.model(x, condition=condition)

    def compute_loss(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """Compute loss based on configured loss type."""
        if self.loss_type == "chamfer":
            return chamfer_distance(
                pred, target, self.num_bones, self.features_per_bone
            )
        elif self.loss_type == "chamfer_quat":
            return chamfer_with_quaternion_loss(
                pred, target, self.num_bones, self.features_per_bone
            )
        else:  # mse
            return F.mse_loss(pred, target)

    def get_teacher_ratio(self) -> float:
        """Get current teacher forcing ratio based on training step."""
        step = self.global_step
        if self.sampling_schedule == "linear":
            ratio = self.initial_teacher_ratio - (
                (self.initial_teacher_ratio - self.final_teacher_ratio)
                * min(step / self.decay_steps, 1.0)
            )
        elif self.sampling_schedule == "exponential":
            decay_rate = max(
                (self.final_teacher_ratio + 1e-8) / (self.initial_teacher_ratio + 1e-8),
                1e-8,
            ) ** (1 / max(self.decay_steps, 1))
            ratio = self.initial_teacher_ratio * (decay_rate**step)
            ratio = max(ratio, self.final_teacher_ratio)
        else:
            ratio = self.initial_teacher_ratio
        return ratio

    def training_step(self, batch, batch_idx):
        x, targets, cond = batch
        # x: (B, F) - starting frame
        # targets: (B, T, F) - sequence of future frames OR (B, F) for single-step

        # Handle single-step datasets
        if targets.dim() == 2:
            pred = self(x, condition=cond)
            loss = self.compute_loss(pred, targets)
            self.log("train_loss", loss, prog_bar=True, on_step=True, on_epoch=True)
            return loss

        # Multi-step dataset: targets is (B, T, F)
        num_steps = min(targets.shape[1], self.rollout_steps)
        teacher_ratio = self.get_teacher_ratio()

        # Decide training mode for this batch
        # Key: entire batch uses same mode for stability
        use_teacher_forcing = torch.rand(1).item() < teacher_ratio

        total_loss = 0.0
        predictions = []
        prev_input = x

        for step in range(num_steps):
            target = targets[:, step, :]  # (B, F)

            # Add noise to input for robustness (always, small amount)
            if self.noise_std > 0:
                noisy_input = prev_input + torch.randn_like(prev_input) * self.noise_std
            else:
                noisy_input = prev_input

            # Forward pass
            pred = self(noisy_input, condition=cond)
            predictions.append(pred)

            # Compute loss with decreasing weight for later steps
            step_weight = 1.0 / (1.0 + 0.05 * step)  # Gentler decay
            step_loss = self.compute_loss(pred, target) * step_weight
            total_loss = total_loss + step_loss

            # Determine next input
            if use_teacher_forcing:
                # Teacher forcing: use ground truth
                prev_input = target
            else:
                # Free running: use prediction
                # KEY FIX: Only detach after gradient_steps to allow some gradient flow
                # but prevent memory explosion
                if step < self.gradient_steps - 1:
                    prev_input = pred  # Keep gradients
                else:
                    prev_input = pred.detach()  # Detach to save memory

        # Velocity consistency loss across entire trajectory
        if self.velocity_weight > 0 and len(predictions) > 1:
            pred_stack = torch.stack(predictions, dim=1)  # (B, T, F)

            # Predicted velocities
            pred_vel = pred_stack[:, 1:, :] - pred_stack[:, :-1, :]

            # Ground truth velocities
            gt_vel = targets[:, 1:num_steps, :] - targets[:, : num_steps - 1, :]

            vel_loss = F.mse_loss(pred_vel, gt_vel) * self.velocity_weight
            total_loss = total_loss + vel_loss
            self.log("vel_loss", vel_loss, on_step=False, on_epoch=True)

        # Normalize loss by number of steps
        total_loss = total_loss / num_steps

        self.log("train_loss", total_loss, prog_bar=True, on_step=True, on_epoch=True)
        self.log("teacher_ratio", teacher_ratio, on_step=False, on_epoch=True)
        self.log(
            "use_teacher", float(use_teacher_forcing), on_step=False, on_epoch=True
        )

        return total_loss

    def validation_step(self, batch, batch_idx):
        """
        Validation always runs in free-running mode (no teacher forcing).
        This gives a realistic estimate of inference quality.
        """
        x, targets, cond = batch

        if targets.dim() == 2:
            pred = self(x, condition=cond)
            loss = self.compute_loss(pred, targets)
            self.log("val_loss", loss, prog_bar=True, on_epoch=True)
            return loss

        num_steps = targets.shape[1]
        total_loss = 0.0
        prev_input = x

        # Pure autoregressive rollout - no teacher forcing
        with torch.no_grad():
            for step in range(num_steps):
                target = targets[:, step, :]
                pred = self(prev_input, condition=cond)
                step_loss = self.compute_loss(pred, target)
                total_loss = total_loss + step_loss
                prev_input = pred  # Always use prediction

        avg_loss = total_loss / num_steps
        self.log("val_loss", avg_loss, prog_bar=True, on_epoch=True)

        # Also log final step loss (most indicative of long-term stability)
        self.log("val_final_step_loss", step_loss, on_epoch=True)

        return avg_loss

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.parameters(), lr=self.lr, weight_decay=1e-4)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer,
            T_0=max(self.decay_steps // 4, 100),
            T_mult=2,
            eta_min=self.lr * 0.01,
        )
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": scheduler,
                "interval": "step",
            },
        }


class MultiStepLitModule(pl.LightningModule):
    """
    Training module for multi-step prediction.

    Trains the model to predict multiple future frames autoregressively,
    accumulating loss at each step. This directly optimizes for rollout quality.

    Args:
        model: The motion prediction model
        lr: Learning rate
        num_steps: Number of steps to unroll during training
        step_loss_weights: Optional weights for each step's loss (default: uniform)
        noise_std: Noise to add to predictions before feeding back
    """

    def __init__(
        self,
        model: nn.Module,
        lr: float = 1e-3,
        num_steps: int = 5,
        step_loss_weights: Optional[list] = None,
        noise_std: float = 0.0,
    ):
        super().__init__()
        self.model = model
        self.lr = lr
        self.num_steps = num_steps
        self.noise_std = noise_std

        # Default: equal weights with slight decay
        if step_loss_weights is None:
            self.step_loss_weights = [1.0 / (i + 1) for i in range(num_steps)]
        else:
            self.step_loss_weights = step_loss_weights

        # Normalize weights
        total = sum(self.step_loss_weights)
        self.step_loss_weights = [w / total for w in self.step_loss_weights]

        self.save_hyperparameters(ignore=["model"])

    def forward(self, x, condition=None):
        return self.model(x, condition=condition)

    def training_step(self, batch, batch_idx):
        x, targets, cond = batch
        # targets shape: (B, num_steps, F)

        total_loss = 0.0
        prev = x

        actual_steps = min(self.num_steps, targets.shape[1])

        for step in range(actual_steps):
            pred = self(prev, condition=cond)
            target = targets[:, step, :]

            step_loss = F.mse_loss(pred, target)
            weighted_loss = step_loss * self.step_loss_weights[step]
            total_loss = total_loss + weighted_loss

            # Use prediction as next input (with optional noise)
            if self.noise_std > 0:
                prev = pred + torch.randn_like(pred) * self.noise_std
            else:
                prev = pred

            self.log(f"step_{step}_loss", step_loss, on_step=False, on_epoch=True)

        self.log("train_loss", total_loss, prog_bar=True, on_step=True, on_epoch=True)

        return total_loss

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.parameters(), lr=self.lr, weight_decay=1e-5)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer, T_0=1000, T_mult=2, eta_min=self.lr * 0.01
        )
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": scheduler,
                "interval": "step",
            },
        }


class SphereCNNLightning(pl.LightningModule):
    """
    Lightning module for SphereMotionCNN training.

    Expects input shape: (batch, joints, 3)
    Target shape: (batch, joints, 3)
    """

    def __init__(
        self,
        hidden: int = 64,
        layers: int = 3,
        kernel_size: int = 3,
        dropout: float = 0.0,
        lr: float = 1e-3,
        loss_fn: str = "mse",
    ):
        super().__init__()
        from optiq.models.sphere_cnn import SphereMotionCNN

        self.model = SphereMotionCNN(
            hidden=hidden,
            layers=layers,
            kernel_size=kernel_size,
            dropout=dropout,
        )

        if loss_fn == "mse":
            self.loss_fn = F.mse_loss
        elif loss_fn == "chamfer":
            self.loss_fn = chamfer_distance
        else:
            raise ValueError(f"Unknown loss function: {loss_fn}")

        self.lr = lr
        self.save_hyperparameters()

    def forward(self, x):
        # Input: (batch, joints, 3) -> (batch, joints, 3)
        return self.model(x)

    def training_step(self, batch, batch_idx):
        x, targets = batch

        # Forward pass
        pred = self(x)

        # Compute loss
        loss = self.loss_fn(pred, targets)

        self.log("train_loss", loss, prog_bar=True, on_step=True, on_epoch=True)

        return loss

    def validation_step(self, batch, batch_idx):
        x, targets = batch
        pred = self(x)
        loss = self.loss_fn(pred, targets)
        self.log("val_loss", loss, on_step=False, on_epoch=True)
        return loss

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.parameters(), lr=self.lr, weight_decay=1e-5)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer, T_0=1000, T_mult=2, eta_min=self.lr * 0.01
        )
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": scheduler,
                "interval": "step",
            },
        }


class ConditionalAutoregLightning(pl.LightningModule):
    """
    Lightning module for ConditionalAutoregressiveModel training.

    Expects input: history (B, T, J, 3), class_ids (B,)
    Target: next_positions (B, J, 3)
    """

    def __init__(
        self,
        joints: int,
        num_classes: int,
        hidden_size: int = 128,
        num_layers: int = 2,
        dropout: float = 0.1,
        lr: float = 1e-3,
        loss_fn: str = "mse",
    ):
        super().__init__()
        from optiq.models.conditional_autoreg import ConditionalAutoregressiveModel

        self.model = ConditionalAutoregressiveModel(
            joints=joints,
            num_classes=num_classes,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout,
        )

        if loss_fn == "mse":
            self.loss_fn = F.mse_loss
        elif loss_fn == "chamfer":
            self.loss_fn = chamfer_distance
        else:
            raise ValueError(f"Unknown loss function: {loss_fn}")

        self.lr = lr
        self.save_hyperparameters()

    def forward(self, history, class_ids):
        # Input: history (B, T, J, 3), class_ids (B,)
        # Output: (B, J, 3)
        return self.model(history, class_ids)

    def training_step(self, batch, batch_idx):
        history, class_ids, targets = batch

        # Forward pass
        pred = self(history, class_ids)

        # Compute loss
        loss = self.loss_fn(pred, targets)

        self.log("train_loss", loss, prog_bar=True, on_step=True, on_epoch=True)

        return loss

    def validation_step(self, batch, batch_idx):
        history, class_ids, targets = batch
        pred = self(history, class_ids)
        loss = self.loss_fn(pred, targets)
        self.log("val_loss", loss, on_step=False, on_epoch=True)
        return loss

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.parameters(), lr=self.lr, weight_decay=1e-5)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer, T_0=1000, T_mult=2, eta_min=self.lr * 0.01
        )
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": scheduler,
                "interval": "step",
            },
        }
