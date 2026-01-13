"""
Base Tracer for Oculus SDK

Provides the core tracing functionality for all platforms.
"""

import time
import asyncio
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from .state import UniversalState
from .connection import WebSocketConnection
from .config import OculusConfig


class BaseTracer(ABC):
    """Base class for all platform tracers"""
    
    def __init__(self, config: OculusConfig):
        self.config = config
        self.connection: Optional[WebSocketConnection] = None
        self.simulation_id: Optional[str] = None
        self.is_connected = False
        self.step_count = 0
        self.start_time: Optional[float] = None
        self.trace_buffer: List[UniversalState] = []
        
    def connect(self) -> bool:
        """Establish connection to Oculus backend"""
        try:
            self.connection = WebSocketConnection(
                api_key=self.config.api_key,
                server_url=self.config.websocket_url
            )
            self.connection.connect()
            self.is_connected = True
            print(f"✅ Connected to Oculus at {self.config.websocket_url}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            if self.config.offline_mode:
                print("📴 Running in offline mode")
                self.is_connected = False
                return True
            return False
    
    def start_simulation(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Start a new simulation run"""
        if not self.is_connected and not self.config.offline_mode:
            if not self.connect():
                raise ConnectionError("Failed to connect to Oculus")
        
        self.start_time = time.time()
        self.step_count = 0
        
        if self.connection:
            meta = metadata or {}
            meta.update({
                'name': name,
                'framework': self.config.framework,
                'robot_type': self.config.robot_type,
            })
            
            self.simulation_id = self.connection.start_run(
                project=self.config.project_name,
                metadata=meta
            )
            print(f"🚀 Simulation started: {self.simulation_id}")
        else:
            import uuid
            self.simulation_id = f"offline_{uuid.uuid4().hex[:12]}"
            print(f"📴 Offline simulation: {self.simulation_id}")
        
        return self.simulation_id
    
    def trace_step(self, state: UniversalState) -> None:
        """Trace a single simulation step"""
        self.step_count += 1
        
        if self.connection:
            # Add to buffer
            self.trace_buffer.append(state)
            
            # Flush if buffer is full or auto-flush is enabled
            if len(self.trace_buffer) >= self.config.buffer_size:
                self.flush_traces()
        
    def flush_traces(self) -> None:
        """Flush buffered traces to server"""
        if not self.connection or not self.trace_buffer:
            return
        
        for state in self.trace_buffer:
            self.connection.send_trace(
                run_id=self.simulation_id,
                step=state.step,
                data=state.to_dict()
            )
        
        self.trace_buffer.clear()
    
    def send_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Send a custom event"""
        if self.connection:
            self.connection.send_event(
                run_id=self.simulation_id,
                event_type=event_type,
                details=details
            )
    
    def detect_failure(self, failure_type: str, severity: str, description: str) -> None:
        """Report a detected failure"""
        if self.connection:
            self.send_event('failure_detected', {
                'type': failure_type,
                'severity': severity,
                'description': description,
                'step': self.step_count
            })
    
    def finish_simulation(self) -> None:
        """Finish the simulation and cleanup"""
        # Flush remaining traces
        self.flush_traces()
        
        if self.connection and self.simulation_id:
            duration = time.time() - self.start_time if self.start_time else 0
            self.connection.finish_run(
                run_id=self.simulation_id,
                step_count=self.step_count,
                duration=duration
            )
            print(f"✅ Simulation finished: {self.step_count} steps in {duration:.2f}s")
            
            self.connection.close()
        
        self.is_connected = False
        self.simulation_id = None
    
    @abstractmethod
    def capture_state(self, *args, **kwargs) -> UniversalState:
        """Capture current state from the platform. Must be implemented by subclasses."""
        pass


def trace_simulation(tracer: BaseTracer, simulation_func, *args, **kwargs):
    """Decorator/wrapper for tracing a simulation"""
    try:
        tracer.start_simulation(kwargs.get('name', 'Simulation'))
        result = simulation_func(*args, **kwargs)
        tracer.finish_simulation()
        return result
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        tracer.finish_simulation()
        raise


__all__ = ["BaseTracer", "trace_simulation"]
