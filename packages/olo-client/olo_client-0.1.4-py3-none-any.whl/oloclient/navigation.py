"""
OLO Navigation API - Navigation and Mapping Management

Handles Nav2 navigation, mapping, localization, and map management.
Mirrors the JavaScript OLONavigationClient API.
"""

import asyncio
import json
import math
import threading
import time
from typing import Dict, Any, Optional, List, Callable


class OLONavigation:
    """
    Navigation API for Nav2 navigation, mapping, and localization.
    
    Provides methods for:
    - Sending navigation goals
    - Getting robot pose
    - Map management (save, load, list, delete)
    - Navigation engine control (start/stop Nav2)
    """

    def __init__(self, ros_client, core):
        """
        Initialize OLO Navigation

        Args:
            ros_client: roslibpy.Ros instance
            core: OLOCore instance for core ROS operations
        """
        self._ros = ros_client
        self._core = core
        self._navigation_callbacks = {}
        self._map_callbacks = {}
        self._navigation_message_handler = None
        self._map_message_handler = None
        self._last_navigation_request_id = None
        self._verbose_logging = False
        self._loop = None  # Store the event loop reference for cross-thread callbacks

    def set_verbose_logging(self, enabled: bool) -> None:
        """
        Enable or disable verbose logging for Nav2 operations.
        
        Args:
            enabled: Whether to enable verbose logging
        """
        self._verbose_logging = enabled

    def _log(self, level: str, *args) -> None:
        """Internal logging helper"""
        # Log errors always, 'log' only if verbose logging is enabled
        if level == 'error' or (self._verbose_logging and level in ('log', 'debug')):
            msg = ' '.join(str(a) for a in args)
            print(f"[OLONavigation] {msg}", flush=True)

    # ===========================================
    # NAV2 NAVIGATION METHODS
    # ===========================================

    async def send_navigation_goal(
        self,
        goal: Dict[str, float],
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Send a navigation goal to Nav2.

        Args:
            goal: Navigation goal with:
                - x: Target X coordinate
                - y: Target Y coordinate
                - yaw: Target orientation (optional, default: 0)
            options: Navigation options:
                - onResult: Callback for navigation result
                - onFeedback: Callback for navigation feedback
                - onError: Callback for navigation errors
                - robotNamespace: Optional robot namespace for multi-robot scenarios
                - timeoutMs: Optional timeout to auto-cancel goal after N ms

        Returns:
            Goal ID (request ID)
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to robot")

        if options is None:
            options = {}

        on_result = options.get('onResult', lambda x: None)
        on_feedback = options.get('onFeedback', lambda x: None)
        on_error = options.get('onError', lambda x: None)
        robot_namespace = options.get('robotNamespace')
        timeout_ms = options.get('timeoutMs')

        request_id = f"nav_request_{int(time.time() * 1000)}_{id(goal) % 10000}"

        namespace_info = f" for robot: {robot_namespace}" if robot_namespace else ""
        self._log('log', f"Sending navigation goal to ({goal.get('x')}, {goal.get('y')}){namespace_info}")

        # Store callbacks for this request
        entry = {
            'callbacks': {
                'onResult': on_result,
                'onFeedback': on_feedback,
                'onError': on_error
            },
            'timeoutId': None
        }
        self._navigation_callbacks[request_id] = entry

        # Set up message handler if not already set
        if not self._navigation_message_handler:
            self._setup_navigation_message_handler()

        # Remember this request for easy cancellation
        self._last_navigation_request_id = request_id

        # Set up timeout if specified
        if timeout_ms and timeout_ms > 0:
            async def timeout_cancel():
                await asyncio.sleep(timeout_ms / 1000.0)
                if request_id in self._navigation_callbacks:
                    self._log('log', f"Navigation goal timed out after {timeout_ms}ms - cancelling")
                    await self.cancel_navigation_goal(request_id)
            
            entry['timeoutTask'] = asyncio.create_task(timeout_cancel())

        # Build navigation message
        nav_message = {
            'op': 'ros2_nav_goal',
            'request_id': request_id,
            'goal': goal
        }

        # Include robot namespace only if it's a real namespace
        if robot_namespace and robot_namespace != '' and robot_namespace != 'global':
            nav_message['robotNamespace'] = robot_namespace

        self._send_ws_message(nav_message)

        return request_id

    async def navigate_to(
        self,
        goal: Dict[str, float],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        High-level helper: navigate to a goal and return when finished/cancelled.

        Args:
            goal: Target pose { x, y, yaw }
            options: Same options as send_navigation_goal

        Returns:
            Dict with result info and goalId
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to robot")

        if options is None:
            options = {}

        loop = asyncio.get_event_loop()
        result_future = loop.create_future()

        def on_result(message):
            if not result_future.done():
                loop.call_soon_threadsafe(result_future.set_result, message)

        def on_error(error):
            if not result_future.done():
                loop.call_soon_threadsafe(result_future.set_exception, Exception(str(error)))

        goal_id = await self.send_navigation_goal(goal, {
            **options,
            'onResult': on_result,
            'onFeedback': options.get('onFeedback', lambda x: None),
            'onError': on_error
        })

        result = await result_future
        return {**result, 'goalId': goal_id} if isinstance(result, dict) else {'result': result, 'goalId': goal_id}

    async def cancel_navigation_goal(
        self,
        request_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Cancel current navigation goal.

        Args:
            request_id: Optional specific request ID to cancel
            options: Cancel options:
                - robotNamespace: Optional robot namespace for multi-robot scenarios
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to robot")

        if options is None:
            options = {}

        robot_namespace = options.get('robotNamespace')
        namespace_info = f" for robot: {robot_namespace}" if robot_namespace else ""
        self._log('log', f"Cancelling navigation goal via ROS2 commands...{namespace_info}")

        # Prefer provided requestId; fall back to last known
        target_request_id = request_id or self._last_navigation_request_id or f"cancel_{int(time.time() * 1000)}"

        cancel_message = {
            'op': 'ros2_nav_cancel',
            'request_id': target_request_id
        }

        if robot_namespace and robot_namespace != '' and robot_namespace != 'global':
            cancel_message['robotNamespace'] = robot_namespace

        self._send_ws_message(cancel_message)
        self._log('log', "Navigation cancellation request sent")

    def _setup_navigation_message_handler(self) -> None:
        """Set up message handler for ROS2 navigation responses"""
        self._log('log', "Setting up navigation message handler")

        def handler(message: Dict[str, Any]) -> None:
            op = message.get('op', '')
            if op.startswith('ros2_nav_'):
                self._handle_navigation_message(message)
            elif op.startswith('nav2_'):
                self._handle_nav2_broadcast_message(message)

        self._navigation_message_handler = handler
        self._register_ws_handler(handler)

    def _handle_navigation_message(self, message: Dict[str, Any]) -> None:
        """Handle navigation messages from the appliance"""
        request_id = message.get('request_id')
        entry = self._navigation_callbacks.get(request_id)
        callbacks = entry.get('callbacks') if entry else None

        if not callbacks:
            # Only warn for unexpected message types
            if message.get('op') not in ['ros2_nav_ack', 'ros2_nav_status', 'ros2_nav_feedback']:
                self._log('log', f"Received navigation message for unknown request: {request_id}")
            return

        op = message.get('op')

        if op == 'ros2_nav_ack':
            self._log('log', "Navigation goal acknowledged")

        elif op == 'ros2_nav_status':
            self._log('log', f"Navigation status: {message.get('status')}")

        elif op == 'ros2_nav_feedback':
            callbacks['onFeedback'](message.get('feedback'))

        elif op == 'ros2_nav_result':
            self._log('log', f"Navigation result received: {message.get('result')}")
            callbacks['onResult'](message)
            self._cleanup_navigation_entry(request_id, entry)

        elif op == 'ros2_nav_cancelled':
            self._log('log', "Navigation cancelled")
            callbacks['onResult']({'result': 'cancelled'})
            self._cleanup_navigation_entry(request_id, entry)

    def _cleanup_navigation_entry(self, request_id: str, entry: Dict) -> None:
        """Clean up navigation entry after completion"""
        if entry and entry.get('timeoutTask'):
            try:
                entry['timeoutTask'].cancel()
            except Exception:
                pass
        # Delay cleanup to avoid warnings for trailing messages
        # Use threading.Timer since we may be called from a non-asyncio thread
        def delayed_cleanup():
            if request_id in self._navigation_callbacks:
                del self._navigation_callbacks[request_id]
        timer = threading.Timer(1.0, delayed_cleanup)
        timer.daemon = True
        timer.start()

    def _handle_nav2_broadcast_message(self, message: Dict[str, Any]) -> None:
        """Handle Nav2 broadcast messages"""
        op = message.get('op')

        if op == 'nav2_log':
            if self._verbose_logging:
                component = message.get('component', 'unknown')
                line = message.get('line', '')
                print(f"[Nav2:{component}] {line}")

        elif op == 'nav2_status':
            if self._verbose_logging:
                event = message.get('event', '')
                component = message.get('component', '')
                self._log('log', f"Nav2 status: {event}" + (f" ({component})" if component else ""))

        elif op == 'nav2_start_result':
            self._handle_nav2_start_result(message)

        elif op == 'nav2_stop_result':
            self._handle_nav2_stop_result(message)

    def _handle_nav2_start_result(self, message: Dict[str, Any]) -> None:
        """Handle Nav2 start result"""
        request_id = message.get('request_id')
        
        if request_id and request_id in self._map_callbacks:
            entry = self._map_callbacks[request_id]
            future = entry.get('future')
            loop = entry.get('loop') or self._loop
            
            self._log('log', f"Found callback entry, future.done={future.done() if future else 'None'}, loop={loop is not None}")
            
            if not future or future.done():
                self._log('log', "Future already done or None, skipping")
                return
                
            if not loop:
                self._log('error', "No event loop available for Nav2 start result callback")
                return
            
            if message.get('success'):
                self._log('log', "Setting result: success=True")
                loop.call_soon_threadsafe(
                    future.set_result,
                    {'success': True, 'mode': message.get('mode')}
                )
            else:
                self._log('log', f"Setting exception: {message.get('error')}")
                loop.call_soon_threadsafe(
                    future.set_exception,
                    Exception(message.get('error', 'Failed to start Nav2'))
                )
            del self._map_callbacks[request_id]
        else:
            self._log('log', f"No callback found for request_id={request_id}")

    def _handle_nav2_stop_result(self, message: Dict[str, Any]) -> None:
        """Handle Nav2 stop result"""
        request_id = message.get('request_id')
        if request_id and request_id in self._map_callbacks:
            entry = self._map_callbacks[request_id]
            future = entry.get('future')
            loop = entry.get('loop') or self._loop
            
            if not future or future.done():
                return
                
            if not loop:
                self._log('error', "No event loop available for Nav2 stop result callback")
                return
            
            if message.get('success'):
                loop.call_soon_threadsafe(future.set_result, {'success': True})
            else:
                loop.call_soon_threadsafe(
                    future.set_exception,
                    Exception(message.get('error', 'Failed to stop Nav2'))
                )
            del self._map_callbacks[request_id]

    # ===========================================
    # POSE AND LOCALIZATION METHODS
    # ===========================================

    async def get_current_pose(self) -> Dict[str, Any]:
        """
        Get current robot pose (works with both AMCL and SLAM).

        Returns:
            Current pose object with x, y, z, orientation, yaw, and source
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to robot")

        pose_sources = [
            {'topic': '/amcl_pose', 'type': 'geometry_msgs/PoseWithCovarianceStamped', 'source': 'AMCL'},
            {'topic': '/pose', 'type': 'geometry_msgs/PoseWithCovarianceStamped', 'source': 'SLAM'},
            {'topic': '/slam_toolbox/pose', 'type': 'geometry_msgs/PoseStamped', 'source': 'SLAM'},
            {'topic': '/robot_pose', 'type': 'geometry_msgs/PoseStamped', 'source': 'SLAM'},
            {'topic': '/odom', 'type': 'nav_msgs/Odometry', 'source': 'Odometry'}
        ]

        for pose_source in pose_sources:
            try:
                self._log('log', f"Trying to get pose from {pose_source['topic']} ({pose_source['source']})")
                pose = await self.get_current_pose_from_topic(
                    pose_source['topic'],
                    pose_source['type']
                )
                pose['source'] = pose_source['source']
                self._log('log', f"Current pose from {pose_source['source']}: {pose}")
                return pose
            except Exception as e:
                self._log('log', f"Could not get pose from {pose_source['topic']}: {e}")
                continue

        raise Exception("Could not get robot pose from any available source (AMCL, SLAM, or Odometry)")

    async def get_current_pose_from_topic(
        self,
        topic: str,
        message_type: str
    ) -> Dict[str, Any]:
        """
        Get current pose from a specific topic.

        Args:
            topic: Topic name
            message_type: ROS message type

        Returns:
            Current pose
        """
        import roslibpy

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to robot")

        loop = asyncio.get_event_loop()
        future = loop.create_future()

        pose_listener = roslibpy.Topic(
            self._ros,
            topic,
            message_type
        )

        def callback(message):
            if future.done():
                return

            try:
                if message_type == 'nav_msgs/Odometry':
                    pose = {
                        'x': message['pose']['pose']['position']['x'],
                        'y': message['pose']['pose']['position']['y'],
                        'z': message['pose']['pose']['position']['z'],
                        'orientation': message['pose']['pose']['orientation']
                    }
                elif message_type == 'geometry_msgs/PoseStamped':
                    pose = {
                        'x': message['pose']['position']['x'],
                        'y': message['pose']['position']['y'],
                        'z': message['pose']['position']['z'],
                        'orientation': message['pose']['orientation']
                    }
                else:  # PoseWithCovarianceStamped
                    pose = {
                        'x': message['pose']['pose']['position']['x'],
                        'y': message['pose']['pose']['position']['y'],
                        'z': message['pose']['pose']['position']['z'],
                        'orientation': message['pose']['pose']['orientation']
                    }

                # Calculate yaw from quaternion
                q = pose['orientation']
                pose['yaw'] = math.atan2(
                    2 * (q['w'] * q['z'] + q['x'] * q['y']),
                    1 - 2 * (q['y'] * q['y'] + q['z'] * q['z'])
                )

                loop.call_soon_threadsafe(future.set_result, pose)
            except Exception as e:
                loop.call_soon_threadsafe(future.set_exception, e)

        pose_listener.subscribe(callback)

        try:
            result = await asyncio.wait_for(future, timeout=3.0)
            return result
        except asyncio.TimeoutError:
            raise TimeoutError(f"Timeout waiting for pose from {topic}")
        finally:
            pose_listener.unsubscribe()

    async def subscribe_to_localization(
        self,
        callback: Callable[[Dict[str, Any]], None]
    ) -> str:
        """
        Subscribe to robot localization updates (works with both AMCL and SLAM).

        Args:
            callback: Callback for pose updates

        Returns:
            Subscription ID
        """
        topics = await self._core.list_topics()

        pose_sources = [
            {'topic': '/amcl_pose', 'type': 'geometry_msgs/PoseWithCovarianceStamped', 'source': 'AMCL'},
            {'topic': '/pose', 'type': 'geometry_msgs/PoseWithCovarianceStamped', 'source': 'SLAM'},
            {'topic': '/slam_toolbox/pose', 'type': 'geometry_msgs/PoseStamped', 'source': 'SLAM'},
            {'topic': '/robot_pose', 'type': 'geometry_msgs/PoseStamped', 'source': 'SLAM'},
            {'topic': '/odom', 'type': 'nav_msgs/Odometry', 'source': 'Odometry'}
        ]

        for pose_source in pose_sources:
            topic_exists = any(t.get('name') == pose_source['topic'] for t in topics)
            if topic_exists:
                self._log('log', f"Subscribing to localization from {pose_source['topic']} ({pose_source['source']})")

                def pose_callback(message):
                    try:
                        if pose_source['type'] == 'nav_msgs/Odometry':
                            pose = {
                                'x': message['pose']['pose']['position']['x'],
                                'y': message['pose']['pose']['position']['y'],
                                'z': message['pose']['pose']['position']['z'],
                                'orientation': message['pose']['pose']['orientation'],
                                'timestamp': int(time.time() * 1000),
                                'frame_id': message.get('header', {}).get('frame_id', 'odom'),
                                'source': pose_source['source']
                            }
                        elif pose_source['type'] == 'geometry_msgs/PoseStamped':
                            pose = {
                                'x': message['pose']['position']['x'],
                                'y': message['pose']['position']['y'],
                                'z': message['pose']['position']['z'],
                                'orientation': message['pose']['orientation'],
                                'timestamp': int(time.time() * 1000),
                                'frame_id': message.get('header', {}).get('frame_id', 'map'),
                                'source': pose_source['source']
                            }
                        else:
                            pose = {
                                'x': message['pose']['pose']['position']['x'],
                                'y': message['pose']['pose']['position']['y'],
                                'z': message['pose']['pose']['position']['z'],
                                'orientation': message['pose']['pose']['orientation'],
                                'timestamp': int(time.time() * 1000),
                                'frame_id': message.get('header', {}).get('frame_id', 'map'),
                                'source': pose_source['source']
                            }

                        q = pose['orientation']
                        pose['yaw'] = math.atan2(
                            2 * (q['w'] * q['z'] + q['x'] * q['y']),
                            1 - 2 * (q['y'] * q['y'] + q['z'] * q['z'])
                        )

                        callback(pose)
                    except Exception as e:
                        self._log('error', f"Error in localization callback: {e}")

                return await self._core.subscribe(
                    pose_source['topic'],
                    pose_callback,
                    message_type=pose_source['type']
                )

        raise Exception("No robot localization topic available (tried AMCL, SLAM, and Odometry)")

    async def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from a topic subscription.
        
        This method delegates to core.unsubscribe for API consistency with 
        the JavaScript OLONavigationClient which inherits unsubscribe from its parent.

        Args:
            subscription_id: The subscription ID returned from subscribe_to_localization or subscribe_to_map

        Returns:
            True if unsubscribed, False if not subscribed
        """
        return await self._core.unsubscribe(subscription_id)

    async def subscribe_to_map(
        self,
        callback: Callable[[Dict[str, Any]], None]
    ) -> str:
        """
        Subscribe to map updates.

        Args:
            callback: Callback for map updates

        Returns:
            Subscription ID
        """
        return await self._core.subscribe('/map', callback, message_type='nav_msgs/msg/OccupancyGrid')

    async def set_initial_pose(
        self,
        pose: Dict[str, float],
        options: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Set initial pose for AMCL localization.

        Args:
            pose: Initial pose with:
                - x: X coordinate
                - y: Y coordinate
                - yaw: Orientation
            options: Optional parameters:
                - robotNamespace: Robot namespace for multi-robot scenarios
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to robot")

        if options is None:
            options = {}

        robot_namespace = options.get('robotNamespace')
        frame_id = f"{robot_namespace}/map" if robot_namespace else "map"
        topic = f"/{robot_namespace}/initialpose" if robot_namespace else "/initialpose"

        now_sec = int(time.time())
        now_nanosec = int((time.time() % 1) * 1e9)

        covariance = [0.0] * 36
        covariance[0] = 0.25   # x
        covariance[7] = 0.25   # y
        covariance[35] = 0.25  # yaw

        message = {
            'header': {
                'frame_id': frame_id,
                'stamp': {
                    'sec': now_sec,
                    'nanosec': now_nanosec
                }
            },
            'pose': {
                'pose': {
                    'position': {
                        'x': pose.get('x', 0.0),
                        'y': pose.get('y', 0.0),
                        'z': 0.0
                    },
                    'orientation': {
                        'x': 0.0,
                        'y': 0.0,
                        'z': math.sin(pose.get('yaw', 0.0) / 2),
                        'w': math.cos(pose.get('yaw', 0.0) / 2)
                    }
                },
                'covariance': covariance
            }
        }

        await self._core.publish(topic, message, {
            'messageType': 'geometry_msgs/PoseWithCovarianceStamped'
        })

    async def clear_costmaps(self) -> None:
        """Clear costmaps to help with recovery."""
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to robot")

        try:
            await self._core.call_service(
                '/global_costmap/clear_entirely_global_costmap',
                'nav2_msgs/ClearEntireCostmap',
                {}
            )
            await self._core.call_service(
                '/local_costmap/clear_entirely_local_costmap',
                'nav2_msgs/ClearEntireCostmap',
                {}
            )
            self._log('log', "Costmaps cleared successfully")
        except Exception:
            self._log('log', "Could not clear costmaps (service may not be available)")

    async def clear_slam_map(self) -> None:
        """Clear/reset the SLAM map to start fresh mapping."""
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to robot")

        try:
            await self._core.call_service('/slam_toolbox/clear_changes', 'slam_toolbox/Clear', {})
            self._log('log', "SLAM map cleared - ready for fresh mapping")
        except Exception:
            self._log('log', "Direct clear service not available, trying alternative method")
            try:
                await self._core.call_service('/slam_toolbox/reset', 'std_srvs/Empty', {})
                self._log('log', "SLAM map reset via reset service")
            except Exception:
                self._log('log', "Reset service also not available - you may need to restart SLAM")
                raise Exception("Unable to clear SLAM map - restart SLAM manually")

    async def get_current_map_info(self) -> Dict[str, Any]:
        """
        Get current map data (uses default /map topic).

        Returns:
            Current map information
        """
        return await self.get_current_map_info_from_topic('/map')

    async def get_current_map_info_from_topic(self, map_topic: str) -> Dict[str, Any]:
        """
        Get current map data from a specific topic.

        Args:
            map_topic: Map topic name

        Returns:
            Current map information
        """
        import roslibpy

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to robot")

        loop = asyncio.get_event_loop()
        future = loop.create_future()

        map_listener = roslibpy.Topic(
            self._ros,
            map_topic,
            'nav_msgs/OccupancyGrid'
        )

        def callback(map_data):
            if future.done():
                return

            try:
                info = map_data.get('info', {})
                header = map_data.get('header', {})

                map_info = {
                    'width': info.get('width'),
                    'height': info.get('height'),
                    'resolution': info.get('resolution'),
                    'origin': info.get('origin'),
                    'map_load_time': info.get('map_load_time'),
                    'frame_id': header.get('frame_id'),
                    'total_cells': info.get('width', 0) * info.get('height', 0),
                    'area_meters': (info.get('width', 0) * info.get('resolution', 0.05)) *
                                   (info.get('height', 0) * info.get('resolution', 0.05))
                }

                self._log('log', f"Current map info from {map_topic}: {map_info}")
                loop.call_soon_threadsafe(future.set_result, map_info)
            except Exception as e:
                loop.call_soon_threadsafe(future.set_exception, e)

        map_listener.subscribe(callback)

        try:
            result = await asyncio.wait_for(future, timeout=5.0)
            return result
        except asyncio.TimeoutError:
            raise TimeoutError(f"Timeout waiting for map data from {map_topic}")
        finally:
            map_listener.unsubscribe()

    # ===========================================
    # MAP MANAGEMENT METHODS
    # ===========================================

    async def save_map(
        self,
        map_name: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Save current map to server database.

        Args:
            map_name: Name for the saved map
            options: Save options:
                - description: Map description (optional)
                - onProgress: Progress callback (optional)
                - onSuccess: Success callback (optional)
                - onError: Error callback (optional)
                - robotNamespace: Robot namespace for multi-robot scenarios (optional)

        Returns:
            Save result
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to robot")

        if not map_name or not map_name.strip():
            raise ValueError("Map name is required")

        if options is None:
            options = {}

        request_id = f"save_map_{int(time.time() * 1000)}_{id(map_name) % 10000}"
        on_progress = options.get('onProgress', lambda x: None)
        on_success = options.get('onSuccess', lambda x: None)
        on_error = options.get('onError', lambda x: None)

        # Set up message handler if needed
        if not self._map_message_handler:
            self._setup_map_message_handler()

        loop = asyncio.get_event_loop()
        self._loop = loop  # Store for cross-thread callbacks
        future = loop.create_future()

        self._map_callbacks[request_id] = {
            'future': future,
            'loop': loop,
            'onProgress': on_progress,
            'onSuccess': on_success,
            'onError': on_error
        }

        on_progress("Initiating map save...")

        save_message = {
            'op': 'ros2_save_map',
            'request_id': request_id,
            'mapName': map_name.strip(),
            'description': options.get('description')
        }

        if options.get('robotNamespace'):
            save_message['robotNamespace'] = options['robotNamespace']

        self._send_ws_message(save_message)
        self._log('log', f"Map save request sent: {map_name}")

        try:
            result = await asyncio.wait_for(future, timeout=180.0)  # 3 minutes
            on_success(result)
            return result
        except asyncio.TimeoutError:
            error = TimeoutError("Map save operation timed out after 3 minutes")
            on_error(error)
            if request_id in self._map_callbacks:
                del self._map_callbacks[request_id]
            raise error

    async def list_maps(
        self,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get list of saved maps for current user.

        Args:
            options: List options:
                - limit: Maximum number of maps to return (default: 50)
                - offset: Offset for pagination (default: 0)
                - search: Search term (optional)
                - mapType: Filter by map type (optional)

        Returns:
            Maps list with pagination info
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to robot")

        if options is None:
            options = {}

        request_id = f"list_maps_{int(time.time() * 1000)}_{id(options) % 10000}"

        if not self._map_message_handler:
            self._setup_map_message_handler()

        loop = asyncio.get_event_loop()
        self._loop = loop  # Store for cross-thread callbacks
        future = loop.create_future()

        self._map_callbacks[request_id] = {'future': future, 'loop': loop}

        list_message = {
            'op': 'map_list',
            'request_id': request_id,
            'limit': options.get('limit', 50),
            'offset': options.get('offset', 0),
            'search': options.get('search'),
            'mapType': options.get('mapType')
        }

        self._send_ws_message(list_message)
        self._log('log', "Map list request sent")

        try:
            return await asyncio.wait_for(future, timeout=30.0)
        except asyncio.TimeoutError:
            if request_id in self._map_callbacks:
                del self._map_callbacks[request_id]
            raise TimeoutError("Map list request timed out")

    async def get_map(
        self,
        map_id: int,
        include_data: bool = False
    ) -> Dict[str, Any]:
        """
        Get a specific map by ID.

        Args:
            map_id: Map ID
            include_data: Whether to include map data (default: False)

        Returns:
            Map information
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to robot")

        request_id = f"get_map_{int(time.time() * 1000)}_{map_id}"

        if not self._map_message_handler:
            self._setup_map_message_handler()

        loop = asyncio.get_event_loop()
        self._loop = loop  # Store for cross-thread callbacks
        future = loop.create_future()

        self._map_callbacks[request_id] = {'future': future, 'loop': loop}

        get_message = {
            'op': 'map_get',
            'request_id': request_id,
            'mapId': map_id,
            'includeData': include_data
        }

        self._send_ws_message(get_message)
        self._log('log', f"Map get request sent: {map_id}")

        try:
            return await asyncio.wait_for(future, timeout=30.0)
        except asyncio.TimeoutError:
            if request_id in self._map_callbacks:
                del self._map_callbacks[request_id]
            raise TimeoutError(f"Get map request timed out for map ID: {map_id}")

    async def delete_map(self, map_id: int) -> Dict[str, Any]:
        """
        Delete a saved map.

        Args:
            map_id: Map ID to delete

        Returns:
            Deletion result
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to robot")

        request_id = f"delete_map_{int(time.time() * 1000)}_{map_id}"

        if not self._map_message_handler:
            self._setup_map_message_handler()

        loop = asyncio.get_event_loop()
        self._loop = loop  # Store for cross-thread callbacks
        future = loop.create_future()

        self._map_callbacks[request_id] = {'future': future, 'loop': loop}

        delete_message = {
            'op': 'map_delete',
            'request_id': request_id,
            'mapId': map_id
        }

        self._send_ws_message(delete_message)
        self._log('log', f"Map delete request sent: {map_id}")

        try:
            return await asyncio.wait_for(future, timeout=30.0)
        except asyncio.TimeoutError:
            if request_id in self._map_callbacks:
                del self._map_callbacks[request_id]
            raise TimeoutError(f"Delete map request timed out for map ID: {map_id}")

    async def get_map_storage_stats(self) -> Dict[str, Any]:
        """
        Get map storage statistics for current user.

        Returns:
            Storage statistics
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to robot")

        request_id = f"map_stats_{int(time.time() * 1000)}"

        if not self._map_message_handler:
            self._setup_map_message_handler()

        loop = asyncio.get_event_loop()
        self._loop = loop  # Store for cross-thread callbacks
        future = loop.create_future()

        self._map_callbacks[request_id] = {'future': future, 'loop': loop}

        stats_message = {
            'op': 'map_storage_stats',
            'request_id': request_id
        }

        self._send_ws_message(stats_message)
        self._log('log', "Map storage stats request sent")

        try:
            return await asyncio.wait_for(future, timeout=30.0)
        except asyncio.TimeoutError:
            if request_id in self._map_callbacks:
                del self._map_callbacks[request_id]
            raise TimeoutError("Map storage stats request timed out")

    # ===========================================
    # NAVIGATION ENGINE CONTROL
    # ===========================================

    async def start_navigation_engine(
        self,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start the Nav2 navigation engine on the appliance.
        Multiple instances can run concurrently if different robotNamespace values are provided.

        Args:
            options: Start options:
                - mode: 'slam' or 'localization' (default: 'slam')
                - mapId: Map ID to use for localization mode
                - initialPose: Initial pose {x, y, yaw}
                - configName: Name of configuration to use
                - configId: ID of configuration to use
                - robotNamespace: Robot namespace for multi-robot scenarios

        Returns:
            Start result with success status and mode
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to robot")

        if options is None:
            options = {}

        mode = options.get('mode', 'slam')
        config_id = options.get('configId')
        config_name = options.get('configName')
        robot_namespace = options.get('robotNamespace')

        # If localization mode with mapId, fetch map data
        map_data_base64 = None
        keepout_mask_data_base64 = None
        if mode == 'localization' and options.get('mapId') is not None:
            map_data = await self.get_map(options['mapId'], True)
            map_data_base64 = map_data.get('map_data')
            keepout_mask_data_base64 = map_data.get('keepout_mask_data')
            if keepout_mask_data_base64:
                self._log('log', "Map has keepout layer - will be applied to navigation")

        request_id = f"nav2_start_{int(time.time() * 1000)}_{id(options) % 10000}"

        if not self._map_message_handler:
            self._setup_map_message_handler()

        loop = asyncio.get_event_loop()
        self._loop = loop  # Store for cross-thread callbacks
        future = loop.create_future()

        self._map_callbacks[request_id] = {
            'future': future,
            'loop': loop,
            'initialPose': options.get('initialPose'),
            'mode': mode,
            'robotNamespace': robot_namespace,
            'needsPoseSet': mode == 'localization'
        }

        start_message = {
            'op': 'nav2_start',
            'request_id': request_id,
            'mode': mode,
            'mapData': map_data_base64,
            'keepoutMaskData': keepout_mask_data_base64,
            'configId': config_id,
            'configName': config_name,
            'robotNamespace': robot_namespace
        }

        self._send_ws_message(start_message)
        print(f"[OLONavigation] Nav2 start request sent (request_id: {request_id}, mode: {mode})", flush=True)

        try:
            return await asyncio.wait_for(future, timeout=120.0)  # 2 minutes for startup
        except asyncio.TimeoutError:
            if request_id in self._map_callbacks:
                del self._map_callbacks[request_id]
            raise TimeoutError("Nav2 start request timed out")

    async def stop_navigation_engine(
        self,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Stop the Nav2 navigation engine on the appliance.

        Args:
            options: Stop options:
                - robotNamespace: Robot namespace to stop (optional, undefined stops all)

        Returns:
            Stop result with success status
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to robot")

        if options is None:
            options = {}

        request_id = f"nav2_stop_{int(time.time() * 1000)}"

        if not self._map_message_handler:
            self._setup_map_message_handler()

        loop = asyncio.get_event_loop()
        self._loop = loop  # Store for cross-thread callbacks
        future = loop.create_future()

        self._map_callbacks[request_id] = {'future': future, 'loop': loop}

        stop_message = {
            'op': 'nav2_stop',
            'request_id': request_id
        }

        if options.get('robotNamespace'):
            stop_message['namespace'] = options['robotNamespace']

        self._send_ws_message(stop_message)

        try:
            return await asyncio.wait_for(future, timeout=60.0)
        except asyncio.TimeoutError:
            if request_id in self._map_callbacks:
                del self._map_callbacks[request_id]
            raise TimeoutError("Nav2 stop request timed out")

    async def get_navigation_status(
        self,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get Nav2 navigation status (uses process-based check for accuracy).

        Args:
            options: Status check options:
                - namespace: Robot namespace to check (optional)

        Returns:
            Navigation status information
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to robot")

        if options is None:
            options = {}

        try:
            self._log('log', "Checking Nav2 navigation status...")

            # Use the reliable process-based check
            engine_status = await self.check_navigation_engine_status(options.get('namespace'))

            self._log('log', f"Engine status result: {engine_status}")

            # Also get topic list for additional info
            topics = await self._core.list_topics()

            # Look for Nav2-specific topics
            nav2_action_topics = [
                t for t in topics
                if any(
                    k in t.get('name', '')
                    for k in ['navigate_to_pose', '/goal_pose', '/cancel_goal', 
                              'nav2', 'global_costmap', 'local_costmap', 'planner', 'controller']
                )
            ]

            result = {
                'nav2_available': engine_status.get('is_running', False),
                'is_running': engine_status.get('is_running', False),
                'running_components': engine_status.get('running_components', []),
                'available_topics': [t.get('name') for t in nav2_action_topics],
                'all_topics': [
                    t.get('name') for t in topics
                    if any(
                        k in t.get('name', '')
                        for k in ['nav', 'goal', 'cmd_vel', 'odom', 'map', 'pose', 'scan']
                    )
                ],
                'error': engine_status.get('error'),
                'timestamp': int(time.time() * 1000)
            }

            self._log('log', f"Final navigation status: {result}")
            return result

        except Exception as e:
            self._log('error', f"Error checking navigation status: {e}")
            return {
                'nav2_available': False,
                'is_running': False,
                'running_components': [],
                'available_topics': [],
                'all_topics': [],
                'error': str(e),
                'timestamp': int(time.time() * 1000)
            }

    async def check_navigation_engine_status(
        self,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check if Nav2 navigation engine is actually running (process-based check).

        Args:
            namespace: Robot namespace to check (optional)

        Returns:
            Status object with is_running and running_components
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to robot")

        request_id = f"nav2_status_check_{int(time.time() * 1000)}"

        if not self._map_message_handler:
            self._setup_map_message_handler()

        loop = asyncio.get_event_loop()
        self._loop = loop  # Store for cross-thread callbacks
        future = loop.create_future()

        self._map_callbacks[request_id] = {'future': future, 'loop': loop}

        message = {
            'op': 'nav2_status_check',
            'request_id': request_id
        }

        if namespace is not None:
            message['namespace'] = namespace

        self._send_ws_message(message)

        self._log('log', f"Nav2 status check request sent: {request_id}")

        try:
            return await asyncio.wait_for(future, timeout=10.0)
        except asyncio.TimeoutError:
            if request_id in self._map_callbacks:
                del self._map_callbacks[request_id]
            raise TimeoutError("Nav2 status check timed out - appliance may be unreachable")

    # ===========================================
    # INTERNAL HELPERS
    # ===========================================

    def _setup_map_message_handler(self) -> None:
        """Set up message handler for map operations"""
        self._log('log', "Setting up map message handler")

        def handler(message: Dict[str, Any]) -> None:
            op = message.get('op', '')
            if op.startswith('map_') or op.startswith('ros2_save_map') or op.startswith('nav2_'):
                # Always print nav2_start_result and nav2_stop_result for debugging
                if op in ('nav2_start_result', 'nav2_stop_result', 'nav2_status_response'):
                    print(f"[OLONavigation] Handler received: {op}", flush=True)
                try:
                    self._handle_map_message(message)
                except Exception as e:
                    import traceback
                    print(f"[OLONavigation] Error handling {op}: {e}", flush=True)
                    print(traceback.format_exc(), flush=True)

        self._map_message_handler = handler
        self._register_ws_handler(handler)

    def _handle_map_message(self, message: Dict[str, Any]) -> None:
        """Handle map operation responses"""
        op = message.get('op')
        request_id = message.get('request_id')

        # Handle Nav2 broadcast messages
        broadcast_ops = ['nav2_log', 'nav2_status', 'nav2_start_result', 'nav2_stop_result']
        if op in broadcast_ops:
            self._handle_nav2_broadcast_message(message)
            return

        entry = self._map_callbacks.get(request_id)
        if not entry:
            return

        future = entry.get('future')
        if not future or future.done():
            return

        # Use stored loop reference for cross-thread safety
        loop = entry.get('loop') or self._loop
        if not loop:
            self._log('error', "No event loop available for callback")
            return

        if op == 'ros2_save_map_ack':
            if entry.get('onProgress'):
                entry['onProgress']("Map save request acknowledged")

        elif op == 'map_save_response':
            if message.get('success'):
                loop.call_soon_threadsafe(future.set_result, message.get('result'))
            else:
                loop.call_soon_threadsafe(
                    future.set_exception,
                    Exception(message.get('error', 'Map save failed'))
                )
            if request_id in self._map_callbacks:
                del self._map_callbacks[request_id]

        elif op == 'map_list_response':
            if message.get('success'):
                loop.call_soon_threadsafe(future.set_result, message.get('result'))
            else:
                loop.call_soon_threadsafe(
                    future.set_exception,
                    Exception(message.get('error', 'Map list failed'))
                )
            if request_id in self._map_callbacks:
                del self._map_callbacks[request_id]

        elif op == 'map_get_response':
            if message.get('success'):
                loop.call_soon_threadsafe(future.set_result, message.get('result'))
            else:
                loop.call_soon_threadsafe(
                    future.set_exception,
                    Exception(message.get('error', 'Map get failed'))
                )
            if request_id in self._map_callbacks:
                del self._map_callbacks[request_id]

        elif op == 'map_delete_response':
            if message.get('success'):
                loop.call_soon_threadsafe(future.set_result, message.get('result'))
            else:
                loop.call_soon_threadsafe(
                    future.set_exception,
                    Exception(message.get('error', 'Map delete failed'))
                )
            if request_id in self._map_callbacks:
                del self._map_callbacks[request_id]

        elif op == 'map_storage_stats_response':
            if message.get('success'):
                loop.call_soon_threadsafe(future.set_result, message.get('result'))
            else:
                loop.call_soon_threadsafe(
                    future.set_exception,
                    Exception(message.get('error', 'Map stats failed'))
                )
            if request_id in self._map_callbacks:
                del self._map_callbacks[request_id]

        elif op == 'nav2_status_response':
            self._log('log', f"Nav2 status check result: {message}")
            if message.get('is_running'):
                components = message.get('running_components', [])
                loop.call_soon_threadsafe(future.set_result, {
                    'is_running': True,
                    'running_components': components,
                    'components': components
                })
            else:
                loop.call_soon_threadsafe(future.set_result, {
                    'is_running': False,
                    'running_components': [],
                    'components': [],
                    'error': message.get('error')
                })
            if request_id in self._map_callbacks:
                del self._map_callbacks[request_id]

        # Note: ros2_save_map_result is no longer used - appliance sends map_save_response directly

    def _send_ws_message(self, message: Dict[str, Any]) -> None:
        """Send a WebSocket message"""
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to robot")

        # Get protocol instance
        proto_instance = None
        if hasattr(self._ros, 'factory') and self._ros.factory:
            proto_instance = getattr(self._ros.factory, '_proto', None)

        if proto_instance:
            proto_instance.sendMessage(json.dumps(message).encode('utf-8'))
        else:
            raise ConnectionError("Cannot send message - protocol not connected")

    def _register_ws_handler(self, handler: Callable[[Dict[str, Any]], None]) -> None:
        """Register a handler for WebSocket messages"""
        # Import the registry function from package
        from . import register_webrtc_handler, _webrtc_message_handlers

        # Create a wrapper that parses the message if needed
        def wrapped_handler(msg):
            if isinstance(msg, dict):
                handler(msg)

        # Add to the webrtc handlers list (which handles all custom ops)
        if wrapped_handler not in _webrtc_message_handlers:
            _webrtc_message_handlers.append(wrapped_handler)

    def cleanup(self) -> None:
        """Clean up navigation callbacks and handlers"""
        self._navigation_callbacks.clear()
        self._map_callbacks.clear()

