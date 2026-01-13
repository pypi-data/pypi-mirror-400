"""
Robotics module for controlling articulated bodies (robots).
"""

from .robot import Robot
from .visual_servo import VisualServoController

__all__ = [
    "Robot",
    "VisualServoController",
]
