"""
Safety algorithms for preventing robot falls and instability.
"""

import math
import numpy as np
from typing import Dict, List, Optional, Tuple


class SafetyResult:
    """Result from a safety check."""

    def __init__(self, risk_score: float, intervention_needed: bool,
                 recommended_action: Optional[Dict] = None, reason: str = ""):
        self.risk_score = risk_score  # 0.0 to 1.0
        self.intervention_needed = intervention_needed
        self.recommended_action = recommended_action or {}
        self.reason = reason

    def __repr__(self):
        return f"SafetyResult(risk={self.risk_score:.2f}, intervention={self.intervention_needed})"


class QuadrupedSafeFall:
    """
    Safety system for quadruped robots (4-legged).
    Monitors stability and prevents falls.
    """

    def __init__(self, robot_type: str = "generic", risk_threshold: float = 0.7):
        """
        Initialize quadruped safety system.

        Args:
            robot_type: Type of robot (generic, unitree_go1, anymal, etc.)
            risk_threshold: Risk score threshold for intervention (0.0-1.0)
        """
        self.robot_type = robot_type
        self.risk_threshold = risk_threshold
        self.history = []

    def check_fall_risk(self, state: Dict) -> SafetyResult:
        """
        Check if robot is at risk of falling.

        Args:
            state: Dictionary with robot state:
                - position: [x, y, z]
                - orientation: [roll, pitch, yaw] in radians
                - velocity: [vx, vy, vz]
                - joint_positions: list of joint angles

        Returns:
            SafetyResult with risk assessment
        """
        risk_score = 0.0
        reasons = []

        # Extract state
        position = state.get("position", [0, 0, 0])
        orientation = state.get("orientation", [0, 0, 0])
        velocity = state.get("velocity", [0, 0, 0])

        # Check 1: Tilt angle (roll/pitch)
        roll, pitch, yaw = orientation[0], orientation[1], orientation[2]
        max_tilt = max(abs(roll), abs(pitch))

        if max_tilt > 0.5:  # 28.6 degrees
            tilt_risk = min(max_tilt / 0.785, 1.0)  # Normalize to 45 deg
            risk_score = max(risk_score, tilt_risk)
            reasons.append(f"High tilt angle: {math.degrees(max_tilt):.1f}°")

        # Check 2: Height (falling detection)
        height = position[2] if len(position) > 2 else 0
        if height < 0.2:  # Below normal standing height
            height_risk = 1.0 - (height / 0.2)
            risk_score = max(risk_score, height_risk)
            reasons.append(f"Low height: {height:.2f}m")

        # Check 3: Velocity (sudden movements)
        vel_magnitude = math.sqrt(sum(v**2 for v in velocity))
        if vel_magnitude > 3.0:  # Fast movement
            vel_risk = min(vel_magnitude / 5.0, 1.0)
            risk_score = max(risk_score, vel_risk * 0.5)  # Lower weight
            reasons.append(f"High velocity: {vel_magnitude:.2f}m/s")

        # Store history
        self.history.append({
            "risk_score": risk_score,
            "state": state
        })
        if len(self.history) > 100:
            self.history.pop(0)

        # Generate intervention if needed
        intervention_needed = risk_score >= self.risk_threshold
        recommended_action = None

        if intervention_needed:
            # Recommend stabilization action
            recommended_action = {
                "type": "stabilize",
                "reduce_speed": 0.5,
                "lower_center_of_mass": True,
                "adjust_stance": True
            }

        return SafetyResult(
            risk_score=risk_score,
            intervention_needed=intervention_needed,
            recommended_action=recommended_action,
            reason="; ".join(reasons) if reasons else "Normal operation"
        )

    def prevent_fall(self, robot_state: Dict, prediction: SafetyResult) -> Dict:
        """
        Generate corrective action to prevent fall.

        Args:
            robot_state: Current robot state
            prediction: Safety prediction result

        Returns:
            Dictionary with corrective actions
        """
        if not prediction.intervention_needed:
            return {"action": "none"}

        # Generate stabilization commands
        correction = {
            "action": "stabilize",
            "joint_corrections": self._calculate_joint_corrections(robot_state),
            "velocity_limit": 0.5,  # Reduce speed
            "stance_adjustment": True
        }

        return correction

    def _calculate_joint_corrections(self, state: Dict) -> List[float]:
        """Calculate joint angle corrections for stability."""
        # Simplified: In real implementation, this would use IK/dynamics
        orientation = state.get("orientation", [0, 0, 0])
        roll, pitch = orientation[0], orientation[1]

        # Simple proportional correction
        corrections = [
            -roll * 0.5,   # Hip joint 1
            -pitch * 0.5,  # Hip joint 2
            roll * 0.3,    # Knee joint 1
            pitch * 0.3,   # Knee joint 2
        ]

        return corrections


