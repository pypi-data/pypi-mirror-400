"""
PyBullet Platform Tracer
"""

from ...core.tracer import BaseTracer


class PyBulletTracer(BaseTracer):
    """
    Tracer for PyBullet simulations.
    
    Usage:
        from oculus.platforms.pybullet import PyBulletTracer
        import pybullet as p
        
        with PyBulletTracer(project="pybullet_robot") as tracer:
            p.connect(p.GUI)
            robotId = p.loadURDF("robot.urdf")
            
            for step in range(1000):
                p.stepSimulation()
                pos, orn = p.getBasePositionAndOrientation(robotId)
                vel, ang_vel = p.getBaseVelocity(robotId)
                
                tracer.auto_capture({
                    "position": list(pos),
                    "orientation": list(orn),
                    "velocity": list(vel)
                })
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.platform = "pybullet"
        
    def capture_pybullet_state(self, p, robot_id):
        """Helper to capture PyBullet state"""
        pos, orn = p.getBasePositionAndOrientation(robot_id)
        vel, ang_vel = p.getBaseVelocity(robot_id)
        
        return {
            "position": list(pos),
            "orientation": list(orn),
            "velocity": list(vel),
            "angular_velocity": list(ang_vel)
        }
