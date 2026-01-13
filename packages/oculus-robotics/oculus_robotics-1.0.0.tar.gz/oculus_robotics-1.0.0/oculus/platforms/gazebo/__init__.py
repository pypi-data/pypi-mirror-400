"""
Gazebo Platform Tracer
"""

from ...core.tracer import BaseTracer


class GazeboTracer(BaseTracer):
    """
    Tracer for Gazebo simulations (via ROS 2).
    
    Usage:
        from oculus.platforms.gazebo import GazeboTracer
        import rclpy
        from geometry_msgs.msg import Twist
        
        with GazeboTracer(project="gazebo_robot") as tracer:
            # Subscribe to Gazebo topics via ROS 2
            # Log robot state
            pass
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.platform = "gazebo"
