# Client Configuration Guide

This guide explains how to configure another device to connect to your network MCP server.

## Overview

The MCP protocol typically uses stdio (standard input/output) for local connections. For network connections, you have two options:

1. **Direct HTTP/WebSocket Client** - Use HTTP/WebSocket directly (requires custom client)
2. **MCP Bridge/Proxy** - Use a bridge that converts HTTP to stdio MCP protocol

## Option 1: Direct HTTP/WebSocket Connection

If your client supports HTTP/WebSocket transport for MCP, you can configure it directly.

### Cursor Configuration (if HTTP transport supported)

**Location:** `~/.cursor/mcp.json` (on the client device)

```json
{
  "mcpServers": {
    "xcode-mcp-remote": {
      "command": "node",
      "args": [
        "-e",
        "const http = require('http'); const ws = require('ws'); const server = 'http://192.168.4.208:8000'; const client = new ws.WebSocket(server.replace('http', 'ws') + '/ws'); client.on('open', () => { process.stdin.on('data', (d) => { client.send(d.toString()); }); client.on('message', (m) => { process.stdout.write(m.toString()); }); });"
      ],
      "env": {
        "MCP_SERVER_URL": "http://192.168.4.208:8000"
      }
    }
  }
}
```

**Note:** This is a simplified example. Cursor may not natively support HTTP transport for MCP.

## Option 2: MCP Bridge Script (Recommended)

Create a bridge script that converts stdio MCP to HTTP/WebSocket.

### Step 1: Create Bridge Script on Client Device

Create a file `mcp_http_bridge.js` on the client device:

```javascript
#!/usr/bin/env node
/**
 * MCP HTTP Bridge - Converts stdio MCP protocol to HTTP/WebSocket
 */

const WebSocket = require('ws');
const http = require('http');
const readline = require('readline');

const SERVER_URL = process.env.MCP_SERVER_URL || 'http://192.168.4.208:8000';
const API_KEY = process.env.MCP_API_KEY || '';

// Parse server URL
const url = new URL(SERVER_URL);
const wsUrl = `ws://${url.hostname}:${url.port}/ws${API_KEY ? `?api_key=${API_KEY}` : ''}`;

// Create WebSocket connection
const ws = new WebSocket(wsUrl);

// Read from stdin (MCP requests)
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

ws.on('open', () => {
  console.error('Connected to MCP server:', SERVER_URL);
  
  // Forward stdin to WebSocket
  rl.on('line', (line) => {
    if (line.trim()) {
      try {
        ws.send(line);
      } catch (e) {
        console.error('Error sending:', e);
      }
    }
  });
});

// Forward WebSocket messages to stdout (MCP responses)
ws.on('message', (data) => {
  process.stdout.write(data.toString() + '\n');
});

ws.on('error', (error) => {
  console.error('WebSocket error:', error);
  process.exit(1);
});

ws.on('close', () => {
  console.error('Connection closed');
  process.exit(0);
});

// Handle stdin end
process.stdin.on('end', () => {
  ws.close();
});
```

### Step 2: Install Dependencies on Client Device

```bash
npm install ws
```

### Step 3: Configure Cursor on Client Device

**Location:** `~/.cursor/mcp.json` (on the client device)

```json
{
  "mcpServers": {
    "xcode-mcp-remote": {
      "command": "node",
      "args": [
        "/path/to/mcp_http_bridge.js"
      ],
      "env": {
        "MCP_SERVER_URL": "http://192.168.4.208:8000",
        "MCP_API_KEY": ""
      }
    }
  }
}
```

**With Authentication:**
```json
{
  "mcpServers": {
    "xcode-mcp-remote": {
      "command": "node",
      "args": [
        "/path/to/mcp_http_bridge.js"
      ],
      "env": {
        "MCP_SERVER_URL": "http://192.168.4.208:8000",
        "MCP_API_KEY": "your-secret-key"
      }
    }
  }
}
```

## Option 3: Python Bridge Script (Alternative)

If you prefer Python, create `mcp_http_bridge.py`:

```python
#!/usr/bin/env python3
"""
MCP HTTP Bridge - Converts stdio MCP protocol to HTTP/WebSocket
"""

import sys
import json
import os
import websocket
import threading

