"""
ROS 2 Platform

Monitors ROS 2 topics, services, and latencies.
"""

from .tracer import ROS2Tracer

__all__ = ["ROS2Tracer"]
    """
    Tracer for ROS 2 systems.
    
    Monitors:
    - Topic latencies
    - Message frequencies
    - Service call times
    - TF tree
    
    Usage:
        from oculus.platforms.ros2 import ROS2Tracer
        import rclpy
        from rclpy.node import Node
        
        class MyRobotNode(Node):
            def __init__(self):
                super().__init__('my_robot')
                self.tracer = ROS2Tracer(project="ros2_robot")
                self.tracer.start_run()
                
                self.subscription = self.create_subscription(
                    JointState,
                    '/joint_states',
                    self.joint_callback,
                    10
                )
            
            def joint_callback(self, msg):
                self.tracer.auto_capture({
                    "joint_positions": list(msg.position),
                    "joint_velocities": list(msg.velocity)
                })
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.platform = "ros2"
        self.topic_stats = {}
        
    def log_topic_message(self, topic: str, msg_data: dict):
        """Log ROS 2 topic message"""
        self.log_step(data={
            "type": "topic_message",
            "topic": topic,
            "data": msg_data
        })
        
    def log_service_call(self, service: str, request: dict, response: dict, duration: float):
        """Log ROS 2 service call"""
        self.log_step(data={
            "type": "service_call",
            "service": service,
            "request": request,
            "response": response,
            "duration_ms": duration * 1000
        })
        
    def log_tf_transform(self, parent_frame: str, child_frame: str, transform: dict):
        """Log TF transform"""
        self.log_step(data={
            "type": "tf_transform",
            "parent_frame": parent_frame,
            "child_frame": child_frame,
            "transform": transform
        })
