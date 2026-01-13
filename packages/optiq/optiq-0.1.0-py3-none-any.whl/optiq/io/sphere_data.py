import json
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np
import torch
from torch.utils.data import Dataset

from optiq.data.frame_sequence import load_sequence


def load_sphere_positions(
    json_path: str, source: str = "bones"
) -> Tuple[np.ndarray, List[str], float]:
    """
    Load sphere (joint) positions from an animation JSON (or Parquet/HDF5 via FrameSequence).

    Returns:
      positions: np.ndarray (frames, joints, 3)
      names: list of joint names in consistent order
      fps: frames per second from the JSON (default 30 if missing)
    """
    path = Path(json_path)
    if path.suffix.lower() in {".parquet", ".pq", ".h5", ".hdf5"}:
        seq = load_sequence(path)
        feat_per_bone = 7
        if seq.frames.shape[1] % feat_per_bone != 0:
            raise ValueError(f"Cannot reshape frames into (T,bones,7) for {path}")
        bones = len(seq.bone_names)
        frames = seq.frames.shape[0]
        reshaped = seq.frames.reshape(frames, bones, feat_per_bone)
        positions = reshaped[:, :, :3]
        return positions, seq.bone_names, float(seq.fps)

    with open(path, "r") as f:
        data = json.load(f)
    tracks: Dict[str, List[Dict[str, Sequence[float]]]] = data.get(source, {})
    if not tracks:
        raise ValueError(f"No '{source}' tracks found in {json_path}")
    names = list(tracks.keys())
    frames = len(next(iter(tracks.values())))
    positions = np.zeros((frames, len(names), 3), dtype=np.float32)
    for j, name in enumerate(names):
        seq = tracks[name]
        if len(seq) != frames:
            raise ValueError(f"Track '{name}' length mismatch: {len(seq)} vs {frames}")
        for i, frame in enumerate(seq):
            positions[i, j, :] = np.array(frame["position"], dtype=np.float32)
    fps = float(data.get("fps", 30.0))
    return positions, names, fps


class SphereSequenceDataset(Dataset):
    """
    Simple dataset: input is positions at time t (joints,3), target is positions at t+1.
    """

    def __init__(self, positions: np.ndarray, horizon: int = 1):
        if positions.ndim != 3 or positions.shape[2] != 3:
            raise ValueError("positions must be (frames, joints, 3)")
        if horizon < 1:
            raise ValueError("horizon must be >= 1")
        self.positions = positions.astype(np.float32)
        self.horizon = horizon

    def __len__(self) -> int:
        return self.positions.shape[0] - self.horizon

    def __getitem__(self, idx: int):
        x = self.positions[idx]
        y = self.positions[idx + self.horizon]
        # Convert to torch tensors: x,y shapes (joints,3)
        return torch.from_numpy(x), torch.from_numpy(y)
