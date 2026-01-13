from __future__ import annotations

import math
from typing import Dict, Iterable, List, Mapping, Sequence

import numpy as np

# Canonical joint ordering for Mujoco Humanoid actions (17-dim)
HUMANOID_ACTION_JOINTS: List[str] = [
    "abdomen_y",
    "abdomen_z",
    "abdomen_x",
    "right_hip_x",
    "right_hip_z",
    "right_hip_y",
    "right_knee",
    "left_hip_x",
    "left_hip_z",
    "left_hip_y",
    "left_knee",
    "right_shoulder1",
    "right_shoulder2",
    "right_elbow",
    "left_shoulder1",
    "left_shoulder2",
    "left_elbow",
]

# qpos layout for Humanoid-v5 (24 dims)
HUMANOID_QPOS_NAMES: List[str] = [
    "root_x",
    "root_y",
    "root_z",
    "root_quat_w",
    "root_quat_x",
    "root_quat_y",
    "root_quat_z",
    "abdomen_z",
    "abdomen_y",
    "abdomen_x",
    "right_hip_x",
    "right_hip_z",
    "right_hip_y",
    "right_knee",
    "left_hip_x",
    "left_hip_z",
    "left_hip_y",
    "left_knee",
    "right_shoulder1",
    "right_shoulder2",
    "right_elbow",
    "left_shoulder1",
    "left_shoulder2",
    "left_elbow",
]

# Common FBX/Mixamo bone aliases to logical joints
# Maps various bone naming conventions to canonical joint names
ALIAS_MAP: Dict[str, str] = {
    # Root/Hips
    "hips": "root",
    "pelvis": "root",
    "mixamorig:Hips": "root",
    "mixamorigHips": "root",
    # Spine/Abdomen
    "spine": "abdomen",
    "spine1": "abdomen",
    "spine2": "abdomen",
    "abdomen": "abdomen",
    "torso": "abdomen",
    "mixamorig:Spine": "abdomen",
    "mixamorig:Spine1": "abdomen",
    "mixamorig:Spine2": "abdomen",
    "mixamorigSpine": "abdomen",
    "mixamorigSpine1": "abdomen",
    "mixamorigSpine2": "abdomen",
    # Right Hip/Upper Leg
    "rightupleg": "right_hip",
    "right_thigh": "right_hip",
    "mixamorig:RightUpLeg": "right_hip",
    "mixamorigRightUpLeg": "right_hip",
    # Left Hip/Upper Leg
    "leftupleg": "left_hip",
    "left_thigh": "left_hip",
    "mixamorig:LeftUpLeg": "left_hip",
    "mixamorigLeftUpLeg": "left_hip",
    # Right Knee/Lower Leg
    "rightleg": "right_knee",
    "right_shin": "right_knee",
    "mixamorig:RightLeg": "right_knee",
    "mixamorigRightLeg": "right_knee",
    # Left Knee/Lower Leg
    "leftleg": "left_knee",
    "left_shin": "left_knee",
    "mixamorig:LeftLeg": "left_knee",
    "mixamorigLeftLeg": "left_knee",
    # Right Shoulder
    "rightshoulder": "right_shoulder",
    "mixamorig:RightShoulder": "right_shoulder",
    "mixamorigRightShoulder": "right_shoulder",
    # Left Shoulder
    "leftshoulder": "left_shoulder",
    "mixamorig:LeftShoulder": "left_shoulder",
    "mixamorigLeftShoulder": "left_shoulder",
    # Right Arm (maps to shoulder rotation in Mujoco)
    "rightarm": "right_arm",
    "mixamorig:RightArm": "right_arm",
    "mixamorigRightArm": "right_arm",
    # Left Arm (maps to shoulder rotation in Mujoco)
    "leftarm": "left_arm",
    "mixamorig:LeftArm": "left_arm",
    "mixamorigLeftArm": "left_arm",
    # Right Elbow/Forearm
    "rightforearm": "right_elbow",
    "mixamorig:RightForeArm": "right_elbow",
    "mixamorigRightForeArm": "right_elbow",
    # Left Elbow/Forearm
    "leftforearm": "left_elbow",
    "mixamorig:LeftForeArm": "left_elbow",
    "mixamorigLeftForeArm": "left_elbow",
}


def _normalize_name(name: str) -> str:
    return name.lower().replace(" ", "")


def euler_to_quat_xyz(euler_degrees: Sequence[float]) -> np.ndarray:
    """
    Convert Euler angles (degrees) to quaternion (x,y,z,w).
    """
    roll, pitch, yaw = np.radians(euler_degrees)
    cr = np.cos(roll * 0.5)
    sr = np.sin(roll * 0.5)
    cp = np.cos(pitch * 0.5)
    sp = np.sin(pitch * 0.5)
    cy = np.cos(yaw * 0.5)
    sy = np.sin(yaw * 0.5)

    w = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy

    return np.array([x, y, z, w], dtype=np.float64)


