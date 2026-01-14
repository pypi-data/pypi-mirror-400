"""
OLO Video Recording Client - Video Recording Management

Handles video recording from ROS camera topics, session management, and file operations.
Mirrors the JavaScript OLOVideoRecordingClient API.
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List, Callable


class OLOVideoRecording:
    """
    Video recording client for OLO robots.
    
    Provides video recording capabilities including:
    - Start/stop recording from camera topics
    - List active recordings and recorded files
    - Delete recordings
    - Completion callbacks
    
    Usage:
        # Through OLOClient
        result = await client.videoRecording.start_recording(
            topic='/camera/image_raw/compressed',
            options={
                'quality': 'medium',
                'maxDurationSeconds': 30,
                'onCompleted': lambda event: print('Done!', event['filename'])
            }
        )
        
        # Later
        await client.videoRecording.stop_recording(result['recordingId'])
    """
    
    def __init__(self, ros_client=None):
        """
        Initialize OLO Video Recording client
        
        Args:
            ros_client: roslibpy.Ros instance (injected by OLOClient)
        """
        self._ros = ros_client
        self._connected = False
        self._request_counter = 0
        
        # Track active recordings with callbacks
        self._active_recordings: Dict[str, Dict[str, Any]] = {}
        
        # Response callbacks for pending requests
        self._response_callbacks: Dict[str, Dict[str, Any]] = {}
        
        # Message handler tracking
        self._message_handler = None
        self._message_handler_installed = False
    
    def set_ros(self, ros_client):
        """Set the ROS client (called by OLOClient after connection)"""
        self._ros = ros_client
        if ros_client:
            self._setup_message_handler()
    
    def set_connected(self, connected: bool):
        """Set connection state"""
        self._connected = connected
    
    def get_connection_status(self) -> bool:
        """Get connection status"""
        if self._ros is None:
            return False
        return self._connected and self._ros.is_connected
    
    def _setup_message_handler(self):
        """Set up message handler for recording events and responses"""
        if self._message_handler_installed:
            return
        
        if not self._ros:
            return
        
        def handler(message: Dict[str, Any]) -> None:
            op = message.get('op', '')
            # Handle all video_recording_ prefixed messages
            if op.startswith('video_recording_'):
                try:
                    self._handle_recording_message(message)
                except Exception as e:
                    import traceback
                    print(f'[OLOVideoRecording] Error handling {op}: {e}', flush=True)
                    print(traceback.format_exc(), flush=True)
        
        self._message_handler = handler
        self._register_ws_handler(handler)
        self._message_handler_installed = True
    
    def _register_ws_handler(self, handler: Callable[[Dict[str, Any]], None]) -> None:
        """Register a handler for WebSocket messages"""
        # Import the registry from package
        from . import _custom_message_handlers
        
        # Create a wrapper that parses the message if needed
        def wrapped_handler(msg):
            if isinstance(msg, dict):
                handler(msg)
        
        # Add to the custom handlers list
        if wrapped_handler not in _custom_message_handlers:
            _custom_message_handlers.append(wrapped_handler)
        
        # Store the wrapped handler for cleanup
        self._wrapped_handler = wrapped_handler
    
    def _send_message(self, message: Dict) -> None:
        """Send a message over the WebSocket"""
        if not self._ros:
            raise ConnectionError("Not connected to robot")
        
        proto_instance = None
        if hasattr(self._ros, 'factory') and self._ros.factory:
            proto_instance = getattr(self._ros.factory, '_proto', None)
        
        if proto_instance and hasattr(proto_instance, 'sendMessage'):
            msg_str = json.dumps(message)
            proto_instance.sendMessage(msg_str.encode('utf-8'))
        else:
            raise ConnectionError("Cannot send message - protocol not connected")
    
    def _handle_recording_message(self, message: Dict) -> None:
        """Handle incoming recording messages"""
        op = message.get('op', '')
        request_id = message.get('request_id')
        
        # Handle recording events (completion callbacks)
        if op == 'video_recording_event':
            self._handle_recording_event(message)
            return
        
        # Handle response messages
        if op.endswith('_response'):
            entry = self._response_callbacks.get(request_id)
            if not entry:
                return
            
            future = entry.get('future')
            loop = entry.get('loop')
            
            if future and not future.done() and loop:
                loop.call_soon_threadsafe(future.set_result, message)
    
    def _handle_recording_event(self, message: Dict) -> None:
        """Handle recording event messages from the appliance"""
        event_type = message.get('event_type')
        recording_id = message.get('recordingId')
        
        # Handle completion events and trigger callbacks
        if event_type == 'recording_completed':
            recording = self._active_recordings.get(recording_id)
            if recording:
                loop = recording.get('loop')
                
                # Resolve the completion future (this allows start_recording to return)
                completion_future = recording.get('completion_future')
                if completion_future and not completion_future.done() and loop:
                    print(f'[OLOVideoRecording] Resolving completion future for {recording_id}', flush=True)
                    loop.call_soon_threadsafe(completion_future.set_result, message)
                
                # Call the onCompleted callback if provided
                if recording.get('onCompleted'):
                    try:
                        print(f'[OLOVideoRecording] Calling onCompleted callback for {recording_id}', flush=True)
                        callback = recording['onCompleted']
                        
                        # Call callback in a thread-safe way if we have a loop reference
                        if loop and loop.is_running():
                            loop.call_soon_threadsafe(callback, message)
                        else:
                            # Fallback to direct call
                            callback(message)
                    except Exception as e:
                        print(f'[OLOVideoRecording] Error in onCompleted callback: {e}', flush=True)
                        import traceback
                        traceback.print_exc()
            else:
                print(f'[OLOVideoRecording] No recording found for {recording_id}', flush=True)
            # Remove from active recordings
            if recording_id in self._active_recordings:
                del self._active_recordings[recording_id]
        elif event_type == 'recording_started':
            # Update local recording info if we have it
            if recording_id in self._active_recordings:
                self._active_recordings[recording_id].update(message)
    
    async def _send_recording_message(self, operation: str, data: Optional[Dict] = None) -> Dict:
        """
        Send a message to the appliance and wait for response
        
        Args:
            operation: Operation name (e.g., 'start', 'stop', 'list_active')
            data: Additional data to send
            
        Returns:
            Response message
        """
        if not self.get_connection_status():
            raise ConnectionError("Not connected to robot. Please connect first.")
        
        if data is None:
            data = {}
        
        # Ensure message handler is set up
        if not self._message_handler_installed:
            self._setup_message_handler()
        
        self._request_counter += 1
        request_id = f'recording_{operation}_{int(time.time() * 1000)}_{self._request_counter}'
        
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        
        # Store callback info
        self._response_callbacks[request_id] = {
            'future': future,
            'loop': loop
        }
        
        try:
            # Send the message
            self._send_message({
                'op': f'video_recording_{operation}',
                'request_id': request_id,
                **data
            })
            
            # Wait for response with timeout
            result = await asyncio.wait_for(future, timeout=30.0)
            
            if result.get('success'):
                return result
            else:
                raise Exception(result.get('error', f'{operation} failed'))
                
        except asyncio.TimeoutError:
            raise TimeoutError(f'Timeout waiting for {operation} response')
        finally:
            # Remove callback entry
            if request_id in self._response_callbacks:
                del self._response_callbacks[request_id]
    
    async def start_recording(
        self,
        topic: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start recording video from a camera topic.
        
        Args:
            topic: ROS camera topic to record from
            options: Recording options:
                - quality: Recording quality: 'low', 'medium', 'high' (default: 'medium')
                - filename: Custom filename (optional, auto-generated if not provided)
                - maxDurationSeconds: Maximum recording duration in seconds (optional, auto-stops)
                - onCompleted: Callback when recording completes (optional)
                
        Returns:
            Recording session information with recordingId, filename, startTime, etc.
            If maxDurationSeconds is set, waits for recording to complete and includes completion data.
        """
        if not topic:
            raise ValueError("Topic is required for recording")
        
        if options is None:
            options = {}
        
        quality = options.get('quality', 'medium')
        filename = options.get('filename')
        max_duration = options.get('maxDurationSeconds')
        on_completed = options.get('onCompleted')
        
        print(f'[OLOVideoRecording] Starting recording for topic: {topic}')
        
        try:
            # Capture the current event loop for thread-safe callbacks
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop()
            
            # Create a future to wait for completion if maxDurationSeconds is set
            completion_future = None
            if max_duration:
                completion_future = loop.create_future()
            
            response = await self._send_recording_message('start', {
                'topic': topic,
                'quality': quality,
                'filename': filename,
                'maxDurationSeconds': max_duration
            })
            
            # Store recording info locally with callback, loop, and completion future
            recording_id = response.get('recordingId')
            self._active_recordings[recording_id] = {
                'recordingId': recording_id,
                'topic': response.get('topic'),
                'filename': response.get('filename'),
                'quality': quality,
                'startTime': response.get('startTime'),
                'onCompleted': on_completed,
                'loop': loop,
                'completion_future': completion_future
            }
            
            print(f'[OLOVideoRecording] Recording started: {recording_id}')
            if on_completed:
                print(f'[OLOVideoRecording] Completion callback registered for {recording_id}')
            
            # If maxDurationSeconds is set, wait for the recording to complete
            if max_duration and completion_future:
                print(f'[OLOVideoRecording] Waiting for recording to complete (max {max_duration}s)...')
                try:
                    # Wait for completion with timeout buffer
                    completion_result = await asyncio.wait_for(
                        completion_future, 
                        timeout=max_duration + 30
                    )
                    print(f'[OLOVideoRecording] Recording completed: {completion_result.get("filename")}')
                    # Include completion data in response
                    response['completion'] = completion_result
                except asyncio.TimeoutError:
                    print(f'[OLOVideoRecording] Timeout waiting for recording completion')
                    response['timeout'] = True
            
            return response
            
        except Exception as error:
            print(f'[OLOVideoRecording] Failed to start recording: {error}')
            
            # Enhance error for duplicate topic recordings
            if 'already being recorded' in str(error):
                enhanced_error = Exception(str(error))
                enhanced_error.code = 'TOPIC_ALREADY_RECORDING'
                raise enhanced_error
            
            raise
    
    async def stop_recording(self, recording_id: str) -> Dict[str, Any]:
        """
        Stop a specific recording.
        
        Args:
            recording_id: ID of the recording to stop
            
        Returns:
            Recording completion information
        """
        if not recording_id:
            raise ValueError("Recording ID is required")
        
        print(f'[OLOVideoRecording] Stopping recording: {recording_id}')
        
        try:
            response = await self._send_recording_message('stop', {
                'recordingId': recording_id
            })
            
            # Remove from local tracking
            if recording_id in self._active_recordings:
                del self._active_recordings[recording_id]
            
            print(f'[OLOVideoRecording] Recording stopped: {response.get("filename")}')
            return response
            
        except Exception as error:
            print(f'[OLOVideoRecording] Failed to stop recording: {error}')
            raise
    
    async def get_active_recordings(self) -> List[Dict[str, Any]]:
        """
        Get list of active recordings.
        
        Returns:
            Array of active recording information
        """
        print('[OLOVideoRecording] Getting active recordings...')
        
        try:
            response = await self._send_recording_message('list_active')
            return response.get('activeRecordings', [])
            
        except Exception as error:
            print(f'[OLOVideoRecording] Failed to get active recordings: {error}')
            raise
    
    async def stop_recordings_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """
        Stop recordings for a specific topic.
        
        Args:
            topic: ROS topic to stop recordings for
            
        Returns:
            Array of stopped recording information
        """
        if not topic:
            raise ValueError("Topic is required")
        
        print(f'[OLOVideoRecording] Stopping recordings for topic: {topic}')
        
        try:
            # Get active recordings and filter by topic
            active_recordings = await self.get_active_recordings()
            topic_recordings = [rec for rec in active_recordings if rec.get('topic') == topic]
            
            if not topic_recordings:
                print(f'[OLOVideoRecording] No active recordings found for topic: {topic}')
                return []
            
            results = []
            for recording in topic_recordings:
                try:
                    result = await self.stop_recording(recording['recordingId'])
                    results.append(result)
                except Exception as error:
                    print(f'[OLOVideoRecording] Failed to stop recording {recording["recordingId"]}: {error}')
                    results.append({
                        'recordingId': recording['recordingId'],
                        'error': str(error),
                        'success': False
                    })
            
            return results
            
        except Exception as error:
            print(f'[OLOVideoRecording] Failed to stop recordings by topic: {error}')
            raise
    
    async def stop_all_recordings(self) -> List[Dict[str, Any]]:
        """
        Stop all active recordings.
        
        Returns:
            Array of stopped recording information
        """
        print('[OLOVideoRecording] Stopping all recordings...')
        
        try:
            active_recordings = await self.get_active_recordings()
            
            if not active_recordings:
                print('[OLOVideoRecording] No active recordings to stop')
                return []
            
            results = []
            for recording in active_recordings:
                try:
                    result = await self.stop_recording(recording['recordingId'])
                    results.append(result)
                except Exception as error:
                    print(f'[OLOVideoRecording] Failed to stop recording {recording["recordingId"]}: {error}')
                    results.append({
                        'recordingId': recording['recordingId'],
                        'error': str(error),
                        'success': False
                    })
            
            return results
            
        except Exception as error:
            print(f'[OLOVideoRecording] Failed to stop all recordings: {error}')
            raise
    
    async def get_recorded_files(self) -> List[Dict[str, Any]]:
        """
        Get list of recorded files.
        
        Returns:
            Array of recorded file information
        """
        print('[OLOVideoRecording] Getting recorded files...')
        
        try:
            response = await self._send_recording_message('list_files')
            return response.get('recordings', [])
            
        except Exception as error:
            print(f'[OLOVideoRecording] Failed to get recorded files: {error}')
            raise
    
    async def delete_recording(self, filename: str) -> Dict[str, Any]:
        """
        Delete a recorded file.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            Deletion confirmation
        """
        if not filename:
            raise ValueError("Filename is required")
        
        print(f'[OLOVideoRecording] Deleting recording: {filename}')
        
        try:
            response = await self._send_recording_message('delete', {
                'filename': filename
            })
            
            print(f'[OLOVideoRecording] Recording deleted: {filename}')
            return response
            
        except Exception as error:
            print(f'[OLOVideoRecording] Failed to delete recording: {error}')
            raise
    
    def get_recording_status(self) -> Dict[str, Any]:
        """
        Get current recording status.
        
        Returns:
            Current recording status with activeRecordings count and list
        """
        return {
            'activeRecordings': len(self._active_recordings),
            'recordings': list(self._active_recordings.values())
        }
    
    def cleanup(self) -> None:
        """Clean up all recording resources"""
        self._active_recordings.clear()
        self._response_callbacks.clear()
        
        # Unregister message handler
        if self._message_handler_installed and hasattr(self, '_wrapped_handler'):
            from . import _custom_message_handlers
            try:
                if self._wrapped_handler in _custom_message_handlers:
                    _custom_message_handlers.remove(self._wrapped_handler)
            except Exception:
                pass
        
        self._message_handler_installed = False
