# Quick Client Setup Guide

## For Another Device to Connect to Your MCP Server

### Server Information
- **IP Address:** `192.168.4.208`
- **Port:** `8000`
- **Server URL:** `http://192.168.4.208:8000`

### Step 1: Copy Bridge Script to Client Device

Copy one of these files to the client device:
- `mcp_http_bridge.js` (Node.js version)
- `mcp_http_bridge.py` (Python version)

### Step 2: Install Dependencies on Client Device

**For Node.js bridge:**
```bash
npm install ws
```

**For Python bridge:**
```bash
pip install websocket-client
```

### Step 3: Configure Cursor on Client Device

Edit `~/.cursor/mcp.json` on the client device:

**For Node.js bridge:**
```json
{
  "mcpServers": {
    "xcode-mcp-remote": {
      "command": "node",
      "args": [
        "/absolute/path/to/mcp_http_bridge.js"
      ],
      "env": {
        "MCP_SERVER_URL": "http://192.168.4.208:8000",
        "MCP_API_KEY": ""
      }
    }
  }
}
```

**For Python bridge:**
```json
{
  "mcpServers": {
    "xcode-mcp-remote": {
      "command": "python3",
      "args": [
        "/absolute/path/to/mcp_http_bridge.py"
      ],
      "env": {
        "MCP_SERVER_URL": "http://192.168.4.208:8000",
        "MCP_API_KEY": ""
      }
    }
  }
}
```

**With Authentication (if enabled on server):**
```json
{
  "mcpServers": {
    "xcode-mcp-remote": {
      "command": "node",
      "args": [
        "/absolute/path/to/mcp_http_bridge.js"
      ],
      "env": {
        "MCP_SERVER_URL": "http://192.168.4.208:8000",
        "MCP_API_KEY": "your-secret-key"
      }
    }
  }
}
```

### Step 4: Restart Cursor

Restart Cursor on the client device to load the new configuration.

### Step 5: Verify Connection

The MCP server should appear in Cursor's MCP panel. You should see:
- Server name: `xcode-mcp-remote`
- Status: Green/Connected
- Tools: 97 tools available

## Troubleshooting

1. **Check server is running:**
   ```bash
   curl http://192.168.4.208:8000/health
   ```

2. **Check bridge script path is absolute** (not relative)

3. **Check dependencies are installed:**
   - Node.js: `npm list ws`
   - Python: `pip list | grep websocket`

4. **Check network connectivity:**
   ```bash
   ping 192.168.4.208
   ```

5. **Check firewall** on server device allows port 8000

## Full Documentation

See `docs/CLIENT_CONFIGURATION.md` for complete details.
