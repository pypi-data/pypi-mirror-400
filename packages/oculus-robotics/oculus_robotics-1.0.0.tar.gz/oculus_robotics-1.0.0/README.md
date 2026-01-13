# Oculus SDK - Research & Implementation

Modular, scalable SDK for robotics observability and safety.

## Installation

```bash
# Basic (all platforms)
pip install oculus-robotics

# With platform-specific extras
pip install oculus-robotics[isaac-lab]
pip install oculus-robotics[ros2]
pip install oculus-robotics[mujoco]
```

## Quick Start

```python
from oculus.platforms.isaac_lab import IsaacLabTracer

with IsaacLabTracer(project="my_simulation") as tracer:
    for step in range(1000):
        # Your simulation code
        state = get_robot_state()
        tracer.auto_capture(state)
```

## Development Setup

```bash
# Clone and install in dev mode
cd oculus-sdk
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## Package Structure

```
oculus/
├── core/              # Base tracer, connection, auth
├── platforms/         # Isaac Sim, Lab, ROS2, Mujoco, etc.
├── safety/            # Fall prevention, collision avoidance
├── prediction/        # Fall prediction, anomaly detection
└── research/          # Research paper implementations
```

## Platform-Specific Usage

### Isaac Sim
```python
from oculus.platforms.isaac_sim import IsaacSimTracer
```

### Isaac Lab
```python
from oculus.platforms.isaac_lab import IsaacLabTracer
```

### ROS 2
```python
from oculus.platforms.ros2 import ROS2Tracer
```

### Mujoco
```python
from oculus.platforms.mujoco import MujocoTracer
```

## Safety Algorithms

```python
from oculus.safety.fall_prevention import QuadrupedSafeFall
from oculus.prediction import FallPredictor

safety = QuadrupedSafeFall(robot_type="unitree_go1")
predictor = FallPredictor()

result = safety.check_fall_risk(robot_state)
if result.intervention_needed:
    correction = safety.prevent_fall(robot_state, result)
```

## Research Implementations

See `oculus/research/` for implementations of:
- Radium paper (Unitree safe fall)
- Custom algorithms from latest research

## Contributing

1. Study research paper
2. Implement in `oculus/research/new_algorithm/`
3. Test in `oculus-testing/`
4. Submit PR with paper reference

## Publishing

```bash
python -m build
twine upload dist/*
```
