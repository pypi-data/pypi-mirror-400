import json
import math
import os
import shutil
import subprocess
import tempfile
from typing import Dict, List, Optional
import numpy as np


class FbxLoader:
    """
    Minimal FBX motion extractor that shells out to the compiled fbx-extract binary.

    Steps:
      1) Convert the source FBX to binary with assimp (handles ASCII inputs).
      2) Run fbx-extract to emit hierarchy/skel/obj files into a temp directory.
      3) Parse hierarchy + skel into a Python dict and save as JSON.
      4) Optionally copy emitted OBJ meshes to the requested mesh_output_dir.

    Data Standardization (Mujoco-compatible):
      - Positions: Scaled from centimeters to meters (factor 0.01)
      - Positions: Rotated +90° around X-axis (Y up → Z up)
      - Quaternions: Normalized to unit length
      - Quaternions: Rotated +90° around X-axis to match position rotation

    Output data regime matches Mujoco Humanoid:
      - Human stands on XY plane with Z up
      - Root position: ~(x, y, z) in meters, height (z) ~1.0-1.4m
      - Quaternions: Unit quaternions (x, y, z, w format)

    Blender is not used anywhere in this path.
    """

    @staticmethod
    def _transform_position(
        px: float, py: float, pz: float, scale: float = 1.0
    ) -> tuple:
        """
        Transform position from FBX coordinate system (Y-up) to Mujoco (Z-up).
        Order: rotate first, then scale.
        Rotate +90° around X-axis: (x, y, z) -> (x, -z, y)
        Then scale (cm to meters).
        """
        # Step 1: Rotate (Y-up to Z-up): (x, y, z) -> (x, -z, y)
        rx, ry, rz = px, -pz, py
        # Step 2: Scale
        return (rx * scale, ry * scale, rz * scale)

    @staticmethod
    def _which_fbx_extract() -> str:
        path = shutil.which("fbx-extract")
        if path:
            return path
        fallback = "/workspace/fbx-extract/build/fbx-extract"
        if os.path.exists(fallback):
            return fallback
        raise RuntimeError(
            "fbx-extract binary not found on PATH or at /workspace/fbx-extract/build/fbx-extract"
        )

    @staticmethod
    def _run(cmd: List[str], cwd: Optional[str] = None) -> None:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        if result.returncode != 0:
            raise RuntimeError(f"Command failed: {' '.join(cmd)}")

    @staticmethod
    def _load_bone_names(hierarchy_path: str) -> List[str]:
        with open(hierarchy_path, "r") as f:
            lines = [
                ln.strip()
                for ln in f.readlines()
                if ln.strip() and not ln.strip().startswith("#")
            ]
        if len(lines) < 2:
            raise RuntimeError("Hierarchy file empty or malformed")
        names: List[str] = []
        for ln in lines[1:]:
            parts = ln.split()
            if len(parts) < 4:
                continue
            name = " ".join(parts[3:])
            names.append(name)
        return names

    @staticmethod
    def _load_motion(
        skel_path: str,
        bone_names: List[str],
        position_scale: float = 0.01,  # Convert cm to meters (FBX default is cm, Mujoco uses meters)
    ) -> Dict[str, List[dict]]:
        """
        Load motion data from skeleton file and standardize to Mujoco-compatible format.

        Standardization applied:
        - Positions: scaled by position_scale (default 0.01 to convert cm -> meters)
        - Positions: rotated +90° around X-axis (Y-up → Z-up): (x,y,z) -> (x,-z,y)
        - Quaternions: normalized only (not rotated - visualization uses positions only)

        Resulting data:
        - Positions in meters (root height ~1.0-1.4m in Z)
        - Human stands on XY plane with Z up
        """
        with open(skel_path, "r") as f:
            lines = [
                ln.strip()
                for ln in f.readlines()
                if ln.strip() and not ln.strip().startswith("#")
            ]
        if not lines:
            raise RuntimeError("Skeleton file empty")
        header = lines[0].split()
        frame_count, bone_count = int(header[0]), int(header[1])
        count = min(bone_count, len(bone_names))
        trajectories: Dict[str, List[dict]] = {name: [] for name in bone_names[:count]}

        for step_idx, ln in enumerate(lines[1:]):
            vals = list(map(float, ln.split()))
            expected = bone_count * 7
            if len(vals) < expected:
                print(
                    f"Skipping frame {step_idx}: not enough values ({len(vals)}/{expected})"
                )
                continue
            for i in range(count):
                off = i * 7
                qx, qy, qz, qw, px, py, pz = vals[off : off + 7]

                # Transform position: scale and rotate
                px, py, pz = FbxLoader._transform_position(px, py, pz, position_scale)

                # Normalize quaternion only (leave orientation as-is for now)
                quat_norm = np.sqrt(qx * qx + qy * qy + qz * qz + qw * qw)
                if quat_norm > 1e-8:
                    qx, qy, qz, qw = (
                        qx / quat_norm,
                        qy / quat_norm,
                        qz / quat_norm,
                        qw / quat_norm,
                    )

                trajectories[bone_names[i]].append(
                    {
                        "position": [float(px), float(py), float(pz)],
                        "quaternion": [float(qx), float(qy), float(qz), float(qw)],
                        "linear_velocity": [0.0, 0.0, 0.0],
                        "angular_velocity": [0.0, 0.0, 0.0],
                        "step": step_idx,
                    }
                )
        return trajectories

    @staticmethod
    def extract_motion(
        fbx_path: str,
        output_path: str,
        blender_path: str = "blender",  # kept for signature compatibility; unused
        mesh_output_dir: Optional[str] = None,
    ) -> None:
        if not os.path.exists(fbx_path):
            raise FileNotFoundError(f"FBX file not found: {fbx_path}")

        fbx_extract_exec = FbxLoader._which_fbx_extract()

        with tempfile.TemporaryDirectory() as workdir:
            # 1) Convert to binary FBX
            bin_fbx = os.path.join(workdir, "scene_bin.fbx")
            FbxLoader._run(
                ["assimp", "export", os.path.abspath(fbx_path), bin_fbx, "-ffbx", "-b"]
            )

            # 2) Run fbx-extract
            FbxLoader._run([fbx_extract_exec, bin_fbx], cwd=workdir)

            base = os.path.splitext(os.path.basename(bin_fbx))[0]
            hierarchy_path = os.path.join(workdir, f"{base}_hierarchy.txt")
            skel_path = os.path.join(workdir, f"{base}_skel.txt")

            if not os.path.exists(hierarchy_path) or not os.path.exists(skel_path):
                raise RuntimeError("fbx-extract outputs missing (hierarchy/skel)")

            # 3) Load and serialize motion
            bone_names = FbxLoader._load_bone_names(hierarchy_path)
            bones_data = FbxLoader._load_motion(skel_path, bone_names)

            # Determine frame count from the first bone's trajectory
            first_bone = next(iter(bones_data.values()))
            frame_count = len(first_bone) if first_bone else 0

            # Build complete output with metadata
            output_data = {
                "fps": 30,  # Default FPS, could be extracted from FBX if available
                "frames": frame_count,
                "bone_names": bone_names,
                "bones": bones_data,
            }

            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(output_data, f, indent=2)

            # 4) Optionally copy meshes out
            if mesh_output_dir:
                os.makedirs(mesh_output_dir, exist_ok=True)
                for fname in os.listdir(workdir):
                    if fname.lower().endswith(".obj"):
                        shutil.copy2(
                            os.path.join(workdir, fname),
                            os.path.join(mesh_output_dir, fname),
                        )
