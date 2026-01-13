from .config import PhysicsConfig, ObjectConfig, PhysicsDefaults, LearnableSpec
from .objects import PhysicalObject, SceneGraph
from .engine import PhysicsEngine

# Optional PyBullet adapter
try:
    from .pybullet_adapter import PyBulletAdapter

    _HAS_PYBULLET_ADAPTER = True
except ImportError:
    PyBulletAdapter = None
    _HAS_PYBULLET_ADAPTER = False

__all__ = [
    "PhysicsConfig",
    "ObjectConfig",
    "PhysicsDefaults",
    "LearnableSpec",
    "PhysicalObject",
    "SceneGraph",
    "PhysicsEngine",
]

# Conditionally add PyBulletAdapter to exports
if _HAS_PYBULLET_ADAPTER:
    __all__.append("PyBulletAdapter")
else:
    # Provide a placeholder that raises an informative error
    def _pybullet_not_available():
        raise ImportError(
            "PyBulletAdapter not available. Install pybullet: pip install pybullet"
        )

    PyBulletAdapter = _pybullet_not_available
