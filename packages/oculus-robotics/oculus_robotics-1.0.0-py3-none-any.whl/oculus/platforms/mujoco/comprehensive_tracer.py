"""
Comprehensive Mujoco Tracer
Captures physics simulation, contacts, sensors, and actuators
"""

import numpy as np
import time
from typing import Dict, Optional
from oculus.core.tracer import BaseTracer

try:
    import mujoco
    MUJOCO_AVAILABLE = True
except ImportError:
    MUJOCO_AVAILABLE = False


class ComprehensiveMujocoTracer(BaseTracer):
    """
    Full Mujoco observability
    Captures: qpos, qvel, qacc, contacts, sensors, actuators, forces
    """
    
    def __init__(self, project: str = "mujoco_project", auto_capture: bool = True):
        super().__init__(project=project, auto_capture=auto_capture)
        
        if not MUJOCO_AVAILABLE:
            raise ImportError("Mujoco not installed. Install with: pip install mujoco")
            
        self.model = None
        self.data = None
        
    def initialize(self, model, data):
        """Initialize with Mujoco model and data"""
        self.model = model
        self.data = data
        
        # Capture model configuration
        model_config = {
            "model_name": model.name if hasattr(model, 'name') else "unknown",
            "nq": model.nq,  # Number of position coordinates
            "nv": model.nv,  # Number of velocity coordinates
            "nu": model.nu,  # Number of actuators
            "nbody": model.nbody,  # Number of bodies
            "njnt": model.njnt,  # Number of joints
            "ngeom": model.ngeom,  # Number of geometries
            "nsensor": model.nsensor,  # Number of sensors
            "timestep": model.opt.timestep,
        }
        
        self.log_event("mujoco_initialized", model_config)
        
    def capture_state(self, step: int):
        """
        Capture comprehensive Mujoco state
        """
        if not self.model or not self.data:
            return {}
            
        timestamp = time.time()
        
        # 1. GENERALIZED COORDINATES
        coord_data = self._capture_coordinates()
        
        # 2. BODY STATES
        body_data = self._capture_body_states()
        
        # 3. JOINT STATES
        joint_data = self._capture_joint_states()
        
        # 4. CONTACT FORCES
        contact_data = self._capture_contacts()
        
        # 5. SENSOR READINGS
        sensor_data = self._capture_sensors()
        
        # 6. ACTUATOR STATES
        actuator_data = self._capture_actuators()
        
        # 7. FORCES & TORQUES
        force_data = self._capture_forces()
        
        # 8. ENERGY & MOMENTUM
        energy_data = self._compute_energy_metrics()
        
        trace = {
            "step": step,
            "timestamp": timestamp,
            "time": self.data.time,
            "coordinates": coord_data,
            "bodies": body_data,
            "joints": joint_data,
            "contacts": contact_data,
            "sensors": sensor_data,
            "actuators": actuator_data,
            "forces": force_data,
            "energy": energy_data,
        }
        
        self.trace(trace)
        return trace
        
    def _capture_coordinates(self) -> Dict:
        """Capture generalized coordinates"""
        return {
            "qpos": self.data.qpos.tolist(),  # Position
            "qvel": self.data.qvel.tolist(),  # Velocity
            "qacc": self.data.qacc.tolist(),  # Acceleration
            "qfrc_applied": self.data.qfrc_applied.tolist(),  # Applied forces
        }
        
    def _capture_body_states(self) -> Dict:
        """Capture body states"""
        bodies = {}
        
        for i in range(self.model.nbody):
            body_name = mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_BODY, i)
            if body_name:
                bodies[body_name] = {
                    "pos": self.data.xpos[i].tolist(),  # 3D position
                    "quat": self.data.xquat[i].tolist(),  # Quaternion orientation
                    "vel": self.data.cvel[i][:3].tolist() if i < len(self.data.cvel) else None,
                    "angular_vel": self.data.cvel[i][3:].tolist() if i < len(self.data.cvel) else None,
                }
                
        return bodies
        
    def _capture_joint_states(self) -> Dict:
        """Capture joint states"""
        joints = {}
        
        for i in range(self.model.njnt):
            joint_name = mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_JOINT, i)
            if joint_name:
                qposadr = self.model.jnt_qposadr[i]
                dofadr = self.model.jnt_dofadr[i]
                
                joints[joint_name] = {
                    "position": float(self.data.qpos[qposadr]),
                    "velocity": float(self.data.qvel[dofadr]),
                    "type": int(self.model.jnt_type[i]),
                }
                
        return joints
        
    def _capture_contacts(self) -> Dict:
        """Capture contact information"""
        contacts = []
        
        for i in range(self.data.ncon):
            contact = self.data.contact[i]
            
            geom1_name = mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_GEOM, contact.geom1)
            geom2_name = mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_GEOM, contact.geom2)
            
            contacts.append({
                "geom1": geom1_name,
                "geom2": geom2_name,
                "pos": contact.pos.tolist(),
                "frame": contact.frame.tolist(),
                "dist": float(contact.dist),
                "friction": [float(contact.friction[j]) for j in range(5)],
            })
            
        return {
            "count": len(contacts),
            "contacts": contacts
        }
        
    def _capture_sensors(self) -> Dict:
        """Capture sensor readings"""
        sensors = {}
        
        for i in range(self.model.nsensor):
            sensor_name = mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_SENSOR, i)
            if sensor_name:
                adr = self.model.sensor_adr[i]
                dim = self.model.sensor_dim[i]
                
                sensors[sensor_name] = {
                    "value": self.data.sensordata[adr:adr+dim].tolist(),
                    "type": int(self.model.sensor_type[i]),
                }
                
        return sensors
        
    def _capture_actuators(self) -> Dict:
        """Capture actuator states"""
        actuators = {}
        
        for i in range(self.model.nu):
            actuator_name = mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_ACTUATOR, i)
            if actuator_name:
                actuators[actuator_name] = {
                    "ctrl": float(self.data.ctrl[i]),
                    "act": float(self.data.act[i]) if i < len(self.data.act) else None,
                    "force": float(self.data.actuator_force[i]) if i < len(self.data.actuator_force) else None,
                }
                
        return actuators
        
    def _capture_forces(self) -> Dict:
        """Capture forces and torques"""
        return {
            "qfrc_actuator": self.data.qfrc_actuator.tolist(),
            "qfrc_passive": self.data.qfrc_passive.tolist(),
            "qfrc_constraint": self.data.qfrc_constraint.tolist(),
            "cfrc_ext": [self.data.cfrc_ext[i].tolist() for i in range(min(10, self.model.nbody))],
        }
        
    def _compute_energy_metrics(self) -> Dict:
        """Compute energy and momentum"""
        return {
            "kinetic_energy": float(self.data.energy[0]) if len(self.data.energy) > 0 else 0.0,
            "potential_energy": float(self.data.energy[1]) if len(self.data.energy) > 1 else 0.0,
        }
