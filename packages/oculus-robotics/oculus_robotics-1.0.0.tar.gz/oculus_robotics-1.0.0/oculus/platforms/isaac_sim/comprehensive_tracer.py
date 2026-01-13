"""
Comprehensive Isaac Sim Tracer
Captures EVERY aspect of Isaac Sim for full observability
"""

import carb
import omni
from omni.isaac.core import World
from omni.isaac.core.utils.physics import simulate_async
import numpy as np
from typing import Dict, List, Optional, Any
import time
import json

from oculus.core.tracer import BaseTracer


class ComprehensiveIsaacSimTracer(BaseTracer):
    """
    Full observability tracer for Isaac Sim
    Captures: Physics, Contacts, Environment, Controllers, Events, Metrics
    """
    
    def __init__(self, project: str = "isaac_sim_project", auto_capture: bool = True):
        super().__init__(project=project, auto_capture=auto_capture)
        
        # Physics data storage
        self.physics_traces = []
        self.contact_traces = []
        self.controller_traces = []
        self.event_traces = []
        
        # World reference
        self.world: Optional[World] = None
        
        # Tracking state
        self.run_config = {}
        self.environment_config = {}
        self.robots = {}
        
        # Event detection
        self.last_contact_state = {}
        self.stability_history = []
        
        # Safety thresholds
        self.fall_threshold = 0.3  # meters
        self.slip_velocity_threshold = 0.1  # m/s
        self.torque_saturation_threshold = 0.95  # 95% of max
        
    def initialize_world(self, world: World):
        """Initialize with Isaac Sim world"""
        self.world = world
        self._capture_environment_config()
        
    def _capture_environment_config(self):
        """Capture complete environment configuration"""
        if not self.world:
            return
            
        self.environment_config = {
            "physics_dt": self.world.get_physics_dt(),
            "rendering_dt": self.world.get_rendering_dt(),
            "gravity": self._get_gravity(),
            "solver_type": self._get_solver_config(),
            "scene_objects": self._get_scene_objects(),
            "ground_plane": self._get_ground_config(),
        }
        
        # Send to backend
        self.log_event("environment_configured", self.environment_config)
        
    def register_robot(self, name: str, robot_prim, controller=None):
        """Register a robot for tracking"""
        self.robots[name] = {
            "prim": robot_prim,
            "controller": controller,
            "joints": self._get_robot_joints(robot_prim),
            "contact_sensors": self._get_contact_sensors(robot_prim),
            "mass_properties": self._get_mass_properties(robot_prim),
        }
        
        self.log_event("robot_registered", {
            "robot": name,
            "num_joints": len(self.robots[name]["joints"]),
            "total_mass": self.robots[name]["mass_properties"]["total_mass"]
        })
        
    def capture_comprehensive_state(self, step: int):
        """
        Capture EVERYTHING about the current simulation state
        This is called every step when auto_capture=True
        """
        
        timestamp = time.time()
        
        # 1. PHYSICS STATE (Base tracking)
        physics_state = self._capture_physics_state()
        
        # 2. CONTACT DYNAMICS
        contact_state = self._capture_contact_dynamics()
        
        # 3. CONTROLLER STATE
        controller_state = self._capture_controller_state()
        
        # 4. DERIVED METRICS
        safety_metrics = self._compute_safety_metrics(physics_state, contact_state)
        
        # 5. EVENT DETECTION
        events = self._detect_events(physics_state, contact_state, safety_metrics)
        
        # 6. PREDICTIVE ANALYSIS
        risk_assessment = self._assess_fall_risk(physics_state, contact_state, safety_metrics)
        
        # Combine into comprehensive trace
        comprehensive_trace = {
            "step": step,
            "timestamp": timestamp,
            "physics": physics_state,
            "contacts": contact_state,
            "controller": controller_state,
            "safety_metrics": safety_metrics,
            "events": events,
            "risk_assessment": risk_assessment,
        }
        
        # Send to platform
        self.trace(comprehensive_trace)
        
        # Store for analysis
        self.physics_traces.append(physics_state)
        self.contact_traces.append(contact_state)
        
        if events:
            self.event_traces.extend(events)
            
        return comprehensive_trace
        
    def _capture_physics_state(self) -> Dict:
        """Capture raw physics data for all robots"""
        states = {}
        
        for robot_name, robot_data in self.robots.items():
            prim = robot_data["prim"]
            
            # Base state
            position, orientation = self._get_world_pose(prim)
            linear_velocity = self._get_linear_velocity(prim)
            angular_velocity = self._get_angular_velocity(prim)
            
            # Joint state
            joint_positions = self._get_joint_positions(robot_data["joints"])
            joint_velocities = self._get_joint_velocities(robot_data["joints"])
            joint_torques = self._get_joint_torques(robot_data["joints"])
            
            # Center of Mass
            com_position = self._compute_com_position(prim, robot_data["mass_properties"])
            com_velocity = self._compute_com_velocity(linear_velocity, angular_velocity)
            
            states[robot_name] = {
                "base": {
                    "position": position.tolist(),
                    "orientation": orientation.tolist(),
                    "linear_velocity": linear_velocity.tolist(),
                    "angular_velocity": angular_velocity.tolist(),
                    "height": position[2],  # Z height
                },
                "joints": {
                    "positions": joint_positions,
                    "velocities": joint_velocities,
                    "torques": joint_torques,
                    "effort_percentage": self._compute_effort_percentage(joint_torques, robot_data["joints"]),
                },
                "com": {
                    "position": com_position.tolist(),
                    "velocity": com_velocity.tolist(),
                },
            }
            
        return states
        
    def _capture_contact_dynamics(self) -> Dict:
        """Capture contact forces, friction, impacts"""
        contacts = {}
        
        for robot_name, robot_data in self.robots.items():
            contact_sensors = robot_data["contact_sensors"]
            
            robot_contacts = []
            for sensor in contact_sensors:
                contact_info = self._read_contact_sensor(sensor)
                if contact_info["in_contact"]:
                    robot_contacts.append({
                        "sensor": sensor["name"],
                        "location": sensor["location"],
                        "force": contact_info["force"],
                        "normal": contact_info["normal"],
                        "friction": contact_info["friction"],
                        "impulse": contact_info["impulse"],
                        "penetration": contact_info["penetration"],
                    })
                    
            contacts[robot_name] = {
                "active_contacts": len(robot_contacts),
                "contacts": robot_contacts,
                "total_force": sum(c["force"] for c in robot_contacts),
            }
            
        return contacts
        
    def _capture_controller_state(self) -> Dict:
        """Capture controller commands and outputs"""
        controller_states = {}
        
        for robot_name, robot_data in self.robots.items():
            controller = robot_data.get("controller")
            if controller:
                controller_states[robot_name] = {
                    "type": controller.__class__.__name__,
                    "target_positions": getattr(controller, "target_positions", None),
                    "target_velocities": getattr(controller, "target_velocities", None),
                    "commanded_torques": getattr(controller, "commanded_torques", None),
                    "control_mode": getattr(controller, "control_mode", "unknown"),
                    "gains": {
                        "kp": getattr(controller, "kp", None),
                        "kd": getattr(controller, "kd", None),
                    },
                }
                
        return controller_states
        
    def _compute_safety_metrics(self, physics_state: Dict, contact_state: Dict) -> Dict:
        """
        Compute derived safety metrics (PRIME feature #4)
        - Stability margin
        - Zero-Moment Point (ZMP)
        - Capture point distance
        - Time-to-fall estimate
        - Control effort risk
        - Recovery feasibility
        """
        metrics = {}
        
        for robot_name in self.robots.keys():
            if robot_name not in physics_state:
                continue
                
            robot_physics = physics_state[robot_name]
            robot_contacts = contact_state.get(robot_name, {})
            
            # Stability Margin
            stability_margin = self._compute_stability_margin(
                robot_physics["com"]["position"],
                robot_contacts
            )
            
            # ZMP calculation
            zmp_position, zmp_deviation = self._compute_zmp(
                robot_physics["com"],
                robot_contacts,
                self.environment_config.get("gravity", [0, 0, -9.81])
            )
            
            # Capture point
            capture_point = self._compute_capture_point(
                robot_physics["com"]["position"],
                robot_physics["com"]["velocity"]
            )
            
            # Time to fall estimate
            time_to_fall = self._estimate_time_to_fall(
                robot_physics["base"]["height"],
                robot_physics["base"]["linear_velocity"][2],
                stability_margin
            )
            
            # Control effort risk (torque saturation)
            control_effort_risk = max(robot_physics["joints"]["effort_percentage"])
            
            # Recovery feasibility
            recovery_feasible = self._assess_recovery_feasibility(
                stability_margin,
                robot_physics["joints"]["effort_percentage"],
                robot_contacts["active_contacts"]
            )
            
            metrics[robot_name] = {
                "stability_margin": stability_margin,
                "zmp": {
                    "position": zmp_position,
                    "deviation": zmp_deviation,
                },
                "capture_point": capture_point,
                "time_to_fall": time_to_fall,
                "control_effort_risk": control_effort_risk,
                "recovery_feasibility": recovery_feasible,
                "overall_safety_score": self._compute_safety_score(
                    stability_margin, zmp_deviation, control_effort_risk, recovery_feasible
                ),
            }
            
        return metrics
        
    def _detect_events(self, physics_state: Dict, contact_state: Dict, safety_metrics: Dict) -> List[Dict]:
        """
        Detect semantic events (PRIME feature #3)
        - Contact loss
        - Foot slippage
        - Torque saturation
        - Support polygon violation
        - COM instability
        - Fall initiation
        - Recovery attempt
        """
        events = []
        
        for robot_name in self.robots.keys():
            if robot_name not in physics_state:
                continue
                
            # Contact loss detection
            current_contacts = contact_state.get(robot_name, {}).get("active_contacts", 0)
            previous_contacts = self.last_contact_state.get(robot_name, current_contacts)
            
            if current_contacts < previous_contacts:
                events.append({
                    "type": "contact_loss",
                    "robot": robot_name,
                    "severity": "high" if current_contacts == 0 else "medium",
                    "data": {
                        "previous_contacts": previous_contacts,
                        "current_contacts": current_contacts,
                    }
                })
                
            # Foot slippage detection
            for contact in contact_state.get(robot_name, {}).get("contacts", []):
                if abs(contact.get("friction", 0)) > self.slip_velocity_threshold:
                    events.append({
                        "type": "foot_slippage",
                        "robot": robot_name,
                        "severity": "medium",
                        "data": {
                            "sensor": contact["sensor"],
                            "slip_velocity": contact["friction"],
                        }
                    })
                    
            # Torque saturation
            effort = physics_state[robot_name]["joints"]["effort_percentage"]
            if max(effort) > self.torque_saturation_threshold:
                events.append({
                    "type": "torque_saturation",
                    "robot": robot_name,
                    "severity": "high",
                    "data": {
                        "max_effort": max(effort),
                        "saturated_joints": [i for i, e in enumerate(effort) if e > self.torque_saturation_threshold]
                    }
                })
                
            # Fall initiation detection
            height = physics_state[robot_name]["base"]["height"]
            velocity_z = physics_state[robot_name]["base"]["linear_velocity"][2]
            
            if height < self.fall_threshold and velocity_z < -0.5:
                events.append({
                    "type": "fall_initiated",
                    "robot": robot_name,
                    "severity": "critical",
                    "data": {
                        "height": height,
                        "velocity": velocity_z,
                        "stability_margin": safety_metrics[robot_name]["stability_margin"]
                    }
                })
                
            # COM instability
            stability_margin = safety_metrics[robot_name]["stability_margin"]
            if stability_margin < 0.05:  # Very unstable
                events.append({
                    "type": "com_instability",
                    "robot": robot_name,
                    "severity": "high",
                    "data": {
                        "stability_margin": stability_margin,
                        "com_position": physics_state[robot_name]["com"]["position"]
                    }
                })
                
            # Update last contact state
            self.last_contact_state[robot_name] = current_contacts
            
        return events
        
    def _assess_fall_risk(self, physics_state: Dict, contact_state: Dict, safety_metrics: Dict) -> Dict:
        """
        Predictive fall risk detection (PRIME feature #5)
        Predict fall probability before impact
        """
        risk_assessment = {}
        
        for robot_name in self.robots.keys():
            if robot_name not in physics_state:
                continue
                
            # Gather risk factors
            stability = safety_metrics[robot_name]["stability_margin"]
            zmp_deviation = safety_metrics[robot_name]["zmp"]["deviation"]
            control_effort = safety_metrics[robot_name]["control_effort_risk"]
            time_to_fall = safety_metrics[robot_name]["time_to_fall"]
            active_contacts = contact_state.get(robot_name, {}).get("active_contacts", 0)
            
            # Risk scoring (0-1)
            risk_factors = {
                "stability_risk": 1.0 - min(stability / 0.1, 1.0),  # Lower stability = higher risk
                "zmp_risk": min(zmp_deviation / 0.1, 1.0),  # Higher deviation = higher risk
                "control_risk": control_effort,  # Direct mapping
                "contact_risk": 1.0 - (active_contacts / 4.0),  # Fewer contacts = higher risk
                "velocity_risk": min(abs(physics_state[robot_name]["base"]["angular_velocity"][0]) / 1.0, 1.0),
            }
            
            # Weighted risk score
            overall_risk = (
                risk_factors["stability_risk"] * 0.3 +
                risk_factors["zmp_risk"] * 0.25 +
                risk_factors["control_risk"] * 0.2 +
                risk_factors["contact_risk"] * 0.15 +
                risk_factors["velocity_risk"] * 0.1
            )
            
            # Risk level
            if overall_risk < 0.3:
                risk_level = "low"
            elif overall_risk < 0.6:
                risk_level = "medium"
            else:
                risk_level = "high"
                
            risk_assessment[robot_name] = {
                "overall_risk": overall_risk,
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "time_to_fall_estimate": time_to_fall,
                "confidence": self._compute_prediction_confidence(risk_factors),
            }
            
        return risk_assessment
        
    def _compute_safety_score(self, stability: float, zmp_dev: float, effort: float, recoverable: bool) -> float:
        """Compute overall safety score (0-100)"""
        score = 100.0
        
        # Penalties
        score -= (1.0 - min(stability / 0.1, 1.0)) * 30  # Stability weight: 30%
        score -= min(zmp_dev / 0.1, 1.0) * 25  # ZMP weight: 25%
        score -= effort * 20  # Effort weight: 20%
        score -= (0 if recoverable else 25)  # Recoverability: 25%
        
        return max(0.0, score)
        
    # Helper methods for physics calculations
    
    def _get_world_pose(self, prim):
        """Get world position and orientation"""
        # Implementation depends on Isaac Sim API
        return np.array([0, 0, 1]), np.array([0, 0, 0, 1])
        
    def _get_linear_velocity(self, prim):
        return np.array([0, 0, 0])
        
    def _get_angular_velocity(self, prim):
        return np.array([0, 0, 0])
        
    def _get_joint_positions(self, joints):
        return [0.0] * len(joints)
        
    def _get_joint_velocities(self, joints):
        return [0.0] * len(joints)
        
    def _get_joint_torques(self, joints):
        return [0.0] * len(joints)
        
    def _compute_effort_percentage(self, torques, joints):
        """Compute effort as percentage of max torque"""
        return [abs(t) / joint.get("max_torque", 100.0) for t, joint in zip(torques, joints)]
        
    def _compute_com_position(self, prim, mass_props):
        """Compute center of mass position"""
        return np.array([0, 0, 0.5])
        
    def _compute_com_velocity(self, linear_vel, angular_vel):
        return linear_vel
        
    def _get_gravity(self):
        return [0, 0, -9.81]
        
    def _get_solver_config(self):
        return {"type": "TGS", "iterations": 4}
        
    def _get_scene_objects(self):
        return []
        
    def _get_ground_config(self):
        return {"friction": 0.5, "restitution": 0.0}
        
    def _get_robot_joints(self, prim):
        return []
        
    def _get_contact_sensors(self, prim):
        return []
        
    def _get_mass_properties(self, prim):
        return {"total_mass": 50.0}
        
    def _read_contact_sensor(self, sensor):
        return {"in_contact": False, "force": 0, "normal": [0, 0, 1], "friction": 0, "impulse": 0, "penetration": 0}
        
    def _compute_stability_margin(self, com_pos, contacts):
        """Distance from COM projection to support polygon edge"""
        return 0.1
        
    def _compute_zmp(self, com, contacts, gravity):
        """Zero-Moment Point calculation"""
        return [0, 0, 0], 0.01
        
    def _compute_capture_point(self, com_pos, com_vel):
        """Capture point for walking robots"""
        return [0, 0, 0]
        
    def _estimate_time_to_fall(self, height, velocity_z, stability):
        """Estimate time until robot falls"""
        if velocity_z >= 0:
            return float('inf')
        return max(0.0, height / abs(velocity_z))
        
    def _assess_recovery_feasibility(self, stability, effort, contacts):
        """Can the robot recover from current state?"""
        return stability > 0.05 and max(effort) < 0.8 and contacts > 0
        
    def _compute_prediction_confidence(self, risk_factors):
        """Confidence in fall prediction"""
        variance = np.var(list(risk_factors.values()))
        return 1.0 - min(variance, 1.0)
