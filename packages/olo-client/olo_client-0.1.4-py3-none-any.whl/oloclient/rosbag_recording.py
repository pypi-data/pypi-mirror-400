"""
OLO ROSBag Recording Client - ROSBag Recording and Playback Management

Handles ROSBag recording from ROS topics, playback, session management, and file operations.
Mirrors the JavaScript OLOROSBagRecordingClient API.
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List, Callable


class OLOROSBagRecording:
    """
    ROSBag recording client for OLO robots.
    
    Provides ROSBag recording and playback capabilities including:
    - Start/stop/pause/resume recording from ROS topics
    - Start/stop/pause/resume playback of recorded bags
    - List active recordings and recorded files
    - Delete recordings
    - Completion callbacks
    
    Usage:
        # Through OLOClient
        result = await client.rosbagRecording.start_recording({
            'topics': ['/scan', '/odom'],
            'maxDurationSeconds': 30,
            'onCompleted': lambda event: print('Done!', event['filename'])
        })
        
        # Later
        await client.rosbagRecording.stop_recording(result['recordingId'])
    """
    
    def __init__(self, ros_client=None):
        """
        Initialize OLO ROSBag Recording client
        
        Args:
            ros_client: roslibpy.Ros instance (injected by OLOClient)
        """
        self._ros = ros_client
        self._connected = False
        self._request_counter = 0
        
        # Track active recordings with callbacks
        self._active_recordings: Dict[str, Dict[str, Any]] = {}
        
        # Track active playback sessions with callbacks
        self._active_playback: Dict[str, Dict[str, Any]] = {}
        
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
            # Handle all rosbag_recording_ and rosbag_playback_ prefixed messages
            if op.startswith('rosbag_recording_') or op.startswith('rosbag_playback_'):
                try:
                    self._handle_message(message)
                except Exception as e:
                    import traceback
                    print(f'[OLOROSBagRecording] Error handling {op}: {e}', flush=True)
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
    
    def _handle_message(self, message: Dict) -> None:
        """Handle incoming recording/playback messages"""
        op = message.get('op', '')
        request_id = message.get('request_id')
        
        # Handle recording events (completion callbacks)
        if op == 'rosbag_recording_event':
            self._handle_recording_event(message)
            return
        
        # Handle playback events
        if op == 'rosbag_playback_event':
            self._handle_playback_event(message)
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
        
        recording = self._active_recordings.get(recording_id)
        if not recording:
            print(f'[OLOROSBagRecording] No recording found for {recording_id}', flush=True)
            return
        
        loop = recording.get('loop')
        
        if event_type == 'recording_completed':
            # Resolve the completion future (this allows start_recording to return)
            completion_future = recording.get('completion_future')
            if completion_future and not completion_future.done() and loop:
                print(f'[OLOROSBagRecording] Resolving completion future for {recording_id}', flush=True)
                loop.call_soon_threadsafe(completion_future.set_result, message)
            
            # Call the onCompleted callback if provided
            if recording.get('onCompleted'):
                self._call_callback(recording['onCompleted'], message, loop)
            
            # Remove from active recordings
            if recording_id in self._active_recordings:
                del self._active_recordings[recording_id]
                
        elif event_type == 'recording_started':
            if recording.get('onStarted'):
                self._call_callback(recording['onStarted'], message, loop)
                
        elif event_type == 'recording_paused':
            if recording.get('onPaused'):
                self._call_callback(recording['onPaused'], message, loop)
                
        elif event_type == 'recording_resumed':
            if recording.get('onResumed'):
                self._call_callback(recording['onResumed'], message, loop)
                
        elif event_type == 'recording_split':
            if recording.get('onSplit'):
                self._call_callback(recording['onSplit'], message, loop)
    
    def _handle_playback_event(self, message: Dict) -> None:
        """Handle playback event messages from the appliance"""
        event_type = message.get('event_type')
        playback_id = message.get('playbackId')
        
        playback = self._active_playback.get(playback_id)
        if not playback:
            print(f'[OLOROSBagRecording] No playback found for {playback_id}', flush=True)
            return
        
        loop = playback.get('loop')
        
        if event_type in ('playback_completed', 'playback_stopped'):
            # Resolve the completion future
            completion_future = playback.get('completion_future')
            if completion_future and not completion_future.done() and loop:
                print(f'[OLOROSBagRecording] Resolving playback completion future for {playback_id}', flush=True)
                loop.call_soon_threadsafe(completion_future.set_result, message)
            
            # Call the appropriate callback
            callback = playback.get('onCompleted') or playback.get('onStopped')
            if callback:
                self._call_callback(callback, message, loop)
            
            # Remove from active playback
            if playback_id in self._active_playback:
                del self._active_playback[playback_id]
                
        elif event_type == 'playback_started':
            if playback.get('onStarted'):
                self._call_callback(playback['onStarted'], message, loop)
                
        elif event_type == 'playback_paused':
            if playback.get('onPaused'):
                self._call_callback(playback['onPaused'], message, loop)
                
        elif event_type == 'playback_resumed':
            if playback.get('onResumed'):
                self._call_callback(playback['onResumed'], message, loop)
    
    def _call_callback(self, callback: Callable, message: Dict, loop) -> None:
        """Call a callback in a thread-safe way"""
        try:
            if loop and loop.is_running():
                loop.call_soon_threadsafe(callback, message)
            else:
                callback(message)
        except Exception as e:
            print(f'[OLOROSBagRecording] Error in callback: {e}', flush=True)
            import traceback
            traceback.print_exc()
    
    async def _send_recording_message(self, operation: str, data: Optional[Dict] = None) -> Dict:
        """
        Send a recording message to the appliance and wait for response
        
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
        request_id = f'rosbag_{operation}_{int(time.time() * 1000)}_{self._request_counter}'
        
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
                'op': f'rosbag_recording_{operation}',
                'request_id': request_id,
                **data
            })
            
            # Wait for response with timeout
            result = await asyncio.wait_for(future, timeout=30.0)
            
            if result.get('success'):
                return result
            else:
                error = Exception(result.get('error', f'{operation} failed'))
                if result.get('existingRecording'):
                    error.code = 'RECORDING_ALREADY_ACTIVE'
                    error.existingRecording = result.get('existingRecording')
                raise error
                
        except asyncio.TimeoutError:
            raise TimeoutError(f'Timeout waiting for {operation} response')
        finally:
            # Remove callback entry
            if request_id in self._response_callbacks:
                del self._response_callbacks[request_id]
    
    async def _send_playback_message(self, operation: str, data: Optional[Dict] = None) -> Dict:
        """
        Send a playback message to the appliance and wait for response
        
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
        request_id = f'playback_{operation}_{int(time.time() * 1000)}_{self._request_counter}'
        
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
                'op': f'rosbag_playback_{operation}',
                'request_id': request_id,
                **data
            })
            
            # Wait for response with timeout
            result = await asyncio.wait_for(future, timeout=30.0)
            
            if result.get('success'):
                return result
            else:
                error = Exception(result.get('error', f'{operation} failed'))
                if result.get('existingPlayback'):
                    error.code = 'PLAYBACK_ALREADY_ACTIVE'
                    error.existingPlayback = result.get('existingPlayback')
                raise error
                
        except asyncio.TimeoutError:
            raise TimeoutError(f'Timeout waiting for {operation} response')
        finally:
            # Remove callback entry
            if request_id in self._response_callbacks:
                del self._response_callbacks[request_id]
    
    # ==================== Recording Methods ====================
    
    async def start_recording(self, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Start recording ROS topics to a bag file.
        
        Args:
            options: Recording options:
                - topics: List of topics to record (required if recordAll is False)
                - recordAll: Record all topics (default: False)
                - filename: Custom filename (optional)
                - maxDurationSeconds: Auto-stop after this many seconds (optional)
                - maxFileSizeBytes: Max bytes per file (default: 2GB)
                - maxDurationPerFileSeconds: Max duration per file (default: 600s)
                - compression: Compression format: 'zstd', 'lz4', 'none' (default: 'none')
                - storageFormat: Storage format: 'mcap', 'sqlite3' (default: 'sqlite3')
                - qosOverrides: QoS overrides (optional)
                - nodeNamespace: ROS node namespace (default: '/olo/rosbag')
                - onCompleted: Callback when recording completes (optional)
                - onPaused: Callback when recording is paused (optional)
                - onResumed: Callback when recording is resumed (optional)
                - onSplit: Callback when recording is split (optional)
                - onStarted: Callback when recording starts (optional)
                
        Returns:
            Recording session information with recordingId, filename, etc.
            If maxDurationSeconds is set, waits for recording to complete.
        """
        if options is None:
            options = {}
        
        topics = options.get('topics', [])
        record_all = options.get('recordAll', False)
        filename = options.get('filename')
        max_duration = options.get('maxDurationSeconds')
        max_file_size = options.get('maxFileSizeBytes', 2000000000)
        max_duration_per_file = options.get('maxDurationPerFileSeconds', 600)
        compression = options.get('compression', 'none')
        storage_format = options.get('storageFormat', 'sqlite3')
        qos_overrides = options.get('qosOverrides')
        node_namespace = options.get('nodeNamespace', '/olo/rosbag')
        
        on_completed = options.get('onCompleted')
        on_paused = options.get('onPaused')
        on_resumed = options.get('onResumed')
        on_split = options.get('onSplit')
        on_started = options.get('onStarted')
        
        if not record_all and (not topics or len(topics) == 0):
            raise ValueError('Either specify topics to record or set recordAll to True')
        
        print(f'[OLOROSBagRecording] Starting recording with {len(topics)} topics')
        
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
                'topics': topics,
                'recordAll': record_all,
                'filename': filename,
                'maxDurationSeconds': max_duration,
                'maxFileSizeBytes': max_file_size,
                'maxDurationPerFileSeconds': max_duration_per_file,
                'compression': compression,
                'storageFormat': storage_format,
                'qosOverrides': qos_overrides,
                'nodeNamespace': node_namespace
            })
            
            # Store recording info locally with callbacks and completion future
            recording_id = response.get('recordingId')
            self._active_recordings[recording_id] = {
                'recordingId': recording_id,
                'filename': response.get('filename'),
                'topics': topics,
                'recordAll': record_all,
                'startTime': response.get('startTime'),
                'onCompleted': on_completed,
                'onPaused': on_paused,
                'onResumed': on_resumed,
                'onSplit': on_split,
                'onStarted': on_started,
                'loop': loop,
                'completion_future': completion_future
            }
            
            print(f'[OLOROSBagRecording] Recording started: {recording_id}')
            
            # If maxDurationSeconds is set, wait for the recording to complete
            if max_duration and completion_future:
                print(f'[OLOROSBagRecording] Waiting for recording to complete (max {max_duration}s)...')
                try:
                    # Wait for completion with timeout buffer
                    completion_result = await asyncio.wait_for(
                        completion_future, 
                        timeout=max_duration + 60  # Extra buffer for file finalization
                    )
                    print(f'[OLOROSBagRecording] Recording completed: {completion_result.get("filename")}')
                    response['completion'] = completion_result
                except asyncio.TimeoutError:
                    print(f'[OLOROSBagRecording] Timeout waiting for recording completion')
                    response['timeout'] = True
            
            return response
            
        except Exception as error:
            print(f'[OLOROSBagRecording] Failed to start recording: {error}')
            raise
    
    async def stop_recording(self, recording_id: str) -> Dict[str, Any]:
        """
        Stop a recording.
        
        Args:
            recording_id: Recording ID to stop
            
        Returns:
            Stop result with file information
        """
        if not recording_id:
            raise ValueError('Recording ID is required')
        
        result = await self._send_recording_message('stop', {'recordingId': recording_id})
        
        # Clean up local tracking
        if recording_id in self._active_recordings:
            del self._active_recordings[recording_id]
        
        return result
    
    async def pause_recording(self, recording_id: str) -> Dict[str, Any]:
        """
        Pause a recording.
        
        Args:
            recording_id: Recording ID to pause
            
        Returns:
            Pause result
        """
        if not recording_id:
            raise ValueError('Recording ID is required')
        
        return await self._send_recording_message('pause', {'recordingId': recording_id})
    
    async def resume_recording(self, recording_id: str) -> Dict[str, Any]:
        """
        Resume a recording.
        
        Args:
            recording_id: Recording ID to resume
            
        Returns:
            Resume result
        """
        if not recording_id:
            raise ValueError('Recording ID is required')
        
        return await self._send_recording_message('resume', {'recordingId': recording_id})
    
    async def split_recording(self, recording_id: str) -> Dict[str, Any]:
        """
        Split a recording into a new file.
        
        Args:
            recording_id: Recording ID to split
            
        Returns:
            Split result
        """
        if not recording_id:
            raise ValueError('Recording ID is required')
        
        return await self._send_recording_message('split', {'recordingId': recording_id})
    
    async def get_active_recordings(self) -> List[Dict[str, Any]]:
        """
        Get list of active recordings.
        
        Returns:
            Array of active recordings
        """
        result = await self._send_recording_message('list_active', {})
        return result.get('activeRecordings', [])
    
    async def get_recorded_files(self) -> List[Dict[str, Any]]:
        """
        Get list of recorded bag files.
        
        Returns:
            Array of recorded files
        """
        result = await self._send_recording_message('list_files', {})
        return result.get('recordings', [])
    
    async def delete_recording(self, recording_name: str) -> Dict[str, Any]:
        """
        Delete a recorded bag.
        
        Args:
            recording_name: Name of recording directory to delete
            
        Returns:
            Delete result
        """
        if not recording_name:
            raise ValueError('Recording name is required')
        
        return await self._send_recording_message('delete', {'recordingName': recording_name})
    
    async def stop_all_recordings(self) -> List[Dict[str, Any]]:
        """
        Stop all active recordings.
        
        Returns:
            Array of stop results
        """
        active_recordings = await self.get_active_recordings()
        results = []
        
        for recording in active_recordings:
            try:
                result = await self.stop_recording(recording.get('recordingId'))
                results.append(result)
            except Exception as e:
                results.append({
                    'recordingId': recording.get('recordingId'),
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    async def stop_recordings_by_topics(self, topics: List[str]) -> List[Dict[str, Any]]:
        """
        Stop recordings by topics.
        
        Args:
            topics: Topics to stop recording
            
        Returns:
            Array of stop results
        """
        if not topics or len(topics) == 0:
            return []
        
        active_recordings = await self.get_active_recordings()
        results = []
        
        for recording in active_recordings:
            recording_topics = recording.get('topics', [])
            # Check if any topic matches
            has_matching_topic = any(
                topic in topics or topic == 'all'
                for topic in recording_topics
            )
            
            if has_matching_topic:
                try:
                    result = await self.stop_recording(recording.get('recordingId'))
                    results.append(result)
                except Exception as e:
                    results.append({
                        'recordingId': recording.get('recordingId'),
                        'success': False,
                        'error': str(e)
                    })
        
        return results
    
    # ==================== Playback Methods ====================
    
    async def start_playback(
        self, 
        recording_name: str, 
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start playing back a recorded bag file.
        
        Args:
            recording_name: Name of the recording directory to play
            options: Playback options:
                - playbackRate: Playback speed multiplier (default: 1.0)
                - loop: Whether to loop playback (default: False)
                - startOffset: Seconds to skip at start (default: 0)
                - topics: Specific topics to play (default: all)
                - clockType: Clock type: 'ros_time' or 'system_time' (default: 'ros_time')
                - onCompleted: Callback when playback completes (optional)
                - onPaused: Callback when playback is paused (optional)
                - onResumed: Callback when playback is resumed (optional)
                - onStopped: Callback when playback is stopped (optional)
                
        Returns:
            Playback information with playbackId
        """
        if not recording_name:
            raise ValueError('Recording name is required for playback')
        
        if options is None:
            options = {}
        
        playback_rate = options.get('playbackRate', 1.0)
        loop_playback = options.get('loop', False)
        start_offset = options.get('startOffset', 0)
        topics = options.get('topics', [])
        clock_type = options.get('clockType', 'ros_time')
        
        on_completed = options.get('onCompleted')
        on_paused = options.get('onPaused')
        on_resumed = options.get('onResumed')
        on_stopped = options.get('onStopped')
        
        print(f'[OLOROSBagRecording] Starting playback for: {recording_name}')
        
        try:
            # Capture the current event loop
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop()
            
            response = await self._send_playback_message('start', {
                'recordingName': recording_name,
                'playbackRate': playback_rate,
                'loop': loop_playback,
                'startOffset': start_offset,
                'topics': topics,
                'clockType': clock_type
            })
            
            # Store playback info locally with callbacks
            playback_id = response.get('playbackId')
            self._active_playback[playback_id] = {
                'playbackId': playback_id,
                'recordingName': recording_name,
                'playbackRate': playback_rate,
                'loop': loop_playback,
                'onCompleted': on_completed,
                'onPaused': on_paused,
                'onResumed': on_resumed,
                'onStopped': on_stopped,
                'loop': loop  # asyncio loop reference
            }
            
            print(f'[OLOROSBagRecording] Playback started: {playback_id}')
            
            return response
            
        except Exception as error:
            print(f'[OLOROSBagRecording] Failed to start playback: {error}')
            raise
    
    async def stop_playback(self, playback_id: str) -> Dict[str, Any]:
        """
        Stop playback.
        
        Args:
            playback_id: ID of the playback to stop
            
        Returns:
            Playback stop information
        """
        if not playback_id:
            raise ValueError('Playback ID is required')
        
        result = await self._send_playback_message('stop', {'playbackId': playback_id})
        
        # Clean up local tracking
        if playback_id in self._active_playback:
            del self._active_playback[playback_id]
        
        return result
    
    async def pause_playback(self, playback_id: str) -> Dict[str, Any]:
        """
        Pause playback.
        
        Args:
            playback_id: ID of the playback to pause
            
        Returns:
            Pause result
        """
        if not playback_id:
            raise ValueError('Playback ID is required')
        
        return await self._send_playback_message('pause', {'playbackId': playback_id})
    
    async def resume_playback(self, playback_id: str) -> Dict[str, Any]:
        """
        Resume playback.
        
        Args:
            playback_id: ID of the playback to resume
            
        Returns:
            Resume result
        """
        if not playback_id:
            raise ValueError('Playback ID is required')
        
        return await self._send_playback_message('resume', {'playbackId': playback_id})
    
    async def control_playback(
        self, 
        playback_id: str, 
        action: str, 
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Control playback (rate, seeking, etc.).
        
        Args:
            playback_id: ID of the playback to control
            action: Control action: 'play', 'pause', 'stop', 'rate', 'seek'
            params: Action parameters (e.g., {'speed': 2.0} or {'position': 30})
            
        Returns:
            Control result
        """
        if not playback_id:
            raise ValueError('Playback ID is required')
        
        return await self._send_playback_message('control', {
            'playbackId': playback_id,
            'action': action,
            'params': params or {}
        })
    
    async def get_active_playback(self) -> List[Dict[str, Any]]:
        """
        Get list of active playback sessions.
        
        Returns:
            Array of active playback sessions
        """
        result = await self._send_playback_message('list_active', {})
        return result.get('activePlayback', [])
    
    async def stop_all_playback(self) -> List[Dict[str, Any]]:
        """
        Stop all active playback sessions.
        
        Returns:
            Array of stop results
        """
        active_playback = await self.get_active_playback()
        results = []
        
        for playback in active_playback:
            try:
                result = await self.stop_playback(playback.get('playbackId'))
                results.append(result)
            except Exception as e:
                results.append({
                    'playbackId': playback.get('playbackId'),
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def cleanup(self):
        """Clean up resources"""
        
        # Clear active recordings and playback
        self._active_recordings.clear()
        self._active_playback.clear()
        self._response_callbacks.clear()
        
        # Unregister message handler
        if self._message_handler_installed and hasattr(self, '_wrapped_handler'):
            from . import _custom_message_handlers
            if self._wrapped_handler in _custom_message_handlers:
                _custom_message_handlers.remove(self._wrapped_handler)
            self._message_handler_installed = False

