"""Frame-by-frame object capture helpers for Blender scenes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple

try:  # pragma: no cover - Blender-specific import
    import bpy  # type: ignore
except ImportError:  # pragma: no cover - Blender specific
    bpy = None

try:  # pragma: no cover - Blender specific
    import mathutils  # type: ignore
except ImportError:  # pragma: no cover - Blender specific
    mathutils = None


AttributeSpec = str | Tuple[str, str]


@dataclass
class FrameSample:
    frame: int
    values: Dict[str, Any]


@dataclass
class ObjectCapture:
    object_name: str
    attributes: Dict[str, str]
    samples: List[FrameSample] = field(default_factory=list)
    scene_name: str | None = None
    frame_start: int | None = None
    frame_end: int | None = None

    def to_rows(self) -> List[Dict[str, Any]]:
        """Return the capture as a list of dictionaries."""

        rows: List[Dict[str, Any]] = []
        for sample in self.samples:
            row = {"frame": sample.frame}
            row.update(sample.values)
            rows.append(row)
        return rows


def capture_object(
    object_name: str,
    attributes: Sequence[AttributeSpec] | None = None,
    frame_start: int | None = None,
    frame_end: int | None = None,
    scene: "bpy.types.Scene | None" = None,
) -> ObjectCapture:
    """Capture arbitrary attributes from a Blender object across frames."""

    _ensure_bpy()
    scene = scene or bpy.context.scene  # type: ignore[union-attr]
    if scene is None:  # pragma: no cover - Blender only
        raise RuntimeError("Unable to find an active Blender scene.")
    attr_map = _normalize_attributes(attributes)
    frame_start = frame_start or scene.frame_start
    frame_end = frame_end or scene.frame_end
    obj = _find_object(scene, object_name)
    samples: List[FrameSample] = []
    for frame in range(frame_start, frame_end + 1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()  # type: ignore[union-attr]
        values: Dict[str, Any] = {}
        for alias, path in attr_map.items():
            values[alias] = _serialize_value(_resolve_attr(obj, path))
        samples.append(FrameSample(frame=frame, values=values))
    return ObjectCapture(
        object_name=obj.name,
        attributes=attr_map,
        samples=samples,
        scene_name=scene.name,
        frame_start=frame_start,
        frame_end=frame_end,
    )


def capture_selected_object(
    attributes: Sequence[AttributeSpec] | None = None,
    frame_start: int | None = None,
    frame_end: int | None = None,
) -> ObjectCapture:
    """Capture attributes for the first selected object in the current scene."""

    _ensure_bpy()
    scene = bpy.context.scene  # type: ignore[union-attr]
    if not scene.objects or not bpy.context.selected_objects:  # type: ignore[union-attr]
        raise RuntimeError("No selected objects found in the active scene.")
    obj = bpy.context.selected_objects[0]  # type: ignore[union-attr]
    return capture_object(
        obj.name,
        attributes=attributes,
        frame_start=frame_start,
        frame_end=frame_end,
        scene=scene,
    )


def _normalize_attributes(attributes: Sequence[AttributeSpec] | None) -> Dict[str, str]:
    if not attributes:
        attributes = ("location", "rotation_euler", "scale")
    attr_map: Dict[str, str] = {}
    for spec in attributes:
        if isinstance(spec, tuple):
            alias, path = spec
        else:
            alias = path = spec
        attr_map[alias] = path
    return attr_map


def _resolve_attr(obj: Any, path: str) -> Any:
    current = obj
    for part in path.split("."):
        current = getattr(current, part)
        if callable(current):
            current = current()
    return current


def _serialize_value(value: Any) -> Any:
    if mathutils is not None:
        if isinstance(value, mathutils.Vector):
            return tuple(value)
        if isinstance(value, mathutils.Euler):
            return tuple(value)
        if isinstance(value, mathutils.Quaternion):
            return tuple(value)
        if isinstance(value, mathutils.Matrix):
            return [tuple(row) for row in value]
    if hasattr(value, "to_tuple"):
        try:
            return tuple(value)
        except TypeError:
            pass
    if isinstance(value, (list, tuple)):
        return tuple(value)
    return value


def _find_object(scene: "bpy.types.Scene", object_name: str):
    obj = scene.objects.get(object_name) or bpy.data.objects.get(object_name)  # type: ignore[union-attr]
    if obj is None:
        raise KeyError(f"Object '{object_name}' not found in the active scene.")
    return obj


def _ensure_bpy() -> None:
    if bpy is None:  # pragma: no cover - Blender-only dependency
        raise RuntimeError(
            "This function must run inside Blender where the bpy module is available."
        )


__all__ = [
    "AttributeSpec",
    "FrameSample",
    "ObjectCapture",
    "capture_object",
    "capture_selected_object",
]
