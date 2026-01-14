"""
OLO Vision Client - Vision AI Analysis Management

Handles vision AI providers, analysis sessions, and real-time computer vision.
Uses server-side processing on the Appliance for better performance and resource management.
Mirrors the JavaScript OLOVisionClient API.
"""

import asyncio
import inspect
import json
import time
from typing import Dict, Any, Optional, List, Callable


class OLOVision:
    """
    Vision AI analysis client for OLO robots.
    
    Provides vision AI capabilities including:
    - Configure vision providers (OpenAI GPT-4V, YOLO, Motion Detection)
    - Start/stop vision analysis sessions
    - Real-time analysis results via callbacks
    - Query analysis results
    
    Usage:
        # Through OLOClient
        providers = await client.vision.get_available_vision_providers()
        
        # Configure OpenAI provider
        await client.vision.configure_vision_provider('openai-gpt4v', {
            'apiKey': 'your-api-key',
            'model': 'gpt-4o'
        })
        
        # Start vision analysis
        analysis_id = await client.vision.start_vision_analysis(
            '/camera/image_raw/compressed',
            'yolo',
            {
                'onResult': lambda result, ts, aid: print(f'Detection: {result}'),
                'onError': lambda error: print(f'Error: {error}'),
                'intervalMs': 2000
            }
        )
        
        # Later
        await client.vision.stop_vision_analysis(analysis_id)
    """
    
    def __init__(self, ros_client=None):
        """
        Initialize OLO Vision client
        
        Args:
            ros_client: roslibpy.Ros instance (injected by OLOClient)
        """
        self._ros = ros_client
        self._connected = False
        self._request_counter = 0
        
        # Track active analysis sessions
        self._active_analysis: Dict[str, Dict[str, Any]] = {}
        
        # Available providers cache
        self._vision_providers: List[Dict[str, Any]] = []
        
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
        """Set up message handler for vision events and responses"""
        if self._message_handler_installed:
            return
        
        if not self._ros:
            return
        
        def handler(message: Dict[str, Any]) -> None:
            op = message.get('op', '')
            # Handle all vision_analysis_ prefixed messages
            if op.startswith('vision_analysis_'):
                try:
                    self._handle_vision_message(message)
                except Exception as e:
                    import traceback
                    print(f'[OLOVision] Error handling {op}: {e}', flush=True)
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
    
    def _handle_vision_message(self, message: Dict) -> None:
        """Handle incoming vision messages"""
        op = message.get('op', '')
        request_id = message.get('request_id')
        
        # Handle vision analysis events
        if op == 'vision_analysis_event':
            self._handle_analysis_event(message)
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
    
    def _handle_analysis_event(self, message: Dict) -> None:
        """Handle vision analysis event messages from the appliance"""
        event_type = message.get('event_type')
        analysis_id = message.get('analysisId')
        
        session = self._active_analysis.get(analysis_id)
        if not session:
            return
        
        loop = session.get('loop')
        
        if event_type == 'analysis_result':
            if session.get('is_running'):
                # Call the onResult callback if provided
                on_result = session.get('onResult')
                if on_result:
                    try:
                        result = message.get('result', {})
                        timestamp = message.get('timestamp', int(time.time() * 1000))
                        
                        if loop and loop.is_running():
                            loop.call_soon_threadsafe(on_result, result, timestamp, analysis_id)
                        else:
                            on_result(result, timestamp, analysis_id)
                    except Exception as e:
                        print(f'[OLOVision] Error in onResult callback: {e}', flush=True)
        
        elif event_type == 'analysis_error':
            if session.get('is_running'):
                on_error = session.get('onError')
                if on_error:
                    try:
                        error_msg = message.get('error', 'Unknown error')
                        
                        if loop and loop.is_running():
                            loop.call_soon_threadsafe(on_error, error_msg)
                        else:
                            on_error(error_msg)
                    except Exception as e:
                        print(f'[OLOVision] Error in onError callback: {e}', flush=True)
        
        elif event_type == 'analysis_completed':
            print(f'[OLOVision] Analysis completed: {analysis_id}', flush=True)
            session['is_running'] = False
            
            # Resolve completion future if waiting
            completion_future = session.get('completion_future')
            if completion_future and not completion_future.done() and loop:
                loop.call_soon_threadsafe(completion_future.set_result, message)
            
            # Call the onStopped callback if provided
            on_stopped = session.get('onStopped')
            if on_stopped:
                try:
                    if loop and loop.is_running():
                        loop.call_soon_threadsafe(on_stopped, analysis_id)
                    else:
                        on_stopped(analysis_id)
                except Exception as e:
                    print(f'[OLOVision] Error in onStopped callback: {e}', flush=True)
            
            # Remove from active sessions
            if analysis_id in self._active_analysis:
                del self._active_analysis[analysis_id]
    
    async def _send_vision_message(self, operation: str, data: Optional[Dict] = None) -> Dict:
        """
        Send a message to the appliance and wait for response
        
        Args:
            operation: Operation name (e.g., 'start', 'stop', 'get_providers')
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
        request_id = f'vision_{operation}_{int(time.time() * 1000)}_{self._request_counter}'
        
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
                'op': f'vision_analysis_{operation}',
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
            # Clean up callback
            if request_id in self._response_callbacks:
                del self._response_callbacks[request_id]
    
    async def configure_vision_provider(
        self,
        provider_name: str,
        config: Dict[str, Any]
    ) -> bool:
        """
        Configure a vision provider on the server (e.g., set API key)
        
        Args:
            provider_name: Provider name (e.g., 'openai-gpt4v')
            config: Provider configuration
                - apiKey: API key for providers that require it
                - model: Model name for AI providers
                - maxTokens: Max tokens for AI providers
                - sensitivity: Sensitivity for motion detection
                - confidenceThreshold: Confidence threshold for object detection
        
        Returns:
            True if provider was configured successfully
        """
        result = await self._send_vision_message('configure_provider', {
            'providerName': provider_name,
            'config': config
        })
        
        print(f"[OLOVision] Provider '{provider_name}' configured successfully")
        return True
    
    async def get_available_vision_providers(self) -> List[Dict[str, Any]]:
        """
        Get available vision providers and their capabilities from the server
        
        Returns:
            Array of provider info objects with fields:
                - name: Provider identifier
                - displayName: Human-readable name
                - description: Provider description
                - requiresApiKey: Whether API key is needed
                - isConfigured: Whether provider is ready to use
                - capabilities: List of provider capabilities
        """
        result = await self._send_vision_message('get_providers', {})
        
        self._vision_providers = result.get('providers', [])
        return self._vision_providers
    
    async def start_vision_analysis(
        self,
        topic_or_filename: str,
        provider_name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start vision analysis on a camera topic or playback video
        
        Args:
            topic_or_filename: Camera topic to analyze (e.g., '/camera/image_raw/compressed')
                              or filename for playback video
            provider_name: Name of vision provider to use ('yolo', 'motion_detection', 'openai-gpt4v')
            config: Analysis configuration
                - onResult: Callback for analysis results (result, timestamp, analysisId)
                - onError: Callback for analysis errors (error)
                - onStopped: Callback when analysis is stopped (analysisId)
                - prompt: Optional prompt for LLM providers
                - intervalMs: Analysis interval in milliseconds (default: 2000)
                - showBoundingBoxes: Enable visual bounding boxes (for object detection)
                - isPlayback: True if analyzing playback video, false for ROS topic
                - playbackOptions: Options for playback analysis (loop, playbackSpeed)
        
        Returns:
            Analysis session ID
        """
        if config is None:
            config = {}
        
        # Auto-detect if this is playback based on filename extension or explicit config
        is_playback = config.get('isPlayback')
        if is_playback is None:
            is_playback = (
                '.mp4' in topic_or_filename or 
                '.avi' in topic_or_filename or 
                '.mkv' in topic_or_filename or 
                not topic_or_filename.startswith('/')
            )
        
        # Build request data - exclude non-serializable objects and callback functions
        excluded_keys = ['onResult', 'onError', 'onStopped', 'playbackOptions', 'videoElement', 'boundingBoxOptions']
        request_data = {
            'providerName': provider_name,
            'config': {k: v for k, v in config.items() if k not in excluded_keys},
            'intervalMs': config.get('intervalMs', 2000),
            'prompt': config.get('prompt'),
            'showBoundingBoxes': config.get('showBoundingBoxes', False),
            'boundingBoxOptions': config.get('boundingBoxOptions', {})
        }
        
        if is_playback:
            request_data['filename'] = topic_or_filename
            if config.get('playbackOptions'):
                request_data['playbackOptions'] = config['playbackOptions']
        else:
            request_data['topic'] = topic_or_filename
        
        result = await self._send_vision_message('start', request_data)
        
        analysis_id = result.get('analysisId')
        print(f"[OLOVision] Started vision analysis: {analysis_id} ({provider_name}) on {'playback' if is_playback else 'topic'} {topic_or_filename}")
        
        # Create local session tracking
        loop = asyncio.get_event_loop()
        session = {
            'id': analysis_id,
            'provider': provider_name,
            'topic': None if is_playback else topic_or_filename,
            'filename': topic_or_filename if is_playback else None,
            'source_id': topic_or_filename,
            'source_type': 'playback' if is_playback else 'ros_topic',
            'is_playback': is_playback,
            'config': config,
            'onResult': config.get('onResult'),
            'onError': config.get('onError'),
            'onStopped': config.get('onStopped'),
            'start_time': time.time(),
            'is_running': True,
            'loop': loop
        }
        
        self._active_analysis[analysis_id] = session
        
        return analysis_id
    
    async def stop_vision_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """
        Stop vision analysis
        
        Args:
            analysis_id: Analysis session ID
        
        Returns:
            Response message
        """
        session = self._active_analysis.get(analysis_id)
        if not session:
            print(f'[OLOVision] Vision analysis session not found: {analysis_id}')
            return {'success': True, 'message': 'Session not found'}
        
        print(f'[OLOVision] Stopping vision analysis: {analysis_id}')
        session['is_running'] = False
        
        try:
            result = await self._send_vision_message('stop', {
                'analysisId': analysis_id
            })
        except Exception as e:
            print(f'[OLOVision] Error stopping analysis: {e}')
            result = {'success': False, 'error': str(e)}
        
        # Clean up local session
        if analysis_id in self._active_analysis:
            on_stopped = self._active_analysis[analysis_id].get('onStopped')
            del self._active_analysis[analysis_id]
            
            if on_stopped:
                try:
                    on_stopped(analysis_id)
                except Exception as e:
                    print(f'[OLOVision] Error in onStopped callback: {e}')
        
        return result
    
    async def stop_all_vision_analysis(self) -> None:
        """Stop all active vision analysis sessions"""
        analysis_ids = list(self._active_analysis.keys())
        
        for analysis_id in analysis_ids:
            try:
                await self.stop_vision_analysis(analysis_id)
            except Exception as e:
                print(f'[OLOVision] Error stopping analysis {analysis_id}: {e}')
    
    async def get_vision_analysis_results(
        self,
        analysis_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get vision analysis results from server
        
        Args:
            analysis_id: Analysis session ID
            options: Options for result retrieval
                - limit: Maximum number of results to return
                - since: Only return results after this timestamp
        
        Returns:
            Array of analysis results
        """
        if options is None:
            options = {}
        
        result = await self._send_vision_message('get_results', {
            'analysisId': analysis_id,
            'limit': options.get('limit'),
            'since': options.get('since')
        })
        
        return result.get('results', [])
    
    async def get_active_vision_analysis_sessions(self) -> List[Dict[str, Any]]:
        """
        Get active vision analysis sessions from server
        
        Returns:
            Array of active analysis session info
        """
        result = await self._send_vision_message('list_active', {})
        
        return result.get('activeAnalysis', [])
    
    async def register_custom_provider(
        self,
        provider_name: str,
        analyze_frame,  # Callable[[bytes, dict], dict]
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        capabilities: Optional[List[str]] = None
    ) -> bool:
        """
        Register a custom vision provider.
        The provider will persist in appliance memory until unregistered or appliance restart.
        
        When running in SDK Playground (on the appliance), the function is stored locally
        in the Python subprocess and frames are processed in-process for best performance.
        
        Args:
            provider_name: Unique name for the provider (cannot override built-in providers)
            analyze_frame: A function that takes (image_buffer: bytes, config: dict) and returns a dict
            display_name: Human-readable name for the provider
            description: Description of what the provider does
            capabilities: List of capabilities (e.g., ['object_detection', 'bounding_boxes'])
        
        Returns:
            True if provider was registered successfully
            
        Example:
            def analyze_frame(image_buffer: bytes, config: dict) -> dict:
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(image_buffer))
                avg = sum(img.convert('L').getdata()) / (img.width * img.height)
                return {'brightness': avg, 'is_light': avg > 128}
            
            await client.vision.register_custom_provider(
                'brightness_detector',
                analyze_frame,
                display_name='Brightness Detector'
            )
        """
        if not provider_name or not isinstance(provider_name, str):
            raise ValueError("Provider name must be a non-empty string")
        
        if not callable(analyze_frame):
            raise ValueError("analyze_frame must be a callable function")
        
        # Check if we're running in the appliance context (SDK Playground)
        # The appliance wrapper injects _register_vision_provider into globals
        import builtins
        register_local = getattr(builtins, '_register_vision_provider', None)
        
        # Also check the frame's globals (for exec'd code)
        if register_local is None:
            import sys
            frame = sys._getframe(1)
            while frame:
                if '_register_vision_provider' in frame.f_globals:
                    register_local = frame.f_globals['_register_vision_provider']
                    break
                frame = frame.f_back
        
        if register_local is not None:
            # Running on appliance - register function locally for in-process execution
            register_local(provider_name, analyze_frame)
            
            # Get execution ID from environment (set by PythonExecutor)
            import os
            execution_id = os.environ.get('OLO_EXECUTION_ID')
            
            # Send registration message to VisionAnalysisService (no code, just metadata)
            # VisionAnalysisService will know to route frames to this Python subprocess
            result = await self._send_vision_message('register_provider', {
                'providerName': provider_name,
                'language': 'python',
                'inProcess': True,  # Flag indicating in-process execution
                'executionId': execution_id,  # ID to route frames to
                'displayName': display_name or provider_name,
                'description': description or 'Custom Python vision provider',
                'capabilities': capabilities or ['custom_analysis']
            })
        else:
            # Running externally - need to send code to appliance
            # Try to get source code from the function
            try:
                analyze_frame_code = inspect.getsource(analyze_frame)
            except (OSError, TypeError) as e:
                raise ValueError(f"Could not get source code of analyze_frame function: {e}. "
                               "This typically happens when running code interactively. "
                               "Try running your code as a script file instead.")
            
            # Dedent the code if it was defined inside another function/class
            analyze_frame_code = inspect.cleandoc(analyze_frame_code)
            
            result = await self._send_vision_message('register_provider', {
                'providerName': provider_name,
                'language': 'python',
                'inProcess': False,
                'analyzeFrameCode': analyze_frame_code,
                'displayName': display_name or provider_name,
                'description': description or 'Custom Python vision provider',
                'capabilities': capabilities or ['custom_analysis']
            })
        
        print(f"[OLOVision] Custom provider '{provider_name}' registered successfully")
        return True
    
    async def unregister_custom_provider(self, provider_name: str) -> bool:
        """
        Unregister a custom vision provider
        
        Args:
            provider_name: Name of the provider to unregister
        
        Returns:
            True if provider was unregistered successfully
        """
        if not provider_name or not isinstance(provider_name, str):
            raise ValueError("Provider name must be a non-empty string")
        
        result = await self._send_vision_message('unregister_provider', {
            'providerName': provider_name
        })
        
        print(f"[OLOVision] Custom provider '{provider_name}' unregistered successfully")
        return True
    
    def cleanup(self) -> None:
        """Clean up resources"""
        
        # Unregister message handler
        if hasattr(self, '_wrapped_handler') and self._wrapped_handler:
            try:
                from . import _custom_message_handlers
                if self._wrapped_handler in _custom_message_handlers:
                    _custom_message_handlers.remove(self._wrapped_handler)
            except Exception:
                pass
        
        # Clear active sessions
        self._active_analysis.clear()
        self._response_callbacks.clear()
        self._message_handler_installed = False

