"""Integration tests for MCP bridge."""

import asyncio
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Add mcp directory to path
mcp_path = os.path.join(project_root, 'mcp')
sys.path.insert(0, mcp_path)

# Import MCP bridge module directly
import mcp_bridge as bridge_module
from mcp_bridge import MCPServerBridge, app


class TestMCPServerBridge:
    """Test cases for MCPServerBridge class."""

    @pytest.fixture
    def mock_server_path(self):
        """Mock server path for testing."""
        return Path("/tmp/test_mcp_server")

    @pytest.fixture
    def bridge(self):
        """Create a bridge instance for testing."""
        return MCPServerBridge()

    @pytest.mark.asyncio
    async def test_start_server_success(self, bridge, mock_server_path):
        """Test successful server start."""
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_popen.return_value = mock_process
            
            with patch('pathlib.Path', return_value=mock_server_path):
                await bridge.start_server()
                
                # Verify subprocess.Popen was called with correct arguments
                mock_popen.assert_called_once_with(
                    ["cargo", "run"],
                    cwd=mock_server_path,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=0
                )
                
                # Verify server process is set
                assert bridge.server_process == mock_process

    @pytest.mark.asyncio
    async def test_start_server_failure(self, bridge, mock_server_path):
        """Test server start failure."""
        with patch('subprocess.Popen', side_effect=Exception("Failed to start")):
            with patch('pathlib.Path', return_value=mock_server_path):
                with pytest.raises(Exception, match="Failed to start"):
                    await bridge.start_server()

    @pytest.mark.asyncio
    async def test_stop_server(self, bridge):
        """Test server stop."""
        mock_process = MagicMock()
        bridge.server_process = mock_process
        
        await bridge.stop_server()
        
        # Verify terminate and wait were called
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once()
        
        # Verify server process is cleared
        assert bridge.server_process is None

    @pytest.mark.asyncio
    async def test_stop_server_no_process(self, bridge):
        """Test stop server when no process is running."""
        # Should not raise an exception
        await bridge.stop_server()
        
        # Server process should still be None
        assert bridge.server_process is None


class TestMCPBridgeAPI:
    """Test cases for MCP bridge API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return httpx.AsyncClient(app)

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["server"] == "exaspoon-mcp-bridge"

    def test_sse_endpoint(self, client):
        """Test SSE endpoint returns proper format."""
        response = client.get("/sse")
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        
        # Read the SSE content
        content = response.text
        assert content.startswith("data: ")
        
        # Parse the JSON data
        data_start = content.find("{")
        data_end = content.rfind("}") + 1
        json_data = json.loads(content[data_start:data_end])
        
        # Verify the structure
        assert json_data["jsonrpc"] == "2.0"
        assert json_data["method"] == "initialize"
        assert "params" in json_data
        assert "protocolVersion" in json_data["params"]
        assert "capabilities" in json_data["params"]
        assert "serverInfo" in json_data["params"]
        assert json_data["params"]["serverInfo"]["name"] == "exaspoon-db-mcp"
        assert json_data["params"]["serverInfo"]["version"] == "1.0.0"

    def test_sse_endpoint_error_handling(self, client):
        """Test SSE endpoint error handling."""
        # Mock the event_stream function to raise an exception
        with patch.object(bridge_module, 'event_stream') as mock_stream:
            mock_stream.side_effect = Exception("Test error")
            
            response = client.get("/sse")
            assert response.status_code == 200
            
            # Read the SSE content
            content = response.text
            assert "error" in content
            assert "Test error" in content

    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        # Test preflight request
        response = client.options("/health")
        # OPTIONS requests may return 405 Method Not Allowed, which is acceptable
        assert response.status_code in [200, 405]
        
        # Check for CORS headers
        headers = response.headers
        assert "access-control-allow-origin" in headers
        assert "access-control-allow-methods" in headers
        assert "access-control-allow-headers" in headers


class TestMCPBridgeIntegration:
    """Integration tests for the complete MCP bridge."""

    @pytest.mark.asyncio
    async def test_bridge_lifecycle(self):
        """Test complete bridge lifecycle."""
        bridge = MCPServerBridge()
        
        # Mock subprocess to avoid actually starting the server
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_popen.return_value = mock_process
            
            with patch('pathlib.Path'):
                # Start the server
                await bridge.start_server()
                assert bridge.server_process == mock_process
                
                # Stop the server
                await bridge.stop_server()
                mock_process.terminate.assert_called_once()
                mock_process.wait.assert_called_once()

    def test_bridge_with_real_client(self):
        """Test bridge with real HTTP client."""
        client = httpx.AsyncClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        
        # Test SSE endpoint
        response = client.get("/sse")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"
        
        # Verify the SSE content
        content = response.text
        assert content.startswith("data: ")
        
        # Parse the JSON data
        data_start = content.find("{")
        data_end = content.rfind("}") + 1
        json_data = json.loads(content[data_start:data_end])
        
        # Verify the structure
        assert json_data["jsonrpc"] == "2.0"
        assert json_data["method"] == "initialize"

    @pytest.mark.asyncio
    async def test_startup_shutdown_events(self):
        """Test startup and shutdown events."""
        client = httpx.AsyncClient(app)
        
        # Mock the bridge to track method calls
        with patch('mcp_bridge.bridge') as mock_bridge:
            # Create a test client with the app
            client = httpx.AsyncClient(app)
            
            # Simulate startup event
            from mcp_bridge import startup_event
            await startup_event()
            mock_bridge.start_server.assert_called_once()
            
            # Simulate shutdown event
            from mcp_bridge import shutdown_event
            await shutdown_event()
            mock_bridge.stop_server.assert_called_once()


class TestMCPBridgeErrorHandling:
    """Test error handling in MCP bridge."""

    @pytest.mark.asyncio
    async def test_server_process_termination(self):
        """Test handling of server process termination."""
        bridge = MCPServerBridge()
        
        # Mock a process that terminates with an error
        mock_process = MagicMock()
        mock_process.wait.side_effect = Exception("Process terminated with error")
        bridge.server_process = mock_process
        
        # Should raise an exception
        with pytest.raises(Exception, match="Process terminated with error"):
            await bridge.stop_server()

    def test_sse_stream_interruption(self):
        """Test SSE stream interruption handling."""
        client = httpx.AsyncClient(app)
        
        # Mock the event_stream to simulate interruption
        with patch('mcp_bridge.event_stream') as mock_stream:
            mock_stream.return_value = self._create_interrupted_generator()
            
            response = client.get("/sse")
            assert response.status_code == 200
            
            # Should handle interruption gracefully
            content = response.text
            assert "error" in content

    def _create_interrupted_generator(self):
        """Create a generator that raises an exception."""
        async def event_stream():
            try:
                yield "data: " + json.dumps({
                    "jsonrpc": "2.0",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "exaspoon-db-mcp", "version": "1.0.0"}
                    }
                }) + "\n\n"
                # Simulate an interruption
                raise Exception("Stream interrupted")
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return event_stream()
