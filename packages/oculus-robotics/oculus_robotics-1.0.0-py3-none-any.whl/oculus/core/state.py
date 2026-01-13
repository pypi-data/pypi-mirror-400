"""Universal state representation for robotics systems"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
import numpy as np


@dataclass
class UniversalState:
    """
    Universal state representation that works across all robotics platforms.
    Minimal required fields with optional extensions for specific platforms.
    """
    
    # Time
    step: int
    timestamp: float
    
    # Joint State (Required)
    joint_positions: List[float]
    joint_velocities: List[float]
    joint_torques: List[float]
    
    # Base State (Required for mobile/legged robots)
    base_position: Tuple[float, float, float]  # (x, y, z)
    base_orientation: Tuple[float, float, float, float]  # (qx, qy, qz, qw)
    base_linear_vel: Tuple[float, float, float]  # (vx, vy, vz)
    base_angular_vel: Tuple[float, float, float]  # (wx, wy, wz)
    
    # Contact Information (Optional)
    contact_forces: Optional[List[Tuple[float, float, float]]] = None
    contact_points: Optional[List[Tuple[float, float, float]]] = None
    contact_bodies: Optional[List[str]] = None
    
    # Additional Data (Platform-specific)
    custom_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for transmission"""
        return {
            'step': self.step,
            'timestamp': self.timestamp,
            'jointPositions': self.joint_positions,
            'jointVelocities': self.joint_velocities,
            'jointTorques': self.joint_torques,
            'basePosition': list(self.base_position),
            'baseOrientation': list(self.base_orientation),
            'baseLinearVel': list(self.base_linear_vel),
            'baseAngularVel': list(self.base_angular_vel),
            'contactForces': [list(f) for f in self.contact_forces] if self.contact_forces else None,
            'contactPoints': [list(p) for p in self.contact_points] if self.contact_points else None,
            'customData': self.custom_data,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UniversalState':
        """Create state from dictionary"""
        return cls(
            step=data['step'],
            timestamp=data['timestamp'],
            joint_positions=data['jointPositions'],
            joint_velocities=data['jointVelocities'],
            joint_torques=data['jointTorques'],
            base_position=tuple(data['basePosition']),
            base_orientation=tuple(data['baseOrientation']),
            base_linear_vel=tuple(data['baseLinearVel']),
            base_angular_vel=tuple(data['baseAngularVel']),
            contact_forces=[tuple(f) for f in data.get('contactForces', [])] if data.get('contactForces') else None,
            contact_points=[tuple(p) for p in data.get('contactPoints', [])] if data.get('contactPoints') else None,
            custom_data=data.get('customData', {}),
        )
    
    def compute_com_position(self, link_masses: List[float], link_positions: List[Tuple[float, float, float]]) -> Tuple[float, float, float]:
        """Compute center of mass position"""
        if not link_masses or not link_positions:
            return self.base_position
        
        total_mass = sum(link_masses)
        com_x = sum(m * p[0] for m, p in zip(link_masses, link_positions)) / total_mass
        com_y = sum(m * p[1] for m, p in zip(link_masses, link_positions)) / total_mass
        com_z = sum(m * p[2] for m, p in zip(link_masses, link_positions)) / total_mass
        
        return (com_x, com_y, com_z)