class UnitreeSafeFall(QuadrupedSafeFall):
    """
    Specialized safety system for Unitree robots (Go1, A1, etc.).
    Tuned for Unitree-specific dynamics.
    """

    def __init__(self, robot_model: str = "go1", risk_threshold: float = 0.7):
        """
        Initialize Unitree-specific safety.

        Args:
            robot_model: Unitree model (go1, a1, go2)
            risk_threshold: Risk threshold for intervention
        """
        super().__init__(robot_type=f"unitree_{robot_model}", risk_threshold=risk_threshold)
        self.robot_model = robot_model

        # Unitree-specific parameters
        self.standing_height = {
            "go1": 0.28,
            "a1": 0.30,
            "go2": 0.32
        }.get(robot_model, 0.28)

    def check_fall_risk(self, state: Dict) -> SafetyResult:
        """Unitree-specific fall risk assessment."""
        result = super().check_fall_risk(state)

        # Additional Unitree-specific checks
        height = state.get("position", [0, 0, 0])[2] if "position" in state else 0

        if height < self.standing_height * 0.7:
            result.risk_score = max(result.risk_score, 0.8)
            result.intervention_needed = True
            result.reason += f" | Below Unitree safe height ({self.standing_height}m)"

        return result


class BipedSafeFall:
    """
    Safety system for biped (humanoid) robots.
    Monitors balance and center of mass.
    """

    def __init__(self, robot_type: str = "generic", risk_threshold: float = 0.75):
        """
        Initialize biped safety system.

        Args:
            robot_type: Type of biped robot
            risk_threshold: Risk threshold for intervention
        """
        self.robot_type = robot_type
        self.risk_threshold = risk_threshold
        self.history = []

    def check_balance(self, state: Dict) -> SafetyResult:
        """
        Check biped balance and fall risk.

        Args:
            state: Robot state with position, orientation, center_of_mass

        Returns:
            SafetyResult with balance assessment
        """
        risk_score = 0.0
        reasons = []

        position = state.get("position", [0, 0, 0])
        orientation = state.get("orientation", [0, 0, 0])
        com = state.get("center_of_mass", position)  # Center of mass

        # Check 1: Tilt (more sensitive for bipeds)
        roll, pitch = orientation[0], orientation[1]
        max_tilt = max(abs(roll), abs(pitch))

        if max_tilt > 0.3:  # 17 degrees (bipeds less stable)
            tilt_risk = min(max_tilt / 0.5, 1.0)
            risk_score = max(risk_score, tilt_risk)
            reasons.append(f"Excessive tilt: {math.degrees(max_tilt):.1f}°")

        # Check 2: Center of mass over support polygon
        # Simplified: check if COM is centered over position
        com_offset = math.sqrt((com[0] - position[0])**2 + (com[1] - position[1])**2)

        if com_offset > 0.15:  # COM too far from base
            com_risk = min(com_offset / 0.3, 1.0)
            risk_score = max(risk_score, com_risk)
            reasons.append(f"COM offset: {com_offset:.2f}m")

        intervention_needed = risk_score >= self.risk_threshold

        return SafetyResult(
            risk_score=risk_score,
            intervention_needed=intervention_needed,
            reason="; ".join(reasons) if reasons else "Balanced"
        )