def quat_multiply(q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
    """
    Multiply two quaternions (q1 * q2).
    """
    x1, y1, z1, w1 = q1
    x2, y2, z2, w2 = q2

    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
    z = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2

    return np.array([x, y, z, w], dtype=np.float64)


def quat_to_euler_xyz(quat: Sequence[float]) -> np.ndarray:
    """
    Convert quaternion (x, y, z, w) or (w, x, y, z) to Euler XYZ (radians).
    """
    q = np.array(quat, dtype=np.float64)
    if q.shape[0] != 4:
        raise ValueError("Quaternion must have 4 elements")
    # Heuristic: if |q[0]| > 1 then probably w is last; prefer (x,y,z,w)
    if abs(q[0]) <= 1.0 and abs(q[3]) > 1.0:
        q = q[[1, 2, 3, 0]]

    x, y, z, w = q
    # Normalize
    norm = math.sqrt(w * w + x * x + y * y + z * z) + 1e-9
    w, x, y, z = w / norm, x / norm, y / norm, z / norm

    # From https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = math.atan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch_y = math.asin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = math.atan2(t3, t4)

    return np.array([roll_x, pitch_y, yaw_z], dtype=np.float64)


class HumanoidRetarget:
    """
    Light-weight retargeting helper to map FBX bone transforms into Mujoco Humanoid qpos/action.

    This is intentionally heuristic: it prefers approximate alignment over exact rig matching.
    You can pass a custom mapping dict if your bone names differ from the defaults/aliases.

    Note: Data extracted via FbxLoader is already standardized to Mujoco-compatible format:
    - Positions in meters (scaled from cm at extraction time)
    - Quaternions normalized
    - Root orientation corrected to upright

    Args:
        joint_axis_map: Custom mapping of joint names to Euler axes
        root_height: Default root height in meters when no root bone found
        scale: Scale factor to apply to input positions (default 1.0 since data is already in meters)
        root_rotation_correction: Euler angles in degrees to correct orientation (None = no correction, typically applied at extraction time)
    """

    def __init__(
        self,
        joint_axis_map: Mapping[str, str] | None = None,
        root_height: float = 1.4,
        scale: float = 1.0,  # Scale factor for positions (1.0 if data already in meters from extraction)
        root_rotation_correction: (
            tuple[float, float, float] | None
        ) = None,  # Euler angles in degrees (None = no correction)
    ):
        # axis map: which Euler axis to take for each joint entry
        self.joint_axis_map = joint_axis_map or {
            "abdomen_z": "z",
            "abdomen_y": "y",
            "abdomen_x": "x",
            "right_hip_x": "x",
            "right_hip_z": "z",
            "right_hip_y": "y",
            "right_knee": "x",
            "left_hip_x": "x",
            "left_hip_z": "z",
            "left_hip_y": "y",
            "left_knee": "x",
            "right_shoulder1": "x",
            "right_shoulder2": "z",
            "right_elbow": "x",
            "left_shoulder1": "x",
            "left_shoulder2": "z",
            "left_elbow": "x",
        }
        self.root_height = root_height
        self.scale = scale
        self.root_rotation_correction = (
            root_rotation_correction  # None means no correction applied
        )

    def _resolve_bone(
        self, frame_bones: Mapping[str, dict], candidates: Iterable[str]
    ) -> dict | None:
        for cand in candidates:
            if cand in frame_bones:
                return frame_bones[cand]
        # try alias-normalized lookup
        norm_map = {_normalize_name(k): v for k, v in frame_bones.items()}
        for cand in candidates:
            aliased = ALIAS_MAP.get(_normalize_name(cand), cand)
            if aliased in frame_bones:
                return frame_bones[aliased]
            if _normalize_name(aliased) in norm_map:
                return norm_map[_normalize_name(aliased)]
        # try alias map directly
        for name, entry in frame_bones.items():
            alias = ALIAS_MAP.get(_normalize_name(name))
            if alias in candidates:
                return entry
        return None

    def frame_to_qpos(self, frame_bones: Mapping[str, dict]) -> np.ndarray:
        """
        Convert a single bone frame (name -> {position, quaternion}) to Humanoid qpos (24,).
        """
        qpos = np.zeros(len(HUMANOID_QPOS_NAMES), dtype=np.float64)

        # Root: use hips translation and global orientation
        root_entry = self._resolve_bone(
            frame_bones, ["mixamorigHips", "root", "hips", "pelvis"]
        )
        if root_entry:
            pos = root_entry.get("position", [0.0, 0.0, self.root_height])
            quat = root_entry.get("quaternion", [0.0, 0.0, 0.0, 1.0])
            if len(pos) >= 3:
                qpos[0:3] = np.array(pos[:3], dtype=np.float64) * self.scale
            else:
                qpos[0:3] = np.array([0.0, 0.0, self.root_height], dtype=np.float64)
            # assume quat is (x,y,z,w); apply rotation correction if specified
            if len(quat) == 4:
                bone_quat = np.array([quat[0], quat[1], quat[2], quat[3]])
                if self.root_rotation_correction is not None:
                    # Apply rotation correction to fix FBX orientation
                    correction_quat = euler_to_quat_xyz(self.root_rotation_correction)
                    bone_quat = quat_multiply(correction_quat, bone_quat)
                # reorder to (w,x,y,z) for Mujoco
                qpos[3] = bone_quat[3]  # w
                qpos[4:7] = bone_quat[0:3]  # x,y,z
            else:
                qpos[3] = 1.0
        else:
            qpos[2] = self.root_height
            qpos[3] = 1.0  # identity quaternion

        # Helper to fill a single joint angle from a bone quaternion
        def _set_angle(joint_name: str, bone_candidates: Iterable[str]):
            entry = self._resolve_bone(frame_bones, bone_candidates)
            if entry is None:
                return
            euler = quat_to_euler_xyz(entry.get("quaternion", [0, 0, 0, 1]))
            axis = self.joint_axis_map.get(joint_name, "x")
            if axis == "x":
                val = euler[0]
            elif axis == "y":
                val = euler[1]
            else:
                val = euler[2]
            idx = HUMANOID_QPOS_NAMES.index(joint_name)
            qpos[idx] = val

        # Abdomen/Spine - use Spine1 or Spine2 for torso rotation
        _set_angle(
            "abdomen_z",
            [
                "mixamorigSpine1",
                "mixamorigSpine2",
                "mixamorigSpine",
                "abdomen",
                "spine1",
                "spine2",
            ],
        )
        _set_angle(
            "abdomen_y",
            [
                "mixamorigSpine1",
                "mixamorigSpine2",
                "mixamorigSpine",
                "abdomen",
                "spine1",
                "spine2",
            ],
        )
        _set_angle(
            "abdomen_x",
            [
                "mixamorigSpine1",
                "mixamorigSpine2",
                "mixamorigSpine",
                "abdomen",
                "spine1",
                "spine2",
            ],
        )

        # Right leg
        _set_angle("right_hip_x", ["mixamorigRightUpLeg", "right_hip", "rightupleg"])
        _set_angle("right_hip_z", ["mixamorigRightUpLeg", "right_hip", "rightupleg"])
        _set_angle("right_hip_y", ["mixamorigRightUpLeg", "right_hip", "rightupleg"])
        _set_angle("right_knee", ["mixamorigRightLeg", "right_knee", "rightleg"])

        # Left leg
        _set_angle("left_hip_x", ["mixamorigLeftUpLeg", "left_hip", "leftupleg"])
        _set_angle("left_hip_z", ["mixamorigLeftUpLeg", "left_hip", "leftupleg"])
        _set_angle("left_hip_y", ["mixamorigLeftUpLeg", "left_hip", "leftupleg"])
        _set_angle("left_knee", ["mixamorigLeftLeg", "left_knee", "leftleg"])

        # Right arm - shoulder rotation comes from RightArm bone, elbow from RightForeArm
        _set_angle(
            "right_shoulder1",
            ["mixamorigRightArm", "mixamorigRightShoulder", "right_shoulder"],
        )
        _set_angle(
            "right_shoulder2",
            ["mixamorigRightArm", "mixamorigRightShoulder", "right_shoulder"],
        )
        _set_angle(
            "right_elbow", ["mixamorigRightForeArm", "right_elbow", "rightforearm"]
        )

        # Left arm - shoulder rotation comes from LeftArm bone, elbow from LeftForeArm
        _set_angle(
            "left_shoulder1",
            ["mixamorigLeftArm", "mixamorigLeftShoulder", "left_shoulder"],
        )
        _set_angle(
            "left_shoulder2",
            ["mixamorigLeftArm", "mixamorigLeftShoulder", "left_shoulder"],
        )
        _set_angle("left_elbow", ["mixamorigLeftForeArm", "left_elbow", "leftforearm"])

        return qpos

    def qpos_delta_to_action(
        self, qpos_t: np.ndarray, qpos_tp1: np.ndarray, dt: float
    ) -> np.ndarray:
        """
        Map qpos delta to 17-D action vector (torque-like proxy).
        """
        delta = (qpos_tp1 - qpos_t) / max(dt, 1e-6)
        actions = np.zeros(len(HUMANOID_ACTION_JOINTS), dtype=np.float64)
        for i, joint in enumerate(HUMANOID_ACTION_JOINTS):
            idx = HUMANOID_QPOS_NAMES.index(joint)
            actions[i] = delta[idx]
        return actions
