"""
Prediction and prevention algorithms for robotics safety.
"""

import math
import numpy as np
from typing import Dict, List, Optional, Tuple


class PredictionResult:
    """Result from a prediction algorithm."""

    def __init__(self, risk_score: float, time_to_event: float,
                 event_type: str, confidence: float):
        self.risk_score = risk_score  # 0.0 to 1.0
        self.time_to_event = time_to_event  # seconds
        self.event_type = event_type  # "fall", "collision", "instability"
        self.confidence = confidence  # 0.0 to 1.0

    def __repr__(self):
        return f"Prediction(risk={self.risk_score:.2f}, type={self.event_type}, t={self.time_to_event:.2f}s)"


class FallPredictor:
    """
    Predicts robot falls before they happen.
    Uses motion history and dynamics to forecast instability.
    """

    def __init__(self, model: str = "basic", prediction_horizon: float = 1.0):
        """
        Initialize fall predictor.

        Args:
            model: Prediction model (basic, advanced, ml)
            prediction_horizon: How far ahead to predict (seconds)
        """
        self.model = model
        self.prediction_horizon = prediction_horizon
        self.state_history = []

    def predict_fall(self, current_state: Dict) -> PredictionResult:
        """
        Predict if robot will fall in near future.

        Args:
            current_state: Current robot state dict

        Returns:
            PredictionResult with fall prediction
        """
        # Add to history
        self.state_history.append(current_state)
        if len(self.state_history) > 50:
            self.state_history.pop(0)

        # Need at least 5 states for prediction
        if len(self.state_history) < 5:
            return PredictionResult(
                risk_score=0.0,
                time_to_event=float('inf'),
                event_type="fall",
                confidence=0.0
            )

        # Calculate motion trends
        recent_states = self.state_history[-10:]

        # Extract orientations
        orientations = [s.get("orientation", [0, 0, 0]) for s in recent_states]

        # Calculate tilt rate (derivative)
        tilt_values = [max(abs(o[0]), abs(o[1])) for o in orientations]
        tilt_rate = (tilt_values[-1] - tilt_values[0]) / len(tilt_values)

        # Calculate height trend
        heights = [s.get("position", [0, 0, 0])[2] if "position" in s else 0
                   for s in recent_states]
        height_rate = (heights[-1] - heights[0]) / len(heights)

        # Predict risk
        risk_score = 0.0
        time_to_fall = float('inf')

        # If tilting rapidly
        if tilt_rate > 0.05:  # Radians per step
            risk_score = min(tilt_rate / 0.1, 1.0)
            # Estimate time to critical tilt (0.785 rad = 45 deg)
            current_tilt = tilt_values[-1]
            if tilt_rate > 0:
                time_to_fall = (0.785 - current_tilt) / (tilt_rate * 100)  # Rough estimate

        # If dropping rapidly
        if height_rate < -0.01:
            height_risk = min(abs(height_rate) / 0.02, 1.0)
            risk_score = max(risk_score, height_risk)
            time_to_fall = min(time_to_fall, abs(heights[-1] / height_rate) * 0.01)

        # Calculate confidence based on history length
        confidence = min(len(self.state_history) / 20.0, 1.0)

        return PredictionResult(
            risk_score=risk_score,
            time_to_event=max(time_to_fall, 0.1),
            event_type="fall",
            confidence=confidence
        )


class CollisionAvoider:
    """
    Predicts and prevents collisions with obstacles.
    """

    def __init__(self, safety_margin: float = 0.5):
        """
        Initialize collision avoider.

        Args:
            safety_margin: Minimum safe distance to obstacles (meters)
        """
        self.safety_margin = safety_margin
        self.obstacle_map = []

    def predict_collision(self, robot_state: Dict, obstacles: Optional[List[Dict]] = None) -> float:
        """
        Predict collision risk.

        Args:
            robot_state: Current robot position/velocity
            obstacles: List of obstacle positions

        Returns:
            Collision risk score (0.0 to 1.0)
        """
        if obstacles is None or len(obstacles) == 0:
            return 0.0

        position = robot_state.get("position", [0, 0, 0])
        velocity = robot_state.get("velocity", [0, 0, 0])

        # Calculate future position (1 second ahead)
        future_pos = [
            position[0] + velocity[0],
            position[1] + velocity[1],
            position[2] + velocity[2]
        ]

        # Find closest obstacle
        min_distance = float('inf')
        for obstacle in obstacles:
            obs_pos = obstacle.get("position", [0, 0, 0])
            distance = math.sqrt(
                (future_pos[0] - obs_pos[0])**2 +
                (future_pos[1] - obs_pos[1])**2 +
                (future_pos[2] - obs_pos[2])**2
            )
            min_distance = min(min_distance, distance)

        # Calculate risk based on distance
        if min_distance < self.safety_margin:
            risk = 1.0 - (min_distance / self.safety_margin)
            return risk

        return 0.0

    def generate_safe_path(self, robot_state: Dict, goal: Optional[Dict] = None) -> Dict:
        """
        Generate collision-free path.

        Args:
            robot_state: Current state
            goal: Target position

        Returns:
            Safe action/path
        """
        # Simplified: just stop if collision imminent
        return {
            "action": "slow_down",
            "velocity_scale": 0.3,
            "direction_adjust": 0.0  # Could add steering logic
        }


class StabilityController:
    """
    Maintains robot stability through active control.
    """

    def __init__(self, control_gains: Optional[Dict] = None):
        """
        Initialize stability controller.

        Args:
            control_gains: PID gains for stability control
        """
        self.gains = control_gains or {
            "kp": 1.0,  # Proportional
            "ki": 0.1,  # Integral
            "kd": 0.5   # Derivative
        }
        self.error_integral = 0.0
        self.last_error = 0.0

    def compute_stabilization(self, current_state: Dict, desired_state: Dict) -> Dict:
        """
        Compute control actions for stability.

        Args:
            current_state: Current robot state
            desired_state: Desired stable state

        Returns:
            Control actions
        """
        # Calculate orientation error
        current_ori = current_state.get("orientation", [0, 0, 0])
        desired_ori = desired_state.get("orientation", [0, 0, 0])

        error = [
            desired_ori[0] - current_ori[0],
            desired_ori[1] - current_ori[1],
            desired_ori[2] - current_ori[2]
        ]

        # PID control
        self.error_integral += error[0] + error[1]
        error_derivative = (error[0] + error[1]) - self.last_error
        self.last_error = error[0] + error[1]

        # Calculate control signal
        control = (
            self.gains["kp"] * (error[0] + error[1]) +
            self.gains["ki"] * self.error_integral +
            self.gains["kd"] * error_derivative
        )

        return {
            "torque_correction": control,
            "joint_adjustments": error,
            "stability_score": 1.0 - min(abs(control), 1.0)
        }
