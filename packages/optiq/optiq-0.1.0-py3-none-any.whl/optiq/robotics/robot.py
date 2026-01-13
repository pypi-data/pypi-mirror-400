from typing import Dict, List, Any, Optional, Tuple, TYPE_CHECKING
import numpy as np

# Optional physics stack (may be absent in minimal installs)
try:
    from ..physics.pybullet_adapter import PyBulletAdapter  # type: ignore

    HAS_PYBULLET = True
except ImportError:
    PyBulletAdapter = None
    HAS_PYBULLET = False

if TYPE_CHECKING:
    from ..physics.pybullet_adapter import PyBulletAdapter


class Robot:
    """
    A generic wrapper for an articulated robot in the simulation.
    Abstraction layer over the physics engine adapter.
    """

    def __init__(
        self, name: str, adapter: "PyBulletAdapter", end_effector_link_index: int
    ):
        self.name = name
        self.adapter = adapter
        self.ee_link_index = end_effector_link_index

        # Cache joint info
        self.joint_info = self.adapter.get_joint_info(name)
        self.actuated_joint_indices = [
            j["index"] for j in self.joint_info if j["type"] != 4  # 4 is JOINT_FIXED
        ]

    def get_joint_positions(self) -> List[float]:
        states = self.adapter.get_joint_states(self.name)
        return [states[idx]["position"] for idx in self.actuated_joint_indices]

    def get_joint_velocities(self) -> List[float]:
        states = self.adapter.get_joint_states(self.name)
        return [states[idx]["velocity"] for idx in self.actuated_joint_indices]

    def set_joint_velocities(self, velocities: List[float]):
        if len(velocities) != len(self.actuated_joint_indices):
            raise ValueError(
                f"Expected {len(self.actuated_joint_indices)} velocities, got {len(velocities)}"
            )

        target_map = {
            idx: vel for idx, vel in zip(self.actuated_joint_indices, velocities)
        }
        self.adapter.set_joint_control(self.name, "velocity", target_map)

    def get_end_effector_pose(self) -> Tuple[np.ndarray, np.ndarray]:
        """Returns (position, orientation_quat) of EE."""
        state = self.adapter.get_link_state(self.name, self.ee_link_index)
        return np.array(state["world_link_frame_pos"]), np.array(
            state["world_link_frame_orn"]
        )

    def get_jacobian(self, local_position=[0, 0, 0]) -> np.ndarray:
        """
        Returns the geometric Jacobian (Linear and Angular stacked) for the End Effector.
        Shape: (6, N_dof)
        """
        # PyBullet requires lists for all joint values
        num_joints = len(self.joint_info)
        # We need ALL joint positions (including fixed ones? No, usually getJointStates returns all)
        # calculateJacobian takes values for ALL joints in range(getNumJoints)

        # Get full state
        states = self.adapter.get_joint_states(self.name)
        # Note: states dict keys are indices.

        # Sort by index to ensure order
        sorted_indices = sorted(states.keys())
        q = [states[i]["position"] for i in sorted_indices]
        dq = [states[i]["velocity"] for i in sorted_indices]
        ddq = [0.0] * len(q)  # Acceleration ignored for kinematic Jacobian

        lin_jac, ang_jac = self.adapter.calculate_jacobian(
            self.name, self.ee_link_index, local_position, q, dq, ddq
        )

        # PyBullet returns Jacobian for ALL joints. We only want columns for actuated joints.
        # However, usually we can just use the full matrix if we filter later or if fixed columns are zero.
        # But typically control loops expect size N_actuated.

        # Filter columns
        # Indices in q list correspond to joint indices.
        # We want columns corresponding to self.actuated_joint_indices

        J_lin = lin_jac[:, self.actuated_joint_indices]
        J_ang = ang_jac[:, self.actuated_joint_indices]

        return np.vstack([J_lin, J_ang])
