import json
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import torch
from torch.utils.data import Dataset


def _normalize_bone_name(name: str) -> str:
    """
    Normalize bone/object names from different FBX exports so they align.
    Current heuristic strips ':' that appears in Mixamo FBX names.
    """
    return name.replace(":", "")


def _extract_tracks_from_frames(
    frames: Sequence[dict],
) -> Dict[str, List[Sequence[float]]]:
    """
    Convert a list of frames (each with a nested 'bones' dict) into
    a map of bone_name -> list of positions.
    """
    tracks: Dict[str, List[Sequence[float]]] = {}
    for frame in frames:
        bones = frame.get("bones", {}) or {}
        for raw_name, state in bones.items():
            name = _normalize_bone_name(raw_name)
            tracks.setdefault(name, []).append(state["position"])
    return tracks


def load_bone_positions(json_path: str) -> Tuple[np.ndarray, List[str], float]:
    """
    Load bone/object positions from supported JSON formats into a dense array.

    Supported formats:
    - { "bones": { name: [ {position: [x,y,z], ...}, ... ] }, "fps": 30 }
      (extracted_jogging/jogging_anim.json)
    - { "<root>": [ { bones: { name: { position: [...] } }, ... } ], "fps": 30 }
      (examples/fbx_capoeira/ground_truth.json)
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    fps = float(data.get("fps", 30.0))
    tracks: Dict[str, List[Sequence[float]]] = {}

    if "bones" in data:
        for raw_name, seq in data["bones"].items():
            name = _normalize_bone_name(raw_name)
            tracks[name] = [frame["position"] for frame in seq]
    else:
        # Look for the first list-valued entry that contains bone data
        frames: Sequence[dict] = []
        for _, val in data.items():
            if (
                isinstance(val, list)
                and val
                and isinstance(val[0], dict)
                and "bones" in val[0]
            ):
                frames = val
                break
        if not frames:
            raise ValueError(f"Could not find bones data in {json_path}")
        tracks = _extract_tracks_from_frames(frames)

    if not tracks:
        raise ValueError(f"No bone tracks found in {json_path}")

    names = sorted(tracks.keys())
    max_len = max(len(seq) for seq in tracks.values())
    positions = np.zeros((max_len, len(names), 3), dtype=np.float32)
    for j, name in enumerate(names):
        seq = tracks[name]
        for i in range(max_len):
            src_idx = min(i, len(seq) - 1)
            positions[i, j, :] = np.asarray(seq[src_idx], dtype=np.float32)

    return positions, names, fps


class ConditionalAutoregDataset(Dataset):
    """
    Sliding-window dataset for conditional autoregressive prediction.
    Returns (window, target, class_id).
    """

    def __init__(
        self,
        sequences: List[Tuple[np.ndarray, int]],
        window: int = 10,
        stride: int = 1,
    ):
        if window < 1:
            raise ValueError("window must be >= 1")
        self.window = window
        self.samples: List[Tuple[np.ndarray, np.ndarray, int]] = []

        for seq, cls_id in sequences:
            if seq.shape[0] <= window:
                continue
            for start in range(0, seq.shape[0] - window, stride):
                window_frames = seq[start : start + window]
                target = seq[start + window]
                self.samples.append((window_frames, target, cls_id))

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int):
        window, target, cls_id = self.samples[idx]
        return (
            torch.from_numpy(window).float(),
            torch.from_numpy(target).float(),
            torch.tensor(cls_id, dtype=torch.long),
        )


def build_conditional_sequences(
    labeled_paths: Iterable[Tuple[str, str]],
) -> Tuple[List[Tuple[np.ndarray, int]], List[str]]:
    """
    Load multiple json_path/class_label pairs and align joints by intersection.

    Returns:
        sequences: list of (positions_array, class_id)
        joint_names: ordered joint names used for all sequences
    """
    loaded = []
    joint_sets = []
    labels: List[str] = []
    for path, label in labeled_paths:
        positions, names, _ = load_bone_positions(path)
        normalized_names = [_normalize_bone_name(n) for n in names]
        joint_sets.append(set(normalized_names))
        loaded.append(
            {"positions": positions, "names": normalized_names, "label": label}
        )
        labels.append(label)

    if not loaded:
        raise ValueError("No datasets provided for conditional training.")

    common = set.intersection(*joint_sets)
    if not common:
        raise ValueError("No common joints across datasets; cannot align sequences.")

    joint_names = sorted(common)
    sequences: List[Tuple[np.ndarray, int]] = []
    label_to_id = {lbl: idx for idx, lbl in enumerate(sorted(set(labels)))}

    for item in loaded:
        name_to_idx = {n: i for i, n in enumerate(item["names"])}
        filtered = np.stack(
            [item["positions"][:, name_to_idx[n], :] for n in joint_names], axis=1
        )
        sequences.append((filtered, label_to_id[item["label"]]))

    return sequences, joint_names
