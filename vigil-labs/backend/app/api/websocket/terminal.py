"""
VIGIL LABS - WebSocket Terminal
Real-time terminal output streaming via WebSocket.
"""
import json
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from app.core.security import decode_token


class ConnectionManager:
    """Manage WebSocket connections for live terminal streaming."""
    
    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}  # execution_id -> websockets
        self._user_connections: Dict[str, Set[WebSocket]] = {}  # user_id -> websockets
    
    async def connect(self, websocket: WebSocket, execution_id: str, user_id: str):
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        
        if execution_id not in self._connections:
            self._connections[execution_id] = set()
        self._connections[execution_id].add(websocket)
        
        if user_id not in self._user_connections:
            self._user_connections[user_id] = set()
        self._user_connections[user_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, execution_id: str, user_id: str):
        """Remove a WebSocket connection."""
        if execution_id in self._connections:
            self._connections[execution_id].discard(websocket)
            if not self._connections[execution_id]:
                del self._connections[execution_id]
        
        if user_id in self._user_connections:
            self._user_connections[user_id].discard(websocket)
            if not self._user_connections[user_id]:
                del self._user_connections[user_id]
    
    async def send_output(self, execution_id: str, data: str, is_stderr: bool = False):
        """Send output to all connections watching an execution."""
        if execution_id not in self._connections:
            return
        
        message = json.dumps({
            "type": "output",
            "execution_id": execution_id,
            "data": data,
            "stream": "stderr" if is_stderr else "stdout",
        })
        
        dead_connections = set()
        for ws in self._connections[execution_id]:
            try:
                await ws.send_text(message)
            except Exception:
                dead_connections.add(ws)
        
        # Cleanup dead connections
        for ws in dead_connections:
            self._connections[execution_id].discard(ws)
    
    async def send_status(self, execution_id: str, status: str, exit_code: int = None):
        """Send status update to watchers."""
        if execution_id not in self._connections:
            return
        
        message = json.dumps({
            "type": "status",
            "execution_id": execution_id,
            "status": status,
            "exit_code": exit_code,
        })
        
        for ws in list(self._connections.get(execution_id, [])):
            try:
                await ws.send_text(message)
            except Exception:
                pass
    
    async def broadcast_to_user(self, user_id: str, message: dict):
        """Broadcast message to all user connections."""
        if user_id not in self._user_connections:
            return
        
        text = json.dumps(message)
        for ws in list(self._user_connections[user_id]):
            try:
                await ws.send_text(text)
            except Exception:
                pass


# Singleton
ws_manager = ConnectionManager()
