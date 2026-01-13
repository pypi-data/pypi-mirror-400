from typing import Optional, Any
from .class_loader import load_class_from_file

# Conditional import of gymnasium (may fail if MuJoCo not available)
try:
    import gymnasium as gym

    HAS_GYMNASIUM = True
except ImportError:
    gym = None
    HAS_GYMNASIUM = False


def load_environment(env_name_or_path: str):
    """
    Loads an environment from a Gym ID or a custom python file path.
    Format for file path: "path/to/file.py:ClassName"
    """
    if ":" in env_name_or_path and (
        os.path.exists(env_name_or_path.split(":")[0]) or "/" in env_name_or_path
    ):
        # Load from file
        try:
            env_class = load_class_from_file(env_name_or_path)
        except (ValueError, FileNotFoundError):
            # Might be a gym ID with colon? unlikely but gym ids are usually Name-v0
            # Assume file path if colon exists and looks like a path
            raise

        # Instantiate
        try:
            env = env_class()
        except TypeError:
            # Try with render_mode if it fails (common in gym)
            try:
                env = env_class(render_mode="rgb_array")
            except TypeError:
                raise ValueError(
                    f"Could not instantiate {env_class.__name__}. Ensure it has a compatible constructor."
                )

        return env

    else:
        # Assume Gym ID
        try:
            env = gym.make(env_name_or_path, render_mode="rgb_array")
            return env
        except (
            Exception
        ) as e:  # gym.error.Error when gym is available, general Exception when not
            raise ValueError(
                f"Could not load Gym environment '{env_name_or_path}': {e}"
            )


import os  # Added import missing in write
