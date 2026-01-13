"""
ROS 2 Platform Adapter

Integrates Oculus tracing with ROS 2 robotics framework.
"""

import time
from typing import Optional, Dict, Any
from ...core.tracer import BaseTracer
from ...core.state import UniversalState
from ...core.config import OculusConfig


class ROS2Tracer(BaseTracer):
    """Tracer for ROS 2 robots"""
    
    def __init__(self, api_key: str, project_name: str, server_url: str = "ws://localhost:8080", **kwargs):
        config = OculusConfig(
            api_key=api_key,
            project_name=project_name,
            websocket_url=server_url,
            framework="ros2",
            robot_type=kwargs.get('robot_type', 'custom')
        )
        super().__init__(config)
        self.joint_state_cache = None
        self.odom_cache = None
        
    def update_joint_state(self, joint_state_msg):
        """Update cached joint state from ROS message"""
        self.joint_state_cache = joint_state_msg
        
    def update_odometry(self, odom_msg):
        """Update cached odometry from ROS message"""
        self.odom_cache = odom_msg
        
    def capture_state(self, step: int = None, joint_state=None, odom=None) -> UniversalState:
        """Capture state from ROS 2 messages"""
        if step is None:
            step = self.step_count
        
        # Use provided messages or cached
        js = joint_state or self.joint_state_cache
        od = odom or self.odom_cache
        
        if js is None:
            raise ValueError("Joint state not available. Call update_joint_state() or provide joint_state parameter.")
        
        try:
            # Extract joint data
            joint_positions = list(js.position) if hasattr(js, 'position') else []
            joint_velocities = list(js.velocity) if hasattr(js, 'velocity') else [0.0] * len(joint_positions)
            joint_torques = list(js.effort) if hasattr(js, 'effort') else [0.0] * len(joint_positions)
            
            # Extract base state from odometry
            if od is not None:
                pose = od.pose.pose
                twist = od.twist.twist
                
                base_position = (pose.position.x, pose.position.y, pose.position.z)
                base_orientation = (pose.orientation.x, pose.orientation.y, 
                                  pose.orientation.z, pose.orientation.w)
                base_linear_vel = (twist.linear.x, twist.linear.y, twist.linear.z)
                base_angular_vel = (twist.angular.x, twist.angular.y, twist.angular.z)
            else:
                # Default base state
                base_position = (0.0, 0.0, 0.0)
                base_orientation = (0.0, 0.0, 0.0, 1.0)
                base_linear_vel = (0.0, 0.0, 0.0)
                base_angular_vel = (0.0, 0.0, 0.0)
            
            state = UniversalState(
                step=step,
                timestamp=time.time(),
                joint_positions=joint_positions,
                joint_velocities=joint_velocities,
                joint_torques=joint_torques,
                base_position=base_position,
                base_orientation=base_orientation,
                base_linear_vel=base_linear_vel,
                base_angular_vel=base_angular_vel
            )
            
            # Trace the step
            self.trace_step(state)
            
            return state
            
        except Exception as e:
            print(f"⚠️ Failed to capture ROS 2 state: {e}")
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
    
    def capture_from_ros(self, joint_state_msg, step: int, odom_msg=None):
        """Convenience method to capture from ROS messages directly"""
        return self.capture_state(step=step, joint_state=joint_state_msg, odom=odom_msg)


__all__ = ["ROS2Tracer"]
