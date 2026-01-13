"""
Base Tracer Class

All platform-specific tracers inherit from this.
"""

import os
import time
import asyncio
from typing import Dict, Any, Optional, Callable
from functools import wraps

from .connection import WebSocketConnection
from .auth import get_api_key


class BaseTracer:
    """
    Base tracer class for all platforms.
    
    Handles:
    - Connection management
    - Authentication
    - Auto-capture timing
    - Event logging
    """
    
    def __init__(
        self,
        project: str = "default-project",
        api_key: Optional[str] = None,
        server_url: Optional[str] = None,
        auto_capture_interval: float = 1.0,
        metadata: Optional[Dict] = None
    ):
        self.project = project
        self.api_key = api_key or get_api_key()
        self.server_url = server_url or os.getenv(
            "OCULUS_SERVER_URL",
            "ws://localhost:8080"
        )
        self.auto_capture_interval = auto_capture_interval
        self.metadata = metadata or {}
        
        # State
        self.connection = None
        self.run_id = None
        self.step_counter = 0
        self.last_capture_time = 0
        self.start_time = None
        
    def start_run(self):
        """Start a new run"""
        self.connection = WebSocketConnection(
            self.api_key,
            self.server_url
        )
        self.connection.connect()
        self.run_id = self.connection.start_run(self.project, self.metadata)
        self.start_time = time.time()
        self.last_capture_time = time.time()
        self.step_counter = 0
        
    def log_step(self, step: Optional[int] = None, data: Optional[Dict] = None):
        """Log a simulation step"""
        if step is None:
            step = self.step_counter
            self.step_counter += 1
            
        if self.connection:
            self.connection.send_trace(self.run_id, step, data or {})
    
    def auto_capture(self, data: Dict):
        """
        Automatically capture data at specified interval.
        Only logs when interval time has passed.
        """
        current_time = time.time()
        if current_time - self.last_capture_time >= self.auto_capture_interval:
            self.log_step(data=data)
            self.last_capture_time = current_time
    
    def log_event(self, event_type: str, message: str, level: str = "INFO"):
        """Log an event"""
        if self.connection:
            self.connection.send_event(
                self.run_id,
                event_type,
                {"message": message, "level": level}
            )
    
    def finish(self):
        """Finish the run"""
        if self.connection:
            duration = time.time() - self.start_time if self.start_time else 0
            self.connection.finish_run(self.run_id, self.step_counter, duration)
            self.connection.close()
    
    def __enter__(self):
        """Context manager entry"""
        self.start_run()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.finish()


def trace_simulation(project: str = "default-project", auto_capture_interval: float = 1.0):
    """
    Decorator to automatically trace a simulation function.
    
    Usage:
        @trace_simulation(project="my_robot_sim")
        def run_simulation(tracer):
            # Your simulation code
            tracer.auto_capture(robot_state)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with BaseTracer(project=project, auto_capture_interval=auto_capture_interval) as tracer:
                if 'tracer' in func.__code__.co_varnames:
                    kwargs['tracer'] = tracer
                return func(*args, **kwargs)
        return wrapper
    return decorator
