"""
PyBullet Platform Adapter

Integrates Oculus tracing with PyBullet physics simulator.
"""

import time
from typing import Optional
from ...core.tracer import BaseTracer
from ...core.state import UniversalState
from ...core.config import OculusConfig


class PyBulletTracer(BaseTracer):
    """Tracer for PyBullet simulator"""
    
    def __init__(self, api_key: str, project_name: str, server_url: str = "ws://localhost:8080",
                 robot_id: int = None, **kwargs):
        config = OculusConfig(
            api_key=api_key,
            project_name=project_name,
            websocket_url=server_url,
            framework="pybullet",
            robot_type=kwargs.get('robot_type', 'custom')
        )
        super().__init__(config)
        self.robot_id = robot_id
        self.physics_client = kwargs.get('physics_client', None)
        
    def capture_state(self, step: int = None, robot_id: int = None) -> UniversalState:
        """Capture state from PyBullet"""
        import pybullet as p
        
        if robot_id is None:
            robot_id = self.robot_id
            
        if robot_id is None:
            raise ValueError("Robot ID not provided")
        
        if step is None:
            step = self.step_count
        
        try:
            # Get base state
            base_pos, base_orn = p.getBasePositionAndOrientation(robot_id)
            base_lin_vel, base_ang_vel = p.getBaseVelocity(robot_id)
            
            # Get number of joints
            num_joints = p.getNumJoints(robot_id)
            
            # Get joint states
            joint_positions = []
            joint_velocities = []
            joint_torques = []
            
            for joint_idx in range(num_joints):
                joint_state = p.getJointState(robot_id, joint_idx)
                joint_positions.append(joint_state[0])  # position
                joint_velocities.append(joint_state[1])  # velocity
                joint_torques.append(joint_state[3])     # applied torque
            
            # Get contact information
            contact_forces = []
            contact_points = []
            
            contact_data = p.getContactPoints(bodyA=robot_id)
            for contact in contact_data:
                contact_force = contact[9]  # normal force
                contact_pos = contact[6]     # position on B
                # Store as 3D force vector (simplified)
                normal = contact[7]
                force_vec = tuple(n * contact_force for n in normal)
                contact_forces.append(force_vec)
                contact_points.append(contact_pos)
            
            state = UniversalState(
                step=step,
                timestamp=time.time(),
                joint_positions=joint_positions,
                joint_velocities=joint_velocities,
                joint_torques=joint_torques,
                base_position=tuple(base_pos),
                base_orientation=tuple(base_orn),
                base_linear_vel=tuple(base_lin_vel),
                base_angular_vel=tuple(base_ang_vel),
                contact_forces=contact_forces if contact_forces else None,
                contact_points=contact_points if contact_points else None
            )
            
            # Trace the step
            self.trace_step(state)
            
            return state
            
        except Exception as e:
            print(f"⚠️ Failed to capture PyBullet state: {e}")
            return UniversalState(
                step=step,
                timestamp=time.time(),
                joint_positions=[],
                joint_velocities=[],
                joint_torques=[],
                base_position=(0.0, 0.0, 0.0),
                base_orientation=(0.0, 0.0, 0.0, 1.0),
                base_linear_vel=(0.0, 0.0, 0.0),
                base_angular_vel=(0.0, 0.0, 0.0)
            )


__all__ = ["PyBulletTracer"]
