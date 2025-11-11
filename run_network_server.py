#!/usr/bin/env python3
"""Network-enabled MCP server entry point."""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run network server
from src.mcp_http_server import app
import uvicorn

if __name__ == "__main__":
    host = os.getenv("MCP_HOST", "0.0.0.0")  # 0.0.0.0 allows network access
    port = int(os.getenv("MCP_PORT", "8000"))
    
    print(f"🚀 Starting Xcode MCP Network Server...")
    print(f"📍 HTTP endpoint: http://{host}:{port}/mcp")
    print(f"🔌 WebSocket endpoint: ws://{host}:{port}/ws")
    print(f"📋 Tools endpoint: http://{host}:{port}/tools")
    print(f"💚 Health check: http://{host}:{port}/health")
    
    api_key = os.getenv("MCP_API_KEY", "")
    require_auth = os.getenv("MCP_REQUIRE_AUTH", "false").lower() == "true"
    
    if require_auth and api_key:
        print(f"🔐 Authentication: Required (API key set)")
    else:
        print(f"🔓 Authentication: Disabled")
    
    print(f"\n💡 To connect from other devices:")
    print(f"   - Get your IP: ifconfig | grep 'inet ' | grep -v 127.0.0.1")
    print(f"   - Use: http://YOUR_IP:{port}/mcp")
    print()
    
    uvicorn.run(app, host=host, port=port)


