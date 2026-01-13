"""PyTorch Geometric helpers for optiq capture data."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Sequence

from .capture import ObjectCapture

if TYPE_CHECKING:
    import torch
    from torch_geometric.data import Data


def _lazy_import_pyg():
    try:
        import torch
        from torch_geometric.data import Data
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "torch and torch_geometric are required for this feature. Install optiq[ml] or add the dependencies manually."
        ) from exc
    return torch, Data


def capture_to_temporal_graph(
    capture: ObjectCapture, attributes: Sequence[str] | None = None
) -> Data:
    """Convert an ObjectCapture into a temporal PyG graph."""

    torch, Data = _lazy_import_pyg()
    if not capture.samples:
        raise ValueError("Capture is empty")
    attr_list = list(attributes) if attributes else list(capture.attributes.keys())
    if not attr_list:
        raise ValueError("No attributes available to build the graph")
    rows = []
    for sample in capture.samples:
        row = []
        for attr in attr_list:
            if attr not in sample.values:
                raise KeyError(f"Attribute '{attr}' not found in capture samples")
            row.extend(_flatten_numeric(sample.values[attr]))
        rows.append(row)
    x = torch.tensor(rows, dtype=torch.float32)
    if x.ndim != 2:
        raise ValueError("Unexpected tensor shape produced from capture rows")
    frames = torch.tensor(
        [sample.frame for sample in capture.samples], dtype=torch.long
    )
    edge_index = _temporal_edges(len(capture.samples))
    data = Data(x=x, edge_index=edge_index)
    data.frame = frames
    data.metadata = {
        "scene": capture.scene_name,
        "object_name": capture.object_name,
        "frame_start": capture.frame_start,
        "frame_end": capture.frame_end,
        "attributes": attr_list,
    }
    return data


def make_sequence_batches(graph: Data, sequence_length: int) -> Iterable[Data]:
    """Yield sliding window sub-graphs for sequence models."""

    torch, Data = _lazy_import_pyg()
    num_nodes = graph.num_nodes
    if sequence_length <= 0:
        raise ValueError("sequence_length must be positive")
    if sequence_length > num_nodes:
        yield graph
        return
    for start in range(0, num_nodes - sequence_length + 1):
        end = start + sequence_length
        subset = Data(x=graph.x[start:end])
        subset.edge_index = _window_edges(sequence_length)
        subset.frame = graph.frame[start:end]
        subset.metadata = graph.metadata
        yield subset


def _temporal_edges(length: int) -> torch.Tensor:
    torch, _ = _lazy_import_pyg()
    if length < 2:
        return torch.empty((2, 0), dtype=torch.long)
    sources = torch.arange(0, length - 1, dtype=torch.long)
    targets = sources + 1
    return torch.stack([torch.cat([sources, targets]), torch.cat([targets, sources])])


def _window_edges(length: int) -> torch.Tensor:
    torch, _ = _lazy_import_pyg()
    if length < 2:
        return torch.empty((2, 0), dtype=torch.long)
    sources = torch.arange(0, length - 1, dtype=torch.long)
    targets = sources + 1
    return torch.stack([torch.cat([sources, targets]), torch.cat([targets, sources])])


def _flatten_numeric(value) -> list[float]:
    if value is None:
        return [0.0]
    if isinstance(value, (int, float)):
        return [float(value)]
    if isinstance(value, (list, tuple)):
        flat = []
        for item in value:
            flat.extend(_flatten_numeric(item))
        return flat
    raise TypeError(
        f"Attribute value {value!r} is not numeric. Provide attributes that evaluate to numbers."
    )


__all__ = ["capture_to_temporal_graph", "make_sequence_batches"]
