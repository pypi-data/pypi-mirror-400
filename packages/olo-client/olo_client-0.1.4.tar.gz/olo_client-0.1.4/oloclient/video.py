"""
OLO Video Client - WebRTC Video Streaming Management

Handles WebRTC video streaming, session management, and video topic detection.
Independent module that can be composed with other OLO modules.

For native Python usage, requires aiortc:
    pip install aiortc

"""

import asyncio
import json
import re
import uuid
from typing import Optional, Dict, Any, List, Callable, Union

# Try to import aiortc for native WebRTC support
try:
    from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, RTCConfiguration, RTCIceServer
    from aiortc.contrib.media import MediaRelay
    from aiortc.sdp import candidate_from_sdp, candidate_to_sdp
    AIORTC_AVAILABLE = True
except ImportError:
    AIORTC_AVAILABLE = False
    RTCPeerConnection = None
    RTCSessionDescription = None
    RTCIceCandidate = None
    RTCConfiguration = None
    RTCIceServer = None
    candidate_from_sdp = None
    candidate_to_sdp = None


class VideoSession:
    """Represents an active video streaming session"""
    
    def __init__(
        self,
        session_id: str,
        topic: Optional[str] = None,
        filename: Optional[str] = None,
        is_playback: bool = False
    ):
        self.session_id = session_id
        self.topic = topic
        self.filename = filename
        self.is_playback = is_playback
        self.pending = True
        self.peer_connection = None
        self.callbacks: Dict[str, Callable] = {
            'on_connection_state_change': lambda state: None,
            'on_error': lambda error: print(f'Video Error: {error}'),
            'on_progress': lambda step: print(f'Video Progress: {step}'),
            'on_playback_state_change': lambda state: None,
            'on_frame': lambda frame: None  # For native Python frame handling
        }
        self.playback_options: Dict[str, Any] = {
            'loop': False,
            'playback_speed': 1.0
        }
        # Buffered ICE candidates (received before remote description is set)
        self._pending_ice_candidates: List[Dict] = []
        self._buffered_remote_ice_candidates: List[Dict] = []
        # Capture the event loop where this session (and its PeerConnection) is created
        # All aiortc operations MUST run on this loop
        try:
            # Prefer get_running_loop() when in async context (Python 3.7+)
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            # Fallback to get_event_loop() for non-async context
            try:
                self.loop = asyncio.get_event_loop()
            except RuntimeError:
                self.loop = None


