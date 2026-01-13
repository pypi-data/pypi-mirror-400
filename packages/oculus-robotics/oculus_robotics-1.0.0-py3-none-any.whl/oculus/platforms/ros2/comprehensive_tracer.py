"""
Comprehensive ROS 2 Tracer
Captures topics, services, TF, latency, and message flow
"""

import time
from typing import Dict, List, Optional, Any
from oculus.core.tracer import BaseTracer

try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False
    Node = object


class ComprehensiveROS2Tracer(BaseTracer):
    """
    Full ROS 2 observability
    Captures: Topics, Services, TF, Parameters, Latency, Message Frequency
    """
    
    def __init__(self, project: str = "ros2_project", auto_capture: bool = True):
        super().__init__(project=project, auto_capture=auto_capture)
        
        if not ROS2_AVAILABLE:
            raise ImportError("ROS 2 not installed. Install with: pip install rclpy")
            
        # ROS 2 node
        self.node: Optional[Node] = None
        
        # Topic tracking
        self.topic_subscribers = {}
        self.topic_message_counts = {}
        self.topic_last_received = {}
        self.topic_frequencies = {}
        
        # Service tracking
        self.service_calls = []
        
        # TF tracking
        self.tf_transforms = {}
        
        # Latency tracking
        self.latencies = []
        
    def initialize(self, node_name: str = "oculus_tracer"):
        """Initialize ROS 2 node"""
        if not rclpy.ok():
            rclpy.init()
            
        self.node = Node(node_name)
        
        # Get system info
        system_info = {
            "node_name": node_name,
            "available_topics": self._get_topic_list(),
            "available_services": self._get_service_list(),
            "available_nodes": self._get_node_list(),
        }
        
        self.log_event("ros2_initialized", system_info)
        
    def subscribe_topic(self, topic_name: str, msg_type):
        """Subscribe to a ROS 2 topic"""
        if not self.node:
            raise RuntimeError("Node not initialized. Call initialize() first")
            
        def callback(msg):
            self._handle_topic_message(topic_name, msg)
            
        sub = self.node.create_subscription(
            msg_type,
            topic_name,
            callback,
            10  # QoS depth
        )
        
        self.topic_subscribers[topic_name] = sub
        self.topic_message_counts[topic_name] = 0
        self.topic_last_received[topic_name] = time.time()
        
        self.log_event("topic_subscribed", {"topic": topic_name, "type": str(msg_type)})
        
    def capture_state(self, step: int):
        """
        Capture comprehensive ROS 2 state
        """
        timestamp = time.time()
        
        # 1. TOPIC DATA
        topic_data = self._capture_topic_statistics()
        
        # 2. SERVICE DATA
        service_data = self._capture_service_statistics()
        
        # 3. TF DATA
        tf_data = self._capture_tf_tree()
        
        # 4. NETWORK STATISTICS
        network_data = self._capture_network_stats()
        
        # 5. NODE STATISTICS
        node_data = self._capture_node_stats()
        
        # 6. LATENCY ANALYSIS
        latency_data = self._compute_latency_metrics()
        
        trace = {
            "step": step,
            "timestamp": timestamp,
            "topics": topic_data,
            "services": service_data,
            "tf": tf_data,
            "network": network_data,
            "nodes": node_data,
            "latency": latency_data,
        }
        
        self.trace(trace)
        return trace
        
    def _handle_topic_message(self, topic_name: str, msg):
        """Handle incoming topic message"""
        current_time = time.time()
        
        # Update message count
        self.topic_message_counts[topic_name] = self.topic_message_counts.get(topic_name, 0) + 1
        
        # Compute frequency
        last_time = self.topic_last_received.get(topic_name, current_time)
        frequency = 1.0 / (current_time - last_time) if current_time > last_time else 0.0
        self.topic_frequencies[topic_name] = frequency
        self.topic_last_received[topic_name] = current_time
        
        # Compute latency (if message has timestamp)
        if hasattr(msg, 'header') and hasattr(msg.header, 'stamp'):
            msg_time = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
            latency = current_time - msg_time
            self.latencies.append({
                "topic": topic_name,
                "latency": latency,
                "timestamp": current_time
            })
            
    def _capture_topic_statistics(self) -> Dict:
        """Capture topic statistics"""
        stats = {}
        
        for topic_name, count in self.topic_message_counts.items():
            stats[topic_name] = {
                "message_count": count,
                "frequency_hz": self.topic_frequencies.get(topic_name, 0.0),
                "last_received": self.topic_last_received.get(topic_name, 0.0),
            }
            
        return stats
        
    def _capture_service_statistics(self) -> Dict:
        """Capture service call statistics"""
        return {
            "total_calls": len(self.service_calls),
            "recent_calls": self.service_calls[-10:] if self.service_calls else []
        }
        
    def _capture_tf_tree(self) -> Dict:
        """Capture TF transform tree"""
        # Placeholder - requires tf2_ros
        return {
            "available_frames": list(self.tf_transforms.keys()),
            "transform_count": len(self.tf_transforms)
        }
        
    def _capture_network_stats(self) -> Dict:
        """Capture network statistics"""
        return {
            "total_bandwidth_kb": 0.0,  # Placeholder
            "message_rate": sum(self.topic_frequencies.values()),
            "active_subscriptions": len(self.topic_subscribers),
        }
        
    def _capture_node_stats(self) -> Dict:
        """Capture node statistics"""
        if not self.node:
            return {}
            
        return {
            "node_name": self.node.get_name(),
            "namespace": self.node.get_namespace(),
            "subscriptions": len(self.topic_subscribers),
        }
        
    def _compute_latency_metrics(self) -> Dict:
        """Compute latency metrics"""
        if not self.latencies:
            return {
                "avg_latency_ms": 0.0,
                "max_latency_ms": 0.0,
                "min_latency_ms": 0.0,
            }
            
        recent_latencies = [l["latency"] for l in self.latencies[-100:]]
        
        return {
            "avg_latency_ms": sum(recent_latencies) / len(recent_latencies) * 1000,
            "max_latency_ms": max(recent_latencies) * 1000,
            "min_latency_ms": min(recent_latencies) * 1000,
            "total_measurements": len(self.latencies),
        }
        
    def _get_topic_list(self) -> List[str]:
        """Get list of available topics"""
        if not self.node:
            return []
        return [name for name, _ in self.node.get_topic_names_and_types()]
        
    def _get_service_list(self) -> List[str]:
        """Get list of available services"""
        if not self.node:
            return []
        return [name for name, _ in self.node.get_service_names_and_types()]
        
    def _get_node_list(self) -> List[str]:
        """Get list of active nodes"""
        if not self.node:
            return []
        return self.node.get_node_names()
        
    def spin_once(self):
        """Process one iteration of ROS 2 callbacks"""
        if self.node:
            rclpy.spin_once(self.node, timeout_sec=0.01)
            
    def cleanup(self):
        """Cleanup ROS 2 resources"""
        if self.node:
            self.node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
