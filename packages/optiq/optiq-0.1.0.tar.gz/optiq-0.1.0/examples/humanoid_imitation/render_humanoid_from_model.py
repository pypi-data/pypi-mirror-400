#!/usr/bin/env python3
"""
Use a pretrained FBX-derived checkpoint to generate predictions and render a Mujoco humanoid movie directly.

Workflow:
1. Load a trained motion model checkpoint (e.g., transformer, unet1d).
2. Run autoregressive rollout to generate predictions.json.
3. Convert predictions to Mujoco qpos and render video directly without RL training.

Usage:
    # Generate 300 frames from model (longer than training data):
    uv run python examples/humanoid_imitation/render_humanoid_from_model.py \
      --checkpoint models/motion_model.pt \
      --dataset examples/humanoid_imitation/data/ground_truth.parquet \
      --steps 300 \
      --video-out examples/humanoid_imitation/data/humanoid_motion.mp4

    # Use existing predictions and extend with model to 500 total frames:
    uv run python examples/humanoid_imitation/render_humanoid_from_model.py \
      --checkpoint models/motion_model.pt \
      --predictions examples/humanoid_imitation/data/predictions.json \
      --steps 500 \
      --video-out examples/humanoid_imitation/data/humanoid_motion.mp4

    # Just render existing predictions (no extension):
    uv run python examples/humanoid_imitation/render_humanoid_from_model.py \
      --predictions examples/humanoid_imitation/data/predictions.json \
      --video-out examples/humanoid_imitation/data/humanoid_motion.mp4
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

import gymnasium as gym
import numpy as np
import torch
from stable_baselines3.common.vec_env import VecVideoRecorder

# Ensure repo root on path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from optiq.data import load_sequence  # noqa: E402
from optiq.models import load_checkpoint  # noqa: E402
from optiq.rl.humanoid_mapping import HumanoidRetarget  # noqa: E402


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


def generate_predictions_json(
    checkpoint_path: Path, dataset_path: Path, steps: int | None = None
) -> Path:
    """Generate predictions.json from model checkpoint."""
    seq = load_sequence(dataset_path)
    frames = torch.tensor(seq.frames, dtype=torch.float32)
    model, meta = load_checkpoint(checkpoint_path)

    # Align feature dims
    target_dim = meta.get("config", {}).get("input_dim") or frames.shape[1]
    if frames.shape[1] > target_dim:
        frames = frames[:, :target_dim]
    elif frames.shape[1] < target_dim:
        raise ValueError(
            f"Dataset feature dim ({frames.shape[1]}) < model input_dim ({target_dim}). "
            "Please provide a dataset with matching feature layout."
        )

    preds = autoregressive_predict(model, frames, steps=steps)
    bones, use_bones = frames_to_bones(preds, seq.bone_names)

    payload = {
        "fps": seq.fps,
        "frames": preds.shape[0],
        "bone_names": seq.bone_names[:use_bones],
        "bones": bones,
    }

    temp_dir = Path(tempfile.gettempdir()) / "optiq_humanoid"
    temp_dir.mkdir(parents=True, exist_ok=True)
    pred_json = temp_dir / "predictions.json"
    pred_json.write_text(json.dumps(payload))
    print(f"Generated predictions: {pred_json}")
    print(f"Metadata: {meta}")
    return pred_json


def extend_predictions_with_model(
    pred_json: Path, checkpoint_path: Path, total_steps: int
) -> Path:
    """Extend existing predictions by continuing autoregressive prediction with a model.

    Args:
        pred_json: Path to existing predictions JSON
        checkpoint_path: Path to model checkpoint
        total_steps: Total number of frames to generate (will extend if needed)

    Returns:
        Path to extended predictions JSON
    """
    # Load existing predictions
    with open(pred_json) as f:
        data = json.load(f)

    existing_frames = data["frames"]
    bone_names = data["bone_names"]
    bones_data = data["bones"]
    fps = data.get("fps", 30)

    if total_steps <= existing_frames:
        print(
            f"Requested {total_steps} steps but already have {existing_frames} frames. No extension needed."
        )
        return pred_json

    # Load model
    model, meta = load_checkpoint(checkpoint_path)
    model.eval()

    # Convert last frame to tensor for seeding
    # Each bone has 7 values (3 position + 4 quaternion)
    last_frame_data = []
    for bone_name in bone_names:
        if bone_name in bones_data:
            frame = bones_data[bone_name][-1]
            last_frame_data.extend(frame["position"])
            last_frame_data.extend(frame["quaternion"])

    prev = torch.tensor([last_frame_data], dtype=torch.float32)

    # Check feature dim alignment
    target_dim = meta.get("config", {}).get("input_dim") or prev.shape[1]
    if prev.shape[1] > target_dim:
        prev = prev[:, :target_dim]
    elif prev.shape[1] < target_dim:
        # Pad with zeros if needed
        padding = torch.zeros(1, target_dim - prev.shape[1])
        prev = torch.cat([prev, padding], dim=1)

    # Generate additional frames
    additional_steps = total_steps - existing_frames
    print(
        f"Extending from {existing_frames} to {total_steps} frames ({additional_steps} new frames)..."
    )

    new_preds = []
    with torch.no_grad():
        for i in range(additional_steps):
            nxt = model(prev)
            new_preds.append(nxt.squeeze(0).cpu())
            prev = nxt
            if (i + 1) % 50 == 0:
                print(f"  Generated {i + 1}/{additional_steps} new frames...")

    # Convert new predictions to bones format and append
    for i, pred in enumerate(new_preds):
        for j, bone_name in enumerate(bone_names):
            if bone_name in bones_data:
                start = j * 7
                end = start + 7
                if end <= len(pred):
                    chunk = pred[start:end]
                    bones_data[bone_name].append(
                        {
                            "position": chunk[:3].tolist(),
                            "quaternion": chunk[3:7].tolist(),
                        }
                    )

    # Update frame count
    data["frames"] = total_steps

    # Save extended predictions
    temp_dir = Path(tempfile.gettempdir()) / "optiq_humanoid"
    temp_dir.mkdir(parents=True, exist_ok=True)
    extended_json = temp_dir / "predictions_extended.json"
    extended_json.write_text(json.dumps(data))
    print(f"Extended predictions saved to: {extended_json}")

    return extended_json


def render_video_from_predictions(
    pred_json: Path, video_out: Path, fps: int = 30
) -> None:
    """Render Mujoco humanoid video directly from predictions without RL training.

    Args:
        pred_json: Path to predictions JSON file
        video_out: Output video path
        fps: Frames per second for video
    """
    try:
        import cv2
    except ImportError:
        print("OpenCV not installed. Please install opencv-python to render videos.")
        return

    # Load predictions
    with open(pred_json) as f:
        data = json.load(f)

    frames_count = data["frames"]
    bones_data = data["bones"]
    bone_names = data["bone_names"]

    print(f"Rendering {frames_count} frames...")

    # Create Mujoco environment
    env = gym.make("Humanoid-v5", render_mode="rgb_array")
    retarget = HumanoidRetarget(
        scale=1.0
    )  # Data is already in meters (standardized at extraction time)

    # Reset environment to get initial state
    obs, info = env.reset()

    # Convert all frames to qpos first
    qpos_sequence = []
    for frame_idx in range(frames_count):
        frame_bones = {}
        for bone_name in bone_names:
            if bone_name in bones_data:
                frame_bones[bone_name] = bones_data[bone_name][frame_idx]
        qpos = retarget.frame_to_qpos(frame_bones)
        qpos_sequence.append(qpos)

    # Set up video writer
    sample_frame = env.render()
    height, width, _ = sample_frame.shape
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter(str(video_out), fourcc, fps, (width, height))

    # Render each frame
    for frame_idx in range(frames_count):
        qpos = qpos_sequence[frame_idx]

        # Set the environment state directly
        env.unwrapped.set_state(qpos, np.zeros_like(env.unwrapped.data.qvel))

        # Render the frame
        frame = env.render()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        video_writer.write(frame_bgr)

        if frame_idx % 30 == 0:
            print(f"Rendered frame {frame_idx}/{frames_count}")

    # Clean up
    video_writer.release()
    env.close()

    print(f"Saved video to: {video_out}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate humanoid motion video from pretrained FBX model or existing predictions"
    )
    parser.add_argument("--checkpoint", help="Path to trained motion model checkpoint")
    parser.add_argument(
        "--dataset", help="Path to ground truth dataset (parquet/hdf5/json)"
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=None,
        help="Total number of frames to generate (extends predictions if needed)",
    )
    parser.add_argument("--predictions", help="Path to existing predictions.json file")
    parser.add_argument(
        "--video-out", default="humanoid_motion.mp4", help="Output video path"
    )
    parser.add_argument("--fps", type=int, default=30, help="Video FPS")
    args = parser.parse_args()

    video_out = Path(args.video_out)
    video_out.parent.mkdir(parents=True, exist_ok=True)

    pred_json = None

    if args.predictions and args.checkpoint and args.steps:
        # Extend existing predictions with model
        pred_json = Path(args.predictions)
        if not pred_json.exists():
            print(f"Error: Predictions file {pred_json} not found")
            return
        checkpoint_path = Path(args.checkpoint)
        print("Step 1: Extending predictions with model...")
        pred_json = extend_predictions_with_model(
            pred_json, checkpoint_path, args.steps
        )

    elif args.predictions:
        # Use existing predictions as-is
        pred_json = Path(args.predictions)
        if not pred_json.exists():
            print(f"Error: Predictions file {pred_json} not found")
            return
        print("Using existing predictions (no extension)...")

    elif args.checkpoint and args.dataset:
        # Generate predictions from model and dataset
        checkpoint_path = Path(args.checkpoint)
        dataset_path = Path(args.dataset)
        print("Step 1: Generating predictions from model...")
        pred_json = generate_predictions_json(checkpoint_path, dataset_path, args.steps)

    else:
        parser.error(
            "Provide either:\n"
            "  --predictions (render existing)\n"
            "  --checkpoint + --dataset (generate new)\n"
            "  --predictions + --checkpoint + --steps (extend existing)"
        )

    print("\nStep 2: Rendering video directly from predictions...")
    render_video_from_predictions(pred_json, video_out, fps=args.fps)

    print(f"\n✓ Complete! Video saved to: {video_out}")


if __name__ == "__main__":
    main()
