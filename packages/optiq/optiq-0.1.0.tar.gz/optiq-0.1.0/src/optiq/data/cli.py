from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import click
import numpy as np

from .frame_sequence import FrameSequence, load_sequence


def _compute_velocities(frames: np.ndarray, fps: int) -> np.ndarray:
    if frames.shape[0] < 2:
        return np.zeros_like(frames)
    dt = 1.0 / float(fps)
    vel = np.zeros_like(frames)
    vel[1:] = (frames[1:] - frames[:-1]) / dt
    vel[0] = vel[1]
    return vel


def _write_sequence(seq: FrameSequence, out_path: Path, compression: str) -> Path:
    if out_path.suffix.lower() in {".h5", ".hdf5"}:
        return seq.to_hdf5(out_path, compression=compression)
    return seq.to_parquet(out_path, compression=compression)


@click.group()
def data_cli():
    """Data conversion and labeling utilities."""


@data_cli.command("convert")
@click.option(
    "--in", "in_path", required=True, help="Input sequence (json/parquet/hdf5)."
)
@click.option(
    "--out", "out_path", required=True, help="Output dataset path (.parquet or .h5)."
)
@click.option(
    "--compression", default="snappy", help="Compression codec (snappy/gzip)."
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["parquet", "hdf5"]),
    default=None,
    help="Override output format.",
)
@click.option(
    "--compute-velocities",
    is_flag=True,
    help="Compute per-frame velocities if missing.",
)
@click.option(
    "--coordinate-space",
    default=None,
    help="Optional coordinate space tag to store in metadata.",
)
def convert_command(
    in_path: str,
    out_path: str,
    compression: str,
    fmt: Optional[str],
    compute_velocities: bool,
    coordinate_space: Optional[str],
):
    """Convert motion JSON/Parquet/HDF5 to canonical Parquet/HDF5."""
    in_p = Path(in_path)
    out_p = Path(out_path)

    if in_p.suffix.lower() == ".json" and compute_velocities:
        seq = FrameSequence.from_json(
            in_p, compute_velocities=True, coordinate_space=coordinate_space
        )
    else:
        seq = load_sequence(in_p)
        if coordinate_space:
            seq.metadata["coordinate_space"] = coordinate_space
        if compute_velocities and seq.velocities is None:
            vel = _compute_velocities(seq.frames, seq.fps)
            seq = FrameSequence(
                fps=seq.fps,
                bone_names=seq.bone_names,
                frames=seq.frames,
                velocities=vel,
                labels=seq.labels,
                label_names=seq.label_names,
                seq_labels=seq.seq_labels,
                metadata=seq.metadata,
                splits=seq.splits,
                raw_bones=seq.raw_bones,
            )

    target_fmt = fmt or (
        "hdf5" if out_p.suffix.lower() in {".h5", ".hdf5"} else "parquet"
    )
    if target_fmt == "parquet":
        out_p = (
            out_p.with_suffix(".parquet")
            if out_p.suffix.lower() not in {".parquet", ".pq"}
            else out_p
        )
    else:
        out_p = (
            out_p.with_suffix(".h5")
            if out_p.suffix.lower() not in {".h5", ".hdf5"}
            else out_p
        )

    result = _write_sequence(seq, out_p, compression=compression)
    click.echo(f"Wrote dataset to {result}")


@data_cli.command("label")
@click.option(
    "--in", "in_path", required=True, help="Input dataset (parquet/hdf5/json)."
)
@click.option(
    "--out", "out_path", required=True, help="Output dataset path (.parquet or .h5)."
)
@click.option(
    "--label",
    "labels",
    multiple=True,
    help="Sequence-level label key=value (repeatable).",
)
@click.option(
    "--frame-labels",
    "frame_labels_path",
    default=None,
    help="Optional JSON file of per-frame labels (list or list of lists).",
)
@click.option(
    "--label-names", default=None, help="Comma-separated label names for frame labels."
)
@click.option(
    "--compression", default="snappy", help="Compression codec (snappy/gzip)."
)
def label_command(
    in_path: str,
    out_path: str,
    labels: tuple[str, ...],
    frame_labels_path: Optional[str],
    label_names: Optional[str],
    compression: str,
):
    """Attach labels to a dataset and write back to Parquet/HDF5."""
    in_p = Path(in_path)
    out_p = Path(out_path)

    seq = load_sequence(in_p)

    seq_labels = {}
    for item in labels:
        if "=" not in item:
            raise click.ClickException("Labels must be in key=value form.")
        key, value = item.split("=", 1)
        seq_labels[key] = value

    frame_labels = None
    label_name_list = (
        [s.strip() for s in label_names.split(",")] if label_names else None
    )
    if frame_labels_path:
        raw = json.loads(Path(frame_labels_path).read_text())
        frame_labels = np.asarray(raw, dtype=np.float32)
        if frame_labels.shape[0] != seq.frames.shape[0]:
            raise click.ClickException(
                "Frame labels length must match number of frames."
            )

    seq = seq.attach_labels(
        frame_labels, label_names=label_name_list, seq_labels=seq_labels or None
    )

    if out_p.suffix.lower() not in {".parquet", ".pq", ".h5", ".hdf5"}:
        out_p = out_p.with_suffix(".parquet")

    result = _write_sequence(seq, out_p, compression=compression)
    click.echo(f"Wrote labeled dataset to {result}")
