"""
Oculus SDK - Robotics Observability & Safety

A modular, platform-agnostic SDK for real-time observability,
safety monitoring, and prediction in robotics simulations.

Supports: Isaac Sim, Isaac Lab, ROS 2, Mujoco, PyBullet, Gazebo
"""

__version__ = "1.0.0"
__author__ = "Oculus Robotics"
__email__ = "support@oculusrobotics.com"

# Core imports
from .core.tracer import BaseTracer
from .core.connection import WebSocketConnection
from .core.auth import authenticate

# Platform imports (lazy loading)
def get_isaac_sim_tracer():
    from .platforms.isaac_sim.tracer import IsaacSimTracer
    return IsaacSimTracer

def get_isaac_lab_tracer():
    from .platforms.isaac_sim.tracer import IsaacSimTracer  # Use IsaacSim for now
    return IsaacSimTracer

def get_ros2_tracer():
    from .platforms.ros2.tracer import ROS2Tracer
    return ROS2Tracer

def get_mujoco_tracer():
    from .platforms.mujoco.tracer import MujocoTracer
    return MujocoTracer

def get_pybullet_tracer():
    from .platforms.pybullet.tracer import PyBulletTracer
    return PyBulletTracer

def get_gazebo_tracer():
    from .platforms.ros2.tracer import ROS2Tracer  # Use ROS2 for Gazebo
    return ROS2Tracer

# Safety imports
from .safety import (
    QuadrupedSafeFall,
    BipedSafeFall,
    SafetyResult
)

__all__ = [
    'BaseTracer',
    'WebSocketConnection',
    'authenticate',
    'QuadrupedSafeFall',
    'BipedSafeFall',
    'SafetyResult',
    'get_isaac_sim_tracer',
    'get_isaac_lab_tracer',
    'get_ros2_tracer',
    'get_mujoco_tracer',
    'get_pybullet_tracer',
    'get_gazebo_tracer',
]

# Prediction imports - optional
try:
    from .prediction import FallPredictor
except ImportError:
    FallPredictor = None

__all__ = [
    # Core
    "BaseTracer",
    "WebSocketConnection",
    "authenticate",
    # Platform getters
    "get_isaac_sim_tracer",
    "get_isaac_lab_tracer",
    "get_ros2_tracer",
    "get_mujoco_tracer",
    "get_pybullet_tracer",
    "get_gazebo_tracer",
    # Safety
    "QuadrupedSafeFall",
    "BipedSafeFall",
    "SafetyResult",
]

if FallPredictor:
    __all__.append("FallPredictor")
