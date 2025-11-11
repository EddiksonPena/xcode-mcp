"""HTTP wrapper that captures MCP server responses for network use."""

import json
import io
import sys
from typing import Any, Dict, Optional, Callable
from contextlib import redirect_stdout, redirect_stderr


class MCPResponseCapture:
    """Capture MCP server responses for HTTP/WebSocket use."""
    
    def __init__(self, server):
        self.server = server
        self.last_response = None
        self.response_callback = None
    
    def set_callback(self, callback: Callable):
        """Set callback for responses."""
        self.response_callback = callback
    
    def capture_response(self, id: Optional[str], result: Any = None, error: Optional[Dict] = None):
        """Capture response instead of writing to stdout."""
        response = {
            "jsonrpc": "2.0",
        }
        if id is not None:
            response["id"] = id
        
        if error:
            response["error"] = error
        else:
            response["result"] = result
        
        self.last_response = response
        
        if self.response_callback:
            self.response_callback(response)
        
        return response


def create_network_mcp_server():
    """Create MCP server with network response capture."""
    from src.unified_mcp_server import UnifiedMCPServer
    
    server = UnifiedMCPServer()
    capture = MCPResponseCapture(server)
    
    # Override send_response to capture instead of stdout
    original_send = server.send_response
    
    def capture_send_response(id, result=None, error=None):
        """Capture response and optionally call original."""
        return capture.capture_response(id, result, error)
    
    server.send_response = capture_send_response
    
    return server, capture

