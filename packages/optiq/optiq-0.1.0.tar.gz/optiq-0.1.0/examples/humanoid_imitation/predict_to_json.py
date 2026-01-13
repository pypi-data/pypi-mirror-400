"""
Generate a prediction JSON from a trained model checkpoint for Plotly comparison.

Usage:
    uv run python examples/humanoid_imitation/predict_to_json.py \
      --checkpoint models/motion_transformer.pt \
      --dataset examples/humanoid_imitation/data/ground_truth.parquet \
      --out predictions.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch

# Ensure repo root on path when executed as a script
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from optiq.data import load_sequence  # noqa: E402
from optiq.models import load_checkpoint  # noqa: E402


def autoregressive_predict(
    model: torch.nn.Module, frames: torch.Tensor, steps: int | None = None
) -> torch.Tensor:
    """Simple autoregressive roll: feed previous output as next input."""
    total = steps or frames.shape[0]
    preds = []
    prev = frames[0].unsqueeze(0)  # (1, F)
    model.eval()
    with torch.no_grad():
        for _ in range(total):
            nxt = model(prev)
            preds.append(nxt.squeeze(0).cpu())
            prev = nxt
    return torch.stack(preds)  # (T, F)


def frames_to_bones(preds: torch.Tensor, bone_names: list[str]) -> tuple[dict, int]:
    """Convert flat frame tensor to bones JSON structure."""
    _, F = preds.shape
    max_bones_available = F // 7
    if max_bones_available == 0:
        raise ValueError(f"Need at least 7 features; got {F}")

    use_bones = min(len(bone_names), max_bones_available)
    if use_bones < len(bone_names):
        print(
            f"[warn] Model output has {F} features (~{use_bones} bones), "
            f"but dataset lists {len(bone_names)} bones. Truncating to first {use_bones} bones."
        )

    bones = {}
    for i, bone in enumerate(bone_names[:use_bones]):
        bone_frames = []
        start = i * 7
        end = (i + 1) * 7
        for t in range(preds.shape[0]):
            chunk = preds[t, start:end]
            bone_frames.append(
                {
                    "position": chunk[:3].tolist(),
                    "quaternion": chunk[3:7].tolist(),
                }
            )
        bones[bone] = bone_frames
    return bones, use_bones


def main():
    parser = argparse.ArgumentParser(
        description="Generate prediction JSON from a trained model."
    )
    parser.add_argument(
        "--checkpoint",
        required=True,
        help="Path to model checkpoint (.pth or TorchScript).",
    )
    parser.add_argument(
        "--dataset",
        required=True,
        help="Path to dataset (parquet/hdf5/json) for bone layout/fps.",
    )
    parser.add_argument(
        "--out", required=True, help="Output JSON path for predictions."
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=None,
        help="Number of steps to roll out (default: dataset length).",
    )
    args = parser.parse_args()

    seq = load_sequence(args.dataset)
    frames = torch.tensor(seq.frames, dtype=torch.float32)
    model, meta = load_checkpoint(args.checkpoint)

    # Align feature dims: if dataset has extra dims, trim; if fewer, error.
    target_dim = meta.get("config", {}).get("input_dim") or frames.shape[1]
    if frames.shape[1] > target_dim:
        frames = frames[:, :target_dim]
    elif frames.shape[1] < target_dim:
        raise ValueError(
            f"Dataset feature dim ({frames.shape[1]}) < model input_dim ({target_dim}). "
            "Please provide a dataset with matching feature layout."
        )

    preds = autoregressive_predict(model, frames, steps=args.steps)
    bones, use_bones = frames_to_bones(preds, seq.bone_names)

    payload = {
        "fps": seq.fps,
        "frames": preds.shape[0],
        "bone_names": seq.bone_names[:use_bones],
        "bones": bones,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload))
    print(f"Wrote predictions to {out_path}")
    print("Metadata:", meta)


if __name__ == "__main__":
    main()
