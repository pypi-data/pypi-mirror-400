from __future__ import annotations

import os
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import trimesh

from .config import LearnableSpec, ObjectConfig, PhysicsConfig, PhysicsDefaults

try:
    from mesh_to_sdf import mesh_to_sdf  # type: ignore
except Exception:  # pragma: no cover - optional dep
    mesh_to_sdf = None


class PhysicalObject(nn.Module):
    """
    Minimal physical object representation with learnable parameters and mesh utilities.
    """

    def __init__(self, config: ObjectConfig, device: str = "cpu"):
        super().__init__()
        self.config = config
        self.device = device
        self.name = config.name
        self.is_static = config.is_static

        self.mesh = self._load_mesh(config.mesh_path)
        self.centroid = torch.tensor(
            self.mesh.centroid, device=device, dtype=torch.float32
        )

        self.sdf_data = None
        if self.is_static:
            self._compute_sdf()

        self.params: Dict[str, nn.Parameter] = nn.ParameterDict()
        self.param_specs: Dict[str, LearnableSpec] = {}
        self.history_buffer: Optional[torch.Tensor] = None

    def _load_mesh(self, path: str) -> trimesh.Trimesh:
        if not os.path.exists(path):
            base, ext = os.path.splitext(path)
            if not ext and os.path.exists(base + ".urdf"):
                path = base + ".urdf"
        if not os.path.exists(path):
            raise FileNotFoundError(f"Mesh not found at {path}")

        if path.lower().endswith((".urdf", ".xml")):
            print(f"Using placeholder sphere mesh for URDF/XML '{path}' (visual only).")
            mesh = trimesh.creation.icosphere(radius=0.5)
        else:
            mesh = trimesh.load(path)
            if isinstance(mesh, trimesh.Scene):
                if len(mesh.geometry) == 0:
                    raise ValueError(f"No geometry found in {path}")
                mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))

        transform = np.array(self.config.initial_transform)
        mesh.apply_transform(transform)
        return mesh

    def _compute_sdf(self, resolution: int = 64):
        if mesh_to_sdf is None:
            print(f"Warning: mesh_to_sdf not installed. Skipping SDF for {self.name}.")
            return
        try:
            # Placeholder: expensive grids avoided; keep proximity mesh for future use.
            self.sdf_data = None
        except Exception as e:  # pragma: no cover
            print(f"SDF computation failed for {self.name}: {e}")
            self.sdf_data = None

    def register_parameters(self, defaults: PhysicsDefaults):
        if not self.is_static:
            self._register_param("mass", defaults.mass_range, default_val=1.0)
            self._register_param("friction", defaults.friction_range, default_val=0.5)
            self._register_param(
                "restitution", defaults.restitution_range, default_val=0.5
            )
        for name, spec in self.config.parameter_overrides.items():
            self._register_param_from_spec(name, spec)

    def _register_param(
        self, name: str, bounds: Tuple[float, float], default_val: float
    ):
        if name in self.config.parameter_overrides:
            return
        if name == "mass":
            raw_init = np.log(np.exp(default_val) - 1)
        else:
            d = np.clip(default_val, 0.01, 0.99)
            raw_init = np.log(d / (1 - d))
        self.params[name] = nn.Parameter(
            torch.tensor(raw_init, device=self.device, dtype=torch.float32),
            requires_grad=True,
        )
        self.param_specs[name] = LearnableSpec(
            initial_guess=default_val, learnable=True, bounds=bounds
        )

    def _register_param_from_spec(self, name: str, spec: LearnableSpec):
        if name == "mass":
            raw_init = np.log(np.exp(spec.initial_guess) - 1)
        else:
            d = np.clip(spec.initial_guess, 0.01, 0.99)
            raw_init = np.log(d / (1 - d))
        self.params[name] = nn.Parameter(
            torch.tensor(raw_init, device=self.device, dtype=torch.float32),
            requires_grad=spec.learnable,
        )
        self.param_specs[name] = spec

    def get_parameter(self, name: str) -> torch.Tensor:
        if name not in self.params:
            raise ValueError(f"Parameter {name} not found")
        raw = self.params[name]
        spec = self.param_specs[name]
        if name == "mass":
            return torch.nn.functional.softplus(raw)
        val = torch.sigmoid(raw)
        if spec.bounds:
            low, high = spec.bounds
            val = val * (high - low) + low
        return val


class SceneGraph:
    """
    Lightweight scene graph to hold physical objects and provide adjacency info.
    """

    def __init__(self, config_path: str, device: str = "cpu"):
        self.config = PhysicsConfig.from_yaml(config_path)
        self.device = device
        self.static_objects: List[PhysicalObject] = []
        self.dynamic_objects: List[PhysicalObject] = []
        self.objects_map: Dict[str, PhysicalObject] = {}
        self._build_scene()

    def _build_scene(self):
        for obj_cfg in self.config.objects:
            obj = PhysicalObject(obj_cfg, device=self.device)
            obj.register_parameters(self.config.physics_defaults)
            self.objects_map[obj.name] = obj
            if obj.is_static:
                self.static_objects.append(obj)
            else:
                self.dynamic_objects.append(obj)

    def get_interaction_graph(self, threshold: float = 1.0) -> List[Tuple[int, int]]:
        all_objects = self.dynamic_objects + self.static_objects
        edges: List[Tuple[int, int]] = []
        if not all_objects:
            return edges
        centroids = torch.stack([obj.centroid for obj in all_objects])
        dists = torch.cdist(centroids.unsqueeze(0), centroids.unsqueeze(0)).squeeze(0)
        src, dst = torch.where(dists < threshold)
        for s, d in zip(src, dst):
            if s == d:
                continue
            edges.append((s.item(), d.item()))
        return edges

    def get_all_parameters(self) -> List[nn.Parameter]:
        params: List[nn.Parameter] = []
        for obj in self.dynamic_objects + self.static_objects:
            params.extend(obj.parameters())
        return params
