"""
Isaac Sim Platform Tracer
"""

from ...core.tracer import BaseTracer

# Import OpenTelemetry tracer
try:
    from .tracer import IsaacSimTracer as OTelIsaacSimTracer
    HAS_OTEL = True
except ImportError:
    HAS_OTEL = False


class IsaacSimTracer(BaseTracer):
    """
    Tracer specifically for NVIDIA Isaac Sim.
    
    Usage:
        from oculus.platforms.isaac_sim import IsaacSimTracer
        
        with IsaacSimTracer(project="isaac_robot") as tracer:
            world = World()
            for step in range(1000):
                world.step(render=True)
                tracer.auto_capture({
                    "position": robot.get_world_pose()[0],
                    "velocity": robot.get_linear_velocity()
                })
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.platform = "isaac_sim"
        
    def capture_physics_state(self, robot):
        """
        Helper to capture common physics state from Isaac Sim robot.
        
        Args:
            robot: Isaac Sim robot object
            
        Returns:
            Dict with position, orientation, velocity
        """
        position, orientation = robot.get_world_pose()
        velocity = robot.get_linear_velocity()
        angular_vel = robot.get_angular_velocity()
        
        return {
            "position": position.tolist() if hasattr(position, 'tolist') else list(position),
            "orientation": orientation.tolist() if hasattr(orientation, 'tolist') else list(orientation),
            "velocity": velocity.tolist() if hasattr(velocity, 'tolist') else list(velocity),
            "angular_velocity": angular_vel.tolist() if hasattr(angular_vel, 'tolist') else list(angular_vel)
        }
