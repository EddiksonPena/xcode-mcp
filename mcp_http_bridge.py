#!/usr/bin/env python3
"""
MCP HTTP Bridge - Converts stdio MCP protocol to HTTP/WebSocket

Usage:
    MCP_SERVER_URL=http://192.168.4.208:8000 python3 mcp_http_bridge.py

Or configure in ~/.cursor/mcp.json:
{
  "mcpServers": {
    "xcode-mcp-remote": {
      "command": "python3",
      "args": ["/path/to/mcp_http_bridge.py"],
      "env": {
        "MCP_SERVER_URL": "http://192.168.4.208:8000",
        "MCP_API_KEY": ""
      }
    }
  }
}
"""

import sys
import os
import threading
import json

try:
    import websocket
except ImportError:
    print("Error: websocket-client not installed", file=sys.stderr)
    print("Install with: pip install websocket-client", file=sys.stderr)
    sys.exit(1)

SERVER_URL = os.getenv("MCP_SERVER_URL", "http://192.168.4.208:8000")
API_KEY = os.getenv("MCP_API_KEY", "")

# Convert HTTP URL to WebSocket URL
if SERVER_URL.startswith("http://"):
    ws_url = SERVER_URL.replace("http://", "ws://") + "/ws"
elif SERVER_URL.startswith("https://"):
    ws_url = SERVER_URL.replace("https://", "wss://") + "/ws"
else:
    print(f"Error: Invalid MCP_SERVER_URL: {SERVER_URL}", file=sys.stderr)
    sys.exit(1)

if API_KEY:
    ws_url += f"?api_key={API_KEY}"

connected = False
message_queue = []
ws = None

def on_message(ws, message):
    """Forward WebSocket message to stdout (MCP response)"""
    try:
        sys.stdout.write(message + "\n")
        sys.stdout.flush()
    except Exception as e:
        print(f"Error writing to stdout: {e}", file=sys.stderr)

def on_error(ws, error):
    """Handle WebSocket errors"""
    print(f"❌ WebSocket error: {error}", file=sys.stderr)
    if not connected:
        print(f"   Make sure the server is running at: {SERVER_URL}", file=sys.stderr)
        print("   Start server with: python run_network_server.py", file=sys.stderr)
    sys.exit(1)

def on_close(ws, close_status_code, close_msg):
    """Handle WebSocket close"""
    print("🔌 Connection closed", file=sys.stderr)
    sys.exit(0)

def on_open(ws):
    """Handle WebSocket open"""
    global connected, message_queue
    connected = True
    print(f"✅ Connected to MCP server: {SERVER_URL}", file=sys.stderr)
    
    # Send queued messages
    while message_queue:
        ws.send(message_queue.pop(0))
    
    # Read from stdin and forward to WebSocket
    def read_stdin():
        try:
            for line in sys.stdin:
                line = line.strip()
                if line:
                    if connected:
                        ws.send(line)
                    else:
                        message_queue.append(line)
        except Exception as e:
            print(f"Error reading stdin: {e}", file=sys.stderr)
            ws.close()
    
    thread = threading.Thread(target=read_stdin)
    thread.daemon = True
    thread.start()

# Create WebSocket connection
ws = websocket.WebSocketApp(
    ws_url,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
    on_open=on_open
)

try:
    ws.run_forever()
except KeyboardInterrupt:
    if ws:
        ws.close()
    sys.exit(0)


