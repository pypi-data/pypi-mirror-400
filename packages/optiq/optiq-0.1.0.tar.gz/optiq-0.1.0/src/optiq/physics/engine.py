from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from .objects import PhysicalObject, SceneGraph


class PhysicsEngine(ABC):
    @abstractmethod
    def initialize(
        self, gravity: Tuple[float, float, float] = (0, 0, -9.81), dt: float = 0.01
    ):
        """Initialize the physics engine with global settings."""

    @abstractmethod
    def add_body(self, obj: PhysicalObject):
        """Add a PhysicalObject to the simulation environment."""

    @abstractmethod
    def step(self, action: Optional[Any] = None):
        """Step the simulation forward by one dt."""

    @abstractmethod
    def get_state(self, obj_name: str) -> Dict[str, Any]:
        """
        Returns dictionary containing:
        - position: [x, y, z]
        - quaternion: [x, y, z, w]
        - linear_velocity: [vx, vy, vz]
        - angular_velocity: [wx, wy, wz]
        """

    @abstractmethod
    def set_params(self, obj_name: str, params_dict: Dict[str, float]):
        """Update physical parameters (mass, friction, etc.) for an object."""

    def generate_ground_truth(
        self, scene: SceneGraph, duration: float
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Runs the simulation for a specified duration and returns trajectories.
        """
        self.initialize(
            dt=scene.config.physics_defaults.mass_range[0]
        )  # dt placeholder; engines can override internally

        for obj in scene.static_objects + scene.dynamic_objects:
            self.add_body(obj)
            params_dict: Dict[str, float] = {}
            for name in obj.params.keys():
                try:
                    params_dict[name] = obj.get_parameter(name).item()
                except Exception:
                    continue
            if params_dict:
                self.set_params(obj.name, params_dict)

        steps = int(
            duration / 0.01
        )  # fallback step count; real engines should override initialize dt
        trajectories = {obj.name: [] for obj in scene.dynamic_objects}

        for _ in range(steps):
            self.step()
            for obj in scene.dynamic_objects:
                state = self.get_state(obj.name)
                trajectories[obj.name].append(state)

        return trajectories