SERVER_URL = os.getenv("MCP_SERVER_URL", "http://192.168.4.208:8000")
API_KEY = os.getenv("MCP_API_KEY", "")

# Convert HTTP URL to WebSocket URL
ws_url = SERVER_URL.replace("http://", "ws://").replace("https://", "wss://") + "/ws"
if API_KEY:
    ws_url += f"?api_key={API_KEY}"

def on_message(ws, message):
    """Forward WebSocket message to stdout (MCP response)"""
    sys.stdout.write(message + "\n")
    sys.stdout.flush()

def on_error(ws, error):
    """Handle WebSocket errors"""
    sys.stderr.write(f"WebSocket error: {error}\n")
    sys.exit(1)

def on_close(ws, close_status_code, close_msg):
    """Handle WebSocket close"""
    sys.stderr.write("Connection closed\n")
    sys.exit(0)

def on_open(ws):
    """Handle WebSocket open"""
    sys.stderr.write(f"Connected to MCP server: {SERVER_URL}\n")
    
    # Read from stdin and forward to WebSocket
    def read_stdin():
        try:
            for line in sys.stdin:
                if line.strip():
                    ws.send(line.strip())
        except Exception as e:
            sys.stderr.write(f"Error reading stdin: {e}\n")
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

ws.run_forever()
```

**Install dependencies:**
```bash
pip install websocket-client
```

**Configure Cursor:**
```json
{
  "mcpServers": {
    "xcode-mcp-remote": {
      "command": "python3",
      "args": [
        "/path/to/mcp_http_bridge.py"
      ],
      "env": {
        "MCP_SERVER_URL": "http://192.168.4.208:8000",
        "MCP_API_KEY": ""
      }
    }
  }
}
```

## Option 4: Simple HTTP Client (For Testing)

For testing or custom clients, you can use HTTP directly:

### Python Example

```python
import requests

BASE_URL = "http://192.168.4.208:8000"
headers = {"X-API-Key": "your-secret-key"} if API_KEY else {}

# Initialize
response = requests.post(
    f"{BASE_URL}/mcp",
    json={
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "python-client", "version": "1.0.0"}
        },
        "id": "1"
    },
    headers=headers
)
print(response.json())

# List tools
response = requests.post(
    f"{BASE_URL}/mcp",
    json={
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": "2"
    },
    headers=headers
)
print(response.json())
```

## Configuration Summary

### Server Information (Your Device)
- **IP Address:** `192.168.4.208`
- **Port:** `8000`
- **HTTP Endpoint:** `http://192.168.4.208:8000/mcp`
- **WebSocket Endpoint:** `ws://192.168.4.208:8000/ws`
- **Tools Endpoint:** `http://192.168.4.208:8000/tools`
- **Health Endpoint:** `http://192.168.4.208:8000/health`

### Client Configuration (Other Device)

**For Cursor with Bridge:**
```json
{
  "mcpServers": {
    "xcode-mcp-remote": {
      "command": "node",
      "args": ["/path/to/mcp_http_bridge.js"],
      "env": {
        "MCP_SERVER_URL": "http://192.168.4.208:8000"
      }
    }
  }
}
```

## Troubleshooting

### Connection Issues

1. **Check Server is Running:**
   ```bash
   curl http://192.168.4.208:8000/health
   ```

2. **Check Firewall:**
   - Ensure port 8000 is open on the server
   - Check macOS firewall settings

3. **Check Network:**
   - Ensure both devices are on the same network
   - Ping the server: `ping 192.168.4.208`

4. **Check Authentication:**
   - If using API key, ensure it matches on both sides
   - Check `MCP_REQUIRE_AUTH` setting on server

### Common Errors

- **Connection Refused:** Server not running or firewall blocking
- **Timeout:** Network connectivity issue
- **Authentication Failed:** API key mismatch
- **Protocol Error:** Bridge script issue or version mismatch

## Next Steps

1. Start the server on your device: `python run_network_server.py`
2. Create bridge script on client device
3. Configure `~/.cursor/mcp.json` on client device
4. Restart Cursor on client device
5. Test connection

## Notes

- The MCP protocol is primarily designed for stdio, so network connections require a bridge
- WebSocket is recommended for real-time communication
- HTTP can be used for simple request/response patterns
- Consider using authentication in production environments


