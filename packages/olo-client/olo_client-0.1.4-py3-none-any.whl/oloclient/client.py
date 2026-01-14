"""
OLO Client - Main client class
"""

import os
import asyncio
from typing import Optional, Dict, Any, List

try:
    import roslibpy
except ImportError:
    raise ImportError(
        "roslibpy is required. Install it with: pip install roslibpy"
    )

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


class OLOClient:
    """
    Main OLO Client class
    Provides access to ROS functionality through a WebSocket connection
    
    Usage:
        # Option 1: Direct ROS URL (for local development)
        client = OLOClient(ros_url='ws://localhost:9090')
        await client.connect()
        
        # Option 2: OLO Platform with authentication
        client = OLOClient(
            server_url='wss://app.olo-robotics.com',
            api_url='https://app.olo-robotics.com'
        )
        # Authenticate and get robots
        await client.authenticate('user@example.com', 'password')
        robots = await client.get_user_robots()
        # Connect to a specific robot
        await client.connect(robot_id=robots[0]['id'])
        
        # Option 3: Direct robot connection with token
        client = OLOClient(server_url='wss://app.olo-robotics.com')
        await client.connect(robot_id='my-robot-id', token='auth-token')
        
        # Use the client
        topics = await client.core.list_topics()
        await client.disconnect()
    """

    VERSION = '0.1.0'

    def __init__(
        self,
        ros_url: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        server_url: Optional[str] = None,
        api_url: Optional[str] = None,
        public_auth_url: Optional[str] = None
    ):
        """
        Initialize OLO Client

        Args:
            ros_url: Full WebSocket URL for direct ROS connection (e.g., ws://localhost:9090)
            host: ROS bridge host (alternative to ros_url)
            port: ROS bridge port (alternative to ros_url)
            server_url: OLO Platform WebSocket URL (e.g., wss://app.olo-robotics.com)
            api_url: OLO Platform API URL for authentication (e.g., https://app.olo-robotics.com)
            public_auth_url: Optional dedicated public auth URL
        """
        # Store platform configuration
        self._server_url = server_url
        self._api_url = api_url or (server_url.replace('wss://', 'https://').replace('ws://', 'http://') if server_url else None)
        self._public_auth_url = public_auth_url
        
        # Initialize auth module if we have API URL
        if self._api_url:
            self._auth = OLOAuth(self._api_url, self._public_auth_url)
        else:
            self._auth = None
        
        # Track connection mode
        self._use_platform = server_url is not None
        self._robot_id: Optional[str] = None
        self._ros: Optional[roslibpy.Ros] = None
        self._core: Optional[OLOCore] = None
        self._logs: Optional[OLOLogs] = None
        self._video: Optional[OLOVideo] = None
        self._video_recording: Optional[OLOVideoRecording] = None
        self._rosbag_recording: Optional[OLOROSBagRecording] = None
        self._vision: Optional[OLOVision] = None
        self._joint: Optional[OLOJoint] = None
        self._navigation: Optional[OLONavigation] = None
        self._globals: Optional[OLOGlobals] = None
        
        # For direct ROS connection mode, set up immediately
        # Determine connection parameters
        if ros_url:
            self._ros_url = ros_url
            # Parse URL to extract host/port for logging purposes
            if ros_url.startswith('ws://'):
                url_part = ros_url[5:]
                is_secure = False
            elif ros_url.startswith('wss://'):
                url_part = ros_url[6:]
                is_secure = True
            else:
                url_part = ros_url
                is_secure = False

            # Extract host and port from URL
            if '/' in url_part:
                host_port = url_part.split('/')[0]
                # URL has a custom path - we need to use full URL mode
                self._use_full_url = True
            else:
                host_port = url_part
                self._use_full_url = False

            if ':' in host_port:
                self._host, port_str = host_port.rsplit(':', 1)
                self._port = int(port_str)
            else:
                self._host = host_port
                self._port = 9090
        else:
            self._host = host or os.environ.get('OLO_ROS_HOST', 'localhost')
            self._port = port or int(os.environ.get('OLO_ROS_PORT', '9090'))
            self._ros_url = f"ws://{self._host}:{self._port}"
            self._use_full_url = False

        # Initialize ROS client only for direct connection mode (not platform mode)
        if not self._use_platform:
            # If we have a custom path in the URL (like /rosbridge), pass the full URL
            # as the host parameter and leave port=None so roslibpy uses it as-is.
            # Otherwise use host+port for default rosbridge path.
            if getattr(self, '_use_full_url', False):
                self._ros = roslibpy.Ros(host=self._ros_url, port=None)
            else:
                self._ros = roslibpy.Ros(host=self._host, port=self._port)
            
            # Initialize core, logs, video, joint, navigation, and globals API
            self._core = OLOCore(self._ros)
            self._logs = OLOLogs(self._ros)
            self._video = OLOVideo(self._ros)
            self._video_recording = OLOVideoRecording(self._ros)
            self._rosbag_recording = OLOROSBagRecording(self._ros)
            self._vision = OLOVision(self._ros)
            self._joint = OLOJoint(self._ros, self._core)
            self._navigation = OLONavigation(self._ros, self._core)
            self._globals = OLOGlobals(self._ros)
        
        # Connection state
        self._connected = False
        self._connection_callbacks = {
            'on_connect': None,
            'on_disconnect': None,
            'on_error': None
        }

    @property
    def core(self) -> OLOCore:
        """Access core API for topics, publishing, subscribing, and robot control"""
        return self._core

    @property
    def logs(self) -> OLOLogs:
        """Access logs API for reading and querying script execution logs"""
        return self._logs

    @property
    def video(self) -> OLOVideo:
        """Access video API for WebRTC video streaming and playback"""
        return self._video

    @property
    def videoRecording(self) -> OLOVideoRecording:
        """Access video recording API for recording from camera topics"""
        return self._video_recording

    @property
    def rosbagRecording(self) -> OLOROSBagRecording:
        """Access ROSBag recording API for recording and playback of bag files"""
        return self._rosbag_recording

    @property
    def vision(self) -> OLOVision:
        """Access vision API for AI-powered vision analysis"""
        return self._vision

    @property
    def joint(self) -> OLOJoint:
        """Access joint API for robot arm joint control and manipulation"""
        return self._joint

    @property
    def navigation(self) -> OLONavigation:
        """Access navigation API for Nav2 navigation, mapping, and localization"""
        return self._navigation

    @property
    def globals(self) -> OLOGlobals:
        """Access globals API for cross-script global variables"""
        return self._globals

    @property
    def ros(self):
        """Access underlying roslibpy.Ros instance for advanced usage"""
        return self._ros

    @property
    def is_connected(self) -> bool:
        """Check if connected to ROS"""
        return self._ros.is_connected if self._ros else False

    def get_connection_status(self) -> bool:
        """
        Get ROS connection status (method form for compatibility with JS API)

        Returns:
            True if connected
        """
        return self._ros.is_connected if self._ros else False

    @property
    def robot_id(self) -> Optional[str]:
        """Get the connected robot ID (platform mode only)"""
        return self._robot_id

    async def connect(
        self,
        robot_id: Optional[str] = None,
        token: Optional[str] = None,
        timeout: float = 10.0,
        on_connect: callable = None,
        on_disconnect: callable = None,
        on_error: callable = None
    ) -> bool:
        """
        Connect to ROS

        Args:
            robot_id: Robot ID (required for platform mode, optional for direct mode)
            token: Auth token (uses stored token from authenticate() if not provided)
            timeout: Connection timeout in seconds
            on_connect: Callback when connected
            on_disconnect: Callback when disconnected
            on_error: Callback on error

        Returns:
            True if connected successfully
            
        Raises:
            ConnectionError: If connection fails or times out
            ValueError: If robot_id is required but not provided
        """
        # Store callbacks
        self._connection_callbacks['on_connect'] = on_connect
        self._connection_callbacks['on_disconnect'] = on_disconnect
        self._connection_callbacks['on_error'] = on_error

        # Platform mode: build WebSocket URL with robot_id and token
        if self._use_platform:
            if not robot_id:
                raise ValueError("robot_id is required for platform connection")
            
            # Use provided token or stored auth token
            auth_token = token or (self._auth.get_auth_token() if self._auth else None)
            if not auth_token:
                raise ValueError("token is required. Either provide it or call authenticate() first.")
            
            self._robot_id = robot_id
            
            # Build WebSocket URL: wss://server/rosbridge?robotId=XXX&token=YYY
            ws_url = f"{self._server_url}/rosbridge?robotId={robot_id}&token={auth_token}"
            
            # Create ROS client for this connection
            self._ros = roslibpy.Ros(host=ws_url, port=None)
            self._core = OLOCore(self._ros)
            self._logs = OLOLogs(self._ros)
            self._video = OLOVideo(self._ros)
            self._video_recording = OLOVideoRecording(self._ros)
            self._rosbag_recording = OLOROSBagRecording(self._ros)
            self._vision = OLOVision(self._ros)
            self._joint = OLOJoint(self._ros, self._core)
            self._navigation = OLONavigation(self._ros, self._core)
            self._globals = OLOGlobals(self._ros)

        # Set up event handlers
        def handle_connect():
            self._connected = True
            if self._connection_callbacks['on_connect']:
                self._connection_callbacks['on_connect']()

        def handle_disconnect():
            self._connected = False
            if self._connection_callbacks['on_disconnect']:
                self._connection_callbacks['on_disconnect']()

        def handle_error(error):
            if self._connection_callbacks['on_error']:
                self._connection_callbacks['on_error'](error)

        self._ros.on_ready(handle_connect)

        # Connect
        loop = asyncio.get_event_loop()
        future = loop.create_future()

        def on_ready():
            if not future.done():
                loop.call_soon_threadsafe(future.set_result, True)

        self._ros.on_ready(on_ready)

        # Run connection in background
        try:
            self._ros.run()
            
            # Wait for connection with timeout
            await asyncio.wait_for(future, timeout=timeout)
            self._connected = True
            
            # Patch roslibpy to handle custom OLO operations silently
            self._patch_custom_ops_handler()
            
            # Set up video module connection
            if self._video:
                self._video.set_ros(self._ros)
                self._video.set_connected(True)
                # Fetch TURN credentials for WebRTC
                await self._video.fetch_turn_credentials()
            
            # Set up video recording module connection
            if self._video_recording:
                self._video_recording.set_ros(self._ros)
                self._video_recording.set_connected(True)
            
            # Set up rosbag recording module connection
            if self._rosbag_recording:
                self._rosbag_recording.set_ros(self._ros)
                self._rosbag_recording.set_connected(True)
            
            # Set up vision module connection
            if self._vision:
                self._vision.set_ros(self._ros)
                self._vision.set_connected(True)
            
            return True
            
        except asyncio.TimeoutError:
            raise ConnectionError(f"Connection timeout after {timeout}s")
        except Exception as e:
            raise ConnectionError(f"Connection failed: {e}")

    def _patch_custom_ops_handler(self):
        """
        Patch roslibpy's message handler to silently handle custom OLO operations.
        The OLO platform sends custom WebSocket messages that aren't standard rosbridge.
        """
        import json
        
        # Custom operations that OLO platform may send
        custom_ops = {
            'execution_complete', 'execution_error', 'execution_stopped',
            'script_execution_started', 'video_offer', 'video_answer',
            'ice_candidate', 'turn_credentials'
        }
        
        # Get the protocol instance
        proto_instance = None
        if hasattr(self._ros, 'factory') and self._ros.factory:
            proto_instance = getattr(self._ros.factory, '_proto', None)
        
        if proto_instance and hasattr(proto_instance, 'onMessage'):
            original_onMessage = proto_instance.onMessage
            
            def patched_onMessage(payload, isBinary):
                if not isBinary:
                    try:
                        msg_str = payload.decode('utf-8') if isinstance(payload, bytes) else payload
                        msg = json.loads(msg_str)
                        op = msg.get('op', '')
                        
                        # Silently ignore custom OLO operations
                        if op in custom_ops:
                            return
                        
                        # Pass to original handler for standard rosbridge ops
                        if original_onMessage:
                            original_onMessage(payload, isBinary)
                    except json.JSONDecodeError:
                        # Not JSON, pass to original handler
                        if original_onMessage:
                            original_onMessage(payload, isBinary)
                else:
                    # Binary message, pass to original handler
                    if original_onMessage:
                        original_onMessage(payload, isBinary)
            
            proto_instance.onMessage = patched_onMessage

    def connect_to_robot(
        self,
        robot_id: str,
        server_host: Optional[str] = None,
        server_port: Optional[int] = None,
        use_ssl: bool = False,
        token: Optional[str] = None,
        timeout: float = 10.0
    ) -> bool:
        """
        Connect to a robot synchronously (blocking).
        
        This is a convenience method for synchronous code. It builds the 
        server URL if not already configured and connects to the robot.

        Args:
            robot_id: Robot ID to connect to
            server_host: Server hostname (uses configured server_url if not provided)
            server_port: Server port
            use_ssl: Whether to use SSL/TLS
            token: Auth token (uses stored token if not provided)
            timeout: Connection timeout in seconds

        Returns:
            True if connected successfully, False otherwise
        """
        import threading
        import time

        # Build server URL if host/port provided
        if server_host:
            protocol = "wss" if use_ssl else "ws"
            self._server_url = f"{protocol}://{server_host}:{server_port}"
            self._use_platform = True
            
            # Also set up API URL if not already set
            if not self._api_url:
                api_protocol = "https" if use_ssl else "http"
                self._api_url = f"{api_protocol}://{server_host}:{server_port}"
                self._auth = OLOAuth(self._api_url, self._public_auth_url)

        # Use provided token or stored auth token
        auth_token = token or (self._auth.get_auth_token() if self._auth else None)
        if not auth_token:
            raise ValueError("token is required. Either provide it or call login() first.")

        self._robot_id = robot_id

        # Build WebSocket URL
        ws_url = f"{self._server_url}/rosbridge?robotId={robot_id}&token={auth_token}"

        # Create ROS client
        self._ros = roslibpy.Ros(host=ws_url, port=None)
        self._core = OLOCore(self._ros)
        self._logs = OLOLogs(self._ros)
        self._video = OLOVideo(self._ros)
        self._video_recording = OLOVideoRecording(self._ros)
        self._rosbag_recording = OLOROSBagRecording(self._ros)
        self._vision = OLOVision(self._ros)
        self._joint = OLOJoint(self._ros, self._core)
        self._navigation = OLONavigation(self._ros, self._core)
        self._globals = OLOGlobals(self._ros)

        # Connection state tracking
        connected_event = threading.Event()
        connection_error = [None]  # Use list to allow modification in nested function

        def on_ready():
            self._connected = True
            connected_event.set()

        def on_error(error):
            connection_error[0] = error
            connected_event.set()

        self._ros.on_ready(on_ready)

        try:
            # Start connection
            self._ros.run()

            # Wait for connection with timeout
            if connected_event.wait(timeout=timeout):
                if connection_error[0]:
                    return False
                
                # Patch roslibpy to handle custom OLO operations silently
                self._patch_custom_ops_handler()
                
                # Set up video module connection
                if self._video:
                    self._video.set_ros(self._ros)
                    self._video.set_connected(True)
                    # Note: TURN credentials are fetched asynchronously in video operations
                
                # Set up video recording module connection
                if self._video_recording:
                    self._video_recording.set_ros(self._ros)
                    self._video_recording.set_connected(True)
                
                # Set up rosbag recording module connection
                if self._rosbag_recording:
                    self._rosbag_recording.set_ros(self._ros)
                    self._rosbag_recording.set_connected(True)
                
                # Set up vision module connection
                if self._vision:
                    self._vision.set_ros(self._ros)
                    self._vision.set_connected(True)
                
                return self._connected
            else:
                # Timeout
                return False

        except Exception as e:
            return False

    async def disconnect(self):
        """Disconnect from ROS"""
        if self._ros and self._ros.is_connected:
            # Clean up subscriptions
            if self._core:
                self._core.cleanup()
            
            # Clean up video sessions
            if self._video:
                self._video.cleanup()
                self._video.set_connected(False)
            
            # Clean up video recording
            if self._video_recording:
                self._video_recording.cleanup()
                self._video_recording.set_connected(False)
            
            # Clean up rosbag recording
            if self._rosbag_recording:
                self._rosbag_recording.cleanup()
                self._rosbag_recording.set_connected(False)
            
            # Clean up vision
            if self._vision:
                self._vision.cleanup()
                self._vision.set_connected(False)
            
            # Close connection
            self._ros.terminate()
            self._connected = False

    # =========================================================================
    # Authentication Methods (delegate to OLOAuth)
    # =========================================================================

    async def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with username and password (async)

        Args:
            username: Username or email
            password: Password

        Returns:
            Dict with 'success' and 'token' keys

        Raises:
            Exception: If authentication fails or auth not configured
        """
        if not self._auth:
            raise Exception("Authentication not configured. Provide api_url or server_url when creating client.")
        return await self._auth.authenticate(username, password)

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with username and password (sync)
        Alias for authenticate() but synchronous.

        Args:
            username: Username or email
            password: Password

        Returns:
            Dict with 'success' and 'token' keys

        Raises:
            Exception: If authentication fails or auth not configured
        """
        if not self._auth:
            raise Exception("Authentication not configured. Provide api_url or server_url when creating client.")
        return self._auth._authenticate_sync(username, password)

    async def get_user_robots(self) -> List[Dict[str, Any]]:
        """
        Get list of robots for the authenticated user (async)

        Returns:
            List of robot dictionaries

        Raises:
            Exception: If not authenticated or request fails
        """
        if not self._auth:
            raise Exception("Authentication not configured. Provide api_url or server_url when creating client.")
        return await self._auth.get_user_robots()

    def get_robots(self) -> List[Dict[str, Any]]:
        """
        Get list of robots for the authenticated user (sync)
        Alias for get_user_robots() but synchronous.

        Returns:
            List of robot dictionaries

        Raises:
            Exception: If not authenticated or request fails
        """
        if not self._auth:
            raise Exception("Authentication not configured. Provide api_url or server_url when creating client.")
        return self._auth._get_user_robots_sync()

    def get_auth_token(self) -> Optional[str]:
        """
        Get stored authentication token

        Returns:
            Current auth token or None
        """
        if not self._auth:
            return None
        return self._auth.get_auth_token()

    def set_auth_token(self, token: str) -> None:
        """
        Set authentication token directly (e.g., from stored credentials)

        Args:
            token: Authentication token
        """
        if self._auth:
            self._auth.set_auth_token(token)

    def clear_auth(self) -> None:
        """Clear authentication token"""
        if self._auth:
            self._auth.clear_auth()

    # =========================================================================
    # Client Info
    # =========================================================================

    def get_client_info(self) -> Dict[str, Any]:
        """
        Get client version and module information

        Returns:
            Dict with version and module info
        """
        # Check if aiortc is available for native WebRTC
        try:
            from .video import AIORTC_AVAILABLE
        except ImportError:
            AIORTC_AVAILABLE = False
        
        return {
            'version': self.VERSION,
            'language': 'Python',
            'modules': [
                'OLOCore (Core ROS functionality)',
                'OLOLogs (Execution logs)',
                'OLOAuth (Authentication)',
                f'OLOVideo (WebRTC video streaming - aiortc: {"available" if AIORTC_AVAILABLE else "not installed"})'
            ],
            'features': [
                'ROS topic management',
                'Real-time messaging',
                'Velocity control with safety holds',
                'User authentication',
                'Robot fleet management',
                'WebRTC video streaming',
                'Video topic auto-detection',
                'Video playback control'
            ]
        }

    def __enter__(self):
        """Context manager entry (sync - requires manual connect)"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self._ros and self._ros.is_connected:
            if self._core:
                self._core.cleanup()
            if self._video:
                self._video.cleanup()
            self._ros.terminate()
        return False

    async def __aenter__(self):
        """Async context manager entry - connects automatically"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - disconnects automatically"""
        await self.disconnect()
        return False

