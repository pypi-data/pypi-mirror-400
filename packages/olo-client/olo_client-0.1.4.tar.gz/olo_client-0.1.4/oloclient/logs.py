"""
OLO Logs API - Read and query script execution logs
"""

import asyncio
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime


class OLOLogs:
    """
    Logs API for reading script execution logs from the appliance.
    
    Provides methods for:
    - Listing execution logs with filtering
    - Getting log entries with date/time/content filtering
    - Quick tail and search helpers
    - Metadata retrieval
    
    Example:
        async with OLOClient(ros_url='ws://localhost:9090') as client:
            # List recent executions
            result = await client.logs.list_executions(limit=10)
            for exec in result['executions']:
                print(f"{exec['scriptName']} - {exec['startedAt']}")
            
            # Get last 50 lines from an execution
            logs = await client.logs.tail(execution_id, lines=50)
            for log in logs['logs']:
                print(f"[{log['timestamp']}] {log['message']}")
    """

    def __init__(self, ros_client):
        """
        Initialize OLO Logs
        
        Args:
            ros_client: roslibpy.Ros instance
        """
        self._ros = ros_client
        self._request_counter = 0
        self._pending_requests = {}

    def _generate_request_id(self) -> str:
        """Generate unique request ID for tracking responses"""
        self._request_counter += 1
        return f"logs_{self._request_counter}_{int(datetime.now().timestamp() * 1000)}"

    async def _send_and_wait(
        self,
        message: Dict[str, Any],
        success_op: str,
        error_op: str,
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        Send a message and wait for response
        
        Args:
            message: Message to send
            success_op: Expected success operation name
            error_op: Expected error operation name
            timeout: Timeout in seconds
            
        Returns:
            Response data
            
        Raises:
            ConnectionError: If not connected
            TimeoutError: If request times out
            Exception: If operation fails
        """
        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        request_id = self._generate_request_id()
        message['requestId'] = request_id

        loop = asyncio.get_event_loop()
        future = loop.create_future()

        def handle_message(msg):
            """Handle incoming messages looking for our response"""
            try:
                if isinstance(msg, str):
                    data = json.loads(msg)
                elif isinstance(msg, dict):
                    data = msg
                else:
                    return

                if data.get('requestId') != request_id:
                    return

                op = data.get('op', '')
                
                if op == success_op:
                    # Remove metadata fields
                    result = {k: v for k, v in data.items() 
                              if k not in ('requestId', 'op')}
                    if not future.done():
                        loop.call_soon_threadsafe(future.set_result, result)
                elif op == error_op:
                    error_msg = data.get('error', 'Operation failed')
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
        custom_ops = {success_op, error_op}

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
            msg_json = json.dumps(message)
            if proto_instance:
                proto_instance.sendMessage(msg_json.encode('utf-8'))
            else:
                raise ConnectionError("Cannot send message - protocol not connected")

            # Wait for response with timeout
            return await asyncio.wait_for(future, timeout=timeout)

        except asyncio.TimeoutError:
            raise TimeoutError(f"Request timed out after {timeout}s")
        finally:
            # Restore original handler
            if proto_instance and old_onMessage is not None:
                proto_instance.onMessage = old_onMessage

    async def list_executions(
        self,
        script_name: Optional[str] = None,
        script_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List execution logs with optional filtering
        
        Args:
            script_name: Filter by script name (partial match)
            script_id: Filter by script ID (exact match)
            start_date: Filter executions after this date (ISO string)
            end_date: Filter executions before this date (ISO string)
            limit: Maximum results (default: 50)
            offset: Pagination offset (default: 0)
            
        Returns:
            Dict with:
                - executions: List of execution info dicts
                - total: Total count
                - offset: Current offset
                - limit: Current limit
                - hasMore: Whether more results exist
                
        Example:
            result = await client.logs.list_executions(script_name='patrol', limit=10)
            for exec in result['executions']:
                print(f"{exec['executionId']}: {exec['scriptName']}")
        """
        message = {
            'op': 'list_executions',
            'limit': limit,
            'offset': offset
        }
        if script_name:
            message['scriptName'] = script_name
        if script_id:
            message['scriptId'] = script_id
        if start_date:
            message['startDate'] = start_date
        if end_date:
            message['endDate'] = end_date

        return await self._send_and_wait(
            message,
            'list_executions_result',
            'list_executions_error'
        )

    async def get_logs(
        self,
        execution_id: str,
        lines: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        search: Optional[str] = None,
        log_type: Optional[str] = None,
        offset: int = 0,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Get log entries with filtering
        
        Args:
            execution_id: Execution ID (required)
            lines: Return last N lines (tail mode)
            start_date: Filter entries after this date (ISO string)
            end_date: Filter entries before this date (ISO string)
            search: Filter entries containing this text
            log_type: Filter by type ('stdout' or 'stderr')
            offset: Pagination offset (default: 0)
            limit: Maximum entries (default: 1000)
            
        Returns:
            Dict with:
                - executionId: The execution ID
                - metadata: Script metadata
                - logs: List of log entry dicts with timestamp, type, message
                - total: Total matching entries
                - offset/limit/hasMore: Pagination info
                
        Example:
            result = await client.logs.get_logs(
                execution_id='abc-123',
                search='error',
                log_type='stderr'
            )
            for log in result['logs']:
                print(f"[{log['timestamp']}] {log['message']}")
        """
        if not execution_id:
            raise ValueError("execution_id is required")

        message = {
            'op': 'query_logs',
            'executionId': execution_id,
            'offset': offset,
            'limit': limit
        }
        if lines is not None:
            message['lines'] = lines
        if start_date:
            message['startDate'] = start_date
        if end_date:
            message['endDate'] = end_date
        if search:
            message['search'] = search
        if log_type:
            message['type'] = log_type

        return await self._send_and_wait(
            message,
            'query_logs_result',
            'query_logs_error'
        )

    async def tail(self, execution_id: str, lines: int = 100) -> Dict[str, Any]:
        """
        Get last N lines of a log (convenience method)
        
        Args:
            execution_id: Execution ID
            lines: Number of lines (default: 100)
            
        Returns:
            Dict with logs array and metadata
            
        Example:
            result = await client.logs.tail('abc-123', 50)
            for log in result['logs']:
                print(log['message'])
        """
        if not execution_id:
            raise ValueError("execution_id is required")

        return await self._send_and_wait(
            {'op': 'tail_logs', 'executionId': execution_id, 'lines': lines},
            'tail_logs_result',
            'tail_logs_error'
        )

    async def search(
        self,
        query: str,
        script_name: Optional[str] = None,
        script_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 10,
        max_executions: int = 20
    ) -> Dict[str, Any]:
        """
        Search across multiple execution logs
        
        Args:
            query: Search text (required)
            script_name: Filter by script name
            script_id: Filter by script ID
            start_date: Filter by date range start
            end_date: Filter by date range end
            limit: Max results per execution (default: 10)
            max_executions: Max executions to search (default: 20)
            
        Returns:
            Dict with:
                - query: The search query
                - results: List of matching executions with matches
                - totalExecutionsSearched: Number of executions searched
                - executionsWithMatches: Number with matching entries
                
        Example:
            result = await client.logs.search('connection failed')
            for exec_result in result['results']:
                print(f"{exec_result['scriptName']}: {exec_result['matchCount']} matches")
        """
        if not query:
            raise ValueError("query is required")

        message = {
            'op': 'search_logs',
            'query': query,
            'limit': limit,
            'maxExecutions': max_executions
        }
        if script_name:
            message['scriptName'] = script_name
        if script_id:
            message['scriptId'] = script_id
        if start_date:
            message['startDate'] = start_date
        if end_date:
            message['endDate'] = end_date

        return await self._send_and_wait(
            message,
            'search_logs_result',
            'search_logs_error'
        )

    async def get_metadata(self, execution_id: str) -> Dict[str, Any]:
        """
        Get metadata for an execution log
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Dict with execution metadata including:
                - executionId, scriptName, scriptId, language
                - startedAt, size, sizeFormatted
                - entryCount, firstEntry, lastEntry
                
        Example:
            meta = await client.logs.get_metadata('abc-123')
            print(f"Script: {meta['scriptName']}, Entries: {meta['entryCount']}")
        """
        if not execution_id:
            raise ValueError("execution_id is required")

        return await self._send_and_wait(
            {'op': 'get_log_metadata', 'executionId': execution_id},
            'log_metadata_result',
            'log_metadata_error'
        )

    async def delete_log(self, execution_id: str) -> bool:
        """
        Delete an execution log
        
        Args:
            execution_id: Execution ID
            
        Returns:
            True if deleted successfully
            
        Raises:
            Exception: If deletion fails
            
        Example:
            await client.logs.delete_log('abc-123')
            print('Log deleted')
        """
        if not execution_id:
            raise ValueError("execution_id is required")

        if not self._ros.is_connected:
            raise ConnectionError("Not connected to ROS")

        loop = asyncio.get_event_loop()
        future = loop.create_future()

        def handle_message(msg):
            try:
                if isinstance(msg, str):
                    data = json.loads(msg)
                elif isinstance(msg, dict):
                    data = msg
                else:
                    return

                if data.get('op') == 'execution_log_deleted' and data.get('executionId') == execution_id:
                    if data.get('success'):
                        if not future.done():
                            loop.call_soon_threadsafe(future.set_result, True)
                    else:
                        error_msg = data.get('error', 'Failed to delete log')
                        if not future.done():
                            loop.call_soon_threadsafe(
                                future.set_exception,
                                Exception(error_msg)
                            )
            except (json.JSONDecodeError, TypeError):
                pass

        # Get protocol instance
        proto_instance = None
        if hasattr(self._ros, 'factory') and self._ros.factory:
            proto_instance = getattr(self._ros.factory, '_proto', None)

        old_onMessage = None
        if proto_instance and hasattr(proto_instance, 'onMessage'):
            old_onMessage = proto_instance.onMessage
            
            def patched_onMessage(payload, isBinary):
                if not isBinary:
                    try:
                        msg_str = payload.decode('utf-8') if isinstance(payload, bytes) else payload
                        handle_message(msg_str)
                        if old_onMessage:
                            old_onMessage(payload, isBinary)
                    except:
                        if old_onMessage:
                            old_onMessage(payload, isBinary)
                else:
                    if old_onMessage:
                        old_onMessage(payload, isBinary)
            
            proto_instance.onMessage = patched_onMessage

        try:
            msg = json.dumps({'op': 'delete_execution_log', 'executionId': execution_id})
            if proto_instance:
                proto_instance.sendMessage(msg.encode('utf-8'))
            else:
                raise ConnectionError("Cannot send message - protocol not connected")

            return await asyncio.wait_for(future, timeout=30.0)
        except asyncio.TimeoutError:
            raise TimeoutError("Delete request timed out")
        finally:
            if proto_instance and old_onMessage is not None:
                proto_instance.onMessage = old_onMessage

    async def get_by_date_range(
        self,
        execution_id: str,
        start_date: str,
        end_date: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get logs for a specific date range (convenience method)
        
        Args:
            execution_id: Execution ID
            start_date: Start date (ISO string or datetime)
            end_date: End date (ISO string or datetime)
            **kwargs: Additional options (search, log_type, limit)
            
        Returns:
            Filtered log entries
        """
        # Convert datetime objects to ISO strings
        if isinstance(start_date, datetime):
            start_date = start_date.isoformat()
        if isinstance(end_date, datetime):
            end_date = end_date.isoformat()

        return await self.get_logs(
            execution_id=execution_id,
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )

    async def get_errors(
        self,
        execution_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get only error logs (stderr) from an execution
        
        Args:
            execution_id: Execution ID
            **kwargs: Additional options (lines, search, limit)
            
        Returns:
            Error log entries
            
        Example:
            errors = await client.logs.get_errors('abc-123')
            if errors['logs']:
                print('Found errors:', len(errors['logs']))
        """
        return await self.get_logs(
            execution_id=execution_id,
            log_type='stderr',
            **kwargs
        )

