"""
MuJoCo Platform Adapter

Integrates Oculus tracing with MuJoCo physics simulator.
"""

import numpy as np
import time
from typing import Optional
from ...core.tracer import BaseTracer
from ...core.state import UniversalState
from ...core.config import OculusConfig


class MujocoTracer(BaseTracer):
    """Tracer for MuJoCo simulator"""
    
    def __init__(self, api_key: str, project_name: str, server_url: str = "ws://localhost:8080", 
                 model=None, **kwargs):
        config = OculusConfig(
            api_key=api_key,
            project_name=project_name,
            websocket_url=server_url,
            framework="mujoco",
            robot_type=kwargs.get('robot_type', 'custom')
        )
        super().__init__(config)
        self.model = model
        self.data = None
        
    def set_data(self, data):
        """Set MuJoCo data object"""
        self.data = data
        
    def capture_state(self, data=None, step: int = None) -> UniversalState:
        """Capture state from MuJoCo data"""
        if data is None:
            data = self.data
            
        if data is None:
            raise ValueError("MuJoCo data not provided")
        
        if step is None:
            step = self.step_count
        
        try:
            # Get joint states (skip first 7 DOFs if they're free joint)
            nq = self.model.nq if self.model else data.qpos.shape[0]
            nv = self.model.nv if self.model else data.qvel.shape[0]
            
            # Check if model has a free joint (floating base)
            has_free_joint = nq >= 7
            
            if has_free_joint:
                # Extract base pose from free joint
                base_position = tuple(data.qpos[0:3].tolist())
                base_orientation = tuple(data.qpos[3:7].tolist())  # quaternion
                base_linear_vel = tuple(data.qvel[0:3].tolist())
                base_angular_vel = tuple(data.qvel[3:6].tolist())
                
                # Joint states start after free joint
                joint_positions = data.qpos[7:].tolist()
                joint_velocities = data.qvel[6:].tolist()
            else:
                # Fixed base robot
                base_position = (0.0, 0.0, 0.0)
                base_orientation = (0.0, 0.0, 0.0, 1.0)
                base_linear_vel = (0.0, 0.0, 0.0)
                base_angular_vel = (0.0, 0.0, 0.0)
                
                joint_positions = data.qpos.tolist()
                joint_velocities = data.qvel.tolist()
            
            # Get actuator forces/torques
            if hasattr(data, 'actuator_force'):
                joint_torques = data.actuator_force.tolist()
            elif hasattr(data, 'qfrc_actuator'):
                joint_torques = data.qfrc_actuator[6 if has_free_joint else 0:].tolist()
            else:
                joint_torques = [0.0] * len(joint_positions)
            
            # Get contact forces
            contact_forces = []
            contact_points = []
            if hasattr(data, 'contact'):
                for i in range(data.ncon):
                    contact = data.contact[i]
                    # Get contact force
                    force = np.zeros(6)
                    import mujoco
                    mujoco.mj_contactForce(self.model, data, i, force)
                    contact_forces.append(tuple(force[0:3].tolist()))
                    contact_points.append(tuple(contact.pos.tolist()))
            
            state = UniversalState(
                step=step,
                timestamp=time.time(),
                joint_positions=joint_positions,
                joint_velocities=joint_velocities,
                joint_torques=joint_torques,
                base_position=base_position,
                base_orientation=base_orientation,
                base_linear_vel=base_linear_vel,
                base_angular_vel=base_angular_vel,
                contact_forces=contact_forces if contact_forces else None,
                contact_points=contact_points if contact_points else None
            )
            
            # Trace the step
            self.trace_step(state)
            
            return state
            
        except Exception as e:
            print(f"⚠️ Failed to capture MuJoCo state: {e}")
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


__all__ = ["MujocoTracer"]
