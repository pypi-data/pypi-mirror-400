"""
OLO Core API - Core ROS functionality
"""

import asyncio
from typing import List, Dict, Any, Optional, Callable


class OLOCore:
    """
    Core API for ROS operations
    Mirrors the JavaScript oloClient.core API
    
    Provides methods for:
    - Topic listing, subscribing, and publishing
    - Service calls
    - Robot velocity control (cmd_vel)
    - Timed movement with abort support
    """

    def __init__(self, ros_client):
        """
        Initialize OLO Core

        Args:
            ros_client: roslibpy.Ros instance
        """
        self._ros = ros_client
        self._subscriptions = {}
        self._publishers = {}
        self._topics_cache = []
        self._active_velocity_holds = {}  # topic -> { task, stop_event }
        self._script_result = None  # For returning values from executeScript
        self._verbose_logging = False

    def set_verbose_logging(self, enabled: bool) -> None:
        """
        Enable or disable verbose logging for core operations.
        
        Args:
            enabled: Whether to enable verbose logging
        """
        self._verbose_logging = enabled
    
    def set_script_result(self, value):
        """
        Set a result value that will be returned to the calling script via execute_script().
        Call this in a spawned script to return data to the parent script.
        
        Args:
            value: Any JSON-serializable value to return
        """
        self._script_result = value
        print("[OLOClient] Script result set")
    
    def get_script_result(self):
        """
        Get the script result (used internally by executor).
        
        Returns:
            The script result value
        """
        return self._script_result

    async def list_topics(self, refresh: bool = False) -> List[Dict[str, Any]]:
        """
        List all available ROS topics

        Args:
            refresh: Force refresh from server (currently ignored, always fetches fresh)

        Returns:
            List of topic dictionaries with keys: name, type, throttling
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        # Use asyncio to wrap the callback-based API
        loop = asyncio.get_event_loop()
        future = loop.create_future()

        def callback(topics_dict):
            try:
                topics = []
                topic_names = topics_dict.get('topics', [])
                topic_types = topics_dict.get('types', [])
                throttling = topics_dict.get('throttling', [])

                for i, name in enumerate(topic_names):
                    topic_info = {
                        'name': name,
                        'type': topic_types[i] if i < len(topic_types) else 'unknown',
                        'throttling': throttling[i] if i < len(throttling) else None
                    }
                    topics.append(topic_info)

                if not future.done():
                    loop.call_soon_threadsafe(future.set_result, topics)
            except Exception as e:
                if not future.done():
                    loop.call_soon_threadsafe(future.set_exception, e)

        # Get topics using roslibpy
        self._ros.get_topics(callback)

        # Wait for result with timeout
        try:
            result = await asyncio.wait_for(future, timeout=10.0)
            self._topics_cache = result
            return result
        except asyncio.TimeoutError:
            raise TimeoutError("Timeout waiting for topic list")

    async def subscribe(
        self,
        topic_name: str,
        callback: Callable[[Dict], None],
        message_type: Optional[str] = None,
        throttle_rate: Optional[int] = None,
        queue_length: Optional[int] = None
    ) -> str:
        """
        Subscribe to a ROS topic

        Args:
            topic_name: Name of the topic to subscribe to
            callback: Function to call when messages are received
            message_type: Message type (auto-detected if not provided)
            throttle_rate: Throttle rate in ms
            queue_length: Queue length for buffering

        Returns:
            Subscription ID (topic name)
        """
        import roslibpy

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        # Auto-detect message type if not provided
        if not message_type:
            # Fetch topics if cache is empty
            if not self._topics_cache:
                try:
                    await self.list_topics(refresh=True)
                except Exception:
                    pass
            
            # Find topic info
            topic_info = next(
                (t for t in self._topics_cache if t.get('name') == topic_name),
                None
            )
            if topic_info:
                message_type = topic_info.get('type', '')
            
            if not message_type:
                raise ValueError(
                    f"Topic '{topic_name}' not found or message type unknown. "
                    f"Available topics: {[t.get('name') for t in self._topics_cache[:5]]}..."
                )

        # Unsubscribe if already subscribed to this topic
        if topic_name in self._subscriptions:
            await self.unsubscribe(topic_name)

        # Build topic kwargs - only include throttle_rate/queue_length if they're set
        # rosbridge rejects None values for these fields
        topic_kwargs = {}
        if throttle_rate is not None:
            topic_kwargs['throttle_rate'] = throttle_rate
        if queue_length is not None:
            topic_kwargs['queue_length'] = queue_length

        # Create topic
        topic = roslibpy.Topic(
            self._ros,
            topic_name,
            message_type,
            **topic_kwargs
        )

        # Wrap callback to catch errors from user code
        def wrapped_callback(message):
            try:
                callback(message)
            except Exception as e:
                import sys
                print(f"[OLOClient] Error in subscription callback for {topic_name}: {e}", 
                      file=sys.stderr, flush=True)

        # Subscribe with wrapped callback
        topic.subscribe(wrapped_callback)

        # Store subscription
        self._subscriptions[topic_name] = topic

        return topic_name

    def _unsubscribe_sync(self, topic_name: str) -> bool:
        """
        Internal sync unsubscribe - used by cleanup and other sync contexts.

        Args:
            topic_name: Name of the topic to unsubscribe from

        Returns:
            True if unsubscribed, False if not subscribed
        """
        topic = self._subscriptions.get(topic_name)
        if topic:
            topic.unsubscribe()
            del self._subscriptions[topic_name]
            return True
        return False

    async def unsubscribe(self, topic_name: str) -> bool:
        """
        Unsubscribe from a topic.
        
        This is an async method for consistency with the rest of the API,
        allowing it to be used with 'await'.

        Args:
            topic_name: Name of the topic to unsubscribe from

        Returns:
            True if unsubscribed, False if not subscribed
        """
        return self._unsubscribe_sync(topic_name)

    async def publish(
        self,
        topic_name: str,
        message: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Publish a message to a topic

        Args:
            topic_name: Name of the topic
            message: Message data as dictionary
            options: Optional dict with:
                - messageType: ROS message type (auto-detected if not provided)
        """
        import roslibpy

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        if options is None:
            options = {}

        message_type = options.get('messageType')

        # Get or create publisher (cached for reuse)
        publisher = self._publishers.get(topic_name)
        
        if not publisher:
            # Auto-detect message type if not provided
            if not message_type:
                # Fetch topics if cache is empty
                if not self._topics_cache:
                    await self.list_topics(refresh=True)

                topic_info = next(
                    (t for t in self._topics_cache if t.get('name') == topic_name),
                    None
                )
                if topic_info:
                    message_type = topic_info.get('type')

                if not message_type:
                    raise ValueError(
                        f"Topic '{topic_name}' not found or message type unknown. "
                        f"Please specify messageType in options."
                    )

            publisher = roslibpy.Topic(
                self._ros,
                topic_name,
                message_type
            )
            self._publishers[topic_name] = publisher
            
            # Wait briefly for subscribers to discover the new publisher
            await asyncio.sleep(0.1)

        publisher.publish(roslibpy.Message(message))

    async def call_service(
        self,
        service_name: str,
        service_type: str,
        request: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call a ROS service

        Args:
            service_name: Name of the service
            service_type: Service type
            request: Service request data

        Returns:
            Service response as dictionary
        """
        import roslibpy

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        loop = asyncio.get_event_loop()
        future = loop.create_future()

        service = roslibpy.Service(
            self._ros,
            service_name,
            service_type
        )

        def callback(result):
            if not future.done():
                loop.call_soon_threadsafe(future.set_result, result)

        def error_callback(error):
            if not future.done():
                loop.call_soon_threadsafe(
                    future.set_exception,
                    Exception(f"Service call failed: {error}")
                )

        service_request = roslibpy.ServiceRequest(request or {})
        service.call(service_request, callback, error_callback)

        try:
            return await asyncio.wait_for(future, timeout=30.0)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Timeout calling service {service_name}")

    def get_connection_status(self) -> bool:
        """
        Get ROS connection status

        Returns:
            True if connected
        """
        return self._ros.is_connected

    async def list_nodes(self) -> List[str]:
        """
        List all ROS nodes

        Returns:
            List of node names
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        loop = asyncio.get_event_loop()
        future = loop.create_future()

        def callback(result):
            try:
                # roslibpy returns ServiceResponse (a UserDict subclass) with {"nodes": [...]}
                # Use 'in' operator and indexing which work with both dict and UserDict
                nodes = []
                if isinstance(result, list):
                    nodes = result
                elif hasattr(result, '__getitem__') and 'nodes' in result:
                    nodes = result['nodes']
                
                if not future.done():
                    loop.call_soon_threadsafe(future.set_result, nodes)
            except Exception as e:
                if not future.done():
                    loop.call_soon_threadsafe(future.set_exception, e)

        def errback(error):
            if not future.done():
                loop.call_soon_threadsafe(
                    future.set_exception,
                    Exception(f"Failed to get nodes: {error}")
                )

        self._ros.get_nodes(callback=callback, errback=errback)

        try:
            return await asyncio.wait_for(future, timeout=10.0)
        except asyncio.TimeoutError:
            raise TimeoutError("Timeout waiting for node list")

    async def list_services(self) -> List[str]:
        """
        List all available ROS services

        Returns:
            List of service names
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        loop = asyncio.get_event_loop()
        future = loop.create_future()

        def callback(result):
            try:
                # roslibpy returns ServiceResponse (a UserDict subclass) with {"services": [...]}
                services = []
                if isinstance(result, list):
                    services = result
                elif hasattr(result, '__getitem__') and 'services' in result:
                    services = result['services']
                
                if not future.done():
                    loop.call_soon_threadsafe(future.set_result, services)
            except Exception as e:
                if not future.done():
                    loop.call_soon_threadsafe(future.set_exception, e)

        def errback(error):
            if not future.done():
                loop.call_soon_threadsafe(
                    future.set_exception,
                    Exception(f"Failed to get services: {error}")
                )

        self._ros.get_services(callback=callback, errback=errback)

        try:
            return await asyncio.wait_for(future, timeout=10.0)
        except asyncio.TimeoutError:
            raise TimeoutError("Timeout waiting for service list")

    async def list_node_parameters(
        self,
        node_name: str,
        options: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        List parameter names for a specific ROS 2 node

        Args:
            node_name: Node name, e.g. '/robot_state_publisher'
            options: Optional dict with:
                - depth: Recursion depth (0 = all, default)
                - prefixes: List of parameter prefixes to filter

        Returns:
            List of parameter names for the node
        """
        import roslibpy

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        if not node_name or not isinstance(node_name, str):
            raise ValueError("node_name is required")

        if options is None:
            options = {}

        depth = options.get('depth', 0)
        if isinstance(depth, (int, float)) and depth >= 0:
            depth = int(depth)
        else:
            depth = 0

        prefixes = options.get('prefixes', [])
        if not isinstance(prefixes, list):
            prefixes = []

        loop = asyncio.get_event_loop()
        future = loop.create_future()

        service = roslibpy.Service(
            self._ros,
            f'{node_name}/list_parameters',
            'rcl_interfaces/srv/ListParameters'
        )

        def callback(result):
            try:
                # ROS 2 ListParametersResponse has 'names' field
                names = []
                if hasattr(result, '__getitem__'):
                    if 'names' in result:
                        names = result['names']
                    elif 'result' in result and hasattr(result['result'], '__getitem__'):
                        names = result['result'].get('names', [])
                elif isinstance(result, list):
                    names = result
                
                if not future.done():
                    loop.call_soon_threadsafe(future.set_result, names)
            except Exception as e:
                if not future.done():
                    loop.call_soon_threadsafe(future.set_exception, e)

        def errback(error):
            if not future.done():
                error_msg = str(error) if error else 'Service call failed'
                loop.call_soon_threadsafe(
                    future.set_exception,
                    Exception(error_msg)
                )

        request = roslibpy.ServiceRequest({'prefixes': prefixes, 'depth': depth})
        service.call(request, callback, errback)

        try:
            return await asyncio.wait_for(future, timeout=10.0)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Timeout listing parameters for {node_name}")

    async def get_node_parameter(self, node_name: str, param_name: str) -> Any:
        """
        Get parameter value from a specific ROS 2 node

        Args:
            node_name: Node name (e.g., '/robot_state_publisher')
            param_name: Parameter name (e.g., 'robot_description')

        Returns:
            Parameter value (type depends on parameter)
        """
        import roslibpy

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        loop = asyncio.get_event_loop()
        future = loop.create_future()

        service = roslibpy.Service(
            self._ros,
            f'{node_name}/get_parameters',
            'rcl_interfaces/srv/GetParameters'
        )

        def callback(result):
            try:
                values = None
                if hasattr(result, '__getitem__') and 'values' in result:
                    values = result['values']
                
                if values and len(values) > 0:
                    param_value = values[0]
                    # Extract value based on ROS 2 parameter type
                    param_type = param_value.get('type', 0) if hasattr(param_value, 'get') else 0
                    
                    if param_type == 1:  # PARAMETER_BOOL
                        value = param_value.get('bool_value')
                    elif param_type == 2:  # PARAMETER_INTEGER
                        value = param_value.get('integer_value')
                    elif param_type == 3:  # PARAMETER_DOUBLE
                        value = param_value.get('double_value')
                    elif param_type == 4:  # PARAMETER_STRING
                        value = param_value.get('string_value')
                    elif param_type == 5:  # PARAMETER_BYTE_ARRAY
                        value = param_value.get('byte_array_value')
                    elif param_type == 6:  # PARAMETER_BOOL_ARRAY
                        value = param_value.get('bool_array_value')
                    elif param_type == 7:  # PARAMETER_INTEGER_ARRAY
                        value = param_value.get('integer_array_value')
                    elif param_type == 8:  # PARAMETER_DOUBLE_ARRAY
                        value = param_value.get('double_array_value')
                    elif param_type == 9:  # PARAMETER_STRING_ARRAY
                        value = param_value.get('string_array_value')
                    else:
                        value = None  # PARAMETER_NOT_SET or unknown
                    
                    if not future.done():
                        loop.call_soon_threadsafe(future.set_result, value)
                else:
                    if not future.done():
                        loop.call_soon_threadsafe(future.set_result, None)
            except Exception as e:
                if not future.done():
                    loop.call_soon_threadsafe(future.set_exception, e)

        def errback(error):
            if not future.done():
                error_msg = str(error) if error else 'Service call failed'
                loop.call_soon_threadsafe(
                    future.set_exception,
                    Exception(error_msg)
                )

        request = roslibpy.ServiceRequest({'names': [param_name]})
        service.call(request, callback, errback)

        try:
            return await asyncio.wait_for(future, timeout=10.0)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Timeout getting parameter {param_name} from {node_name}")

    async def get_parameter(self, param_name: str) -> Any:
        """
        Get ROS 2 parameter value with automatic discovery

        Args:
            param_name: Parameter name or full path
                - Simple name: 'robot_description' (searches across all nodes)
                - Full path: '/robot_state_publisher/robot_description' (direct node access)

        Returns:
            Parameter value
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        # If param_name contains a node path, extract node and parameter
        if param_name.startswith('/') and '/' in param_name[1:]:
            parts = param_name.split('/')
            if len(parts) >= 3:
                node_name = '/' + parts[1]
                parameter_name = '/'.join(parts[2:])
                return await self.get_node_parameter(node_name, parameter_name)

        # For simple parameter names, search across all nodes
        if not param_name.startswith('/') or '/' not in param_name[1:]:
            nodes = await self.list_nodes()
            for node in nodes:
                try:
                    node_params = await self.list_node_parameters(node, {'depth': 0})
                    if param_name in node_params:
                        return await self.get_node_parameter(node, param_name)
                except Exception:
                    # Skip nodes that don't support parameter listing
                    continue
            
            raise Exception(f"Parameter '{param_name}' not found in any accessible node")

        raise Exception(
            f"Invalid parameter name format: '{param_name}'. "
            "Use either a simple name (e.g., 'robot_description') or "
            "full path (e.g., '/robot_state_publisher/robot_description')"
        )

    async def set_node_parameter(self, node_name: str, param_name: str, value: Any) -> Dict:
        """
        Set parameter value on a specific ROS 2 node

        Args:
            node_name: Node name (e.g., '/robot_state_publisher')
            param_name: Parameter name
            value: Parameter value (bool, int, float, str, or arrays)

        Returns:
            Set parameter result
        """
        import roslibpy

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        loop = asyncio.get_event_loop()
        future = loop.create_future()

        service = roslibpy.Service(
            self._ros,
            f'{node_name}/set_parameters',
            'rcl_interfaces/srv/SetParameters'
        )

        # Create parameter value based on type
        param_value = {'type': 0}  # PARAMETER_NOT_SET by default
        
        if isinstance(value, bool):
            param_value = {'type': 1, 'bool_value': value}
        elif isinstance(value, int):
            param_value = {'type': 2, 'integer_value': value}
        elif isinstance(value, float):
            param_value = {'type': 3, 'double_value': value}
        elif isinstance(value, str):
            param_value = {'type': 4, 'string_value': value}
        elif isinstance(value, (list, tuple)) and len(value) > 0:
            if isinstance(value[0], bool):
                param_value = {'type': 6, 'bool_array_value': list(value)}
            elif isinstance(value[0], int):
                param_value = {'type': 7, 'integer_array_value': list(value)}
            elif isinstance(value[0], float):
                param_value = {'type': 8, 'double_array_value': list(value)}
            elif isinstance(value[0], str):
                param_value = {'type': 9, 'string_array_value': list(value)}

        def callback(result):
            if not future.done():
                loop.call_soon_threadsafe(future.set_result, dict(result) if hasattr(result, 'keys') else result)

        def errback(error):
            if not future.done():
                error_msg = str(error) if error else 'Service call failed'
                loop.call_soon_threadsafe(
                    future.set_exception,
                    Exception(error_msg)
                )

        request = roslibpy.ServiceRequest({
            'parameters': [{
                'name': param_name,
                'value': param_value
            }]
        })
        service.call(request, callback, errback)

        try:
            return await asyncio.wait_for(future, timeout=10.0)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Timeout setting parameter {param_name} on {node_name}")

    async def set_parameter(self, param_path: str, value: Any) -> Dict:
        """
        Set ROS 2 parameter value using full node path

        Args:
            param_path: Full parameter path (e.g., '/robot_state_publisher/my_param')
            value: Parameter value

        Returns:
            Set parameter result
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        # Parse the full parameter path
        if not param_path.startswith('/') or '/' not in param_path[1:]:
            raise ValueError(
                f"Parameter path must be in format '/node_name/parameter_name', got: '{param_path}'"
            )

        parts = param_path.split('/')
        if len(parts) < 3:
            raise ValueError(
                f"Invalid parameter path format: '{param_path}'. Expected '/node_name/parameter_name'"
            )

        node_name = '/' + parts[1]
        parameter_name = '/'.join(parts[2:])

        return await self.set_node_parameter(node_name, parameter_name, value)

    # =========================================================================
    # Robot Control Methods
    # =========================================================================

    async def resolve_cmd_vel_topic(self, preferred_topic: Optional[str] = None) -> str:
        """
        Resolve cmd_vel topic, optionally from a preferred topic name

        Args:
            preferred_topic: Optional preferred topic name to use

        Returns:
            Resolved cmd_vel topic name
        """
        if preferred_topic:
            return preferred_topic

        if not self._ros.is_connected:
            return '/cmd_vel'

        # Try to get topics if not cached
        if not self._topics_cache:
            try:
                self._topics_cache = await self.list_topics(refresh=True)
            except Exception:
                pass

        # Find a topic ending with /cmd_vel
        for topic in self._topics_cache:
            if topic.get('name', '').endswith('/cmd_vel'):
                return topic['name']

        return '/cmd_vel'

    async def send_velocity(
        self,
        topic_name: str = '/cmd_vel',
        velocity: Optional[Dict[str, float]] = None
    ) -> None:
        """
        Send velocity command to robot

        Args:
            topic_name: cmd_vel topic name (default: '/cmd_vel')
            velocity: Velocity dict with 'linear' and 'angular' keys (m/s, rad/s)
        """
        if velocity is None:
            velocity = {}

        message = {
            'linear': {
                'x': velocity.get('linear', 0),
                'y': 0,
                'z': 0
            },
            'angular': {
                'x': 0,
                'y': 0,
                'z': velocity.get('angular', 0)
            }
        }

        await self.publish(topic_name, message, {'messageType': 'geometry_msgs/Twist'})

    async def stop_robot(self, topic_name: Optional[str] = None) -> None:
        """
        Stop robot movement

        Args:
            topic_name: cmd_vel topic name (default: auto-resolved)
        """
        resolved_topic = await self.resolve_cmd_vel_topic(topic_name)
        
        # Cancel any active velocity hold for this topic
        await self._cancel_velocity_hold(resolved_topic)
        
        # Send zero velocity (only if connected)
        if self._ros.is_connected:
            await self.send_velocity(resolved_topic, {'linear': 0, 'angular': 0})

    async def start_velocity_hold(
        self,
        velocity: Dict[str, float],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start continuously publishing velocity at a fixed rate until cancelled.

        Args:
            velocity: Dict with 'linear' and 'angular' velocities
            options: Options dict with:
                - topicName: Optional topic name (defaults to resolved cmd_vel)
                - rateHz: Publish rate (default 10Hz)
                - abortSignal: Optional abort signal dict with 'aborted' key
                - stopOnCancel: Whether to publish zero twist when cancelled (default True)

        Returns:
            Dict with 'topicName' and 'stop' function
        """
        if options is None:
            options = {}

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to robot")

        topic_name = await self.resolve_cmd_vel_topic(options.get('topicName'))
        rate_hz = max(1, options.get('rateHz', 10))
        interval_s = max(0.05, 1.0 / rate_hz)
        stop_on_cancel = options.get('stopOnCancel', True)
        abort_signal = options.get('abortSignal')

        # Cancel any existing hold for this topic
        await self._cancel_velocity_hold(topic_name)

        # Create stop event
        stop_event = asyncio.Event()
        stopped = False

        async def publish_loop():
            nonlocal stopped
            try:
                while not stop_event.is_set() and self._ros.is_connected:
                    if abort_signal and abort_signal.get('aborted'):
                        break
                    try:
                        await self.send_velocity(topic_name, velocity)
                    except Exception:
                        pass
                    await asyncio.sleep(interval_s)
            finally:
                stopped = True
                # Clean up from tracking dict
                if topic_name in self._active_velocity_holds:
                    del self._active_velocity_holds[topic_name]

        def stop():
            """Synchronously signal the publish loop to stop"""
            nonlocal stopped
            if stopped:
                return
            stop_event.set()
            # Don't use create_task here - let the caller handle cleanup
            # The publish_loop's finally block will handle removal from tracking dict

        # Start the publish loop
        task = asyncio.create_task(publish_loop())
        self._active_velocity_holds[topic_name] = {
            'task': task,
            'stop_event': stop_event,
            'stop': stop
        }

        # Wire abort signal
        if abort_signal and abort_signal.get('aborted'):
            stop()

        return {'topicName': topic_name, 'stop': stop}

    async def _cancel_velocity_hold(self, topic_name: str) -> None:
        """Cancel active velocity hold for a topic without publishing"""
        hold = self._active_velocity_holds.get(topic_name)
        if hold:
            hold['stop_event'].set()
            try:
                hold['task'].cancel()
                await asyncio.sleep(0)  # Allow task to cancel
            except Exception:
                pass
            if topic_name in self._active_velocity_holds:
                del self._active_velocity_holds[topic_name]

    async def move_for(
        self,
        velocity: Dict[str, float],
        duration_ms: int,
        options: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Move with the given velocity for a duration, cancellable via abort signal.

        Args:
            velocity: Dict with 'linear' and 'angular' velocities
            duration_ms: Duration in milliseconds
            options: Options dict with:
                - topicName: Optional topic name
                - rateHz: Publish rate (default 10Hz)
                - abortSignal: Optional abort signal dict with 'aborted' key
                - throwOnAbort: Whether to throw on abort (default True if abortSignal provided)
        """
        if options is None:
            options = {}

        abort_signal = options.get('abortSignal')
        throw_on_abort = options.get('throwOnAbort')
        if throw_on_abort is None:
            throw_on_abort = abort_signal is not None

        handle = await self.start_velocity_hold(velocity, {
            'topicName': options.get('topicName'),
            'rateHz': options.get('rateHz'),
            'abortSignal': abort_signal,
            'stopOnCancel': True
        })

        topic_name = handle['topicName']
        abort_error = None
        try:
            await self.abortable_delay(duration_ms / 1000.0, abort_signal)
        except Exception as e:
            if 'aborted' in str(e).lower():
                abort_error = e
            else:
                raise
        finally:
            # Stop the velocity hold
            handle['stop']()
            # Send zero velocity directly (not fire-and-forget)
            try:
                if self._ros.is_connected:
                    await self.send_velocity(topic_name, {'linear': 0, 'angular': 0})
            except Exception:
                pass  # Ignore errors during cleanup

        if abort_error and throw_on_abort:
            raise abort_error

    async def abortable_delay(
        self,
        seconds: float,
        abort_signal: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Create an abortable delay that can be cancelled.

        Args:
            seconds: Delay time in seconds
            abort_signal: Optional abort signal dict with 'aborted' key

        Raises:
            Exception: If aborted
        """
        if abort_signal and abort_signal.get('aborted'):
            raise Exception('Aborted')

        # Check abort signal periodically during delay
        check_interval = 0.1  # Check every 100ms
        elapsed = 0.0

        while elapsed < seconds:
            if abort_signal and abort_signal.get('aborted'):
                raise Exception('Aborted')
            
            sleep_time = min(check_interval, seconds - elapsed)
            await asyncio.sleep(sleep_time)
            elapsed += sleep_time

    async def stop_all_velocity_holds(self) -> None:
        """Stop all active velocity holds"""
        topics = list(self._active_velocity_holds.keys())
        for topic in topics:
            try:
                await self._cancel_velocity_hold(topic)
                if self._ros.is_connected:
                    await self.send_velocity(topic, {'linear': 0, 'angular': 0})
            except Exception:
                pass

    async def execute_script(self, script_name: str) -> dict:
        """
        Execute a saved script by name and wait for it to complete.

        Args:
            script_name: Name of the saved script to execute

        Returns:
            Dict with 'executionId' and 'duration' of the completed script

        Raises:
            ConnectionError: If not connected
            ValueError: If script_name is not provided
            Exception: If script execution fails or is stopped
            TimeoutError: If script doesn't start within 15 seconds
        """
        import uuid
        import json

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        if not script_name or not isinstance(script_name, str):
            raise ValueError("Script name is required")

        # Generate unique execution ID
        execution_id = str(uuid.uuid4())

        loop = asyncio.get_event_loop()
        started_future = loop.create_future()
        complete_future = loop.create_future()

        def handle_message(message):
            """Handle incoming messages looking for script execution response"""
            try:
                if isinstance(message, str):
                    msg = json.loads(message)
                elif isinstance(message, dict):
                    msg = message
                else:
                    return

                # Check for script execution started confirmation
                if msg.get('op') == 'script_execution_started' and msg.get('executionId') == execution_id:
                    if not started_future.done():
                        loop.call_soon_threadsafe(started_future.set_result, True)

                # Check for execution complete - this is when we're done
                if msg.get('op') == 'execution_complete' and msg.get('executionId') == execution_id:
                    if not complete_future.done():
                        result = {
                            'executionId': execution_id,
                            'duration': msg.get('duration')
                        }
                        # Include script result if provided
                        if 'result' in msg:
                            result['result'] = msg.get('result')
                        loop.call_soon_threadsafe(complete_future.set_result, result)

                # Check for execution error
                if msg.get('op') == 'execution_error' and msg.get('executionId') == execution_id:
                    error_msg = msg.get('error', 'Script execution failed')
                    if not started_future.done():
                        loop.call_soon_threadsafe(started_future.set_exception, Exception(error_msg))
                    if not complete_future.done():
                        loop.call_soon_threadsafe(complete_future.set_exception, Exception(error_msg))

                # Check for execution stopped
                if msg.get('op') == 'execution_stopped' and msg.get('executionId') == execution_id:
                    if not complete_future.done():
                        loop.call_soon_threadsafe(
                            complete_future.set_exception,
                            Exception('Script execution was stopped')
                        )
            except (json.JSONDecodeError, TypeError):
                pass

        # Get the protocol instance for sending messages
        proto_instance = None
        if hasattr(self._ros, 'factory') and self._ros.factory:
            proto_instance = getattr(self._ros.factory, '_proto', None)
        
        # Hook into roslibpy's message handling by patching the protocol's onMessage
        old_onMessage = None
        custom_ops = {'script_execution_started', 'execution_complete', 'execution_error', 'execution_stopped'}
        
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
                        # Not JSON, pass to original handler
                        if old_onMessage:
                            old_onMessage(payload, isBinary)
                else:
                    # Binary message, pass to original handler
                    if old_onMessage:
                        old_onMessage(payload, isBinary)
            proto_instance.onMessage = patched_onMessage

        try:
            # Send execute_script message
            message = json.dumps({
                'op': 'execute_script',
                'scriptName': script_name,
                'executionId': execution_id
            })

            # Use roslibpy's protocol instance to send the message
            # _proto is the actual protocol instance after connection
            if proto_instance:
                proto_instance.sendMessage(message.encode('utf-8'))
            else:
                raise ConnectionError("Cannot send message - protocol not connected")

            print(f"[OLOClient] Spawning script: '{script_name}'")

            # Wait for script to start (with timeout)
            await asyncio.wait_for(started_future, timeout=15.0)
            print(f"[OLOClient] Script '{script_name}' started (ID: {execution_id})")

            # Wait for script to complete (no timeout - scripts can run indefinitely)
            result = await complete_future
            print(f"[OLOClient] Script '{script_name}' completed (ID: {execution_id})")
            return result

        except asyncio.TimeoutError:
            raise TimeoutError("Script execution request timed out")
        finally:
            # Restore original handler
            if proto_instance and old_onMessage is not None:
                proto_instance.onMessage = old_onMessage

    # =========================================================================
    # Robot Discovery Methods
    # =========================================================================

    async def discover_robots(self, options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Discover robot instances in the ROS environment.
        Analyzes TF frames, topics, and services to identify distinct robot instances.

        Args:
            options: Optional discovery options:
                - filterFn: Optional filter function to apply to discovered robots
                - windowMs: Time window to collect TF data (default: 800ms)
                - maxCacheMs: Cache validity duration (default: 8000ms)

        Returns:
            List of discovered robot instances with:
                - id: Unique identifier
                - namespace: ROS namespace
                - name: Friendly name
                - baseFrame: Base TF frame
                - frameCount: Number of TF frames
                - signals: Dict of capability flags (hasCmdVel, hasJointStates, etc.)
                - confidence: Confidence score (0-5)
                - topics: List of relevant topics with types
        """
        import roslibpy
        import re
        import time

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        if options is None:
            options = {}

        filter_fn = options.get('filterFn')
        window_ms = options.get('windowMs', 800)
        max_cache_ms = options.get('maxCacheMs', 8000)

        # Initialize cache if needed
        if not hasattr(self, '_discovery_cache'):
            self._discovery_cache = {}

        # Build cache key
        cache_key = 'discovery'
        now = time.time() * 1000

        # Check cache
        if cache_key in self._discovery_cache:
            cached = self._discovery_cache[cache_key]
            if (now - cached['timestamp']) < max_cache_ms:
                results = cached['instances']
                if filter_fn:
                    results = [r for r in results if filter_fn(r)]
                return results

        # 1) Collect TF edges for a short window
        edges = {}  # child -> parent

        def add_edges(msg):
            transforms = msg.get('transforms', [])
            for t in transforms:
                child = t.get('child_frame_id')
                header = t.get('header', {})
                parent = header.get('frame_id')
                if child and parent:
                    edges[child] = parent

        # Subscribe to TF topics
        tf_topic = roslibpy.Topic(
            self._ros, '/tf', 'tf2_msgs/TFMessage'
        )
        tf_static_topic = roslibpy.Topic(
            self._ros, '/tf_static', 'tf2_msgs/TFMessage'
        )

        try:
            tf_topic.subscribe(add_edges)
            tf_static_topic.subscribe(add_edges)
        except Exception:
            pass  # Continue with topics-only discovery

        # Wait for TF data collection
        await asyncio.sleep(window_ms / 1000.0)

        try:
            tf_topic.unsubscribe()
        except Exception:
            pass
        try:
            tf_static_topic.unsubscribe()
        except Exception:
            pass

        # 2) Build connected components from TF edges
        components = self._build_connected_components(edges)

        # 3) Get topics and types
        topics = await self.list_topics(refresh=True)
        topic_names = [t['name'] for t in topics]
        type_by_topic = {t['name']: t['type'] for t in topics}

        topics_by_ns = {}
        for t in topic_names:
            ns = self._namespace_of(t)
            if ns not in topics_by_ns:
                topics_by_ns[ns] = []
            topics_by_ns[ns].append(t)

        # 4) Map each TF component to a namespace
        guessed = []
        for idx, frames in enumerate(components):
            # Base frame heuristic
            base_candidates = []
            for f in frames:
                if re.search(r'(base_link|base_footprint|base|body)', f, re.I):
                    base_candidates.append(f)
            base_frame = base_candidates[0] if base_candidates else None

            # Namespace via TF frame prefixes
            excluded = {'map', 'world', 'odom'}
            sensor_frame_pattern = re.compile(r'^(camera|imu|lidar|laser|scan|sensor|gps|rgbd|realsense|zed|oak|kinect)_', re.I)
            ns_counts = {}

            for f in frames:
                if not isinstance(f, str):
                    continue
                if not f.startswith('/'):
                    continue
                parts = [p for p in f.split('/') if p]
                if len(parts) > 1:
                    c = parts[0]
                    if c not in excluded and not sensor_frame_pattern.match(c):
                        ns_counts[c] = ns_counts.get(c, 0) + 1

            best_ns = ''
            best_ns_count = -1
            for ns, count in ns_counts.items():
                if count > best_ns_count:
                    best_ns_count = count
                    best_ns = ns

            # Topic scoring fallback if TF prefixes inconclusive
            if best_ns == '':
                best_score = -1
                sensor_ns_pattern = re.compile(r'^(camera|realsense|zed|oak|kinect|rgbd|lidar|laser|scan|imu|gps)$', re.I)
                for ns, tlist in topics_by_ns.items():
                    if ns and sensor_ns_pattern.match(ns):
                        continue
                    score = self._score_namespace_topics(tlist)
                    if score > best_score:
                        best_score = score
                        best_ns = ns

            # Signals detection
            ns_topics = topics_by_ns.get(best_ns, [])
            global_topics = topics_by_ns.get('', [])
            all_relevant_topics = ns_topics + global_topics

            re_cmd_vel = re.compile(r'(?:^|/)cmd_vel(?:$|/)')
            re_joint_states = re.compile(r'(?:^|/)joint_states(?:$|/)')
            re_odom = re.compile(r'(?:^|/)odom(?:$|/)')
            re_controllers = re.compile(r'controller_manager')
            re_sensors = re.compile(r'(?:/image|/camera|/scan)(?:$|/)')

            has_cmd_vel = any(re_cmd_vel.search(t) for t in all_relevant_topics)
            has_joint_states = any(re_joint_states.search(t) for t in all_relevant_topics)
            has_odom = any(re_odom.search(t) for t in all_relevant_topics)
            has_controllers = any(re_controllers.search(t) for t in all_relevant_topics)
            has_sensors = any(re_sensors.search(t) for t in all_relevant_topics)
            confidence = sum([has_cmd_vel, has_joint_states, has_odom, has_controllers, has_sensors])

            # Friendly name
            if best_ns:
                derived_name = best_ns
            elif base_frame:
                frame_base = base_frame.split('::')[0].split('/')[0] or base_frame
                if 'turtlebot' in frame_base.lower() or 'robot' in frame_base.lower():
                    derived_name = frame_base.replace('_', ' ').title()
                else:
                    derived_name = f"Robot {idx + 1}"
            else:
                derived_name = f"Robot {idx + 1}"

            # Namespace topics with types
            namespace_topics = []
            for topic in (topics_by_ns.get(best_ns, []) + topics_by_ns.get('', [])):
                namespace_topics.append({
                    'topic': topic,
                    'messageType': type_by_topic.get(topic, '')
                })

            guessed.append({
                'id': f'instance_{idx + 1}',
                'namespace': best_ns,
                'name': derived_name,
                'baseFrame': base_frame,
                'frameCount': len(frames),
                'signals': {
                    'hasCmdVel': has_cmd_vel,
                    'hasJointStates': has_joint_states,
                    'hasOdom': has_odom,
                    'hasControllers': has_controllers,
                    'hasSensors': has_sensors
                },
                'confidence': confidence,
                'topics': namespace_topics
            })

        # 5) Check for additional global namespace robot
        global_topics = topics_by_ns.get('', [])
        has_global_robot_topics = any(
            re.search(r'\b(joint_states|robot_description|controller_manager|panda_arm|ur_arm|controller)\b', t)
            for t in global_topics
        )
        has_global_assignment = any(g['namespace'] == '' for g in guessed)

        if has_global_robot_topics and not has_global_assignment:
            re_cmd_vel = re.compile(r'(?:^|/)cmd_vel(?:$|/)')
            re_joint_states = re.compile(r'(?:^|/)joint_states(?:$|/)')
            re_odom = re.compile(r'(?:^|/)odom(?:$|/)')
            re_controllers = re.compile(r'controller_manager')
            re_sensors = re.compile(r'(?:/image|/camera|/scan)(?:$|/)')

            has_cmd_vel = any(re_cmd_vel.search(t) for t in global_topics)
            has_joint_states = any(re_joint_states.search(t) for t in global_topics)
            has_odom = any(re_odom.search(t) for t in global_topics)
            has_controllers = any(re_controllers.search(t) for t in global_topics)
            has_sensors = any(re_sensors.search(t) for t in global_topics)
            confidence = sum([has_cmd_vel, has_joint_states, has_odom, has_controllers, has_sensors])

            global_namespace_topics = [
                {'topic': t, 'messageType': type_by_topic.get(t, '')}
                for t in global_topics
            ]

            guessed.append({
                'id': 'instance_global',
                'namespace': '',
                'name': 'Global',
                'baseFrame': None,
                'frameCount': 0,
                'signals': {
                    'hasCmdVel': has_cmd_vel,
                    'hasJointStates': has_joint_states,
                    'hasOdom': has_odom,
                    'hasControllers': has_controllers,
                    'hasSensors': has_sensors
                },
                'confidence': confidence,
                'topics': global_namespace_topics
            })

        # 6) Filter/merge/dedupe
        camera_pattern = re.compile(r'^(camera|realsense|zed|oak|kinect|rgbd)', re.I)
        sensor_pattern = re.compile(r'^(lidar|laser|scan|imu|gps)', re.I)

        results = []
        for g in guessed:
            if g['frameCount'] > 1 or g['namespace'] == '':
                is_likely_camera = bool(camera_pattern.match(g['namespace']))
                is_likely_sensor = bool(sensor_pattern.match(g['namespace']))

                if is_likely_camera or is_likely_sensor:
                    has_robot_signals = (
                        g['signals']['hasCmdVel'] or
                        g['signals']['hasJointStates'] or
                        g['signals']['hasControllers']
                    )
                    if has_robot_signals:
                        results.append(g)
                else:
                    results.append(g)

        # Merge components with same namespace
        by_ns = {}
        for inst in results:
            k = inst['namespace'] or '(global)'
            if k not in by_ns:
                by_ns[k] = dict(inst)
            else:
                existing = by_ns[k]
                existing['frameCount'] += inst['frameCount']
                existing['confidence'] = max(existing['confidence'], inst['confidence'])
                existing['topics'] = existing['topics'] + inst['topics']

        results = list(by_ns.values())

        # 7) Apply filter function if provided
        if filter_fn:
            results = [r for r in results if filter_fn(r)]

        # 8) Sort by confidence then namespace
        results.sort(key=lambda x: (-x['confidence'], x['name']))

        # 9) Cache results
        self._discovery_cache[cache_key] = {
            'timestamp': now,
            'instances': results
        }

        return results

    def _build_connected_components(self, edges: Dict[str, str]) -> List[set]:
        """Build connected components from TF edges (undirected)"""
        adjacency = {}

        def add_edge(a, b):
            if not a or not b:
                return
            if a not in adjacency:
                adjacency[a] = set()
            if b not in adjacency:
                adjacency[b] = set()
            adjacency[a].add(b)
            adjacency[b].add(a)

        for child, parent in edges.items():
            add_edge(child, parent)

        seen = set()
        components = []

        for node in adjacency.keys():
            if node in seen:
                continue
            stack = [node]
            comp = set()
            while stack:
                cur = stack.pop()
                if cur in seen:
                    continue
                seen.add(cur)
                comp.add(cur)
                neighbors = adjacency.get(cur, set())
                for n in neighbors:
                    if n not in seen:
                        stack.append(n)
            if comp:
                components.append(comp)

        return components

    def _namespace_of(self, path: str) -> str:
        """Extract first namespace segment from a path"""
        parts = [p for p in (path or '').split('/') if p]
        return parts[0] if len(parts) > 1 else ''

    def _score_namespace_topics(self, topic_list: List[str]) -> int:
        """Score namespace by common robot signals"""
        import re
        score = 0
        for t in topic_list:
            if re.search(r'\bcmd_vel\b', t):
                score += 5
            elif re.search(r'\b(joint_states|odom)\b', t):
                score += 3
            elif re.search(r'\bcontroller_manager\b', t):
                score += 2
            elif re.search(r'\b(scan|lidar)\b', t):
                score += 2
            elif re.search(r'\b(image|camera)\b', t):
                score += 1
        return score

    def cleanup(self):
        """Clean up all subscriptions and velocity holds"""
        for topic_name in list(self._subscriptions.keys()):
            self._unsubscribe_sync(topic_name)
        
        # Best-effort stop velocity holds
        for topic, hold in list(self._active_velocity_holds.items()):
            try:
                hold['stop_event'].set()
                hold['task'].cancel()
            except Exception:
                pass
        self._active_velocity_holds.clear()

