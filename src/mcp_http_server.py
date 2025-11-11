"""HTTP/WebSocket server wrapper for MCP protocol over network."""

import json
import os
from typing import Any, Dict, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.unified_mcp_server import UnifiedMCPServer


# Configuration
API_KEY = os.getenv("MCP_API_KEY", "")  # Set MCP_API_KEY env var for authentication
REQUIRE_AUTH = os.getenv("MCP_REQUIRE_AUTH", "false").lower() == "true"
ALLOWED_ORIGINS = os.getenv("MCP_ALLOWED_ORIGINS", "*").split(",")


class MCPRequest(BaseModel):
    """JSON-RPC request model."""
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[str] = None


class MCPResponse(BaseModel):
    """JSON-RPC response model."""
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """Verify API key for authentication."""
    if not REQUIRE_AUTH:
        return True
    if not API_KEY:
        return True  # No key set, allow access
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return True


# Create FastAPI app
app = FastAPI(
    title="Xcode MCP Network Server",
    description="HTTP/WebSocket wrapper for Xcode MCP server",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if "*" not in ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create MCP server instance with response capture
from src.mcp_http_wrapper import create_network_mcp_server
mcp_server, response_capture = create_network_mcp_server()


@app.get("/")
async def root():
    """Root endpoint - server info."""
    return {
        "service": "Xcode MCP Network Server",
        "version": "2.0.0",
        "status": "running",
        "protocol": "JSON-RPC 2.0",
        "endpoints": {
            "http": "/mcp",
            "websocket": "/ws",
            "health": "/health",
            "tools": "/tools"
        },
        "authentication": "required" if REQUIRE_AUTH and API_KEY else "optional"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "tools_loaded": len(mcp_server.registry.tools),
        "langgraph_enabled": mcp_server.langgraph_enabled,
        "initialized": mcp_server.initialized
    }


@app.get("/tools")
async def list_tools():
    """List all available tools (direct endpoint)."""
    tools = []
    for tool_def in mcp_server.registry.list_tools():
        tool_schema = {
            "name": tool_def.get("name"),
            "description": tool_def.get("description", "")
        }
        params = tool_def.get("parameters", [])
        properties = {}
        if params:
            for param in params:
                param_name = param.get("name")
                param_type = param.get("type", "string")
                properties[param_name] = {
                    "type": param_type,
                    "description": param.get("description", "")
                }
        tool_schema["inputSchema"] = {
            "type": "object",
            "properties": properties,
            "additionalProperties": True
        }
        tools.append(tool_schema)
    
    # Add LangGraph tools if enabled
    if mcp_server.langgraph_enabled:
        tools.extend([
            {
                "name": "langgraph_query",
                "description": "Execute a natural language query using LangGraph agent",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string"},
                        "model": {"type": "string"},
                        "persona": {"type": "object"}
                    },
                    "required": ["prompt"]
                }
            },
            {
                "name": "langgraph_workflow",
                "description": "Execute a multi-step Xcode workflow using LangGraph",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "workflow": {"type": "string"},
                        "context": {"type": "object"},
                        "persona": {"type": "object"}
                    },
                    "required": ["workflow"]
                }
            },
            {
                "name": "langgraph_status",
                "description": "Get LangGraph agent status",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ])
    
    return {
        "tools": tools,
        "count": len(tools),
        "direct_tools": len(mcp_server.registry.tools),
        "langgraph_tools": 3 if mcp_server.langgraph_enabled else 0
    }


