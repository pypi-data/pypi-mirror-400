import json
from typing import List, Optional, Sequence, Tuple

import numpy as np
import torch
from torch.utils.data import Dataset


def _safe_normalize_quat(q: np.ndarray) -> np.ndarray:
    q = np.asarray(q, dtype=np.float64)
    norm = np.linalg.norm(q, axis=-1, keepdims=True)
    norm = np.where(norm < 1e-8, 1.0, norm)
    return q / norm


def _slerp(q0: np.ndarray, q1: np.ndarray, alpha: float) -> np.ndarray:
    """
    Spherical linear interpolation between two quaternions.
    q0, q1: (..., 4)
    alpha: scalar in [0, 1]
    """
    q0 = _safe_normalize_quat(q0)
    q1 = _safe_normalize_quat(q1)

    dot = np.sum(q0 * q1, axis=-1, keepdims=True)
    # Ensure shortest path
    q1 = np.where(dot < 0.0, -q1, q1)
    dot = np.abs(dot)

    # If quats are very close, fall back to linear
    close = dot > 0.9995
    sin_theta = np.sqrt(1.0 - np.square(dot))

    theta = np.arccos(np.clip(dot, -1.0, 1.0))
    w1 = np.sin((1.0 - alpha) * theta) / np.where(sin_theta < 1e-8, 1.0, sin_theta)
    w2 = np.sin(alpha * theta) / np.where(sin_theta < 1e-8, 1.0, sin_theta)

    out = w1 * q0 + w2 * q1
    # For near-identical quats, blend linearly to avoid NaNs
    if np.any(close):
        out = np.where(close, (1.0 - alpha) * q0 + alpha * q1, out)
    return _safe_normalize_quat(out)


def _load_motion(path: str) -> Tuple[np.ndarray, np.ndarray, List[str], float]:
    """
    Load motion data (positions + quaternions) from a Kindr FBX JSON export.
    Supports the Node.js extractor format: { "bones": { name: [ {position, quaternion,...}, ... ] }, "fps": 30 }
    """
    with open(path, "r") as f:
        data = json.load(f)

    fps = float(data.get("fps", 30.0))
    if "bones" not in data:
        raise ValueError(f"Expected 'bones' in {path}")

    names = sorted(list(data["bones"].keys()))
    n_frames = len(next(iter(data["bones"].values())))
    positions = np.zeros((n_frames, len(names), 3), dtype=np.float32)
    quats = np.zeros((n_frames, len(names), 4), dtype=np.float32)

    for j, name in enumerate(names):
        seq = data["bones"][name]
        if len(seq) != n_frames:
            raise ValueError(f"Bone {name} has inconsistent length in {path}")
        for i, frame in enumerate(seq):
            positions[i, j, :] = np.asarray(frame["position"], dtype=np.float32)
            quats[i, j, :] = np.asarray(frame["quaternion"], dtype=np.float32)

    return positions, quats, names, fps


class ContinuousFBXMotionDataset(Dataset):
    """
    Continuous-time sampler over FBX-extracted motion.

    - Samples fractional timesteps t in [0, T-1) and interpolates positions/quaternions
      between the neighboring discrete frames.
    - Interpolation methods:
        * "linear" (default): linear for positions, SLERP for quaternions
        * "nearest": nearest neighbor (no interpolation)
        * "slerp": same as "linear" (alias) but explicit name for rotations
    """

    def __init__(
        self,
        motion_json: str,
        interpolation: str = "linear",
        num_samples: Optional[int] = None,
        times: Optional[Sequence[float]] = None,
    ):
        self.positions, self.quats, self.bone_names, self.fps = _load_motion(
            motion_json
        )
        self.n_frames = self.positions.shape[0]

        if self.n_frames < 2:
            raise ValueError("Motion must have at least 2 frames for interpolation.")

        self.interp = interpolation.lower()
        if self.interp not in {"linear", "nearest", "slerp"}:
            raise ValueError(
                f"Unsupported interpolation '{interpolation}'. Choose from ['linear','nearest','slerp']."
            )

        if times is not None:
            self.times = np.asarray(times, dtype=np.float32)
        else:
            n = num_samples if num_samples is not None else self.n_frames * 10
            # Avoid sampling exactly at the last frame to keep t+1 in-bounds
            self.times = np.linspace(0.0, self.n_frames - 1 - 1e-6, n, dtype=np.float32)

    def __len__(self) -> int:
        return len(self.times)

    def _interpolate(self, t: float) -> Tuple[np.ndarray, np.ndarray]:
        if self.interp == "nearest":
            idx = int(round(np.clip(t, 0, self.n_frames - 1)))
            return self.positions[idx], self.quats[idx]

        t_clamped = np.clip(t, 0.0, self.n_frames - 1 - 1e-6)
        i0 = int(np.floor(t_clamped))
        i1 = min(i0 + 1, self.n_frames - 1)
        alpha = float(t_clamped - i0)

        pos0, pos1 = self.positions[i0], self.positions[i1]
        q0, q1 = self.quats[i0], self.quats[i1]

        pos = (1.0 - alpha) * pos0 + alpha * pos1
        quat = _slerp(q0, q1, alpha)
        return pos.astype(np.float32), quat.astype(np.float32)

    def __getitem__(self, idx: int):
        t = float(self.times[idx])
        pos, quat = self._interpolate(t)
        return (
            torch.from_numpy(pos),  # (J, 3)
            torch.from_numpy(quat),  # (J, 4)
            torch.tensor(t, dtype=torch.float32),
        )

    @property
    def joint_names(self) -> List[str]:
        return self.bone_names
