"""
Test basic imports and package structure
"""

import pytest


def test_package_import():
    """Test that main package can be imported"""
    import oculus
    assert oculus.__version__ == "1.0.0"


def test_core_imports():
    """Test core module imports"""
    from oculus import BaseTracer, WebSocketConnection, authenticate
    assert BaseTracer is not None
    assert WebSocketConnection is not None
    assert authenticate is not None


def test_platform_getters():
    """Test platform tracer getters"""
    from oculus import (
        get_isaac_sim_tracer,
        get_isaac_lab_tracer,
        get_ros2_tracer,
        get_mujoco_tracer,
        get_pybullet_tracer,
        get_gazebo_tracer
    )
    assert get_isaac_sim_tracer is not None
    assert get_isaac_lab_tracer is not None
    assert get_ros2_tracer is not None
    assert get_mujoco_tracer is not None
    assert get_pybullet_tracer is not None
    assert get_gazebo_tracer is not None


def test_safety_imports():
    """Test safety module imports"""
    from oculus import QuadrupedSafeFall, BipedSafeFall, SafetyResult
    assert QuadrupedSafeFall is not None
    assert BipedSafeFall is not None
    assert SafetyResult is not None


def test_lazy_platform_loading():
    """Test that platforms can be loaded lazily"""
    from oculus import get_isaac_sim_tracer
    IsaacSimTracer = get_isaac_sim_tracer()
    assert IsaacSimTracer is not None


def test_all_exports():
    """Test that __all__ exports are valid"""
    import oculus
    for name in oculus.__all__:
        assert hasattr(oculus, name), f"Missing export: {name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
