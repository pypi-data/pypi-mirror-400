"""
OLO Client - Python SDK for ROS robot control
Connects to ROS via roslibpy through WebSocket

Usage:
    from oloclient import OLOClient

    # Direct ROS connection
    async with OLOClient(ros_url='ws://localhost:9090') as client:
        topics = await client.core.list_topics()
        print(topics)
    
    # Platform connection with authentication
    client = OLOClient(
        server_url='wss://app.olo-robotics.com',
        api_url='https://app.olo-robotics.com'
    )
    await client.authenticate('user@example.com', 'password')
    robots = await client.get_user_robots()
    await client.connect(robot_id=robots[0]['id'])
    
    # Control the robot
    await client.core.move_for({'linear': 0.3, 'angular': 0}, 2000)
"""

# Global registry for custom platform message handlers
# Handles WebRTC, navigation, video recording, and other non-rosbridge messages
_custom_message_handlers = []

# Alias for backwards compatibility
_webrtc_message_handlers = _custom_message_handlers

def register_custom_handler(handler):
    """Register a handler for custom platform messages"""
    if handler not in _custom_message_handlers:
        _custom_message_handlers.append(handler)

def unregister_custom_handler(handler):
    """Unregister a custom platform message handler"""
    if handler in _custom_message_handlers:
        _custom_message_handlers.remove(handler)

# Backwards compatible aliases
def register_webrtc_handler(handler):
    """Register a handler for WebRTC messages (deprecated, use register_custom_handler)"""
    register_custom_handler(handler)

def unregister_webrtc_handler(handler):
    """Unregister a WebRTC message handler (deprecated, use unregister_custom_handler)"""
    unregister_custom_handler(handler)