@app.post("/mcp", dependencies=[Depends(verify_api_key)])
async def mcp_http(request: MCPRequest):
    """Handle MCP JSON-RPC requests over HTTP POST."""
    try:
        # Convert Pydantic model to dict
        request_dict = request.dict(exclude_none=True)
        
        # Handle request using MCP server
        method = request_dict.get("method")
        params = request_dict.get("params", {})
        request_id = request_dict.get("id")
        
        # Capture response
        captured_response = None
        
        def capture_callback(response):
            nonlocal captured_response
            captured_response = response
        
        response_capture.set_callback(capture_callback)
        
        # Initialize if needed
        if method == "initialize":
            mcp_server.handle_initialize(params, request_id)
        elif method == "tools/list":
            if not mcp_server.initialized:
                return JSONResponse(
                    status_code=400,
                    content={
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32002,
                            "message": "Server not initialized"
                        },
                        "id": request_id
                    }
                )
            mcp_server.handle_tools_list(request_id)
        elif method == "tools/call":
            if not mcp_server.initialized:
                return JSONResponse(
                    status_code=400,
                    content={
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32002,
                            "message": "Server not initialized"
                        },
                        "id": request_id
                    }
                )
            mcp_server.handle_tools_call(params, request_id)
        elif method == "notifications/initialized":
            # Notification, no response needed
            return {"jsonrpc": "2.0", "result": None}
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    },
                    "id": request_id
                }
            )
        
        # Return captured response
        if captured_response:
            return captured_response
        
        # Fallback if no response captured
        return {
            "jsonrpc": "2.0",
            "result": {"status": "processed"},
            "id": request_id
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                },
                "id": request_dict.get("id")
            }
        )


class MCPWebSocketHandler:
    """WebSocket handler for MCP protocol."""
    
    def __init__(self, server, capture):
        self.server = server
        self.capture = capture
    
    async def handle_message(self, websocket: WebSocket, message: str):
        """Handle incoming WebSocket message."""
        try:
            request = json.loads(message)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            # Capture response
            captured_response = None
            
            def capture_callback(response):
                nonlocal captured_response
                captured_response = response
            
            self.capture.set_callback(capture_callback)
            
            # Handle request
            if method == "initialize":
                self.server.handle_initialize(params, request_id)
            elif method == "tools/list":
                if not self.server.initialized:
                    await websocket.send_json({
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32002,
                            "message": "Server not initialized"
                        },
                        "id": request_id
                    })
                    return
                self.server.handle_tools_list(request_id)
            elif method == "tools/call":
                if not self.server.initialized:
                    await websocket.send_json({
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32002,
                            "message": "Server not initialized"
                        },
                        "id": request_id
                    })
                    return
                self.server.handle_tools_call(params, request_id)
            elif method == "notifications/initialized":
                pass  # Notification, no response
            else:
                await websocket.send_json({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    },
                    "id": request_id
                })
                return
            
            # Send captured response
            if captured_response:
                await websocket.send_json(captured_response)
            else:
                await websocket.send_json({
                    "jsonrpc": "2.0",
                    "result": {"status": "processed"},
                    "id": request_id
                })
            
        except json.JSONDecodeError:
            await websocket.send_json({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            })
        except Exception as e:
            await websocket.send_json({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            })


ws_handler = MCPWebSocketHandler(mcp_server, response_capture)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for MCP protocol."""
    await websocket.accept()
    
    # Optional: Verify API key from query params
    if REQUIRE_AUTH and API_KEY:
        api_key = websocket.query_params.get("api_key")
        if api_key != API_KEY:
            await websocket.close(code=1008, reason="Invalid API key")
            return
    
    try:
        while True:
            message = await websocket.receive_text()
            await ws_handler.handle_message(websocket, message)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}", file=sys.stderr)


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("MCP_HOST", "0.0.0.0")  # 0.0.0.0 allows network access
    port = int(os.getenv("MCP_PORT", "8000"))
    
    print(f"🚀 Starting Xcode MCP Network Server...")
    print(f"📍 HTTP endpoint: http://{host}:{port}/mcp")
    print(f"🔌 WebSocket endpoint: ws://{host}:{port}/ws")
    print(f"📋 Tools endpoint: http://{host}:{port}/tools")
    print(f"💚 Health check: http://{host}:{port}/health")
    if REQUIRE_AUTH and API_KEY:
        print(f"🔐 Authentication: Required (API key)")
    else:
        print(f"🔓 Authentication: Disabled")
    print()
    
    uvicorn.run(app, host=host, port=port)

