"""
Comprehensive PyBullet Tracer
Captures physics simulation, rigid bodies, constraints, and debug info
"""

import numpy as np
import time
from typing import Dict, List, Optional
from oculus.core.tracer import BaseTracer

try:
    import pybullet as p
    PYBULLET_AVAILABLE = True
except ImportError:
    PYBULLET_AVAILABLE = False


class ComprehensivePyBulletTracer(BaseTracer):
    """
    Full PyBullet observability
    Captures: Bodies, joints, contacts, constraints, debug info
    """
    
    def __init__(self, project: str = "pybullet_project", auto_capture: bool = True):
        super().__init__(project=project, auto_capture=auto_capture)
        
        if not PYBULLET_AVAILABLE:
            raise ImportError("PyBullet not installed. Install with: pip install pybullet")
            
        self.physics_client = None
        self.robot_ids = []
        
    def initialize(self, physics_client_id: int = 0):
        """Initialize with PyBullet physics client"""
        self.physics_client = physics_client_id
        
        # Capture simulation parameters
        sim_params = {
            "gravity": p.getGravity(physicsClientId=self.physics_client),
            "timestep": p.getPhysicsEngineParameters(physicsClientId=self.physics_client).get('fixedTimeStep', 0.0),
            "num_bodies": p.getNumBodies(physicsClientId=self.physics_client),
        }
        
        self.log_event("pybullet_initialized", sim_params)
        
    def register_robot(self, robot_id: int):
        """Register a robot for tracking"""
        if robot_id not in self.robot_ids:
            self.robot_ids.append(robot_id)
            
            robot_info = {
                "robot_id": robot_id,
                "num_joints": p.getNumJoints(robot_id, physicsClientId=self.physics_client),
                "base_name": p.getBodyInfo(robot_id, physicsClientId=self.physics_client)[0].decode('utf-8'),
            }
            
            self.log_event("robot_registered", robot_info)
            
    def capture_state(self, step: int):
        """
        Capture comprehensive PyBullet state
        """
        if self.physics_client is None:
            return {}
            
        timestamp = time.time()
        
        # 1. ROBOT STATES
        robot_data = self._capture_robot_states()
        
        # 2. JOINT STATES
        joint_data = self._capture_joint_states()
        
        # 3. CONTACT POINTS
        contact_data = self._capture_contacts()
        
        # 4. CONSTRAINTS
        constraint_data = self._capture_constraints()
        
        # 5. DYNAMICS INFO
        dynamics_data = self._capture_dynamics()
        
        # 6. COLLISION INFO
        collision_data = self._capture_collisions()
        
        trace = {
            "step": step,
            "timestamp": timestamp,
            "robots": robot_data,
            "joints": joint_data,
            "contacts": contact_data,
            "constraints": constraint_data,
            "dynamics": dynamics_data,
            "collisions": collision_data,
        }
        
        self.trace(trace)
        return trace
        
    def _capture_robot_states(self) -> Dict:
        """Capture robot base states"""
        robots = {}
        
        for robot_id in self.robot_ids:
            pos, orn = p.getBasePositionAndOrientation(robot_id, physicsClientId=self.physics_client)
            lin_vel, ang_vel = p.getBaseVelocity(robot_id, physicsClientId=self.physics_client)
            
            robots[f"robot_{robot_id}"] = {
                "id": robot_id,
                "position": list(pos),
                "orientation": list(orn),
                "linear_velocity": list(lin_vel),
                "angular_velocity": list(ang_vel),
            }
            
        return robots
        
    def _capture_joint_states(self) -> Dict:
        """Capture joint states for all robots"""
        all_joints = {}
        
        for robot_id in self.robot_ids:
            num_joints = p.getNumJoints(robot_id, physicsClientId=self.physics_client)
            robot_joints = {}
            
            for i in range(num_joints):
                joint_info = p.getJointInfo(robot_id, i, physicsClientId=self.physics_client)
                joint_state = p.getJointState(robot_id, i, physicsClientId=self.physics_client)
                
                joint_name = joint_info[1].decode('utf-8')
                robot_joints[joint_name] = {
                    "position": float(joint_state[0]),
                    "velocity": float(joint_state[1]),
                    "reaction_forces": list(joint_state[2]),
                    "applied_torque": float(joint_state[3]),
                    "type": int(joint_info[2]),
                }
                
            all_joints[f"robot_{robot_id}"] = robot_joints
            
        return all_joints
        
    def _capture_contacts(self) -> Dict:
        """Capture contact points"""
        all_contacts = []
        
        for robot_id in self.robot_ids:
            contacts = p.getContactPoints(bodyA=robot_id, physicsClientId=self.physics_client)
            
            for contact in contacts:
                all_contacts.append({
                    "body_a": contact[1],
                    "body_b": contact[2],
                    "link_a": contact[3],
                    "link_b": contact[4],
                    "position_on_a": list(contact[5]),
                    "position_on_b": list(contact[6]),
                    "normal": list(contact[7]),
                    "distance": float(contact[8]),
                    "normal_force": float(contact[9]),
                    "friction1": float(contact[10]),
                    "friction2": float(contact[12]),
                })
                
        return {
            "count": len(all_contacts),
            "contacts": all_contacts[:50]  # Limit to 50 contacts
        }
        
    def _capture_constraints(self) -> Dict:
        """Capture user constraints"""
        num_constraints = p.getNumConstraints(physicsClientId=self.physics_client)
        
        constraints = []
        for i in range(num_constraints):
            constraint_info = p.getConstraintInfo(i, physicsClientId=self.physics_client)
            constraints.append({
                "id": i,
                "parent_body": constraint_info[2],
                "child_body": constraint_info[4],
                "type": constraint_info[6],
            })
            
        return {
            "count": num_constraints,
            "constraints": constraints
        }
        
    def _capture_dynamics(self) -> Dict:
        """Capture dynamics information"""
        dynamics = {}
        
        for robot_id in self.robot_ids:
            dynamics_info = p.getDynamicsInfo(robot_id, -1, physicsClientId=self.physics_client)
            
            dynamics[f"robot_{robot_id}"] = {
                "mass": float(dynamics_info[0]),
                "lateral_friction": float(dynamics_info[1]),
                "local_inertia_diagonal": list(dynamics_info[2]),
                "local_inertia_pos": list(dynamics_info[3]),
                "local_inertia_orn": list(dynamics_info[4]),
                "restitution": float(dynamics_info[5]),
                "rolling_friction": float(dynamics_info[6]),
                "spinning_friction": float(dynamics_info[7]),
            }
            
        return dynamics
        
    def _capture_collisions(self) -> Dict:
        """Capture collision information"""
        num_bodies = p.getNumBodies(physicsClientId=self.physics_client)
        
        return {
            "total_bodies": num_bodies,
            "tracked_robots": len(self.robot_ids),
        }
