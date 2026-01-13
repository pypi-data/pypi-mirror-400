#!/usr/bin/env python3
"""
Example of registering a custom model and training loop, then running training via the runner API.

Usage:
  uv run python examples/register_custom.py
"""

import os
import sys

# Ensure repo src/ is on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import torch
import torch.nn as nn

from optiq.training.sphere_cnn_runner import (
    register_model,
    register_training,
    train_sphere_cnn,
)


# Register a tiny linear model
def build_tiny(**kwargs):
    hidden = kwargs.get("hidden", 32)
    return nn.Sequential(
        nn.Flatten(start_dim=1),  # (B, J, 3) -> (B, J*3)
        nn.Linear(hidden, hidden),
        nn.ReLU(inplace=True),
        nn.Linear(hidden, hidden),
        nn.ReLU(inplace=True),
        nn.Linear(
            hidden, 3 * kwargs.get("joints", 65)
        ),  # assumes ~65 joints by default
    )


# Register a simple L1 training strategy
def make_l1_strategy(params):
    weight = params.get("my_weight", 1.0)
    loss_fn = nn.L1Loss(reduction="sum")

    def train_step(model, x, y, _, opt, device):
        x, y = x.to(device), y.to(device)
        b, j, c = y.shape
        pred = model(x).view(b, j, c)
        loss = weight * loss_fn(pred, y)
        opt.zero_grad()
        loss.backward()
        opt.step()
        return loss.item()

    def eval_step(model, x, y, _, device):
        x, y = x.to(device), y.to(device)
        b, j, c = y.shape
        pred = model(x).view(b, j, c)
        loss = weight * loss_fn(pred, y)
        return loss.item()

    return train_step, eval_step


def main():
    # Register custom components
    register_model("my_custom_model", build_tiny)
    register_training("my_custom_training", make_l1_strategy)

    # Run training using the custom entries (config could also set these)
    train_sphere_cnn(
        json_path="extracted_jogging/jogging_anim.json",
        source="bones",
        epochs=1,
        batch_size=16,
        lr=1e-3,
        model_type="my_custom_model",
        model_cfg={"params": {"hidden": 64}},
        training_type="my_custom_training",
        training_cfg={"params": {"my_weight": 1.0}},
        out_path="custom_registered.pt",
        export_pred="predicted_custom_registered.json",
    )


if __name__ == "__main__":
    main()
