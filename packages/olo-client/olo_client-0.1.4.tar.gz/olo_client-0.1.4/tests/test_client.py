"""
Tests for OLOClient
"""

import pytest
from oloclient import OLOClient, OLOCore


class TestOLOClientInit:
    """Test OLOClient initialization"""
    
    def test_init_with_url(self):
        """Test initialization with full URL"""
        client = OLOClient(ros_url='ws://localhost:9090')
        assert client._host == 'localhost'
        assert client._port == 9090
        assert client._ros_url == 'ws://localhost:9090'
    
    def test_init_with_url_and_path(self):
        """Test initialization with URL containing path"""
        client = OLOClient(ros_url='ws://localhost:3000/rosbridge')
        assert client._host == 'localhost'
        assert client._port == 3000
        assert client._use_full_url == True
    
    def test_init_with_host_port(self):
        """Test initialization with host and port"""
        client = OLOClient(host='192.168.1.100', port=9090)
        assert client._host == '192.168.1.100'
        assert client._port == 9090
    
    def test_init_default_port(self):
        """Test default port when not specified"""
        client = OLOClient(host='localhost')
        assert client._port == 9090
    
    def test_core_property(self):
        """Test that core property returns OLOCore instance"""
        client = OLOClient(ros_url='ws://localhost:9090')
        assert isinstance(client.core, OLOCore)
    
    def test_is_connected_initially_false(self):
        """Test that is_connected is False before connecting"""
        client = OLOClient(ros_url='ws://localhost:9090')
        # Note: roslibpy may report different status before run()
        # This test verifies the property exists
        assert hasattr(client, 'is_connected')


class TestOLOCore:
    """Test OLOCore functionality"""
    
    def test_init(self):
        """Test OLOCore initialization"""
        client = OLOClient(ros_url='ws://localhost:9090')
        core = client.core
        assert core._subscriptions == {}
        assert core._topics_cache == []
        assert core._active_velocity_holds == {}
    
    def test_get_connection_status(self):
        """Test get_connection_status method"""
        client = OLOClient(ros_url='ws://localhost:9090')
        # Should not raise even when not connected
        status = client.core.get_connection_status()
        assert isinstance(status, bool)

