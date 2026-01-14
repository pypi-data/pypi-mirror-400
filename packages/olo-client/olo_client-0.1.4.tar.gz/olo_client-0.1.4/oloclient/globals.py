"""
OLO Globals - Global variables API for cross-script communication

Provides methods to get/set global variables on the appliance that
persist across script executions. Variables can be either:
- Runtime only (lost on appliance restart)
- Persisted (saved to disk, survives restarts)
"""

import json
import asyncio
import uuid
from typing import Any, Optional, Dict


class OLOGlobals:
    """
    Global variables API
    
    Provides methods to set, get, and manage global variables on the appliance.
    These variables are shared across all scripts and can be used for
    cross-script communication and configuration.
    
    Usage:
        # Set a runtime global (lost on restart)
        await oloclient.globals.set_global('speed', 0.5)
        
        # Set a persisted global (survives restarts)
        await oloclient.globals.set_global('waypoints', [...], persist=True)
        
        # Get a global
        speed = await oloclient.globals.get_global('speed')
        
        # Get all globals
        all_vars = await oloclient.globals.get_all_globals()
    """
    
    def __init__(self, ros):
        """
        Initialize OLOGlobals
        
        Args:
            ros: roslibpy.Ros instance
        """
        self._ros = ros
        self._pending_requests: Dict[str, asyncio.Future] = {}
        self._message_handler_registered = False
    
    def set_ros(self, ros):
        """Update the ROS connection"""
        self._ros = ros
        self._message_handler_registered = False
    
    def _ensure_message_handler(self):
        """Ensure the message handler is registered"""
        if self._message_handler_registered:
            return
        
        # Register handler for globals responses
        from . import register_custom_handler
        register_custom_handler(self._handle_globals_message)
        self._message_handler_registered = True
    
    def _handle_globals_message(self, msg: dict):
        """Handle incoming globals messages from the appliance"""
        op = msg.get('op', '')
        if not op.startswith('global') and op != 'all_globals':
            return
        
        request_id = msg.get('requestId')
        if not request_id or request_id not in self._pending_requests:
            return
        
        future = self._pending_requests.pop(request_id)
        if future.done():
            return
        
        if op == 'global_error':
            future.set_exception(Exception(msg.get('error', 'Unknown error')))
        else:
            future.set_result(msg)
    
    def _get_socket(self):
        """Get the underlying WebSocket"""
        if not self._ros or not self._ros.is_connected:
            raise ConnectionError('Not connected to robot')
        
        # Access the underlying socket
        if hasattr(self._ros, '_comm') and self._ros._comm:
            return self._ros._comm
        
        # Fallback for different roslibpy versions
        if hasattr(self._ros, 'factory') and self._ros.factory:
            proto = getattr(self._ros.factory, '_proto', None)
            if proto:
                return proto
        
        return None
    
    def _send_message(self, message: dict):
        """Send a message via the WebSocket"""
        if not self._ros or not self._ros.is_connected:
            raise ConnectionError('Not connected to robot')
        
        # Use roslibpy's internal send method
        msg_str = json.dumps(message)
        
        # Try different methods to send
        if hasattr(self._ros, 'send'):
            self._ros.send(msg_str)
        elif hasattr(self._ros, '_comm') and hasattr(self._ros._comm, 'send'):
            self._ros._comm.send(msg_str)
        else:
            # Fallback: use the factory/protocol
            if hasattr(self._ros, 'factory') and self._ros.factory:
                proto = getattr(self._ros.factory, '_proto', None)
                if proto and hasattr(proto, 'sendMessage'):
                    proto.sendMessage(msg_str.encode('utf-8'))
                    return
            raise ConnectionError('Cannot send message: no valid transport found')
    
    async def set_global(self, key: str, value: Any, persist: bool = False) -> bool:
        """
        Set a global variable on the appliance
        
        Args:
            key: Variable name (non-empty string)
            value: JSON-serializable value
            persist: If True, save to disk (survives appliance restart). Default: False
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If key is invalid or value is not JSON-serializable
            ConnectionError: If not connected to robot
            TimeoutError: If request times out
        """
        if not isinstance(key, str) or not key.strip():
            raise ValueError('Key must be a non-empty string')
        
        # Validate JSON-serializable
        try:
            json.dumps(value)
        except (TypeError, ValueError) as e:
            raise ValueError(f'Value must be JSON-serializable: {e}')
        
        self._ensure_message_handler()
        
        request_id = str(uuid.uuid4())
        future = asyncio.get_event_loop().create_future()
        self._pending_requests[request_id] = future
        
        try:
            self._send_message({
                'op': 'set_global',
                'key': key,
                'value': value,
                'persist': persist,
                'requestId': request_id
            })
            
            result = await asyncio.wait_for(future, timeout=5.0)
            return result.get('success', True)
            
        except asyncio.TimeoutError:
            self._pending_requests.pop(request_id, None)
            raise TimeoutError('Set global request timed out')
    
    async def get_global(self, key: str) -> Optional[Any]:
        """
        Get a global variable from the appliance
        
        Args:
            key: Variable name
            
        Returns:
            The value, or None if not set
            
        Raises:
            ConnectionError: If not connected to robot
            TimeoutError: If request times out
        """
        self._ensure_message_handler()
        
        request_id = str(uuid.uuid4())
        future = asyncio.get_event_loop().create_future()
        self._pending_requests[request_id] = future
        
        try:
            self._send_message({
                'op': 'get_global',
                'key': key,
                'requestId': request_id
            })
            
            result = await asyncio.wait_for(future, timeout=5.0)
            return result.get('value') if result.get('exists') else None
            
        except asyncio.TimeoutError:
            self._pending_requests.pop(request_id, None)
            raise TimeoutError('Get global request timed out')
    
    async def get_all_globals(self) -> Dict[str, Any]:
        """
        Get all global variables from the appliance
        
        Returns:
            Dictionary with all key-value pairs
            
        Raises:
            ConnectionError: If not connected to robot
            TimeoutError: If request times out
        """
        self._ensure_message_handler()
        
        request_id = str(uuid.uuid4())
        future = asyncio.get_event_loop().create_future()
        self._pending_requests[request_id] = future
        
        try:
            self._send_message({
                'op': 'get_all_globals',
                'requestId': request_id
            })
            
            result = await asyncio.wait_for(future, timeout=5.0)
            return result.get('globals', {})
            
        except asyncio.TimeoutError:
            self._pending_requests.pop(request_id, None)
            raise TimeoutError('Get all globals request timed out')
    
    async def delete_global(self, key: str, persist: bool = False) -> bool:
        """
        Delete a global variable from the appliance
        
        Args:
            key: Variable name
            persist: If True, also remove from persisted storage. Default: False
            
        Returns:
            True if the key existed
            
        Raises:
            ConnectionError: If not connected to robot
            TimeoutError: If request times out
        """
        self._ensure_message_handler()
        
        request_id = str(uuid.uuid4())
        future = asyncio.get_event_loop().create_future()
        self._pending_requests[request_id] = future
        
        try:
            self._send_message({
                'op': 'delete_global',
                'key': key,
                'persist': persist,
                'requestId': request_id
            })
            
            result = await asyncio.wait_for(future, timeout=5.0)
            return result.get('existed', False)
            
        except asyncio.TimeoutError:
            self._pending_requests.pop(request_id, None)
            raise TimeoutError('Delete global request timed out')
    
    async def clear_globals(self, persist: bool = False) -> Dict[str, int]:
        """
        Clear all global variables from the appliance
        
        Args:
            persist: If True, also clear persisted storage. Default: False
            
        Returns:
            Dictionary with 'runtimeCleared' and 'persistedCleared' counts
            
        Raises:
            ConnectionError: If not connected to robot
            TimeoutError: If request times out
        """
        self._ensure_message_handler()
        
        request_id = str(uuid.uuid4())
        future = asyncio.get_event_loop().create_future()
        self._pending_requests[request_id] = future
        
        try:
            self._send_message({
                'op': 'clear_globals',
                'persist': persist,
                'requestId': request_id
            })
            
            result = await asyncio.wait_for(future, timeout=5.0)
            return {
                'runtimeCleared': result.get('runtimeCleared', 0),
                'persistedCleared': result.get('persistedCleared', 0)
            }
            
        except asyncio.TimeoutError:
            self._pending_requests.pop(request_id, None)
            raise TimeoutError('Clear globals request timed out')
    
    def cleanup(self):
        """Clean up pending requests"""
        for request_id, future in self._pending_requests.items():
            if not future.done():
                future.cancel()
        self._pending_requests.clear()

