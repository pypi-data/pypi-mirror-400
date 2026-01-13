from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np


def _json_default(obj):
    if isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    return obj


def _normalize_quaternion(quat: List[float]) -> List[float]:
    q = np.asarray(quat, dtype=np.float32)
    norm = np.linalg.norm(q)
    if norm == 0:
        # fallback to identity quaternion
        return [0.0, 0.0, 0.0, 1.0]
    return (q / norm).tolist()


def _finite_difference(data: np.ndarray, fps: int) -> np.ndarray:
    """Simple forward difference velocities scaled by dt."""
    if data.shape[0] < 2:
        return np.zeros_like(data)
    dt = 1.0 / float(fps)
    vel = np.zeros_like(data)
    vel[1:] = (data[1:] - data[:-1]) / dt
    vel[0] = vel[1]
    return vel


@dataclass
class FrameSequence:
    """In-memory representation of motion frames plus metadata."""

    fps: int
    bone_names: List[str]
    frames: np.ndarray  # (T, F)
    velocities: Optional[np.ndarray] = None  # (T, F) optional
    labels: Optional[np.ndarray] = None  # (T, L) optional
    label_names: Optional[List[str]] = None
    seq_labels: Optional[Dict] = None  # sequence-level labels
    metadata: Dict = field(default_factory=dict)
    splits: Optional[Dict[str, np.ndarray]] = None  # split masks (train/val/test)
    raw_bones: Optional[Dict[str, List[Dict]]] = None  # optional original structure

    @classmethod
    def from_json(
        cls,
        path: Union[str, Path],
        compute_velocities: bool = False,
        coordinate_space: Optional[str] = None,
    ) -> "FrameSequence":
        path = Path(path)
        data = json.loads(path.read_text())
        bones: Dict[str, List[Dict]] = data.get("bones", data)
        bone_names = data.get("bone_names") or list(bones.keys())
        fps = data.get("fps", 30)
        frames = []
        for t in range(len(next(iter(bones.values())))):
            frame_vals: List[float] = []
            for b in bone_names:
                entry = bones[b][t]
                frame_vals.extend(entry.get("position", [0, 0, 0]))
                frame_vals.extend(
                    _normalize_quaternion(entry.get("quaternion", [0, 0, 0, 1]))
                )
            frames.append(frame_vals)
        frames_np = np.asarray(frames, dtype=np.float32)
        velocities = _finite_difference(frames_np, fps) if compute_velocities else None
        meta_extra = {
            k: v for k, v in data.items() if k not in {"bones", "bone_names", "fps"}
        }
        if coordinate_space:
            meta_extra["coordinate_space"] = coordinate_space
        return cls(
            fps=fps,
            bone_names=bone_names,
            frames=frames_np,
            velocities=velocities,
            metadata=meta_extra,
            raw_bones=bones,
        )

    def attach_labels(
        self,
        frame_labels: Optional[np.ndarray] = None,
        label_names: Optional[List[str]] = None,
        seq_labels: Optional[Dict] = None,
    ) -> "FrameSequence":
        if frame_labels is not None and frame_labels.shape[0] != self.frames.shape[0]:
            raise ValueError("frame_labels length must match number of frames.")
        return replace(
            self,
            labels=frame_labels,
            label_names=label_names or self.label_names,
            seq_labels=seq_labels or self.seq_labels,
        )

    def with_splits(self, splits: Dict[str, np.ndarray]) -> "FrameSequence":
        for name, mask in splits.items():
            if mask.shape[0] != self.frames.shape[0]:
                raise ValueError(f"Split '{name}' length must match frames.")
            if mask.dtype != np.bool_:
                splits[name] = mask.astype(bool)
        return replace(self, splits=splits)

    def with_labels(
        self,
        frame_labels: Optional[np.ndarray] = None,
        seq_labels: Optional[Dict] = None,
        conditions: Optional[Dict] = None,
        label_names: Optional[List[str]] = None,
    ) -> "LabeledSequence":
        return LabeledSequence(
            base=self,
            labels=frame_labels,
            seq_labels=seq_labels,
            label_names=label_names or self.label_names,
            conditions=conditions or {},
        )

    def to_parquet(
        self, out_path: Union[str, Path], compression: str = "snappy"
    ) -> Path:
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError as e:  # pragma: no cover - optional dep
            raise ImportError(
                "pyarrow is required to write parquet. Install optiq[ml]."
            ) from e

        out_path = Path(out_path)
        meta = {
            "fps": self.fps,
            "bone_names": self.bone_names,
            "metadata": self.metadata,
            "has_velocities": self.velocities is not None,
            "has_labels": self.labels is not None,
            "label_names": self.label_names,
            "seq_labels": self.seq_labels,
            "splits": list(self.splits.keys()) if self.splits else [],
        }

        arrays = {
            "frames": pa.array(self.frames.tolist(), type=pa.list_(pa.float32())),
        }
        if self.velocities is not None:
            arrays["velocities"] = pa.array(
                self.velocities.tolist(), type=pa.list_(pa.float32())
            )
        if self.labels is not None:
            arrays["labels"] = pa.array(
                self.labels.tolist(), type=pa.list_(pa.float32())
            )
        if self.splits:
            for name, mask in self.splits.items():
                arrays[f"split_{name}"] = pa.array(
                    mask.astype(bool).tolist(), type=pa.bool_()
                )

        table = pa.table(arrays)
        table = table.replace_schema_metadata(
            {"optiq_metadata": json.dumps(meta, default=_json_default)}
        )
        pq.write_table(table, out_path, compression=compression)
        return out_path

    def to_hdf5(self, out_path: Union[str, Path], compression: str = "gzip") -> Path:
        try:
            import h5py
        except ImportError as e:  # pragma: no cover - optional dep
            raise ImportError(
                "h5py is required to write HDF5. Install optiq[ml]."
            ) from e

        out_path = Path(out_path)
        with h5py.File(out_path, "w") as f:
            f.create_dataset("frames", data=self.frames, compression=compression)
            f.attrs["fps"] = self.fps
            f.attrs["bone_names"] = json.dumps(self.bone_names)
            f.attrs["metadata"] = json.dumps(self.metadata, default=_json_default)
            if self.velocities is not None:
                f.create_dataset(
                    "velocities", data=self.velocities, compression=compression
                )
            if self.labels is not None:
                f.create_dataset("labels", data=self.labels, compression=compression)
            if self.label_names is not None:
                f.attrs["label_names"] = json.dumps(
                    self.label_names, default=_json_default
                )
            if self.seq_labels is not None:
                f.attrs["seq_labels"] = json.dumps(
                    self.seq_labels, default=_json_default
                )
            if self.splits:
                grp = f.create_group("splits")
                for name, mask in self.splits.items():
                    grp.create_dataset(
                        name, data=mask.astype(bool), compression=compression
                    )
        return out_path


