"""Configuration management for Oculus SDK"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class OculusConfig:
    """Configuration for Oculus Tracer"""
    
    # API Configuration
    api_key: str
    api_url: str = "http://localhost:3000/api"
    websocket_url: str = "ws://localhost:8080"
    
    # Project Information
    project_name: str = "default-project"
    framework: str = "custom"
    robot_type: str = "custom"
    
    # Tracing Configuration
    trace_frequency: int = 10  # Hz
    buffer_size: int = 100  # Number of traces to buffer
    auto_flush: bool = True
    
    # Safety Configuration
    enable_failure_detection: bool = True
    detection_threshold: float = 0.8
    
    # Network Configuration
    retry_attempts: int = 3
    timeout: int = 30
    offline_mode: bool = False
    
    @classmethod
    def from_dict(cls, config: dict) -> 'OculusConfig':
        """Create config from dictionary"""
        return cls(**{k: v for k, v in config.items() if k in cls.__annotations__})
