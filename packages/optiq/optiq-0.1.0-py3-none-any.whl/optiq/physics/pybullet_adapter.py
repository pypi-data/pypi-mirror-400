"""
PyBullet adapter for physics simulation.
Provides a high-level interface to PyBullet for robotics applications.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np

# Optional PyBullet import
try:
    import pybullet as p
    import pybullet_data

    HAS_PYBULLET = True
except ImportError:
    p = None
    HAS_PYBULLET = False


class PyBulletAdapter:
    """
    Adapter for PyBullet physics engine.
    Provides robotics-specific methods for joint and link manipulation.
    """

    def __init__(self, gui: bool = False, dt: float = 0.01):
        """Initialize PyBullet simulation.

        Args:
            gui: Whether to show GUI
            dt: Simulation time step
        """
        if not HAS_PYBULLET:
            raise ImportError(
                "PyBullet not available. Install with: pip install pybullet"
            )

        self.client_id = p.connect(p.GUI if gui else p.DIRECT)
        self.dt = dt

        # Set gravity and time step
        p.setGravity(0, 0, -9.81)
        p.setTimeStep(dt)

        # Add search path for default data
        p.setAdditionalSearchPath(pybullet_data.getDataPath())

    def load_urdf(
        self,
        urdf_path: str,
        position: Tuple[float, float, float] = (0, 0, 0),
        orientation: Tuple[float, float, float, float] = (0, 0, 0, 1),
        name: Optional[str] = None,
    ) -> int:
        """Load a URDF file and return the body ID.

        Args:
            urdf_path: Path to URDF file
            position: Initial position (x, y, z)
            orientation: Initial orientation quaternion (x, y, z, w)
            name: Optional name for the body

        Returns:
            PyBullet body ID
        """
        body_id = p.loadURDF(
            urdf_path, position, orientation, physicsClientId=self.client_id
        )
        if name:
            # Store name mapping (PyBullet doesn't have built-in naming)
            if not hasattr(self, "_body_names"):
                self._body_names = {}
            self._body_names[name] = body_id
        return body_id

    def get_body_id(self, name: str) -> int:
        """Get PyBullet body ID by name."""
        if hasattr(self, "_body_names") and name in self._body_names:
            return self._body_names[name]
        raise ValueError(f"Body '{name}' not found")

    def get_joint_info(self, name: str) -> List[Dict[str, Any]]:
        """Get information about all joints in a body."""
        body_id = self.get_body_id(name)
        joint_info = []

        num_joints = p.getNumJoints(body_id, physicsClientId=self.client_id)
        for i in range(num_joints):
            info = p.getJointInfo(body_id, i, physicsClientId=self.client_id)
            joint_info.append(
                {
                    "index": info[0],
                    "name": (
                        info[1].decode("utf-8")
                        if isinstance(info[1], bytes)
                        else info[1]
                    ),
                    "type": info[2],  # JOINT_REVOLUTE, JOINT_PRISMATIC, etc.
                    "lower_limit": info[8],
                    "upper_limit": info[9],
                    "max_force": info[10],
                    "max_velocity": info[11],
                }
            )

        return joint_info

    def get_joint_states(self, name: str) -> Dict[int, Dict[str, float]]:
        """Get current state of all joints in a body."""
        body_id = self.get_body_id(name)
        states = {}

        joint_states = p.getJointStates(
            body_id, range(p.getNumJoints(body_id)), physicsClientId=self.client_id
        )

        for i, state in enumerate(joint_states):
            states[i] = {
                "position": state[0],
                "velocity": state[1],
                "reaction_forces": state[2],
                "applied_torque": state[3],
            }

        return states

    def set_joint_control(
        self, name: str, control_type: str, target_map: Dict[int, float]
    ):
        """Set joint control targets.

        Args:
            name: Body name
            control_type: "position" or "velocity"
            target_map: Dict of joint_index -> target_value
        """
        body_id = self.get_body_id(name)

        for joint_idx, target_value in target_map.items():
            if control_type == "velocity":
                p.setJointMotorControl2(
                    body_id,
                    joint_idx,
                    p.VELOCITY_CONTROL,
                    targetVelocity=target_value,
                    physicsClientId=self.client_id,
                )
            elif control_type == "position":
                p.setJointMotorControl2(
                    body_id,
                    joint_idx,
                    p.POSITION_CONTROL,
                    targetPosition=target_value,
                    physicsClientId=self.client_id,
                )
            else:
                raise ValueError(f"Unknown control type: {control_type}")

    def get_link_state(self, name: str, link_index: int) -> Dict[str, Any]:
        """Get state of a specific link."""
        body_id = self.get_body_id(name)

        link_state = p.getLinkState(body_id, link_index, physicsClientId=self.client_id)

        return {
            "world_link_frame_pos": link_state[0],
            "world_link_frame_orn": link_state[1],
            "local_inertial_pos": link_state[2],
            "local_inertial_orn": link_state[3],
            "world_link_linear_vel": link_state[6],
            "world_link_angular_vel": link_state[7],
        }

    def calculate_jacobian(
        self,
        name: str,
        link_index: int,
        local_position: List[float],
        q: List[float],
        dq: List[float],
        ddq: List[float],
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate geometric Jacobian for a link."""
        body_id = self.get_body_id(name)

        # PyBullet's calculateJacobian expects numpy arrays
        q_np = np.array(q)
        dq_np = np.array(dq)
        ddq_np = np.array(ddq)

        linear_jac, angular_jac = p.calculateJacobian(
            body_id,
            link_index,
            local_position,
            q_np,
            dq_np,
            ddq_np,
            physicsClientId=self.client_id,
        )

        return np.array(linear_jac), np.array(angular_jac)

    def step_simulation(self):
        """Step the simulation forward by one time step."""
        p.stepSimulation(physicsClientId=self.client_id)

    def disconnect(self):
        """Disconnect from PyBullet."""
        if hasattr(self, "client_id"):
            p.disconnect(physicsClientId=self.client_id)

    def __del__(self):
        """Cleanup on deletion."""
        self.disconnect()