@dataclass
class LabeledSequence:
    base: FrameSequence
    labels: Optional[np.ndarray] = None  # (T, L) or None
    seq_labels: Optional[Dict] = None
    label_names: Optional[List[str]] = None
    conditions: Dict = field(default_factory=dict)

    @property
    def fps(self) -> int:
        return self.base.fps

    @property
    def frames(self) -> np.ndarray:
        return self.base.frames

    @property
    def bone_names(self) -> List[str]:
        return self.base.bone_names


def _load_parquet(path: Path) -> FrameSequence:
    import pyarrow.parquet as pq

    table = pq.read_table(path)
    meta_raw = table.schema.metadata or {}
    meta_json = meta_raw.get(b"optiq_metadata", b"{}")
    meta = json.loads(meta_json.decode("utf-8"))

    frames = np.asarray(table["frames"].to_pylist(), dtype=np.float32)
    velocities = None
    labels = None
    splits = {}
    if "velocities" in table.column_names:
        velocities = np.asarray(table["velocities"].to_pylist(), dtype=np.float32)
    if "labels" in table.column_names:
        labels = np.asarray(table["labels"].to_pylist(), dtype=np.float32)
    for name in table.column_names:
        if name.startswith("split_"):
            split_name = name.replace("split_", "", 1)
            splits[split_name] = np.asarray(table[name].to_pylist(), dtype=bool)
    if not splits:
        splits = None

    return FrameSequence(
        fps=int(meta.get("fps", 30)),
        bone_names=list(meta.get("bone_names", [])),
        frames=frames,
        velocities=velocities,
        metadata=meta.get("metadata", {}),
        labels=labels,
        label_names=meta.get("label_names"),
        seq_labels=meta.get("seq_labels"),
        splits=splits,
    )


def _load_hdf5(path: Path) -> FrameSequence:
    import h5py

    with h5py.File(path, "r") as f:
        frames = np.asarray(f["frames"], dtype=np.float32)
        velocities = (
            np.asarray(f["velocities"], dtype=np.float32) if "velocities" in f else None
        )
        labels = np.asarray(f["labels"], dtype=np.float32) if "labels" in f else None
        fps = int(f.attrs.get("fps", 30))
        bone_names = json.loads(f.attrs.get("bone_names", "[]"))
        metadata = json.loads(f.attrs.get("metadata", "{}"))
        seq_labels = (
            json.loads(f.attrs.get("seq_labels", "{}"))
            if "seq_labels" in f.attrs
            else None
        )
        label_names = (
            json.loads(f.attrs.get("label_names", "[]"))
            if "label_names" in f.attrs
            else None
        )
        splits = None
        if "splits" in f:
            splits = {}
            for name in f["splits"].keys():
                splits[name] = np.asarray(f["splits"][name], dtype=bool)
    return FrameSequence(
        fps=fps,
        bone_names=bone_names,
        frames=frames,
        velocities=velocities,
        metadata=metadata,
        labels=labels,
        seq_labels=seq_labels,
        label_names=label_names,
        splits=splits,
    )


def load_sequence(path: Union[str, Path]) -> FrameSequence:
    """Load a FrameSequence from parquet/hdf5/json."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in {".parquet", ".pq"}:
        return _load_parquet(path)
    if suffix in {".h5", ".hdf5"}:
        return _load_hdf5(path)
    if suffix == ".json":
        return FrameSequence.from_json(path)
    raise ValueError(f"Unsupported sequence format for {path}")
