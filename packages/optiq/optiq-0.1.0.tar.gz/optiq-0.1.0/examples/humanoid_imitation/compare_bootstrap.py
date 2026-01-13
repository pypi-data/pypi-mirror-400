"""
Compare PPO training with and without a bootstrapped TorchScript encoder+adapter.

Steps:
1) Extract FBX to ground_truth.json (via node script, or mock fallback).
2) Train a tiny autoencoder on the FBX features and export its encoder as TorchScript.
3) Run two PPO trainings:
   - Baseline: no TorchScript / no adapter.
   - Bootstrapped: TorchScript encoder applied (obs or feature mode).
4) Read EvalCallback logs from both runs and generate a Plotly comparison graph.

Usage:
    uv run python examples/humanoid_imitation/compare_bootstrap.py \
      --fbx Walking.fbx \
      --ppo-steps 50000 \
      --bootstrap-mode feature
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Tuple

import numpy as np
import plotly.graph_objects as go
import torch
from torch import nn
from torch.utils.data import DataLoader

from optiq.data.frame_sequence import FrameSequence

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).parent


def _run_node_extract(fbx_path: Path, out_json: Path, fps: int = 30):
    extract_script = PROJECT_ROOT / "scripts" / "extract_fbx_anim.js"
    if not extract_script.exists():
        raise FileNotFoundError(f"Extraction script not found at {extract_script}")
    cmd = ["node", str(extract_script), str(fbx_path), str(out_json), f"--fps={fps}"]
    print(f"Executing: {' '.join(cmd)}")
    subprocess.check_call(cmd)


def _generate_mock(out_path: Path):
    frames = 30
    bones = {"hip": []}
    for _ in range(frames):
        bones["hip"].append({"position": [0, 0, 0], "quaternion": [0, 0, 0, 1]})
    out_path.write_text(json.dumps({"bones": bones, "fps": 30}))


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


def _fit_autoencoder(
    json_path: Path, epochs: int = 5, batch_size: int = 64, lr: float = 1e-3
) -> Tuple[TinyAutoencoder, int]:
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


def _export_torchscript_encoder(model: TinyAutoencoder, input_dim: int, out_path: Path):
    model.eval()
    example = torch.zeros(1, input_dim)
    scripted = torch.jit.trace(model.encoder, example)
    scripted.save(str(out_path))
    return out_path


def _run_ppo(log_dir: Path, extra_args: list[str]):
    trainer = SCRIPT_DIR / "train_mujoco.py"
    # ensure no duplicate log-dir
    filtered = [
        a
        for i, a in enumerate(extra_args)
        if not (a == "--log-dir" or (i > 0 and extra_args[i - 1] == "--log-dir"))
    ]
    cmd = [sys.executable, str(trainer)] + filtered + ["--log-dir", str(log_dir)]
    print(f"Launching PPO: {' '.join(cmd)}")
    subprocess.check_call(cmd)


def _read_eval(log_dir: Path):
    eval_path = log_dir / "evaluations.npz"
    if not eval_path.exists():
        return [], []
    data = np.load(eval_path)
    timesteps = data["timesteps"]
    results = data["results"]  # shape (n_eval, n_episodes)
    mean = results.mean(axis=1)
    std = results.std(axis=1)
    return timesteps, (mean, std)


def main():
    parser = argparse.ArgumentParser(
        description="Compare PPO baseline vs bootstrapped (TorchScript+adapter) and plot."
    )
    parser.add_argument("--fbx", default="Walking.fbx")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--ppo-steps", type=int, default=50000)
    parser.add_argument(
        "--bootstrap-mode", choices=["obs", "feature"], default="feature"
    )
    parser.add_argument("--ae-epochs", type=int, default=5)
    args = parser.parse_args()

    base_dir = SCRIPT_DIR
    data_dir = base_dir / "data"
    data_dir.mkdir(exist_ok=True, parents=True)
    gt_json = data_dir / "ground_truth.json"
    gt_parquet = data_dir / "ground_truth.parquet"

    # 1) Extract FBX
    fbx_path = base_dir / args.fbx
    if fbx_path.exists():
        try:
            _run_node_extract(fbx_path, gt_json, fps=args.fps)
        except Exception as e:
            print(f"Extraction failed ({e}), using mock data.")
            _generate_mock(gt_json)
    else:
        print("FBX not found, using mock data.")
        _generate_mock(gt_json)

    dataset_path = gt_json
    try:
        seq = FrameSequence.from_json(gt_json, compute_velocities=True)
        seq.to_parquet(gt_parquet, compression="snappy")
        dataset_path = gt_parquet
    except Exception as e:
        print(f"Parquet export failed ({e}); continuing with JSON path.")

    # 2) Train AE and export TorchScript
    ae, in_dim = _fit_autoencoder(dataset_path, epochs=args.ae_epochs)
    ts_path = data_dir / "fbx_encoder.ts"
    _export_torchscript_encoder(ae, in_dim, ts_path)

    # 3) Run PPO baseline
    baseline_log = data_dir / "compare_baseline_logs"
    if baseline_log.exists():
        subprocess.call(["rm", "-rf", str(baseline_log)])
    baseline_args = [
        "--algo",
        "sac",
        "--total-timesteps",
        str(args.ppo_steps),
        "--adapter-mode",
        "none",
    ]
    _run_ppo(baseline_log, baseline_args)

    # 4) Run PPO bootstrapped
    boot_log = data_dir / "compare_boot_logs"
    if boot_log.exists():
        subprocess.call(["rm", "-rf", str(boot_log)])
    boot_args = [
        "--algo",
        "sac",
        "--total-timesteps",
        str(args.ppo_steps),
        "--adapter-mode",
        args.bootstrap_mode,
        "--torchscript-path",
        str(ts_path),
        "--torchscript-in-dim",
        str(in_dim),
    ]
    _run_ppo(boot_log, boot_args)

    # 5) Read evals and plot
    t_base, (m_base, s_base) = _read_eval(baseline_log)
    t_boot, (m_boot, s_boot) = _read_eval(boot_log)

    if len(t_base) > 0 and len(t_boot) > 0:
        print("=== Final Eval Comparison ===")
        print(
            f"Baseline: mean={m_base[-1]:.2f}, std={s_base[-1]:.2f} at t={t_base[-1]}"
        )
        print(
            f"Bootstrapped: mean={m_boot[-1]:.2f}, std={s_boot[-1]:.2f} at t={t_boot[-1]}"
        )
        diff = m_boot[-1] - m_base[-1]
        print(f"Delta (boot - base): {diff:.2f}")
    else:
        print("Could not compute final comparison (missing eval data).")

    fig = go.Figure()
    if len(t_base) > 0:
        fig.add_trace(
            go.Scatter(x=t_base, y=m_base, mode="markers", name="Baseline mean")
        )
        fig.add_trace(
            go.Scatter(
                x=np.concatenate([t_base, t_base[::-1]]),
                y=np.concatenate([m_base - s_base, (m_base + s_base)[::-1]]),
                fill="toself",
                line=dict(color="rgba(0,0,255,0.1)"),
                hoverinfo="skip",
                name="Baseline std",
            )
        )
    if len(t_boot) > 0:
        fig.add_trace(
            go.Scatter(x=t_boot, y=m_boot, mode="markers", name="Bootstrapped mean")
        )
        fig.add_trace(
            go.Scatter(
                x=np.concatenate([t_boot, t_boot[::-1]]),
                y=np.concatenate([m_boot - s_boot, (m_boot + s_boot)[::-1]]),
                fill="toself",
                line=dict(color="rgba(255,0,0,0.1)"),
                hoverinfo="skip",
                name="Bootstrapped std",
            )
        )

    fig.update_layout(
        title="PPO Eval Reward: Baseline vs Bootstrapped",
        xaxis_title="Timesteps",
        yaxis_title="Mean Eval Reward",
        template="plotly_white",
    )
    out_html = data_dir / "ppo_compare.html"
    fig.write_html(out_html)
    print(f"Saved comparison plot to {out_html}")


if __name__ == "__main__":
    main()
