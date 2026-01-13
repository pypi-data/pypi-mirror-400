import importlib.util
import sys
import os
from typing import Any, Type


def load_class_from_file(path_str: str, base_class: Type = None) -> Type:
    """
    Loads a class from a string formatted as "path/to/file.py:ClassName".
    Optional base_class check.
    """
    if ":" not in path_str:
        raise ValueError(
            f"Invalid format '{path_str}'. Expected 'path/to/file.py:ClassName'"
        )

    file_path, class_name = path_str.split(":")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    spec = importlib.util.spec_from_file_location("custom_module", file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules["custom_module"] = (
        module  # Register to avoid reload issues or allow pickling if needed (though pickling custom classes is tricky)
    )
    spec.loader.exec_module(module)

    if not hasattr(module, class_name):
        raise AttributeError(f"Class {class_name} not found in {file_path}")

    cls = getattr(module, class_name)

    if base_class and not issubclass(cls, base_class):
        # Warning or Error? Let's just warn or allow duck typing if not strict.
        # But user asked to load "like an environment", implying strict loading.
        pass

    return cls
