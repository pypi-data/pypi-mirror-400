"""
Demo: pretrain a TinyAutoencoder on FBX-derived data, export a TorchScript encoder,
and bootstrap Mujoco PPO using the exported encoder.

Usage:
    uv run python examples/humanoid_imitation/bootstrap_from_fbx.py \
      --data examples/humanoid_imitation/data/ground_truth.parquet \
      --ts-out examples/humanoid_imitation/data/fbx_encoder.ts \
      --epochs 5 \
      --ppo-steps 50000 \
      --adapter-mode obs
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader

# Ensure repo root is on path so example modules can be imported when run as a script
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.humanoid_imitation.run import (  # noqa: E402
    TinyAutoencoder,
    FBXDataSet,
    _export_torchscript_encoder,
)


def train_encoder(
    data_path: Path, epochs: int = 5, batch_size: int = 64, lr: float = 1e-3
):
    ds = FBXDataSet(str(data_path))
    in_dim = ds[0][0].numel()
    model = TinyAutoencoder(input_dim=in_dim)
    loader = DataLoader(ds, batch_size=batch_size, shuffle=True)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    model.train()
    for _ in range(epochs):
        for x, _ in loader:
            opt.zero_grad()
            recon = model(x)
            loss = torch.nn.functional.mse_loss(recon, x)
            loss.backward()
            opt.step()
    return model, in_dim


def main():
    parser = argparse.ArgumentParser(
        description="Pretrain encoder on FBX data and run PPO bootstrap."
    )
    parser.add_argument(
        "--data", required=True, help="Path to Parquet/HDF5/JSON FBX data."
    )
    parser.add_argument("--ts-out", required=True, help="Output TorchScript path.")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--adapter-mode", choices=["obs", "feature"], default="obs")
    parser.add_argument("--ppo-steps", type=int, default=50000)
    args = parser.parse_args()

    data_path = Path(args.data)
    ts_path = Path(args.ts_out)
    ts_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Training TinyAutoencoder on {data_path} ...")
    model, in_dim = train_encoder(
        data_path, epochs=args.epochs, batch_size=args.batch_size, lr=args.lr
    )
    _export_torchscript_encoder(model, in_dim, ts_path)
    print(f"Exported TorchScript encoder to {ts_path}")

    cmd = [
        "uv",
        "run",
        "python",
        str(Path(__file__).parent / "train_mujoco.py"),
        "--torchscript-path",
        str(ts_path),
        "--adapter-mode",
        args.adapter_mode,
        "--torchscript-in-dim",
        str(in_dim),
        "--total-timesteps",
        str(args.ppo_steps),
    ]
    print("Launching PPO bootstrap:", " ".join(cmd))
    subprocess.check_call(cmd)


if __name__ == "__main__":
    main()