# Patch roslibpy to handle custom OLO operations silently
# This must be done before any roslibpy usage
def _patch_roslibpy_for_olo():
    """
    Monkey-patch roslibpy to silently ignore custom OLO platform operations.
    The OLO platform sends custom WebSocket messages that aren't standard rosbridge.
    """
    try:
        from roslibpy.comm import comm
        
        # Store original on_message
        original_on_message = comm.RosBridgeProtocol.on_message
        
        # Custom operations that OLO platform may send (to ignore)
        custom_ops = {
            'execution_complete', 'execution_error', 'execution_stopped',
            'execution_output', 'script_execution_started', 
            'video_offer', 'video_answer', 'ice_candidate', 'turn_credentials',
            'robot_status', 'connection_info',
            # Status/scheduling operations
            'execution_status_all', 'schedule_list', 'execution_status',
            'robot_state', 'robot_list', 'config_update',
        }
        
        # Custom platform operations that need to be routed to handlers
        # (WebRTC, navigation, video recording, etc.)
        platform_ops = {
            'webrtc_session_started', 'webrtc_answer', 'webrtc_ice_candidate',
            'webrtc_error', 'webrtc_stop_session', 'webrtc_playback_ended',
            'turn_credentials_response',
            # Navigation operations
            'ros2_nav_ack', 'ros2_nav_status', 'ros2_nav_feedback', 
            'ros2_nav_result', 'ros2_nav_cancelled',
            'nav2_log', 'nav2_status', 'nav2_start_result', 'nav2_stop_result',
            'nav2_status_response',
            # Map operations
            'ros2_save_map_ack', 'map_save_response', 'map_list_response',
            'map_get_response', 'map_delete_response', 'map_storage_stats_response',
            'ros2_load_map_ack', 'ros2_load_map_result', 'ros2_save_map_result',
            # Video recording operations
            'video_recording_event', 'video_recording_start_response',
            'video_recording_stop_response', 'video_recording_list_active_response',
            'video_recording_list_files_response', 'video_recording_delete_response',
            # ROSBag recording operations
            'rosbag_recording_event', 'rosbag_recording_start_response',
            'rosbag_recording_stop_response', 'rosbag_recording_pause_response',
            'rosbag_recording_resume_response', 'rosbag_recording_split_response',
            'rosbag_recording_list_active_response', 'rosbag_recording_list_files_response',
            'rosbag_recording_delete_response',
            # ROSBag playback operations
            'rosbag_playback_event', 'rosbag_playback_start_response',
            'rosbag_playback_stop_response', 'rosbag_playback_pause_response',
            'rosbag_playback_resume_response', 'rosbag_playback_control_response',
            'rosbag_playback_list_active_response',
            # Vision analysis operations
            'vision_analysis_event', 'vision_analysis_start_response',
            'vision_analysis_stop_response', 'vision_analysis_get_providers_response',
            'vision_analysis_configure_provider_response', 'vision_analysis_get_results_response',
            'vision_analysis_list_active_response',
            # Global variables operations
            'global_set', 'global_value', 'all_globals', 'global_deleted',
            'globals_cleared', 'global_error'
        }
        
        def patched_on_message(self, payload):
            """Handle message, routing WebRTC ops and ignoring custom OLO operations."""
            import json
            try:
                # Decode for inspection only
                if isinstance(payload, (bytes, bytearray)):
                    message_str = payload.decode('utf-8')
                else:
                    message_str = payload
                    
                msg = json.loads(message_str)
                op = msg.get('op', '')
                
                # Debug: log video recording messages
                
                # Route custom platform operations to registered handlers
                if (op in platform_ops or op.startswith('webrtc_') or 
                    op.startswith('video_recording_') or 
                    op.startswith('rosbag_recording_') or op.startswith('rosbag_playback_') or
                    op.startswith('vision_analysis_')):
                    for handler in _custom_message_handlers:
                        try:
                            handler(msg)
                        except Exception as e:
                            print(f'[OLO] Custom message handler error: {e}')
                    return  # Don't pass to roslibpy
                
                # Silently ignore other custom OLO operations
                if op in custom_ops:
                    return
                
                # Pass original payload to original handler for standard rosbridge ops
                # Wrap in try/except to suppress orphaned service response errors
                try:
                    return original_on_message(self, payload)
                except Exception:
                    # Silently ignore orphaned service responses
                    pass
            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                # Not valid JSON, pass to original handler
                try:
                    return original_on_message(self, payload)
                except Exception:
                    pass
        
        # Apply patch
        comm.RosBridgeProtocol.on_message = patched_on_message
        
    except Exception:
        # If patching fails, continue without it
        pass

# Apply patch at import time
_patch_roslibpy_for_olo()

from .client import OLOClient
from .core import OLOCore
from .logs import OLOLogs
from .auth import OLOAuth
from .video import OLOVideo
from .video_recording import OLOVideoRecording
from .rosbag_recording import OLOROSBagRecording
from .vision import OLOVision
from .joint import OLOJoint
from .navigation import OLONavigation
from .globals import OLOGlobals


class AbortController:
    """
    Abort controller for cancellable operations.
    Similar to JavaScript's AbortController.
    
    Usage:
        controller = AbortController()
        signal = controller.signal
        
        # Pass signal to operations
        await client.core.move_for(velocity, duration, {'abortSignal': signal})
        
        # To abort:
        controller.abort()
    """
    
    def __init__(self):
        self._signal = {'aborted': False}
    
    @property
    def signal(self):
        """Get the abort signal dict"""
        return self._signal
    
    def abort(self):
        """Abort the operation"""
        self._signal['aborted'] = True


__version__ = '0.1.0'
__all__ = ['OLOClient', 'OLOCore', 'OLOLogs', 'OLOAuth', 'OLOVideo', 'OLOVideoRecording', 
           'OLOROSBagRecording', 'OLOVision', 'OLOJoint', 'OLONavigation', 'OLOGlobals',
           'AbortController', 'register_custom_handler', 'unregister_custom_handler',
           'register_webrtc_handler', 'unregister_webrtc_handler']

