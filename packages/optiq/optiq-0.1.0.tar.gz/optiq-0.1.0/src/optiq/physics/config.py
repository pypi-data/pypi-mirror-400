from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None


@dataclass
class LearnableSpec:
    initial_guess: float
    learnable: bool = True
    bounds: Optional[Tuple[float, float]] = None


@dataclass
class PhysicsDefaults:
    mass_range: Tuple[float, float] = (0.1, 100.0)
    friction_range: Tuple[float, float] = (0.0, 1.0)
    restitution_range: Tuple[float, float] = (0.0, 1.0)


@dataclass
class ObjectConfig:
    name: str
    mesh_path: str
    is_static: bool = False
    initial_transform: List[List[float]] = field(
        default_factory=lambda: [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]
    )
    parameter_overrides: Dict[str, LearnableSpec] = field(default_factory=dict)


@dataclass
class PhysicsConfig:
    objects: List[ObjectConfig]
    physics_defaults: PhysicsDefaults = field(default_factory=PhysicsDefaults)

    @classmethod
    def from_yaml(cls, path: str) -> "PhysicsConfig":
        if yaml is None:
            raise ImportError("pyyaml is required to load physics configs")
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}

        defaults_dict = data.get("physics_defaults", {}) or {}
        defaults = PhysicsDefaults(
            mass_range=tuple(defaults_dict.get("mass_range", (0.1, 100.0))),
            friction_range=tuple(defaults_dict.get("friction_range", (0.0, 1.0))),
            restitution_range=tuple(defaults_dict.get("restitution_range", (0.0, 1.0))),
        )

        objs = []
        for obj_cfg in data.get("objects", []):
            overrides_raw = obj_cfg.get("parameter_overrides", {}) or {}
            overrides: Dict[str, LearnableSpec] = {}
            for name, spec in overrides_raw.items():
                overrides[name] = LearnableSpec(
                    initial_guess=float(spec.get("initial_guess", 0.0)),
                    learnable=bool(spec.get("learnable", True)),
                    bounds=tuple(spec.get("bounds")) if spec.get("bounds") else None,
                )
            objs.append(
                ObjectConfig(
                    name=obj_cfg["name"],
                    mesh_path=obj_cfg["mesh_path"],
                    is_static=bool(obj_cfg.get("is_static", False)),
                    initial_transform=obj_cfg.get("initial_transform")
                    or [
                        [1, 0, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1],
                    ],
                    parameter_overrides=overrides,
                )
            )

        return cls(objects=objs, physics_defaults=defaults)