class OLOVideo:
    """
    Video streaming client for OLO robots.
    
    Provides WebRTC video streaming capabilities including:
    - Live video streaming from robot cameras
    - Video topic auto-detection
    - Recorded video playback
    - Playback control (play, pause, seek, speed)
    
    Usage:
        # Through OLOClient
        video_result = await client.video.detect_video_topics()
        session_id = await client.video.start_video(
            topic=video_result['bestTopic'],
            on_frame=handle_frame,
            on_progress=lambda s: print(s)
        )
        
        # Later
        await client.video.stop_video(session_id)
    """
    
    def __init__(self, ros_client=None):
        """
        Initialize OLO Video client
        
        Args:
            ros_client: roslibpy.Ros instance (injected by OLOClient)
        """
        self._ros = ros_client
        self._connected = False
        
        # WebRTC configuration
        self._rtc_config = {
            'iceServers': [
                {'urls': 'stun:stun.l.google.com:19302'},
                {'urls': 'stun:stun1.l.google.com:19302'}
            ]
        }
        
        # Session management
        self._active_sessions: Dict[str, VideoSession] = {}
        self._session_counter = 0
        
        # Message handler tracking
        self._message_handler_installed = False
        self._original_on_message = None
        
        # Topics cache
        self._topics_cache: List[Dict] = []
    
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
    
    def _schedule_async(self, coro, session: Optional[VideoSession] = None):
        """
        Schedule an async coroutine to run on the correct event loop.
        
        If a session is provided and has a captured loop, the coroutine will be
        dispatched to that loop (thread-safe). This is critical for aiortc operations
        which must run on the same loop where the PeerConnection was created.
        """
        target_loop = None
        
        # If session has a captured loop, use that
        if session and session.loop:
            target_loop = session.loop
        
        try:
            # Try to get current running loop
            current_loop = asyncio.get_running_loop()
            
            if target_loop and target_loop != current_loop:
                # Need to dispatch to a different loop (thread-safe)
                return asyncio.run_coroutine_threadsafe(coro, target_loop)
            else:
                # Same loop or no target - just create task
                return asyncio.create_task(coro)
                
        except RuntimeError:
            # No running loop - we're in a different thread
            if target_loop and target_loop.is_running():
                # Target loop is running in another thread - dispatch to it
                return asyncio.run_coroutine_threadsafe(coro, target_loop)
            elif self.loop and self.loop.is_running():
                # Use the stored main loop if available and running
                return asyncio.run_coroutine_threadsafe(coro, self.loop)
            else:
                # Try to get or create an event loop for this thread
                try:
                    # Use get_running_loop first if available, then fall back
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        loop = asyncio.get_event_loop()
                    
                    if loop.is_running():
                        # Loop exists but in another thread - use thread-safe method
                        return asyncio.run_coroutine_threadsafe(coro, loop)
                    else:
                        # Loop exists but not running - run the coroutine
                        return loop.run_until_complete(coro)
                except RuntimeError:
                    # No event loop at all - create a new one and run
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        return loop.run_until_complete(coro)
                    finally:
                        loop.close()
                        asyncio.set_event_loop(None)
    
    async def list_topics(self, refresh: bool = False) -> List[Dict[str, Any]]:
        """
        List all available ROS topics
        
        Args:
            refresh: Force refresh from server
            
        Returns:
            List of topic dictionaries with name and type
        """
        if not self.get_connection_status():
            raise ConnectionError("Not connected to robot")
        
        if not refresh and self._topics_cache:
            return self._topics_cache
        
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        
        def callback(topics_dict):
            try:
                topics = []
                topic_names = topics_dict.get('topics', [])
                topic_types = topics_dict.get('types', [])
                
                for i, name in enumerate(topic_names):
                    topics.append({
                        'name': name,
                        'type': topic_types[i] if i < len(topic_types) else 'unknown'
                    })
                
                if not future.done():
                    loop.call_soon_threadsafe(future.set_result, topics)
            except Exception as e:
                if not future.done():
                    loop.call_soon_threadsafe(future.set_exception, e)
        
        self._ros.get_topics(callback)
        
        try:
            result = await asyncio.wait_for(future, timeout=10.0)
            self._topics_cache = result
            return result
        except asyncio.TimeoutError:
            raise TimeoutError("Timeout waiting for topic list")
    
    def _setup_message_handler(self):
        """Set up WebRTC message handler using the centralized routing"""
        if self._message_handler_installed:
            return
        
        if not self._ros:
            return
        
        # Register with centralized WebRTC message routing
        # Use sys.modules to avoid circular import issues
        import sys
        try:
            oloclient_module = sys.modules.get('oloclient')
            if oloclient_module and hasattr(oloclient_module, 'register_webrtc_handler'):
                oloclient_module.register_webrtc_handler(self._handle_webrtc_message)
                self._message_handler_installed = True
            else:
                print('[OLOVideo] Warning: Could not register WebRTC handler - module not found')
        except Exception as e:
            print(f'[OLOVideo] Warning: Could not register WebRTC handler: {e}')
    
    def _send_message(self, message: Dict):
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
    
    def _handle_webrtc_message(self, message: Dict):
        """Handle incoming WebRTC messages"""
        op = message.get('op', '')
        session_id = message.get('session_id')
        
        if op == 'webrtc_session_started':
            self._handle_session_started(message)
        elif op == 'webrtc_answer':
            session = self._active_sessions.get(session_id)
            if session:
                self._handle_answer(message, session)
        elif op == 'webrtc_ice_candidate':
            session = self._active_sessions.get(session_id)
            if session:
                self._handle_ice_candidate(message, session)
        elif op == 'webrtc_error':
            session = self._active_sessions.get(session_id)
            if session:
                self._handle_error(message, session)
        elif op == 'webrtc_stop_session':
            session = self._active_sessions.get(session_id)
            if session:
                self._handle_session_stopped(message, session)
        elif op == 'webrtc_playback_ended':
            session = self._active_sessions.get(session_id)
            if session:
                self._handle_playback_ended(message, session)
        elif op == 'turn_credentials_response':
            self._handle_turn_credentials_response(message)
    
    def _handle_session_started(self, message: Dict):
        """Handle video session started message"""
        server_session_id = message.get('session_id')
        topic = message.get('topic')
        filename = message.get('filename')
        
        
        # Find the pending session
        for temp_id, session in list(self._active_sessions.items()):
            if session.pending and (session.topic == topic or session.filename == filename):
                # Update session with real ID
                del self._active_sessions[temp_id]
                session.session_id = server_session_id
                session.pending = False
                self._active_sessions[server_session_id] = session
                
                session.callbacks['on_progress']('Session established, creating offer...')
                
                # If using aiortc, create and send offer
                if AIORTC_AVAILABLE and session.peer_connection:
                    self._schedule_async(self._create_and_send_offer(session), session)
                
                # Send any pending ICE candidates
                for candidate in session._pending_ice_candidates:
                    self._send_message({
                        'op': 'webrtc_ice_candidate',
                        'session_id': server_session_id,
                        'candidate': candidate
                    })
                session._pending_ice_candidates.clear()
                
                break
        else:
            print(f'[OLOVideo] No matching pending session found!')
    
    def _handle_answer(self, message: Dict, session: VideoSession):
        """Handle WebRTC answer from server"""
        session.callbacks['on_progress']('Processing server response...')
        
        if AIORTC_AVAILABLE and session.peer_connection:
            self._schedule_async(self._set_remote_description(message, session), session)
    
    async def _set_remote_description(self, message: Dict, session: VideoSession):
        """Set remote description (answer) on peer connection"""
        try:
            answer = message.get('answer', {})
            sdp = answer.get('sdp', '')
            sdp_type = answer.get('type', 'answer')
            
            remote_desc = RTCSessionDescription(sdp=sdp, type=sdp_type)
            await session.peer_connection.setRemoteDescription(remote_desc)
            
            session.callbacks['on_progress']('Finalizing connection...')
            
            # Process buffered ICE candidates
            for candidate_data in session._buffered_remote_ice_candidates:
                await self._add_ice_candidate(session, candidate_data)
            session._buffered_remote_ice_candidates.clear()
            
        except Exception as e:
            print(f'[OLOVideo] Error setting remote description: {e}')
            session.callbacks['on_error']('Failed to process WebRTC answer')
    
    def _handle_ice_candidate(self, message: Dict, session: VideoSession):
        """Handle ICE candidate from server"""
        candidate_data = message.get('candidate', {})
        
        if AIORTC_AVAILABLE and session.peer_connection:
            # Check if we have remote description yet
            if session.peer_connection.remoteDescription:
                self._schedule_async(self._add_ice_candidate(session, candidate_data), session)
            else:
                # Buffer the candidate
                # Buffer the candidate until remote description is set
                session._buffered_remote_ice_candidates.append(candidate_data)
    
    async def _add_ice_candidate(self, session: VideoSession, candidate_data: Dict):
        """Add an ICE candidate to the peer connection"""
        try:
            # Extract candidate data - handle nested format
            if isinstance(candidate_data, dict) and 'candidate' in candidate_data:
                candidate_string = candidate_data['candidate']
                sdp_mid = candidate_data.get('sdpMid')
                sdp_mline_index = candidate_data.get('sdpMLineIndex')
            else:
                candidate_string = candidate_data
                sdp_mid = None
                sdp_mline_index = None
            
            # Skip empty candidates (end-of-candidates signal)
            if not candidate_string:
                return
            
            # Use aiortc's candidate_from_sdp to parse the candidate string
            candidate = candidate_from_sdp(candidate_string)
            
            # Set the additional SDP metadata
            candidate.sdpMid = sdp_mid
            candidate.sdpMLineIndex = sdp_mline_index
            
            await session.peer_connection.addIceCandidate(candidate)
            
        except Exception as e:
            print(f'[OLOVideo] Error adding ICE candidate: {e}')
            import traceback
            traceback.print_exc()
    
    def _handle_error(self, message: Dict, session: VideoSession):
        """Handle video error from server"""
        error = message.get('error', 'Unknown error')
        print(f'[OLOVideo] Received video error: {error}')
        session.callbacks['on_error'](error)
        self._schedule_async(self.stop_video(session.session_id), session)
    
    def _handle_session_stopped(self, message: Dict, session: VideoSession):
        """Handle video session stopped by server"""
        print('[OLOVideo] Video session stopped by server')
        session.callbacks['on_connection_state_change']('closed')
        self._cleanup_session(session.session_id)
    
    def _handle_playback_ended(self, message: Dict, session: VideoSession):
        """Handle playback ended event"""
        print(f'[OLOVideo] Video playback ended for session: {session.session_id}')
        
        if not session.is_playback:
            return
        
        session.callbacks['on_playback_state_change']('ended')
        
        # If looping is enabled, restart playback
        if session.playback_options.get('loop'):
            print('[OLOVideo] Looping enabled, restarting playback from beginning')
            
            async def restart_playback():
                await asyncio.sleep(0.3)  # Brief delay for smooth transition
                current = self._active_sessions.get(session.session_id)
                if current and current.is_playback:
                    await self.control_video_playback(session.session_id, 'seek', {'position': 0})
                    session.callbacks['on_playback_state_change']('playing')
            
            self._schedule_async(restart_playback())
    
    def _handle_turn_credentials_response(self, message: Dict):
        """Handle TURN credentials response"""
        if message.get('success') and message.get('iceServers'):
            self._rtc_config['iceServers'] = message['iceServers']
            pass  # Successfully updated ICE servers with TURN credentials
    
    async def fetch_turn_credentials(self):
        """Fetch TURN credentials via WebSocket"""
        if not self.get_connection_status():
            print('[OLOVideo] No WebSocket connection available, using fallback STUN servers')
            return
        
        try:
            
            request_id = f'turn_{int(asyncio.get_event_loop().time() * 1000)}_{uuid.uuid4().hex[:9]}'
            
            self._send_message({
                'op': 'get_turn_credentials',
                'request_id': request_id
            })
            
            # The response will be handled by _handle_turn_credentials_response
            
        except Exception as e:
            print(f'[OLOVideo] Error fetching TURN credentials: {e}')
    
    async def _create_and_send_offer(self, session: VideoSession):
        """Create WebRTC offer and send to server (aiortc)"""
        if not AIORTC_AVAILABLE:
            return
        
        try:
            session.callbacks['on_progress']('Creating connection offer...')
            
            pc = session.peer_connection
            
            # Add transceiver for receiving video
            pc.addTransceiver('video', direction='recvonly')
            
            # Create offer
            offer = await pc.createOffer()
            await pc.setLocalDescription(offer)
            
            session.callbacks['on_progress']('Sending offer to server...')
            
            # Use trickle ICE - send offer immediately without waiting for ICE gathering
            # ICE candidates will be sent as they're discovered via the icecandidate event
            # This significantly reduces connection time
            self._send_message({
                'op': 'webrtc_offer',
                'session_id': session.session_id,
                'offer': {
                    'type': pc.localDescription.type,
                    'sdp': pc.localDescription.sdp
                }
            })
            
        except Exception as e:
            print(f'[OLOVideo] Error creating offer: {e}')
            session.callbacks['on_error']('Failed to create WebRTC offer')
    
    async def detect_video_topics(self) -> Dict[str, Any]:
        """
        Auto-detect video topics available on the robot
        
        Returns:
            Dict with 'bestTopic' (str or None) and 'videoTopics' (list)
        """
        if not self.get_connection_status():
            raise ConnectionError("Not connected to robot")
        
        topics = await self.list_topics(refresh=True)
        
        # Video topic patterns with priorities
        video_patterns = [
            (re.compile(r'/compressed$'), 10),
            (re.compile(r'camera.*/compressed$'), 9),
            (re.compile(r'image.*/compressed$'), 8),
            (re.compile(r'/image_raw$'), 6),
            (re.compile(r'camera.*/image_raw$'), 5),
            (re.compile(r'camera', re.IGNORECASE), 3),
            (re.compile(r'image', re.IGNORECASE), 2),
            (re.compile(r'rgb', re.IGNORECASE), 2),
            (re.compile(r'color', re.IGNORECASE), 2),
            (re.compile(r'usb_cam', re.IGNORECASE), 1),
        ]
        
        video_topics = []
        best_topic = None
        best_score = -1
        
        for topic_info in topics:
            topic_type = topic_info.get('type', '')
            topic_name = topic_info.get('name', '')
            
            # Must be an Image type
            if 'Image' not in topic_type:
                continue
            
            # Calculate score
            score = 0
            for pattern, priority in video_patterns:
                if pattern.search(topic_name):
                    score = max(score, priority)
            
            # Bonus for CompressedImage type
            if topic_type == 'sensor_msgs/CompressedImage':
                score += 15
            
            # Bonus for shorter paths
            path_depth = len(topic_name.split('/'))
            if path_depth <= 4:
                score += 3
            elif path_depth <= 6:
                score += 1
            
            video_topics.append({
                **topic_info,
                'score': score
            })
            
            if score > best_score:
                best_score = score
                best_topic = topic_name
        
        # Sort by score descending
        video_topics.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'bestTopic': best_topic,
            'videoTopics': video_topics
        }
    
    async def start_video(
        self,
        topic: str,
        video_element: Any = None,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start video streaming from a topic
        
        Args:
            topic: Video topic name (e.g., '/camera/image_raw/compressed')
            video_element: HTML video element (for browser) or None for native
            options: Optional configuration:
                - on_connection_state_change: Callback for connection state changes
                - on_error: Callback for errors
                - on_progress: Callback for progress updates
                - on_frame: Callback for video frames (native Python only)
                
        Returns:
            Session ID for this video stream
        """
        if not self.get_connection_status():
            raise ConnectionError("Not connected to robot")
        
        if options is None:
            options = {}
        
        # Stop any existing sessions for this video element
        if video_element is not None:
            await self.stop_video_for_element(video_element)
        
        self._session_counter += 1
        session_id = f'temp_{self._session_counter}'
        
        # Create session
        session = VideoSession(session_id=session_id, topic=topic)
        
        # Set callbacks
        if options.get('on_connection_state_change'):
            session.callbacks['on_connection_state_change'] = options['on_connection_state_change']
        if options.get('onConnectionStateChange'):
            session.callbacks['on_connection_state_change'] = options['onConnectionStateChange']
        if options.get('on_error'):
            session.callbacks['on_error'] = options['on_error']
        if options.get('onError'):
            session.callbacks['on_error'] = options['onError']
        if options.get('on_progress'):
            session.callbacks['on_progress'] = options['on_progress']
        if options.get('onProgress'):
            session.callbacks['on_progress'] = options['onProgress']
        if options.get('on_frame'):
            session.callbacks['on_frame'] = options['on_frame']
        if options.get('onFrame'):
            session.callbacks['on_frame'] = options['onFrame']
        
        try:
            session.callbacks['on_progress']('Initializing video connection...')
            session.callbacks['on_connection_state_change']('connecting')
            
            # Create RTCPeerConnection if aiortc is available
            if AIORTC_AVAILABLE:
                ice_servers = []
                for server in self._rtc_config.get('iceServers', []):
                    urls = server.get('urls', [])
                    if isinstance(urls, str):
                        urls = [urls]
                    for url in urls:
                        ice_server = RTCIceServer(
                            urls=url,
                            username=server.get('username'),
                            credential=server.get('credential')
                        )
                        ice_servers.append(ice_server)
                
                config = RTCConfiguration(iceServers=ice_servers)
                pc = RTCPeerConnection(configuration=config)
                session.peer_connection = pc
                
                # Set up connection state monitoring
                @pc.on('connectionstatechange')
                async def on_connection_state_change():
                    state = pc.connectionState
                    session.callbacks['on_connection_state_change'](state)
                    
                    if state == 'connected':
                        print(f'[OLOVideo] Video connected')
                        session.callbacks['on_progress']('Video stream established')
                    elif state == 'failed':
                        print(f'[OLOVideo] Video connection failed')
                        session.callbacks['on_progress']('Video connection failed')
                        session.callbacks['on_error']('WebRTC connection failed')
                        await self.stop_video(session_id)
                    elif state == 'closed':
                        session.callbacks['on_progress']('Video connection closed')
                        self._cleanup_session(session_id)
                
                @pc.on('iceconnectionstatechange')
                async def on_ice_connection_state_change():
                    state = pc.iceConnectionState
                    if state == 'checking':
                        session.callbacks['on_progress']('Finding network path...')
                    elif state == 'connected':
                        session.callbacks['on_progress']('Network connection established')
                
                @pc.on('icegatheringstatechange')
                async def on_ice_gathering_state_change():
                    state = pc.iceGatheringState
                    if state == 'gathering':
                        session.callbacks['on_progress']('Gathering network candidates...')
                    elif state == 'complete':
                        session.callbacks['on_progress']('Network setup complete')
                
                @pc.on('icecandidate')
                async def on_ice_candidate(candidate):
                    if candidate:
                        # Use candidate_to_sdp to generate proper SDP string
                        try:
                            candidate_sdp = candidate_to_sdp(candidate)
                        except Exception:
                            # Fallback: construct manually
                            candidate_sdp = f"candidate:{getattr(candidate,'foundation','0')} {getattr(candidate,'component','1')} {getattr(candidate,'protocol','udp')} {getattr(candidate,'priority', 0)} {getattr(candidate,'ip','0.0.0.0')} {getattr(candidate,'port', 9)} typ {getattr(candidate,'type','host')}"
                        
                        if pc.connectionState == 'closed':
                            return
                        
                        candidate_dict = {
                            'candidate': candidate_sdp,
                            'sdpMid': getattr(candidate, 'sdpMid', None),
                            'sdpMLineIndex': getattr(candidate, 'sdpMLineIndex', None)
                        }
                        
                        if not session.pending and session.session_id:
                            self._send_message({
                                'op': 'webrtc_ice_candidate',
                                'session_id': session.session_id,
                                'candidate': candidate_dict
                            })
                        else:
                            session._pending_ice_candidates.append(candidate_dict)
                
                @pc.on('track')
                def on_track(track):
                    if track.kind == 'video':
                        # Handle video frames
                        asyncio.create_task(self._process_video_track(track, session))
            
            session.callbacks['on_progress']('Setting up video receiver...')
            
            # Store session
            self._active_sessions[session_id] = session
            
            session.callbacks['on_progress']('Requesting video stream...')
            
            # Request video stream from server
            print(f'[OLOVideo] Starting video: {topic}')
            self._send_message({
                'op': 'webrtc_start_video',
                'topic': topic
            })
            
            return session_id
            
        except Exception as e:
            print(f'[OLOVideo] Error starting video stream: {e}')
            session.callbacks['on_error'](str(e))
            session.callbacks['on_connection_state_change']('failed')
            self._cleanup_session(session_id)
            raise
    
    async def _process_video_track(self, track, session: VideoSession):
        """Process incoming video track frames"""
        frame_count = 0
        try:
            while True:
                frame = await track.recv()
                frame_count += 1
                if frame_count == 1:
                    print(f'[OLOVideo] Video streaming started')
                session.callbacks['on_frame'](frame)
        except Exception as e:
            if frame_count > 0:
                print(f'[OLOVideo] Video track ended after {frame_count} frames')
    
    async def stop_video(self, session_id: str):
        """
        Stop a video stream
        
        Args:
            session_id: Session ID returned from start_video()
        """
        session = self._active_sessions.get(session_id)
        if not session:
            print(f'[OLOVideo] Video session not found: {session_id}')
            return
        
        
        # Send stop message if we have a real session ID
        if session.session_id and not session.pending:
            try:
                self._send_message({
                    'op': 'webrtc_stop_video',
                    'session_id': session.session_id
                })
            except Exception:
                pass  # Best effort stop request
        
        self._cleanup_session(session_id)
    
    async def stop_video_for_element(self, video_element):
        """
        Stop any video streams associated with a specific video element
        
        Args:
            video_element: The video element to stop streams for
        """
        # In native Python, this is a no-op since we don't have video elements
        # When running in browser context, this would find sessions by video element reference
        pass
    
    def _cleanup_session(self, session_id: str):
        """Clean up a video session"""
        session = self._active_sessions.get(session_id)
        if not session:
            return
        
        
        # Close peer connection
        if session.peer_connection:
            self._schedule_async(self._close_peer_connection(session.peer_connection))
        
        # Remove from active sessions
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
        
        # Also try the server session ID
        if session.session_id and session.session_id in self._active_sessions:
            del self._active_sessions[session.session_id]
        
        session.callbacks['on_connection_state_change']('closed')
    
    async def _close_peer_connection(self, pc):
        """Close a peer connection"""
        try:
            await pc.close()
        except Exception as e:
            pass  # Error closing peer connection (already cleaned up)
    
    async def stop_all_videos(self):
        """Stop all active video streams"""
        session_ids = list(self._active_sessions.keys())
        for session_id in session_ids:
            await self.stop_video(session_id)
    
    def get_active_video_sessions(self) -> List[str]:
        """
        Get list of active video session IDs
        
        Returns:
            List of session IDs
        """
        return list(self._active_sessions.keys())
    
    # =========================================================================
    # Video Playback Methods
    # =========================================================================
    
    async def start_video_playback(
        self,
        filename: str,
        video_element: Any = None,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start video playback of a recorded file
        
        Args:
            filename: Name of the recorded video file to play
            video_element: HTML video element (for browser execution) or None for native
            options: Optional configuration:
                - on_connection_state_change: Callback for connection state changes
                - on_error: Callback for errors
                - on_progress: Callback for progress updates
                - on_playback_state_change: Callback for playback state changes
                - loop: Whether to loop the video (default: False)
                - playback_speed: Playback speed multiplier (default: 1.0)
                
        Returns:
            Session ID for this playback stream
        """
        if not self.get_connection_status():
            raise ConnectionError("Not connected to robot")
        
        if options is None:
            options = {}
        
        # Stop any existing sessions for this video element
        if video_element is not None:
            await self.stop_video_for_element(video_element)
        
        self._session_counter += 1
        session_id = f'playback_{self._session_counter}'
        
        # Create session
        session = VideoSession(
            session_id=session_id,
            filename=filename,
            is_playback=True
        )
        
        # Set callbacks
        if options.get('on_connection_state_change'):
            session.callbacks['on_connection_state_change'] = options['on_connection_state_change']
        if options.get('onConnectionStateChange'):
            session.callbacks['on_connection_state_change'] = options['onConnectionStateChange']
        if options.get('on_error'):
            session.callbacks['on_error'] = options['on_error']
        if options.get('onError'):
            session.callbacks['on_error'] = options['onError']
        if options.get('on_progress'):
            session.callbacks['on_progress'] = options['on_progress']
        if options.get('onProgress'):
            session.callbacks['on_progress'] = options['onProgress']
        if options.get('on_playback_state_change'):
            session.callbacks['on_playback_state_change'] = options['on_playback_state_change']
        if options.get('onPlaybackStateChange'):
            session.callbacks['on_playback_state_change'] = options['onPlaybackStateChange']
        if options.get('on_frame'):
            session.callbacks['on_frame'] = options['on_frame']
        if options.get('onFrame'):
            session.callbacks['on_frame'] = options['onFrame']
        
        # Set playback options
        session.playback_options['loop'] = options.get('loop', False)
        session.playback_options['playback_speed'] = options.get('playback_speed', options.get('playbackSpeed', 1.0))
        
        try:
            session.callbacks['on_progress']('Initializing video playback connection...')
            session.callbacks['on_connection_state_change']('connecting')
            
            # Create RTCPeerConnection if aiortc is available (same as start_video)
            if AIORTC_AVAILABLE:
                ice_servers = []
                for server in self._rtc_config.get('iceServers', []):
                    urls = server.get('urls', [])
                    if isinstance(urls, str):
                        urls = [urls]
                    for url in urls:
                        ice_server = RTCIceServer(
                            urls=url,
                            username=server.get('username'),
                            credential=server.get('credential')
                        )
                        ice_servers.append(ice_server)
                
                config = RTCConfiguration(iceServers=ice_servers)
                pc = RTCPeerConnection(configuration=config)
                session.peer_connection = pc
                
                # Set up event handlers (same as start_video)
                @pc.on('connectionstatechange')
                async def on_connection_state_change():
                    state = pc.connectionState
                    print(f'[OLOVideo] Playback connection state: {state}')
                    session.callbacks['on_connection_state_change'](state)
                    
                    if state == 'connected':
                        session.callbacks['on_progress']('Video playback stream established')
                        session.callbacks['on_playback_state_change']('ready')
                    elif state == 'failed':
                        session.callbacks['on_progress']('Video playback connection failed')
                        session.callbacks['on_error']('WebRTC playback connection failed')
                        await self.stop_video_playback(session_id)
                    elif state == 'closed':
                        session.callbacks['on_progress']('Video playback connection closed')
                        session.callbacks['on_playback_state_change']('ended')
                        self._cleanup_session(session_id)
                
                @pc.on('icecandidate')
                async def on_ice_candidate(candidate):
                    if candidate:
                        # Use candidate_to_sdp to generate proper SDP string
                        try:
                            candidate_sdp = candidate_to_sdp(candidate)
                        except Exception:
                            # Fallback: construct manually
                            candidate_sdp = f"candidate:{getattr(candidate,'foundation','0')} {getattr(candidate,'component','1')} {getattr(candidate,'protocol','udp')} {getattr(candidate,'priority', 0)} {getattr(candidate,'ip','0.0.0.0')} {getattr(candidate,'port', 9)} typ {getattr(candidate,'type','host')}"
                        
                        candidate_dict = {
                            'candidate': candidate_sdp,
                            'sdpMid': getattr(candidate, 'sdpMid', None),
                            'sdpMLineIndex': getattr(candidate, 'sdpMLineIndex', None)
                        }
                        
                        if not session.pending and session.session_id:
                            self._send_message({
                                'op': 'webrtc_ice_candidate',
                                'session_id': session.session_id,
                                'candidate': candidate_dict
                            })
                        else:
                            session._pending_ice_candidates.append(candidate_dict)
                
                @pc.on('track')
                def on_track(track):
                    print(f'[OLOVideo] Received playback video track: {track.kind}')
                    if track.kind == 'video':
                        asyncio.create_task(self._process_video_track(track, session))
            
            session.callbacks['on_progress']('Setting up video playback receiver...')
            
            # Store session
            self._active_sessions[session_id] = session
            
            session.callbacks['on_progress']('Requesting video playback...')
            
            # Request video playback from server
            print(f'[OLOVideo] Requesting video playback for file: {filename}')
            print(f'[OLOVideo] Loop setting (client-side): {session.playback_options["loop"]}')
            
            self._send_message({
                'op': 'webrtc_start_video_playback',
                'filename': filename,
                'playbackSpeed': session.playback_options['playback_speed']
            })
            
            return session_id
            
        except Exception as e:
            print(f'[OLOVideo] Error starting video playback: {e}')
            session.callbacks['on_error'](str(e))
            session.callbacks['on_connection_state_change']('failed')
            self._cleanup_session(session_id)
            raise
    
    async def control_video_playback(
        self,
        session_id: str,
        action: str,
        params: Optional[Dict[str, Any]] = None
    ):
        """
        Control video playback
        
        Args:
            session_id: Playback session ID
            action: Control action: 'play', 'pause', 'seek', 'speed', 'stop'
            params: Action parameters (e.g., {'position': 30} for seek, {'speed': 2.0} for speed)
        """
        session = self._active_sessions.get(session_id)
        if not session or not session.is_playback:
            print(f'[OLOVideo] Playback session not found: {session_id}')
            return
        
        if not session.session_id or session.pending:
            print(f'[OLOVideo] Playback session not ready for control: {session_id}')
            return
        
        if params is None:
            params = {}
        
        print(f'[OLOVideo] Controlling playback {session_id}: {action} {params}')
        
        self._send_message({
            'op': 'webrtc_control_playback',
            'session_id': session.session_id,
            'action': action,
            'params': params
        })
    
    async def stop_video_playback(self, session_id: str):
        """
        Stop video playback
        
        Args:
            session_id: Playback session ID
        """
        session = self._active_sessions.get(session_id)
        if not session or not session.is_playback:
            print(f'[OLOVideo] Playback session not found: {session_id}')
            return
        
        print(f'[OLOVideo] Stopping video playback for session: {session_id}')
        
        if session.session_id and not session.pending:
            try:
                self._send_message({
                    'op': 'webrtc_stop_video_playback',
                    'session_id': session.session_id
                })
            except Exception:
                pass  # Best effort stop request
        
        self._cleanup_session(session_id)
    
    # =========================================================================
    # Cleanup
    # =========================================================================
    
    def cleanup(self):
        """Clean up all video resources"""
        self._schedule_async(self.stop_all_videos())
        
        # Unregister from centralized WebRTC message routing
        if self._message_handler_installed:
            import sys
            try:
                oloclient_module = sys.modules.get('oloclient')
                if oloclient_module and hasattr(oloclient_module, 'unregister_webrtc_handler'):
                    oloclient_module.unregister_webrtc_handler(self._handle_webrtc_message)
            except Exception:
                pass
        
        self._message_handler_installed = False
        self._original_on_message = None

