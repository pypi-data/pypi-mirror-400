"""
OLO Joint API - Joint Control and Manipulation
Handles robot joint control, joint state management, and trajectory publishing.
"""

import asyncio
import re
from typing import List, Dict, Any, Optional, Callable


class OLOJoint:
    """
    Joint control API for robot arm manipulation.
    Mirrors the JavaScript OLOJointClient API.
    
    Provides methods for:
    - Joint state reading and monitoring
    - Arm joint detection
    - Joint trajectory publishing
    - Movement control with abort support
    """

    def __init__(self, ros_client, core):
        """
        Initialize OLO Joint module

        Args:
            ros_client: roslibpy.Ros instance
            core: OLOCore instance for publishing/subscribing
        """
        self._ros = ros_client
        self._core = core
        self._cached_joint_states = None
        self._joint_state_subscription = None
        # Caching for robot info auto-detection
        self._cached_srdf = None
        self._cached_srdf_timestamp = 0
        self._cached_urdf = None
        self._cached_urdf_timestamp = 0
        self._cached_robot_info = None
        self._cached_robot_info_timestamp = 0

    async def get_current_joint_states(self) -> Dict[str, Any]:
        """
        Get current joint states

        Returns:
            Dict with:
                - names: List of joint names
                - positions: List of positions
                - velocities: List of velocities
                - efforts: List of efforts
                - jointStates: Dict mapping name -> position
                - timestamp: Timestamp
        """
        import roslibpy

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        import time as time_module
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        topic = roslibpy.Topic(
            self._ros,
            '/joint_states',
            'sensor_msgs/JointState'
        )

        def callback(message):
            try:
                names = message.get('name', [])
                positions = message.get('position', [])
                velocities = message.get('velocity', [])
                efforts = message.get('effort', [])

                if not names or not positions:
                    if not future.done():
                        loop.call_soon_threadsafe(
                            future.set_exception,
                            Exception('Invalid joint states message')
                        )
                    return

                joint_states = {}
                for i, name in enumerate(names):
                    joint_states[name] = positions[i] if i < len(positions) else 0.0

                result = {
                    'names': names,
                    'positions': positions,
                    'velocities': velocities,
                    'efforts': efforts,
                    'jointStates': joint_states,
                    'timestamp': time_module.time()
                }

                # Cache the joint states
                self._cached_joint_states = result

                topic.unsubscribe()
                if not future.done():
                    loop.call_soon_threadsafe(future.set_result, result)
            except Exception as e:
                topic.unsubscribe()
                if not future.done():
                    loop.call_soon_threadsafe(future.set_exception, e)

        topic.subscribe(callback)

        try:
            return await asyncio.wait_for(future, timeout=3.0)
        except asyncio.TimeoutError:
            topic.unsubscribe()
            raise TimeoutError("Timeout waiting for joint states")

    async def subscribe_to_joint_states(self, callback: Callable[[Dict], None]) -> str:
        """
        Subscribe to joint states with callback

        Args:
            callback: Function to call with joint state updates

        Returns:
            Subscription ID (topic name)
        """
        # Unsubscribe from any existing subscription
        if self._joint_state_subscription:
            await self._core.unsubscribe('/joint_states')
            self._joint_state_subscription = None

        import time as time_module

        def wrapped_callback(message):
            names = message.get('name', [])
            positions = message.get('position', [])
            velocities = message.get('velocity', [])
            efforts = message.get('effort', [])

            if names and positions:
                joint_states = {}
                for i, name in enumerate(names):
                    joint_states[name] = positions[i] if i < len(positions) else 0.0

                result = {
                    'names': names,
                    'positions': positions,
                    'velocities': velocities,
                    'efforts': efforts,
                    'jointStates': joint_states,
                    'timestamp': time_module.time()
                }

                # Cache the joint states
                self._cached_joint_states = result

                callback(result)

        self._joint_state_subscription = await self._core.subscribe(
            '/joint_states',
            wrapped_callback,
            message_type='sensor_msgs/JointState'
        )

        return self._joint_state_subscription

    async def detect_arm_joints(self, options: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Auto-detect arm joints from joint states

        Args:
            options: Optional dict with:
                - excludePatterns: List of regex patterns to exclude (default: gripper/finger)
                - maxJoints: Maximum number of joints to return (default: 7)

        Returns:
            List of detected arm joint names
        """
        if options is None:
            options = {}

        joint_states = await self.get_current_joint_states()
        joint_names = joint_states['names']

        exclude_patterns = options.get('excludePatterns', [
            re.compile(r'(finger|hand|grip|gripper|thumb|palm)', re.I)
        ])
        max_joints = options.get('maxJoints', 7)

        # Helper: detect a group of numbered joints
        def detect_numbered_joint_group(names):
            groups = {}

            for idx, n in enumerate(names):
                # Try to capture a prefix and trailing number
                m = re.match(r'^(.*?)(?:[_-]?(?:joint))?[_-]?(\d+)$', n, re.I)
                if not m:
                    continue
                prefix = m.group(1) or ''
                num = int(m.group(2))
                if prefix not in groups:
                    groups[prefix] = []
                groups[prefix].append({'name': n, 'idx': idx, 'num': num})

            # Choose the group with the largest number of members
            best = None
            for arr in groups.values():
                if not best or len(arr) > len(best):
                    best = arr

            if not best or len(best) < 2:
                return None

            best.sort(key=lambda x: x['num'])
            return [x['name'] for x in best]

        # Try numbered group detection first
        arm_joints = detect_numbered_joint_group(joint_names)

        if not arm_joints:
            # Fallback: filter out gripper/finger joints
            filtered = []
            for name in joint_names:
                excluded = False
                for pattern in exclude_patterns:
                    if pattern.search(name):
                        excluded = True
                        break
                if not excluded:
                    filtered.append(name)
            arm_joints = filtered[:min(max_joints, len(filtered))]

        if not arm_joints:
            raise Exception('No arm joints detected')

        print(f'[OLOJoint] Detected arm joints: {", ".join(arm_joints)}')
        return arm_joints

    async def detect_joint_trajectory_topic(self) -> str:
        """
        Auto-detect joint trajectory topic for arm control

        Returns:
            Trajectory topic name
        """
        topics = await self._core.list_topics(refresh=True)

        # Score candidates
        candidates = []
        for t in topics:
            name = t.get('name', '')
            msg_type = t.get('type', '')

            if msg_type == 'trajectory_msgs/JointTrajectory' or \
               'joint_trajectory' in name.lower():
                score = 0
                if msg_type == 'trajectory_msgs/JointTrajectory':
                    score += 10
                if 'controller' in name.lower():
                    score += 5
                if 'arm' in name.lower() or 'manipulator' in name.lower():
                    score += 2
                if 'joint_trajectory' in name.lower():
                    score += 1
                candidates.append({'name': name, 'type': msg_type, 'score': score})

        if not candidates:
            raise Exception('No joint trajectory topic found')

        # Sort by score descending
        candidates.sort(key=lambda x: -x['score'])
        selected = candidates[0]['name']

        print(f'[OLOJoint] Detected trajectory topic: {selected}')
        return selected

    async def publish_joint_trajectory(
        self,
        topic: str,
        joint_names: List[str],
        points: List[Dict[str, Any]],
        options: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Publish joint trajectory

        Args:
            topic: Trajectory topic name
            joint_names: Joint names in order
            points: Trajectory points with positions, velocities, time_from_start
            options: Publishing options (frameId, etc.)
        """
        if options is None:
            options = {}

        # Build trajectory message
        message = {
            'header': {
                'frame_id': options.get('frameId', ''),
                'stamp': {
                    'sec': 0,
                    'nanosec': 0
                }
            },
            'joint_names': joint_names,
            'points': []
        }

        for point in points:
            traj_point = {
                'positions': point.get('positions', []),
                'velocities': point.get('velocities', [0.0] * len(joint_names)),
                'accelerations': point.get('accelerations', [0.0] * len(joint_names)),
                'time_from_start': point.get('time_from_start', {'sec': 1, 'nanosec': 0})
            }
            message['points'].append(traj_point)

        print(f'[OLOJoint] Publishing trajectory to {topic} for joints: {", ".join(joint_names)}')
        await self._core.publish(topic, message, {'messageType': 'trajectory_msgs/JointTrajectory'})

    async def move_joints_to_positions(
        self,
        joint_names: List[str],
        target_positions: List[float],
        options: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Move joints to target positions

        Args:
            joint_names: Joint names in order
            target_positions: Target positions for each joint
            options: Movement options:
                - topic: Trajectory topic (optional, auto-detected)
                - duration: Movement duration in seconds (default: 2)
                - currentPositions: Current positions (optional, fetched if not provided)
                - abortSignal: Signal dict with 'aborted' key
        """
        if options is None:
            options = {}

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        abort_signal = options.get('abortSignal')

        # Check if already aborted
        if abort_signal and abort_signal.get('aborted'):
            raise Exception('Aborted')

        if len(joint_names) != len(target_positions):
            raise ValueError('Joint names and positions arrays must have same length')

        # Get current positions if not provided
        current_positions = options.get('currentPositions')
        if not current_positions:
            if abort_signal and abort_signal.get('aborted'):
                raise Exception('Aborted')

            joint_states = await self.get_current_joint_states()
            current_positions = [
                joint_states['jointStates'].get(name, 0.0)
                for name in joint_names
            ]

        # Auto-detect trajectory topic if not provided
        topic = options.get('topic')
        if not topic:
            if abort_signal and abort_signal.get('aborted'):
                raise Exception('Aborted')

            topic = await self.detect_joint_trajectory_topic()

        # Final abort check
        if abort_signal and abort_signal.get('aborted'):
            raise Exception('Aborted')

        duration = options.get('duration', 2)
        points = [
            # Start point (current positions)
            {
                'positions': current_positions,
                'time_from_start': {'sec': 0, 'nanosec': 0}
            },
            # End point (target positions)
            {
                'positions': target_positions,
                'time_from_start': {'sec': duration, 'nanosec': 0}
            }
        ]

        print(f'[OLOJoint] Moving {len(joint_names)} joints over {duration}s')

        # Publish the trajectory
        await self.publish_joint_trajectory(topic, joint_names, points, options)
        print('[OLOJoint] Trajectory published, robot is moving...')

        # Wait for trajectory duration while checking abort signal
        trajectory_duration_s = duration
        check_interval = 0.1
        elapsed = 0.0

        while elapsed < trajectory_duration_s:
            if abort_signal and abort_signal.get('aborted'):
                print('[OLOJoint] Joint movement aborted - stopping')
                try:
                    await self.stop_joint_movement(topic, joint_names)
                    print('[OLOJoint] Joint movement successfully stopped')
                except Exception as e:
                    print(f'[OLOJoint] Could not send stop trajectory: {e}')
                raise Exception('Aborted')

            await asyncio.sleep(check_interval)
            elapsed += check_interval

        print('[OLOJoint] Joint trajectory completed successfully')

    async def stop_joint_movement(self, topic: str, joint_names: List[str]) -> None:
        """
        Stop joint movement by publishing a hold trajectory

        Args:
            topic: Trajectory topic name
            joint_names: Joint names
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        print('[OLOJoint] Stopping joint movement')

        # Get current positions
        joint_states = await self.get_current_joint_states()
        current_positions = [
            joint_states['jointStates'].get(name, 0.0)
            for name in joint_names
        ]

        # Send hold trajectory (two points at current position)
        hold_duration = 0.05
        hold_points = [
            {
                'positions': current_positions,
                'time_from_start': {'sec': 0, 'nanosec': 0}
            },
            {
                'positions': current_positions,
                'time_from_start': {
                    'sec': int(hold_duration),
                    'nanosec': int((hold_duration % 1) * 1_000_000_000)
                }
            }
        ]

        await self.publish_joint_trajectory(topic, joint_names, hold_points)
        print('[OLOJoint] Hold trajectory sent')

    async def stop_all_joints(self) -> None:
        """
        Stop all arm joints immediately
        """
        try:
            arm_joints = await self.detect_arm_joints()
            topic = await self.detect_joint_trajectory_topic()
            await self.stop_joint_movement(topic, arm_joints)
        except Exception as e:
            print(f'[OLOJoint] Failed to stop all joints: {e}')
            raise

    def get_cached_joint_states(self) -> Optional[Dict[str, Any]]:
        """
        Get cached joint states if available

        Returns:
            Cached joint states or None
        """
        return self._cached_joint_states

    async def move_end_effector_to_position(
        self,
        target_pose: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Move end effector to target position using inverse kinematics planning.

        Args:
            target_pose: Target pose for end effector
                - position: Dict with x, y, z in meters
                - orientation: Optional Dict with x, y, z, w quaternion
            options: Movement options
                - planningGroup: MoveIt planning group (auto-detected if not provided)
                - endEffectorLink: End effector link name (auto-detected if not provided)
                - baseFrame: Base frame for pose coordinates (auto-detected if not provided)
                - timeout: Planning timeout in seconds (default: 5)
                - executeTrajectory: Whether to execute (default: True)
                - speed: Speed multiplier (default: 1.0)
                - maxJointDisplacement: Max radians each joint can move from current position.
                    Default is PI (180 deg). Use lower values like 0.5 (30 deg) to prevent
                    sweeping moves and force nearby IK solutions.
                - abortSignal: Signal dict with 'aborted' key

        Returns:
            Dict with planning result including joint_names, joint_positions, etc.
        """
        import json
        import time
        import random
        import string

        if options is None:
            options = {}

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        abort_signal = options.get('abortSignal')

        # Check if already aborted
        if abort_signal and abort_signal.get('aborted'):
            raise Exception('Aborted')

        if not target_pose or 'position' not in target_pose:
            raise ValueError('Target pose with position {x, y, z} is required')

        print(f'[OLOJoint] Planning end effector movement to position: {target_pose["position"]}')

        # Get orientation - use provided or default to identity quaternion
        orientation = target_pose.get('orientation')
        if not orientation:
            print('[OLOJoint] No orientation specified, using identity quaternion')
            orientation = {'x': 0, 'y': 0, 'z': 0, 'w': 1}

        # Get options or auto-detect planning group, end effector, and base frame
        planning_group = options.get('planningGroup')
        end_effector_link = options.get('endEffectorLink')
        base_frame = options.get('baseFrame')
        timeout = options.get('timeout', 5)
        execute_trajectory = options.get('executeTrajectory', True)
        speed = options.get('speed', 1.0)

        # Auto-detect planning group, end effector, and base frame if not provided
        if not planning_group or not end_effector_link or not base_frame:
            # Check abort signal before potentially slow operation
            if abort_signal and abort_signal.get('aborted'):
                raise Exception('Aborted')
            
            try:
                robot_info = await self.detect_robot_info()
                if robot_info:
                    planning_group = planning_group or robot_info.get('planning_group')
                    end_effector_link = end_effector_link or robot_info.get('end_effector_link')
                    base_frame = base_frame or robot_info.get('base_frame')
            except Exception as e:
                print(f'[OLOJoint] Could not auto-detect robot info: {e}')
        
        # Final fallbacks if auto-detection failed
        if not planning_group:
            print('[OLOJoint] Warning: Could not auto-detect planning group, using fallback')
            planning_group = 'manipulator'  # Common default for UR robots
        if not end_effector_link:
            print('[OLOJoint] Warning: Could not auto-detect end effector, using fallback')
            end_effector_link = 'tool0'  # Common default for UR robots
        if not base_frame:
            print('[OLOJoint] Warning: Could not auto-detect base frame, using fallback')
            base_frame = 'base_link'

        # Final abort check before planning
        if abort_signal and abort_signal.get('aborted'):
            raise Exception('Aborted')

        print(f'[OLOJoint] Using planning group: {planning_group}, end effector: {end_effector_link}')
        print(f'[OLOJoint] Using base frame: {base_frame}')

        # Generate unique request ID
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        request_id = f'ik_{int(time.time() * 1000)}_{random_suffix}'

        # Create IK request
        ik_request = {
            'op': 'execute_moveit_ik',
            'request_id': request_id,
            'planning_group': planning_group,
            'end_effector_link': end_effector_link,
            'target_pose': {
                'position': target_pose['position'],
                'orientation': orientation
            },
            'timeout': timeout,
            'execute_trajectory': execute_trajectory,
            'base_frame': base_frame,
            'speed': speed
        }
        
        # Add maxJointDisplacement if provided
        max_joint_displacement = options.get('maxJointDisplacement')
        if max_joint_displacement is not None:
            ik_request['max_joint_displacement'] = max_joint_displacement

        print(f'[OLOJoint] Sending IK planning request')

        # Send request and wait for response
        result = await self._send_ik_request(ik_request, timeout + 2)

        # Check abort after completion
        if abort_signal and abort_signal.get('aborted'):
            print('[OLOJoint] IK planning/execution aborted by user')
            try:
                await self.stop_all_joints()
                print('[OLOJoint] Robot movement successfully stopped')
            except Exception as e:
                print(f'[OLOJoint] Could not stop robot movement: {e}')
            raise Exception('Aborted')

        print('[OLOJoint] End effector movement completed successfully')
        return result

    async def _send_ik_request(
        self,
        ik_request: Dict[str, Any],
        timeout: float
    ) -> Dict[str, Any]:
        """
        Send IK request to the appliance and wait for response

        Args:
            ik_request: The IK request dict
            timeout: Timeout in seconds

        Returns:
            Planning result dict
        """
        import json

        loop = asyncio.get_running_loop()
        future = loop.create_future()
        request_id = ik_request['request_id']

        def handle_message(msg):
            """Handle incoming messages looking for our response"""
            try:
                if isinstance(msg, str):
                    data = json.loads(msg)
                elif isinstance(msg, dict):
                    data = msg
                else:
                    return

                if data.get('request_id') != request_id:
                    return

                op = data.get('op', '')

                if op == 'moveit_ik_result':
                    if data.get('success'):
                        print('[OLOJoint] IK planning successful')
                        result = data.get('result', {})
                        if not future.done():
                            loop.call_soon_threadsafe(future.set_result, result)
                    else:
                        error_msg = data.get('error', 'IK planning failed')
                        print(f'[OLOJoint] IK planning failed: {error_msg}')
                        if not future.done():
                            loop.call_soon_threadsafe(
                                future.set_exception,
                                Exception(error_msg)
                            )
            except (json.JSONDecodeError, TypeError):
                pass

        # Get the protocol instance for sending/receiving messages
        proto_instance = None
        if hasattr(self._ros, 'factory') and self._ros.factory:
            proto_instance = getattr(self._ros.factory, '_proto', None)

        # Hook into roslibpy's message handling
        old_onMessage = None
        custom_ops = {'moveit_ik_result'}

        if proto_instance and hasattr(proto_instance, 'onMessage'):
            old_onMessage = proto_instance.onMessage

            def patched_onMessage(payload, isBinary):
                if not isBinary:
                    try:
                        msg_str = payload.decode('utf-8') if isinstance(payload, bytes) else payload
                        msg = json.loads(msg_str)
                        op = msg.get('op', '')

                        # Handle our custom messages
                        handle_message(msg_str)

                        # Only call original handler for non-custom ops
                        if op not in custom_ops and old_onMessage:
                            old_onMessage(payload, isBinary)
                    except json.JSONDecodeError:
                        if old_onMessage:
                            old_onMessage(payload, isBinary)
                else:
                    if old_onMessage:
                        old_onMessage(payload, isBinary)

            proto_instance.onMessage = patched_onMessage

        try:
            # Send the message
            msg_json = json.dumps(ik_request)
            if proto_instance:
                proto_instance.sendMessage(msg_json.encode('utf-8'))
            else:
                raise ConnectionError("Cannot send message - protocol not connected")

            # Wait for response with timeout
            return await asyncio.wait_for(future, timeout=timeout)

        except asyncio.TimeoutError:
            raise TimeoutError(f"IK planning request timed out after {timeout}s")
        finally:
            # Restore original handler
            if proto_instance and old_onMessage is not None:
                proto_instance.onMessage = old_onMessage

    async def execute_planned_trajectory(
        self,
        plan_result: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a previously planned trajectory.
        
        This allows for a two-step workflow: plan first (with executeTrajectory: false),
        review/validate the plan, then execute it separately.

        Args:
            plan_result: The planning result from move_end_effector_to_position
                - joint_names: List of joint names
                - joint_positions: List of target positions
            options: Execution options
                - speed: Speed multiplier (default: 1.0)
                - abortSignal: Signal dict with 'aborted' key

        Returns:
            Dict with execution result
        """
        import json
        import time
        import random
        import string

        if options is None:
            options = {}

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        abort_signal = options.get('abortSignal')

        # Check if already aborted
        if abort_signal and abort_signal.get('aborted'):
            raise Exception('Aborted')

        # Validate plan result
        if not plan_result:
            raise ValueError('Plan result is required')

        joint_names = plan_result.get('joint_names', [])
        joint_positions = plan_result.get('joint_positions', [])

        if not joint_names or len(joint_names) == 0:
            raise ValueError('Invalid plan result: missing joint_names array')

        if not joint_positions or len(joint_positions) == 0:
            raise ValueError('Invalid plan result: missing joint_positions array')

        if len(joint_names) != len(joint_positions):
            raise ValueError('Invalid plan result: joint_names and joint_positions must have same length')

        print(f'[OLOJoint] Executing planned trajectory for {len(joint_names)} joints')

        # Generate unique request ID
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        request_id = f'exec_{int(time.time() * 1000)}_{random_suffix}'

        # Create execution request
        execution_request = {
            'op': 'execute_planned_trajectory',
            'request_id': request_id,
            'joint_names': joint_names,
            'joint_positions': joint_positions,
            'speed': options.get('speed', 1.0)
        }

        # Send request and wait for response
        result = await self._send_execution_request(execution_request, 30)

        # Check abort after completion
        if abort_signal and abort_signal.get('aborted'):
            print('[OLOJoint] Trajectory execution aborted by user')
            try:
                await self.stop_all_joints()
                print('[OLOJoint] Robot movement successfully stopped')
            except Exception as e:
                print(f'[OLOJoint] Could not stop robot movement: {e}')
            raise Exception('Aborted')

        print('[OLOJoint] Planned trajectory execution completed successfully')
        return result

    async def _send_execution_request(
        self,
        execution_request: Dict[str, Any],
        timeout: float
    ) -> Dict[str, Any]:
        """
        Send execution request to the appliance and wait for response

        Args:
            execution_request: The execution request dict
            timeout: Timeout in seconds

        Returns:
            Execution result dict
        """
        import json

        loop = asyncio.get_running_loop()
        future = loop.create_future()
        request_id = execution_request['request_id']

        def handle_message(msg):
            """Handle incoming messages looking for our response"""
            try:
                if isinstance(msg, str):
                    data = json.loads(msg)
                elif isinstance(msg, dict):
                    data = msg
                else:
                    return

                if data.get('request_id') != request_id:
                    return

                op = data.get('op', '')

                if op == 'execute_planned_trajectory_result':
                    if data.get('success'):
                        print('[OLOJoint] Trajectory execution successful')
                        result = data.get('result', {})
                        if not future.done():
                            loop.call_soon_threadsafe(future.set_result, result)
                    else:
                        error_msg = data.get('error', 'Trajectory execution failed')
                        print(f'[OLOJoint] Trajectory execution failed: {error_msg}')
                        if not future.done():
                            loop.call_soon_threadsafe(
                                future.set_exception,
                                Exception(error_msg)
                            )
            except (json.JSONDecodeError, TypeError):
                pass

        # Get the protocol instance for sending/receiving messages
        proto_instance = None
        if hasattr(self._ros, 'factory') and self._ros.factory:
            proto_instance = getattr(self._ros.factory, '_proto', None)

        # Hook into roslibpy's message handling
        old_onMessage = None
        custom_ops = {'execute_planned_trajectory_result'}

        if proto_instance and hasattr(proto_instance, 'onMessage'):
            old_onMessage = proto_instance.onMessage

            def patched_onMessage(payload, isBinary):
                if not isBinary:
                    try:
                        msg_str = payload.decode('utf-8') if isinstance(payload, bytes) else payload
                        msg = json.loads(msg_str)
                        op = msg.get('op', '')

                        # Handle our custom messages
                        handle_message(msg_str)

                        # Only call original handler for non-custom ops
                        if op not in custom_ops and old_onMessage:
                            old_onMessage(payload, isBinary)
                    except json.JSONDecodeError:
                        if old_onMessage:
                            old_onMessage(payload, isBinary)
                else:
                    if old_onMessage:
                        old_onMessage(payload, isBinary)

            proto_instance.onMessage = patched_onMessage

        try:
            # Send the message
            msg_json = json.dumps(execution_request)
            if proto_instance:
                proto_instance.sendMessage(msg_json.encode('utf-8'))
                print('[OLOJoint] Sent trajectory execution request to appliance')
            else:
                raise ConnectionError("Cannot send message - protocol not connected")

            # Wait for response with timeout
            return await asyncio.wait_for(future, timeout=timeout)

        except asyncio.TimeoutError:
            raise TimeoutError(f"Trajectory execution request timed out after {timeout}s")
        finally:
            # Restore original handler
            if proto_instance and old_onMessage is not None:
                proto_instance.onMessage = old_onMessage

    async def get_available_planning_groups(self) -> List[str]:
        """
        Get list of available planning groups from robot configuration.

        Returns:
            List of planning group names
        """
        try:
            robot_info = await self.detect_robot_info()
            if robot_info and robot_info.get('available_groups'):
                return robot_info['available_groups']
        except Exception as e:
            print(f'[OLOJoint] Could not get planning groups: {e}')
        return []

    async def get_srdf(self) -> str:
        """
        Get SRDF (Semantic Robot Description Format) data from the appliance.
        
        Returns:
            SRDF XML string
        """
        import json
        import time as time_module
        import random
        import string
        import base64

        # Return cached SRDF if fresh (1 minute cache)
        now = time_module.time()
        if self._cached_srdf and (now - self._cached_srdf_timestamp) < 60:
            print('[OLOJoint] Using cached SRDF')
            return self._cached_srdf

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        loop = asyncio.get_running_loop()
        future = loop.create_future()

        # Generate unique request ID
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        request_id = f'srdf_{int(time_module.time() * 1000)}_{random_suffix}'

        def handle_message(msg):
            try:
                if isinstance(msg, str):
                    data = json.loads(msg)
                elif isinstance(msg, dict):
                    data = msg
                else:
                    return

                if data.get('request_id') != request_id:
                    return

                op = data.get('op', '')

                if op == 'srdf_data':
                    if data.get('error'):
                        if not future.done():
                            loop.call_soon_threadsafe(
                                future.set_exception,
                                Exception(data['error'])
                            )
                    else:
                        # Decode base64 SRDF data
                        srdf_data = base64.b64decode(data.get('data', '')).decode('utf-8')
                        if not future.done():
                            loop.call_soon_threadsafe(future.set_result, srdf_data)
            except (json.JSONDecodeError, TypeError):
                pass

        # Get the protocol instance
        proto_instance = None
        if hasattr(self._ros, 'factory') and self._ros.factory:
            proto_instance = getattr(self._ros.factory, '_proto', None)

        old_onMessage = None
        custom_ops = {'srdf_data'}

        if proto_instance and hasattr(proto_instance, 'onMessage'):
            old_onMessage = proto_instance.onMessage

            def patched_onMessage(payload, isBinary):
                if not isBinary:
                    try:
                        msg_str = payload.decode('utf-8') if isinstance(payload, bytes) else payload
                        msg = json.loads(msg_str)
                        op = msg.get('op', '')
                        handle_message(msg_str)
                        if op not in custom_ops and old_onMessage:
                            old_onMessage(payload, isBinary)
                    except json.JSONDecodeError:
                        if old_onMessage:
                            old_onMessage(payload, isBinary)
                else:
                    if old_onMessage:
                        old_onMessage(payload, isBinary)

            proto_instance.onMessage = patched_onMessage

        try:
            request = {
                'op': 'get_srdf',
                'request_id': request_id
            }
            msg_json = json.dumps(request)
            if proto_instance:
                proto_instance.sendMessage(msg_json.encode('utf-8'))
            else:
                raise ConnectionError("Cannot send message - protocol not connected")

            result = await asyncio.wait_for(future, timeout=5.0)
            
            # Cache the result
            self._cached_srdf = result
            self._cached_srdf_timestamp = time_module.time()
            
            return result

        except asyncio.TimeoutError:
            raise TimeoutError("Timeout waiting for SRDF data")
        finally:
            if proto_instance and old_onMessage is not None:
                proto_instance.onMessage = old_onMessage

    async def get_robot_description(self) -> str:
        """
        Get URDF robot description from the /robot_description topic.
        
        Returns:
            URDF XML string
        """
        import time as time_module

        # Return cached URDF if fresh (1 minute cache)
        now = time_module.time()
        if self._cached_urdf and (now - self._cached_urdf_timestamp) < 60:
            print('[OLOJoint] Using cached robot description')
            return self._cached_urdf

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        loop = asyncio.get_running_loop()
        future = loop.create_future()

        # Subscribe to /robot_description topic
        from roslibpy import Topic

        topic = Topic(self._ros, '/robot_description', 'std_msgs/String')

        def callback(message):
            if not future.done():
                loop.call_soon_threadsafe(future.set_result, message.get('data', ''))
            topic.unsubscribe()

        topic.subscribe(callback)

        try:
            result = await asyncio.wait_for(future, timeout=5.0)
            
            # Cache the result
            self._cached_urdf = result
            self._cached_urdf_timestamp = time_module.time()
            
            return result
        except asyncio.TimeoutError:
            topic.unsubscribe()
            raise TimeoutError("Timeout waiting for robot description")

    async def detect_robot_info(self) -> Optional[Dict[str, Any]]:
        """
        Auto-detect robot configuration from SRDF and URDF.
        Returns planning group, end effector link, base frame, and available groups.
        
        Returns:
            Dict with planningGroup, endEffectorLink, baseFrame, availableGroups
        """
        import time as time_module
        import xml.etree.ElementTree as ET

        # Return cached robot info if fresh
        now = time_module.time()
        is_fallback = self._cached_robot_info and self._cached_robot_info.get('is_fallback', False)
        ttl = 5 if is_fallback else 60  # 5s for fallback, 1min for proper detection
        
        if self._cached_robot_info and (now - self._cached_robot_info_timestamp) < ttl:
            print('[OLOJoint] Using cached robot info')
            return self._cached_robot_info

        try:
            # Get SRDF data
            srdf_data = await self.get_srdf()
            print('[OLOJoint] Parsing SRDF data for robot configuration...')
            
            # Parse SRDF XML
            root = ET.fromstring(srdf_data)
            
            # Find all planning groups
            planning_groups = []
            group_defs = {}
            
            for group in root.findall('.//group'):
                name = group.get('name')
                if not name:
                    continue
                
                # Get joints, links, and chains defined in this group
                joints = [j.get('name') for j in group.findall('joint') if j.get('name')]
                links = [l.get('name') for l in group.findall('link') if l.get('name')]
                chains = [{'base': c.get('base_link'), 'tip': c.get('tip_link')} 
                         for c in group.findall('chain') if c.get('base_link') and c.get('tip_link')]
                
                if joints or links or chains:
                    print(f"[OLOJoint] Group '{name}': joints={joints}, links={links}, chains={chains}")
                    planning_groups.append(name)
                    group_defs[name] = {'joints': joints, 'links': links, 'chains': chains}
            
            print(f'[OLOJoint] Found planning groups: {planning_groups}')
            
            # Choose the best planning group (prefer arm-like groups)
            selected_group = None
            arm_priorities = ['arm', 'manipulator', 'robot']
            
            for priority in arm_priorities:
                for group in planning_groups:
                    if priority in group.lower():
                        selected_group = group
                        break
                if selected_group:
                    break
            
            # If no arm-like group found, use the first non-gripper group
            if not selected_group and planning_groups:
                for group in planning_groups:
                    if 'gripper' not in group.lower() and 'hand' not in group.lower():
                        selected_group = group
                        break
                if not selected_group:
                    selected_group = planning_groups[0]
            
            # Extract end effector information from SRDF
            end_effector_link = None
            for ee in root.findall('.//end_effector'):
                parent_link = ee.get('parent_link')
                if parent_link:
                    end_effector_link = parent_link
                    print(f'[OLOJoint] Found end effector from SRDF: {end_effector_link}')
                    break
            
            # If no end effector in SRDF, look at selected group's chains
            if not end_effector_link and selected_group and selected_group in group_defs:
                chains = group_defs[selected_group].get('chains', [])
                if chains:
                    end_effector_link = chains[0].get('tip')
                    print(f'[OLOJoint] Found end effector from chain tip: {end_effector_link}')
            
            # Try to get end effector from URDF if still not found
            if not end_effector_link:
                try:
                    end_effector_link = await self._detect_end_effector_from_urdf()
                    print(f'[OLOJoint] Got end effector from URDF: {end_effector_link}')
                except Exception as e:
                    print(f'[OLOJoint] Could not detect end effector from URDF: {e}')
                    end_effector_link = 'tool0'  # Final fallback
            
            # Detect base frame from URDF
            base_frame = 'base_link'
            try:
                base_frame = await self._detect_base_frame_from_urdf()
            except Exception as e:
                print(f'[OLOJoint] Could not detect base frame from URDF: {e}')
            
            robot_info = {
                'planning_group': selected_group,
                'end_effector_link': end_effector_link,
                'base_frame': base_frame,
                'available_groups': planning_groups,
                'group_definitions': group_defs
            }
            
            # Cache the result
            self._cached_robot_info = robot_info
            self._cached_robot_info_timestamp = time_module.time()
            
            print(f'[OLOJoint] Detected robot info: {robot_info}')
            return robot_info
            
        except Exception as e:
            print(f'[OLOJoint] Could not detect robot info from SRDF: {e}')
            return None

    async def _detect_end_effector_from_urdf(self) -> str:
        """
        Detect end effector link from URDF by finding leaf links or pattern matching.
        
        Returns:
            End effector link name
        """
        urdf = await self.get_robot_description()
        
        # Method 1: Look for links with end effector naming patterns
        end_effector_patterns = ['tool0', 'tcp', 'end_effector', 'eef', 'gripper', 'hand']
        
        for pattern in end_effector_patterns:
            import re
            match = re.search(rf'<link\s+name="([^"]*{pattern}[^"]*)"', urdf, re.IGNORECASE)
            if match:
                print(f'[OLOJoint] Found end effector link by pattern: {match.group(1)}')
                return match.group(1)
        
        # Method 2: Find leaf link (link that is not a parent in any joint)
        import re
        link_matches = re.findall(r'<link\s+name="([^"]+)"', urdf)
        all_links = set(link_matches)
        
        parent_matches = re.findall(r'<parent\s+link="([^"]+)"', urdf)
        parent_links = set(parent_matches)
        
        # Leaf links are links that are never parents
        child_matches = re.findall(r'<child\s+link="([^"]+)"', urdf)
        child_links = set(child_matches)
        
        # Links that are children but not parents
        leaf_links = [l for l in all_links if l not in parent_links and l in child_links]
        if leaf_links:
            print(f'[OLOJoint] Found end effector as leaf link: {leaf_links[0]}')
            return leaf_links[0]
        
        return 'tool0'

    async def _detect_base_frame_from_urdf(self) -> str:
        """
        Detect base frame from URDF.
        
        Returns:
            Base frame name
        """
        urdf = await self.get_robot_description()
        import re
        
        # Prefer common base names if present
        common_bases = ['base_link', 'world', 'base', 'base_footprint']
        for base in common_bases:
            if re.search(rf'<link\s+name="{base}"', urdf):
                return base
        
        # Compute root link: link that never appears as a child in any joint
        link_matches = re.findall(r'<link\s+name="([^"]+)"', urdf)
        all_links = set(link_matches)
        
        child_matches = re.findall(r'<child\s+link="([^"]+)"', urdf)
        child_links = set(child_matches)
        
        roots = [name for name in all_links if name not in child_links]
        if roots:
            return roots[0]
        
        # Fallback: look for names like *_link0
        link0 = next((n for n in all_links if re.search(r'link0$', n, re.IGNORECASE)), None)
        if link0:
            return link0
        
        return 'base_link'

    async def get_action_servers(self) -> List[str]:
        """
        Get available action servers from the appliance.

        Returns:
            List of action server names
        """
        import json
        import time
        import random
        import string

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        loop = asyncio.get_running_loop()
        future = loop.create_future()

        # Generate unique request ID
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        request_id = f'actions_{int(time.time() * 1000)}_{random_suffix}'

        def handle_message(msg):
            try:
                if isinstance(msg, str):
                    data = json.loads(msg)
                elif isinstance(msg, dict):
                    data = msg
                else:
                    return

                if data.get('request_id') != request_id:
                    return

                op = data.get('op', '')

                if op == 'action_servers_data':
                    if data.get('error'):
                        if not future.done():
                            loop.call_soon_threadsafe(
                                future.set_exception,
                                Exception(data['error'])
                            )
                    else:
                        actions = data.get('actions', [])
                        # Extract action names from objects or strings
                        action_names = []
                        for action in actions:
                            if isinstance(action, str):
                                action_names.append(action.split(' ')[0])
                            elif isinstance(action, dict):
                                action_names.append(action.get('name', str(action)))
                        if not future.done():
                            loop.call_soon_threadsafe(future.set_result, action_names)
            except (json.JSONDecodeError, TypeError):
                pass

        # Get the protocol instance
        proto_instance = None
        if hasattr(self._ros, 'factory') and self._ros.factory:
            proto_instance = getattr(self._ros.factory, '_proto', None)

        old_onMessage = None
        custom_ops = {'action_servers_data'}

        if proto_instance and hasattr(proto_instance, 'onMessage'):
            old_onMessage = proto_instance.onMessage

            def patched_onMessage(payload, isBinary):
                if not isBinary:
                    try:
                        msg_str = payload.decode('utf-8') if isinstance(payload, bytes) else payload
                        msg = json.loads(msg_str)
                        op = msg.get('op', '')
                        handle_message(msg_str)
                        if op not in custom_ops and old_onMessage:
                            old_onMessage(payload, isBinary)
                    except json.JSONDecodeError:
                        if old_onMessage:
                            old_onMessage(payload, isBinary)
                else:
                    if old_onMessage:
                        old_onMessage(payload, isBinary)

            proto_instance.onMessage = patched_onMessage

        try:
            request = {
                'op': 'get_action_servers',
                'request_id': request_id
            }
            msg_json = json.dumps(request)
            if proto_instance:
                proto_instance.sendMessage(msg_json.encode('utf-8'))
            else:
                raise ConnectionError("Cannot send message - protocol not connected")

            return await asyncio.wait_for(future, timeout=5.0)

        except asyncio.TimeoutError:
            raise TimeoutError("Timeout waiting for action servers")
        finally:
            if proto_instance and old_onMessage is not None:
                proto_instance.onMessage = old_onMessage

    async def get_current_end_effector_pose(
        self,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get current end effector pose.

        Args:
            options: Optional dict with planningGroup, endEffectorLink, baseFrame

        Returns:
            Dict with position {x, y, z} and orientation {x, y, z, w}
        """
        import json
        import time
        import random
        import string

        if options is None:
            options = {}

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        # Get options or auto-detect planning group, end effector, and base frame
        planning_group = options.get('planningGroup')
        end_effector_link = options.get('endEffectorLink')
        base_frame = options.get('baseFrame')

        # Auto-detect if not provided
        if not planning_group or not end_effector_link or not base_frame:
            try:
                robot_info = await self.detect_robot_info()
                if robot_info:
                    planning_group = planning_group or robot_info.get('planning_group')
                    end_effector_link = end_effector_link or robot_info.get('end_effector_link')
                    base_frame = base_frame or robot_info.get('base_frame')
            except Exception as e:
                print(f'[OLOJoint] Could not auto-detect robot info: {e}')
        
        # Final fallbacks if auto-detection failed
        if not planning_group:
            planning_group = 'manipulator'
        if not end_effector_link:
            end_effector_link = 'tool0'
        if not base_frame:
            base_frame = 'base_link'

        loop = asyncio.get_running_loop()
        future = loop.create_future()

        import time
        import random
        import string
        # Generate unique request ID
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        request_id = f'pose_{int(time.time() * 1000)}_{random_suffix}'

        def handle_message(msg):
            try:
                if isinstance(msg, str):
                    data = json.loads(msg)
                elif isinstance(msg, dict):
                    data = msg
                else:
                    return

                if data.get('request_id') != request_id:
                    return

                op = data.get('op', '')

                if op == 'end_effector_pose_result':
                    if data.get('success'):
                        pose = data.get('pose', {})
                        if not future.done():
                            loop.call_soon_threadsafe(future.set_result, pose)
                    else:
                        error_msg = data.get('error', 'Failed to get end effector pose')
                        if not future.done():
                            loop.call_soon_threadsafe(
                                future.set_exception,
                                Exception(error_msg)
                            )
            except (json.JSONDecodeError, TypeError):
                pass

        # Get the protocol instance
        proto_instance = None
        if hasattr(self._ros, 'factory') and self._ros.factory:
            proto_instance = getattr(self._ros.factory, '_proto', None)

        old_onMessage = None
        custom_ops = {'end_effector_pose_result'}

        if proto_instance and hasattr(proto_instance, 'onMessage'):
            old_onMessage = proto_instance.onMessage

            def patched_onMessage(payload, isBinary):
                if not isBinary:
                    try:
                        msg_str = payload.decode('utf-8') if isinstance(payload, bytes) else payload
                        msg = json.loads(msg_str)
                        op = msg.get('op', '')
                        handle_message(msg_str)
                        if op not in custom_ops and old_onMessage:
                            old_onMessage(payload, isBinary)
                    except json.JSONDecodeError:
                        if old_onMessage:
                            old_onMessage(payload, isBinary)
                else:
                    if old_onMessage:
                        old_onMessage(payload, isBinary)

            proto_instance.onMessage = patched_onMessage

        try:
            request = {
                'op': 'get_end_effector_pose',
                'request_id': request_id,
                'planning_group': planning_group,
                'end_effector_link': end_effector_link,
                'base_frame': base_frame
            }
            msg_json = json.dumps(request)
            if proto_instance:
                proto_instance.sendMessage(msg_json.encode('utf-8'))
            else:
                raise ConnectionError("Cannot send message - protocol not connected")

            return await asyncio.wait_for(future, timeout=5.0)

        except asyncio.TimeoutError:
            raise TimeoutError("Timeout waiting for end effector pose")
        finally:
            if proto_instance and old_onMessage is not None:
                proto_instance.onMessage = old_onMessage

    async def control_gripper(
        self,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Control gripper using MoveIt planning.

        Args:
            options: Gripper control options
                - planningGroup: Planning group name for gripper (required)
                - controllerName: Controller name for gripper (required)
                - position: Target position (0.0 = closed, 1.0 = open)
                - maxEffort: Maximum effort (default: 20.0)
                - timeout: Command timeout in seconds (default: 5)
                - abortSignal: Signal dict with 'aborted' key

        Returns:
            Dict with gripper control result
        """
        import json
        import time
        import random
        import string

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        abort_signal = options.get('abortSignal')

        if abort_signal and abort_signal.get('aborted'):
            raise Exception('Aborted')

        if options.get('position') is None:
            raise ValueError('Position is required (0.0 = closed, 1.0 = open)')

        if not options.get('planningGroup'):
            raise ValueError('Planning group is required for gripper control')

        if not options.get('controllerName'):
            raise ValueError('Controller name is required for gripper control')

        planning_group = options['planningGroup']
        controller_name = options['controllerName']
        position = options['position']
        max_effort = options.get('maxEffort', 20.0)
        timeout = options.get('timeout', 5)

        print(f'[OLOJoint] Controlling gripper to position: {position}')
        print(f'[OLOJoint] Using gripper planning group: {planning_group}')
        print(f'[OLOJoint] Using gripper controller: {controller_name}')

        if abort_signal and abort_signal.get('aborted'):
            raise Exception('Aborted')

        loop = asyncio.get_running_loop()
        future = loop.create_future()

        # Generate unique request ID
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        request_id = f'gripper_{int(time.time() * 1000)}_{random_suffix}'

        def handle_message(msg):
            try:
                if isinstance(msg, str):
                    data = json.loads(msg)
                elif isinstance(msg, dict):
                    data = msg
                else:
                    return

                if data.get('request_id') != request_id:
                    return

                op = data.get('op', '')

                if op == 'joint_control_result':
                    if data.get('success'):
                        print('[OLOJoint] Gripper control successful')
                        result = data.get('result', {'success': True})
                        if not future.done():
                            loop.call_soon_threadsafe(future.set_result, result)
                    else:
                        error_msg = data.get('error', 'Gripper control failed')
                        print(f'[OLOJoint] Gripper control failed: {error_msg}')
                        if not future.done():
                            loop.call_soon_threadsafe(
                                future.set_exception,
                                Exception(error_msg)
                            )
            except (json.JSONDecodeError, TypeError):
                pass

        # Get the protocol instance
        proto_instance = None
        if hasattr(self._ros, 'factory') and self._ros.factory:
            proto_instance = getattr(self._ros.factory, '_proto', None)

        old_onMessage = None
        custom_ops = {'joint_control_result'}

        if proto_instance and hasattr(proto_instance, 'onMessage'):
            old_onMessage = proto_instance.onMessage

            def patched_onMessage(payload, isBinary):
                if not isBinary:
                    try:
                        msg_str = payload.decode('utf-8') if isinstance(payload, bytes) else payload
                        msg = json.loads(msg_str)
                        op = msg.get('op', '')
                        handle_message(msg_str)
                        if op not in custom_ops and old_onMessage:
                            old_onMessage(payload, isBinary)
                    except json.JSONDecodeError:
                        if old_onMessage:
                            old_onMessage(payload, isBinary)
                else:
                    if old_onMessage:
                        old_onMessage(payload, isBinary)

            proto_instance.onMessage = patched_onMessage

        try:
            request = {
                'op': 'execute_joint_control',
                'request_id': request_id,
                'command_type': 'moveit_gripper',
                'controller_name': controller_name,
                'position': position,
                'max_effort': max_effort,
                'timeout': timeout
            }
            msg_json = json.dumps(request)
            if proto_instance:
                proto_instance.sendMessage(msg_json.encode('utf-8'))
                print('[OLOJoint] Sent gripper control request')
            else:
                raise ConnectionError("Cannot send message - protocol not connected")

            result = await asyncio.wait_for(future, timeout=timeout + 2)

            if abort_signal and abort_signal.get('aborted'):
                raise Exception('Aborted')

            print('[OLOJoint] Gripper control completed successfully')
            return result

        except asyncio.TimeoutError:
            raise TimeoutError(f"Gripper control request timed out after {timeout}s")
        finally:
            if proto_instance and old_onMessage is not None:
                proto_instance.onMessage = old_onMessage

    async def open_gripper(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Open gripper (convenience method).

        Args:
            options: Options for gripper control (planningGroup and controllerName required)

        Returns:
            Dict with gripper control result
        """
        return await self.control_gripper({**options, 'position': 1.0})

    async def close_gripper(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Close gripper (convenience method).

        Args:
            options: Options for gripper control (planningGroup and controllerName required)

        Returns:
            Dict with gripper control result
        """
        return await self.control_gripper({**options, 'position': 0.0})

    async def list_moveit_configs(self) -> List[Dict[str, Any]]:
        """
        List available MoveIt configuration packages on the appliance.

        Returns:
            List of config objects with package name and launch file info
        """
        import json
        import time
        import random
        import string

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        loop = asyncio.get_running_loop()
        future = loop.create_future()

        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        request_id = f'moveit_list_{int(time.time() * 1000)}_{random_suffix}'

        def handle_message(msg):
            try:
                if isinstance(msg, str):
                    data = json.loads(msg)
                elif isinstance(msg, dict):
                    data = msg
                else:
                    return

                if data.get('request_id') != request_id:
                    return

                op = data.get('op', '')

                if op == 'moveit_list_configs_result':
                    if data.get('success'):
                        configs = data.get('configs', [])
                        print(f'[OLOJoint] Available MoveIt configs: {configs}')
                        if not future.done():
                            loop.call_soon_threadsafe(future.set_result, configs)
                    else:
                        error_msg = data.get('error', 'Failed to list MoveIt configs')
                        if not future.done():
                            loop.call_soon_threadsafe(
                                future.set_exception,
                                Exception(error_msg)
                            )
            except (json.JSONDecodeError, TypeError):
                pass

        proto_instance = None
        if hasattr(self._ros, 'factory') and self._ros.factory:
            proto_instance = getattr(self._ros.factory, '_proto', None)

        old_onMessage = None
        custom_ops = {'moveit_list_configs_result'}

        if proto_instance and hasattr(proto_instance, 'onMessage'):
            old_onMessage = proto_instance.onMessage

            def patched_onMessage(payload, isBinary):
                if not isBinary:
                    try:
                        msg_str = payload.decode('utf-8') if isinstance(payload, bytes) else payload
                        msg = json.loads(msg_str)
                        op = msg.get('op', '')
                        handle_message(msg_str)
                        if op not in custom_ops and old_onMessage:
                            old_onMessage(payload, isBinary)
                    except json.JSONDecodeError:
                        if old_onMessage:
                            old_onMessage(payload, isBinary)
                else:
                    if old_onMessage:
                        old_onMessage(payload, isBinary)

            proto_instance.onMessage = patched_onMessage

        try:
            request = {
                'op': 'moveit_list_configs',
                'request_id': request_id
            }
            msg_json = json.dumps(request)
            if proto_instance:
                proto_instance.sendMessage(msg_json.encode('utf-8'))
            else:
                raise ConnectionError("Cannot send message - protocol not connected")

            return await asyncio.wait_for(future, timeout=10.0)

        except asyncio.TimeoutError:
            raise TimeoutError("Timeout waiting for MoveIt configs list")
        finally:
            if proto_instance and old_onMessage is not None:
                proto_instance.onMessage = old_onMessage

    async def start_moveit_engine(
        self,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start the MoveIt2 motion planning engine on the appliance.

        Args:
            options: Configuration options
                - configPackage: MoveIt config package name (e.g., 'moveit_resources_panda_moveit_config')
                - moveGroupOnly: If True, only start move_group (robot must already be running)
                - useSimTime: Use simulation time (auto-detected if not specified)
                - robotNamespace: Robot namespace for multi-robot scenarios

        Returns:
            Dict with success status, launchPackage, launchFile, etc.
        """
        import json
        import time
        import random
        import string

        if options is None:
            options = {}

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        loop = asyncio.get_running_loop()
        future = loop.create_future()

        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        request_id = f'moveit_start_{int(time.time() * 1000)}_{random_suffix}'

        def handle_message(msg):
            try:
                if isinstance(msg, str):
                    data = json.loads(msg)
                elif isinstance(msg, dict):
                    data = msg
                else:
                    return

                if data.get('request_id') != request_id:
                    return

                op = data.get('op', '')

                if op == 'moveit_start_result':
                    if data.get('success'):
                        print('[OLOJoint] MoveIt engine started successfully')
                        result = {
                            'success': True,
                            'message': data.get('message'),
                            'launchPackage': data.get('launchPackage'),
                            'launchFile': data.get('launchFile'),
                            'warning': data.get('warning'),
                            'already_running': data.get('already_running', False)
                        }
                        if not future.done():
                            loop.call_soon_threadsafe(future.set_result, result)
                    else:
                        error_msg = data.get('error', 'Failed to start MoveIt engine')
                        print(f'[OLOJoint] Failed to start MoveIt: {error_msg}')
                        if not future.done():
                            loop.call_soon_threadsafe(
                                future.set_exception,
                                Exception(error_msg)
                            )
            except (json.JSONDecodeError, TypeError):
                pass

        proto_instance = None
        if hasattr(self._ros, 'factory') and self._ros.factory:
            proto_instance = getattr(self._ros.factory, '_proto', None)

        old_onMessage = None
        custom_ops = {'moveit_start_result'}

        if proto_instance and hasattr(proto_instance, 'onMessage'):
            old_onMessage = proto_instance.onMessage

            def patched_onMessage(payload, isBinary):
                if not isBinary:
                    try:
                        msg_str = payload.decode('utf-8') if isinstance(payload, bytes) else payload
                        msg = json.loads(msg_str)
                        op = msg.get('op', '')
                        handle_message(msg_str)
                        if op not in custom_ops and old_onMessage:
                            old_onMessage(payload, isBinary)
                    except json.JSONDecodeError:
                        if old_onMessage:
                            old_onMessage(payload, isBinary)
                else:
                    if old_onMessage:
                        old_onMessage(payload, isBinary)

            proto_instance.onMessage = patched_onMessage

        try:
            mode = ' (move_group only)' if options.get('moveGroupOnly') else ''
            config = options.get('configPackage')
            if config:
                print(f'[OLOJoint] Starting MoveIt engine{mode} with config: {config}')
            else:
                print(f'[OLOJoint] Starting MoveIt engine{mode} (auto-detect configuration)')

            request = {
                'op': 'moveit_start',
                'request_id': request_id,
                'configPackage': options.get('configPackage'),
                'moveGroupOnly': options.get('moveGroupOnly', False),
                'robotNamespace': options.get('robotNamespace'),
                'useSimTime': options.get('useSimTime')
            }
            msg_json = json.dumps(request)
            if proto_instance:
                proto_instance.sendMessage(msg_json.encode('utf-8'))
            else:
                raise ConnectionError("Cannot send message - protocol not connected")

            return await asyncio.wait_for(future, timeout=60.0)

        except asyncio.TimeoutError:
            raise TimeoutError("Timeout waiting for MoveIt start response")
        finally:
            if proto_instance and old_onMessage is not None:
                proto_instance.onMessage = old_onMessage

    async def stop_moveit_engine(self) -> Dict[str, Any]:
        """
        Stop the MoveIt2 motion planning engine on the appliance.

        Returns:
            Dict with success status
        """
        import json
        import time
        import random
        import string

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        loop = asyncio.get_running_loop()
        future = loop.create_future()

        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        request_id = f'moveit_stop_{int(time.time() * 1000)}_{random_suffix}'

        def handle_message(msg):
            try:
                if isinstance(msg, str):
                    data = json.loads(msg)
                elif isinstance(msg, dict):
                    data = msg
                else:
                    return

                if data.get('request_id') != request_id:
                    return

                op = data.get('op', '')

                if op == 'moveit_stop_result':
                    if data.get('success'):
                        print('[OLOJoint] MoveIt engine stopped successfully')
                        if not future.done():
                            loop.call_soon_threadsafe(future.set_result, {'success': True})
                    else:
                        error_msg = data.get('error', 'Failed to stop MoveIt engine')
                        print(f'[OLOJoint] Failed to stop MoveIt: {error_msg}')
                        if not future.done():
                            loop.call_soon_threadsafe(
                                future.set_exception,
                                Exception(error_msg)
                            )
            except (json.JSONDecodeError, TypeError):
                pass

        proto_instance = None
        if hasattr(self._ros, 'factory') and self._ros.factory:
            proto_instance = getattr(self._ros.factory, '_proto', None)

        old_onMessage = None
        custom_ops = {'moveit_stop_result'}

        if proto_instance and hasattr(proto_instance, 'onMessage'):
            old_onMessage = proto_instance.onMessage

            def patched_onMessage(payload, isBinary):
                if not isBinary:
                    try:
                        msg_str = payload.decode('utf-8') if isinstance(payload, bytes) else payload
                        msg = json.loads(msg_str)
                        op = msg.get('op', '')
                        handle_message(msg_str)
                        if op not in custom_ops and old_onMessage:
                            old_onMessage(payload, isBinary)
                    except json.JSONDecodeError:
                        if old_onMessage:
                            old_onMessage(payload, isBinary)
                else:
                    if old_onMessage:
                        old_onMessage(payload, isBinary)

            proto_instance.onMessage = patched_onMessage

        try:
            print('[OLOJoint] Stopping MoveIt engine')
            request = {
                'op': 'moveit_stop',
                'request_id': request_id
            }
            msg_json = json.dumps(request)
            if proto_instance:
                proto_instance.sendMessage(msg_json.encode('utf-8'))
            else:
                raise ConnectionError("Cannot send message - protocol not connected")

            return await asyncio.wait_for(future, timeout=10.0)

        except asyncio.TimeoutError:
            raise TimeoutError("Timeout waiting for MoveIt stop response")
        finally:
            if proto_instance and old_onMessage is not None:
                proto_instance.onMessage = old_onMessage

    async def get_moveit_status(self) -> Dict[str, Any]:
        """
        Check the MoveIt engine status on the appliance.

        Returns:
            Dict with is_running, moveit_available, running_components, source
        """
        import json
        import time
        import random
        import string

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        loop = asyncio.get_running_loop()
        future = loop.create_future()

        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        request_id = f'moveit_status_{int(time.time() * 1000)}_{random_suffix}'

        def handle_message(msg):
            try:
                if isinstance(msg, str):
                    data = json.loads(msg)
                elif isinstance(msg, dict):
                    data = msg
                else:
                    return

                if data.get('request_id') != request_id:
                    return

                op = data.get('op', '')

                if op == 'moveit_status_response':
                    print(f'[OLOJoint] MoveIt status: {data}')
                    result = {
                        'is_running': data.get('is_running', False),
                        'moveit_available': data.get('moveit_available', False),
                        'running_components': data.get('running_components', []),
                        'source': data.get('source')
                    }
                    if not future.done():
                        loop.call_soon_threadsafe(future.set_result, result)
            except (json.JSONDecodeError, TypeError):
                pass

        proto_instance = None
        if hasattr(self._ros, 'factory') and self._ros.factory:
            proto_instance = getattr(self._ros.factory, '_proto', None)

        old_onMessage = None
        custom_ops = {'moveit_status_response'}

        if proto_instance and hasattr(proto_instance, 'onMessage'):
            old_onMessage = proto_instance.onMessage

            def patched_onMessage(payload, isBinary):
                if not isBinary:
                    try:
                        msg_str = payload.decode('utf-8') if isinstance(payload, bytes) else payload
                        msg = json.loads(msg_str)
                        op = msg.get('op', '')
                        handle_message(msg_str)
                        if op not in custom_ops and old_onMessage:
                            old_onMessage(payload, isBinary)
                    except json.JSONDecodeError:
                        if old_onMessage:
                            old_onMessage(payload, isBinary)
                else:
                    if old_onMessage:
                        old_onMessage(payload, isBinary)

            proto_instance.onMessage = patched_onMessage

        try:
            request = {
                'op': 'moveit_status_check',
                'request_id': request_id
            }
            msg_json = json.dumps(request)
            if proto_instance:
                proto_instance.sendMessage(msg_json.encode('utf-8'))
            else:
                raise ConnectionError("Cannot send message - protocol not connected")

            return await asyncio.wait_for(future, timeout=5.0)

        except asyncio.TimeoutError:
            raise TimeoutError("Timeout waiting for MoveIt status response")
        finally:
            if proto_instance and old_onMessage is not None:
                proto_instance.onMessage = old_onMessage

    def cleanup(self):
        """Clean up joint control resources"""
        self._cached_joint_states = None
        self._joint_state_subscription = None

