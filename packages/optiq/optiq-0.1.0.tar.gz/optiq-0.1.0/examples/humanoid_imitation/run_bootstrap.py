"""
End-to-end example:
1) Extract FBX animation (via node script).
2) Fit a tiny autoencoder on FBX features (TorchScript export).
3) Run PPO with Mujoco Humanoid, bootstrapped from the TorchScript encoder as
   either an observation wrapper or feature extractor.

Usage (defaults, quick):
    uv run python examples/humanoid_imitation/run_bootstrap.py --mode obs

Mode choices:
    --mode obs     # wraps observations with the TorchScript encoder
    --mode feature # uses TorchScript encoder as PPO feature extractor
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent


def run_node_extract(fbx_path: Path, out_json: Path, fps: int = 30):
    extract_script = PROJECT_ROOT / "scripts" / "extract_fbx_anim.js"
    if not extract_script.exists():
        raise FileNotFoundError(f"Extraction script missing: {extract_script}")
    cmd = ["node", str(extract_script), str(fbx_path), str(out_json), f"--fps={fps}"]
    subprocess.check_call(cmd)


class TinyAutoencoder(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 256, bottleneck: int = 128):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, bottleneck),
            nn.ReLU(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(bottleneck, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
        )

    def forward(self, x):
        z = self.encoder(x)
        out = self.decoder(z)
        return out

    def encode(self, x):
        return self.encoder(x)


def fit_autoencoder(
    json_path: Path, epochs: int = 5, batch_size: int = 64, lr: float = 1e-3
):
    from optiq.rl.fbx_dataset import FBXDataSet

    ds = FBXDataSet(str(json_path))
    input_dim = ds[0][0].numel()
    model = TinyAutoencoder(input_dim=input_dim)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loader = DataLoader(ds, batch_size=batch_size, shuffle=True)
    model.train()
    for _ in range(epochs):
        for x, _ in loader:
            opt.zero_grad()
            recon = model(x)
            loss = nn.functional.mse_loss(recon, x)
            loss.backward()
            opt.step()
    return model, input_dim


def export_torchscript_encoder(model: TinyAutoencoder, input_dim: int, out_path: Path):
    model.eval()
    example = torch.zeros(1, input_dim)
    scripted = torch.jit.trace(model.encoder, example)
    scripted.save(str(out_path))
    return out_path


def launch_ppo(
    scripted_encoder: Path,
    mode: str,
    input_dim: int,
    bc_json: Path,
    bc_steps: int,
    bc_batch_size: int,
):
    trainer = SCRIPT_DIR / "train_mujoco.py"
    cmd = [
        sys.executable,
        str(trainer),
        "--torchscript-path",
        str(scripted_encoder),
        "--adapter-mode",
        mode,
        "--total-timesteps",
        "100000",
        "--torchscript-in-dim",
        str(input_dim),
        "--bc-json",
        str(bc_json),
        "--bc-steps",
        str(bc_steps),
        "--bc-batch-size",
        str(bc_batch_size),
    ]
    subprocess.check_call(cmd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fbx", default=str(SCRIPT_DIR / "Walking.fbx"))
    parser.add_argument("--mode", choices=["obs", "feature"], default="obs")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument(
        "--bc-steps",
        type=int,
        default=1000,
        help="Behavior cloning gradient steps before PPO.",
    )
    parser.add_argument("--bc-batch-size", type=int, default=256)
    args = parser.parse_args()

    data_dir = SCRIPT_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    gt_json = data_dir / "ground_truth.json"

    run_node_extract(Path(args.fbx), gt_json)
    ae, in_dim = fit_autoencoder(gt_json, epochs=args.epochs)
    ts_path = data_dir / "fbx_encoder.ts"
    export_torchscript_encoder(ae, in_dim, ts_path)
    launch_ppo(
        ts_path,
        mode=args.mode,
        input_dim=in_dim,
        bc_json=gt_json,
        bc_steps=args.bc_steps,
        bc_batch_size=args.bc_batch_size,
    )


if __name__ == "__main__":
    main()
