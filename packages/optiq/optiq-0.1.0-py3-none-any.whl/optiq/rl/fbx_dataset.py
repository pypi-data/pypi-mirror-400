"""
FBXDataSet: minimal dataset wrapper for extracted FBX motion JSON.

Assumes ground_truth.json (or similar) with structure:
{
  "bones": {
     "<bone_name>": [ { "position": [x,y,z], "quaternion": [qx,qy,qz,qw] }, ... ],
     ...
  },
  "fps": 30
}
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple
import torch
from torch.utils.data import Dataset

from optiq.data.frame_sequence import load_sequence
from optiq.data.datasets import BehaviorCloneDataset

# Local import guarded to avoid circular deps on lightweight users
try:
    from optiq.rl.humanoid_mapping import HumanoidRetarget
except Exception:  # pragma: no cover - mapping only needed for BC path
    HumanoidRetarget = None


class FBXDataSet(Dataset):
    def __init__(
        self, json_path: str, use_positions: bool = True, use_rotations: bool = True
    ):
        self.path = Path(json_path)
        seq = load_sequence(self.path)
        if seq.frames.ndim != 2:
            raise ValueError("Sequence frames must be 2D (T, F).")

        feats: List[torch.Tensor] = []
        feat_per_bone = 7
        for frame in seq.frames:
            vals: List[float] = []
            if use_positions or use_rotations:
                frame_reshaped = frame.reshape(len(seq.bone_names), feat_per_bone)
                for row in frame_reshaped:
                    if use_positions:
                        vals.extend(row[:3])
                    if use_rotations:
                        vals.extend(row[3:7])
            feats.append(torch.tensor(vals, dtype=torch.float32))
        self.features = torch.stack(feats, dim=0)  # (T, F_filtered)

    def __len__(self) -> int:
        return self.features.size(0)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        x = self.features[idx]
        return x, x  # autoencoder-style


class HumanoidPoseActionDataset(Dataset):
    """
    Turn extracted FBX JSON (positions + quaternions) into (obs, action) pairs
    aligned with the Gymnasium Mujoco Humanoid env.

    For each consecutive frame t -> t+1:
    - Build qpos_t, qpos_{t+1} from bone transforms via HumanoidRetarget.
    - Finite-difference to get qvel_t.
    - Set env state to (qpos_t, qvel_t) and grab the env's observation vector.
    - Label action as scaled joint delta: a = clip((qpos_{t+1}-qpos_t)/dt / action_scale).

    This produces supervision that matches the policy input/output sizes without
    needing to manually recreate Humanoid's observation function.
    """

    def __init__(
        self,
        json_path: str,
        env_id: str = "Humanoid-v5",
        dt: float | None = None,
        joint_gain: float = 1.0,
        device: str = "cpu",
    ):
        if HumanoidRetarget is None:
            raise ImportError(
                "optiq.rl.humanoid_mapping is required for HumanoidPoseActionDataset"
            )

        _ = (joint_gain, device)  # kept for backward-compatible signature

        self.path = Path(json_path)
        self.fps = None
        seq = load_sequence(self.path)
        self.fps = seq.fps
        self.dt = float(dt) if dt is not None else 1.0 / float(self.fps)

        retarget = HumanoidRetarget(
            scale=1.0
        )  # Data is already in meters (standardized at extraction time)
        bc = BehaviorCloneDataset(
            seq=seq,
            env_id=env_id,
            retarget_fn=retarget.frame_to_qpos,
            action_fn=retarget.qpos_delta_to_action,
            dt=self.dt,
        )

        self.observations = bc.observations
        self.actions = bc.actions

    def __len__(self) -> int:
        return self.observations.shape[0]

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.observations[idx], self.actions[idx]
