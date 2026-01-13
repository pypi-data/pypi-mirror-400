"""WebSocket client for real-time communication with Oculus platform"""
import socketio
import time
from typing import Dict, Any, List, Callable, Optional
from threading import Thread, Event
import logging

logger = logging.getLogger(__name__)


class WebSocketClient:
    """WebSocket client for sending traces and receiving updates"""
    
    def __init__(self, api_key: str, server_url: str = "ws://localhost:8080"):
        self.api_key = api_key
        self.server_url = server_url
        self.sio = socketio.Client(reconnection=True, reconnection_attempts=5)
        self.connected = False
        self.simulation_id: Optional[str] = None
        
        # Setup event handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup Socket.IO event handlers"""
        
        @self.sio.event
        def connect():
            self.connected = True
            logger.info(f"Connected to WebSocket server: {self.server_url}")
        
        @self.sio.event
        def disconnect():
            self.connected = False
            logger.warning("Disconnected from WebSocket server")
        
        @self.sio.event
        def connect_error(data):
            logger.error(f"Connection error: {data}")
        
        @self.sio.on('trace_ack')
        def on_trace_ack(data):
            logger.debug(f"Traces acknowledged: {data.get('count', 0)}")
        
        @self.sio.on('error')
        def on_error(data):
            logger.error(f"Server error: {data.get('message', 'Unknown error')}")
    
    def connect(self) -> bool:
        """Connect to WebSocket server"""
        try:
            if self.connected:
                return True
            
            self.sio.connect(
                self.server_url,
                auth={'apiKey': self.api_key},
                wait_timeout=10
            )
            
            # Wait for connection
            timeout = 5
            start = time.time()
            while not self.connected and (time.time() - start) < timeout:
                time.sleep(0.1)
            
            return self.connected
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from WebSocket server"""
        if self.connected:
            self.sio.disconnect()
            self.connected = False
    
    def send_trace_batch(self, simulation_id: str, traces: List[Dict[str, Any]]):
        """Send batch of traces to server"""
        if not self.connected:
            logger.warning("Not connected, attempting to reconnect...")
            if not self.connect():
                raise ConnectionError("Failed to connect to WebSocket server")
        
        try:
            self.sio.emit('trace_batch', {
                'simulationId': simulation_id,
                'traces': traces,
            })
        except Exception as e:
            logger.error(f"Failed to send trace batch: {e}")
            raise
    
    def send_metric_batch(self, simulation_id: str, metrics: List[Dict[str, Any]]):
        """Send batch of metrics to server"""
        if not self.connected:
            if not self.connect():
                raise ConnectionError("Failed to connect to WebSocket server")
        
        try:
            self.sio.emit('metric_batch', {
                'simulationId': simulation_id,
                'metrics': metrics,
            })
        except Exception as e:
            logger.error(f"Failed to send metric batch: {e}")
            raise
    
    def send_failure(self, simulation_id: str, failure: Dict[str, Any]):
        """Send failure detection to server"""
        if not self.connected:
            if not self.connect():
                raise ConnectionError("Failed to connect to WebSocket server")
        
        try:
            self.sio.emit('failure_detected', {
                'simulationId': simulation_id,
                'failure': failure,
            })
        except Exception as e:
            logger.error(f"Failed to send failure: {e}")
            raise
    
    def update_status(self, simulation_id: str, status: str):
        """Update simulation status"""
        if not self.connected:
            if not self.connect():
                raise ConnectionError("Failed to connect to WebSocket server")
        
        try:
            self.sio.emit('simulation_status', {
                'simulationId': simulation_id,
                'status': status,
            })
        except Exception as e:
            logger.error(f"Failed to update status: {e}")
            raise
    
    def is_connected(self) -> bool:
        """Check if connected to server"""
        return self.connected
