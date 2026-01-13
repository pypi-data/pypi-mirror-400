"""
WebSocket Connection Manager

Handles WebSocket communication with Oculus backend.
"""

import json
import time
import asyncio
import websockets
from typing import Dict, Any, Optional


class WebSocketConnection:
    """Manages WebSocket connection to Oculus backend"""
    
    def __init__(self, api_key: str, server_url: str):
        self.api_key = api_key
        self.server_url = server_url
        self.ws = None
        self.loop = None
        
    def connect(self):
        """Establish connection"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._connect())
        
    async def _connect(self):
        """Async connect"""
        try:
            self.ws = await websockets.connect(self.server_url)
            
            # Authenticate
            await self.ws.send(json.dumps({
                "type": "authenticate",
                "api_key": self.api_key
            }))
            
            response = await self.ws.recv()
            data = json.loads(response)
            
            if not data.get("success"):
                raise Exception(f"Authentication failed: {data.get('error')}")
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            raise
    
    def start_run(self, project: str, metadata: Dict) -> str:
        """Start a new run"""
        import uuid
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        
        self.loop.run_until_complete(self.ws.send(json.dumps({
            "type": "run_start",
            "run_id": run_id,
            "project": project,
            "metadata": metadata,
            "timestamp": time.time()
        })))
        
        return run_id
    
    def send_trace(self, run_id: str, step: int, data: Dict):
        """Send trace data"""
        self.loop.run_until_complete(self.ws.send(json.dumps({
            "type": "trace",
            "run_id": run_id,
            "step": step,
            "data": data,
            "timestamp": time.time()
        })))
    
    def send_event(self, run_id: str, event_type: str, details: Dict):
        """Send event"""
        self.loop.run_until_complete(self.ws.send(json.dumps({
            "type": "event",
            "run_id": run_id,
            "event_type": event_type,
            "details": details,
            "timestamp": time.time()
        })))
    
    def finish_run(self, run_id: str, step_count: int, duration: float):
        """Finish run"""
        self.loop.run_until_complete(self.ws.send(json.dumps({
            "type": "run_end",
            "run_id": run_id,
            "total_steps": step_count,
            "duration": duration,
            "timestamp": time.time()
        })))
    
    def close(self):
        """Close connection"""
        if self.ws:
            self.loop.run_until_complete(self.ws.close())
        if self.loop:
            self.loop.close()
