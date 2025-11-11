# Network Setup Guide

This guide explains how to expose the Xcode MCP server to other devices on your network.

## Overview

The MCP server can be exposed over HTTP/WebSocket for network access. This allows:
- Remote access from other devices (laptops, tablets, etc.)
- Integration with web applications
- API access from any programming language
- Real-time communication via WebSocket

## Quick Start

### 1. Start the Network Server

```bash
# Activate conda environment
conda activate xcode-mcp

# Start network server (default: port 8000)
python run_network_server.py
```

Or with custom settings:

```bash
# Custom host and port
MCP_HOST=0.0.0.0 MCP_PORT=8080 python run_network_server.py

# With authentication
MCP_API_KEY=your-secret-key MCP_REQUIRE_AUTH=true python run_network_server.py
```

### 2. Find Your IP Address

```bash
# macOS/Linux
ifconfig | grep 'inet ' | grep -v 127.0.0.1

# Or use
hostname -I  # Linux
ipconfig getifaddr en0  # macOS (WiFi)
ipconfig getifaddr en1  # macOS (Ethernet)
```

### 3. Connect from Other Devices

**HTTP Endpoint:**
```
http://YOUR_IP:8000/mcp
```

**WebSocket Endpoint:**
```
ws://YOUR_IP:8000/ws
```

**Tools List:**
```
http://YOUR_IP:8000/tools
```

**Health Check:**
```
http://YOUR_IP:8000/health
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_HOST` | `0.0.0.0` | Bind address (0.0.0.0 = all interfaces) |
| `MCP_PORT` | `8000` | Server port |
| `MCP_API_KEY` | (empty) | API key for authentication |
| `MCP_REQUIRE_AUTH` | `false` | Require API key (true/false) |
| `MCP_ALLOWED_ORIGINS` | `*` | CORS allowed origins (comma-separated) |

### Example Configuration

Create a `.env` file or export variables:

```bash
export MCP_HOST=0.0.0.0
export MCP_PORT=8000
export MCP_API_KEY=my-secret-key-123
export MCP_REQUIRE_AUTH=true
export MCP_ALLOWED_ORIGINS=http://localhost:3000,https://myapp.com
```

## Authentication

### Without Authentication (Development)

```bash
# No API key required
python run_network_server.py
```

### With API Key (Production)

```bash
# Set API key
export MCP_API_KEY=your-secret-key
export MCP_REQUIRE_AUTH=true

# Start server
python run_network_server.py
```

**HTTP Request with API Key:**
```bash
curl -X POST http://YOUR_IP:8000/mcp \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": "1"
  }'
```

**WebSocket with API Key:**
```
ws://YOUR_IP:8000/ws?api_key=your-secret-key
```

## API Usage Examples

### 1. Initialize Server

```bash
curl -X POST http://YOUR_IP:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "my-client",
        "version": "1.0.0"
      }
    },
    "id": "1"
  }'
```

### 2. List Tools

```bash
curl -X POST http://YOUR_IP:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": "2"
  }'
```

### 3. Call a Tool

```bash
curl -X POST http://YOUR_IP:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "list_projects",
      "arguments": {}
    },
    "id": "3"
  }'
```

### 4. Python Client Example

```python
import requests
import json

BASE_URL = "http://YOUR_IP:8000"

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
    headers={"X-API-Key": "your-secret-key"}  # If auth enabled
)

# List tools
response = requests.post(
    f"{BASE_URL}/mcp",
    json={
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": "2"
    }
)

tools = response.json()["result"]["tools"]
print(f"Available tools: {len(tools)}")

# Call a tool
response = requests.post(
    f"{BASE_URL}/mcp",
    json={
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "list_projects",
            "arguments": {}
        },
        "id": "3"
    }
)

result = response.json()["result"]
print(result)
```

### 5. JavaScript/WebSocket Example

```javascript
const ws = new WebSocket('ws://YOUR_IP:8000/ws?api_key=your-secret-key');

ws.onopen = () => {
  console.log('Connected to MCP server');
  
  // Initialize
  ws.send(JSON.stringify({
    jsonrpc: "2.0",
    method: "initialize",
    params: {
      protocolVersion: "2024-11-05",
      capabilities: {},
      clientInfo: { name: "js-client", version: "1.0.0" }
    },
    id: "1"
  }));
};

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log('Response:', response);
  
  if (response.id === "1") {
    // Initialize complete, list tools
    ws.send(JSON.stringify({
      jsonrpc: "2.0",
      method: "tools/list",
      id: "2"
    }));
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

## Direct Endpoints

### List All Tools (REST)

```bash
curl http://YOUR_IP:8000/tools
```

Returns:
```json
{
  "tools": [...],
  "count": 97,
  "direct_tools": 94,
  "langgraph_tools": 3
}
```

### Health Check

```bash
curl http://YOUR_IP:8000/health
```

Returns:
```json
{
  "status": "healthy",
  "tools_loaded": 94,
  "langgraph_enabled": true,
  "initialized": true
}
```

## Security Considerations

1. **Use Authentication in Production**
   - Always set `MCP_REQUIRE_AUTH=true` for production
   - Use a strong, random API key
   - Rotate keys regularly

2. **Firewall Configuration**
   - Only expose necessary ports
   - Consider using a reverse proxy (nginx, Caddy)
   - Use HTTPS/WSS in production (via reverse proxy)

3. **Network Isolation**
   - Consider VPN for remote access
   - Use private networks when possible
   - Monitor access logs

4. **Rate Limiting**
   - Consider adding rate limiting middleware
   - Monitor for abuse

## Troubleshooting

### Server Won't Start

```bash
# Check if port is in use
lsof -i :8000

# Try different port
MCP_PORT=8080 python run_network_server.py
```

### Can't Connect from Other Device

1. **Check Firewall:**
   ```bash
   # macOS - allow incoming connections
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /path/to/python
   ```

2. **Check IP Address:**
   - Ensure you're using the correct IP
   - Try `ping YOUR_IP` from the other device

3. **Check Network:**
   - Ensure both devices are on the same network
   - Check router settings

### CORS Issues

If accessing from a web browser, set allowed origins:

```bash
export MCP_ALLOWED_ORIGINS=http://localhost:3000,https://myapp.com
python run_network_server.py
```

## Production Deployment

### Using systemd (Linux)

Create `/etc/systemd/system/xcode-mcp.service`:

```ini
[Unit]
Description=Xcode MCP Network Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/xcode-mcp
Environment="PATH=/path/to/conda/envs/xcode-mcp/bin"
Environment="MCP_HOST=0.0.0.0"
Environment="MCP_PORT=8000"
Environment="MCP_API_KEY=your-secret-key"
Environment="MCP_REQUIRE_AUTH=true"
ExecStart=/path/to/conda/envs/xcode-mcp/bin/python run_network_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable xcode-mcp
sudo systemctl start xcode-mcp
sudo systemctl status xcode-mcp
```

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM continuumio/miniconda3

WORKDIR /app
COPY . .

RUN conda env create -f environment.yml
SHELL ["conda", "run", "-n", "xcode-mcp", "/bin/bash", "-c"]

EXPOSE 8000

CMD ["conda", "run", "-n", "xcode-mcp", "python", "run_network_server.py"]
```

Build and run:
```bash
docker build -t xcode-mcp .
docker run -p 8000:8000 \
  -e MCP_API_KEY=your-secret-key \
  -e MCP_REQUIRE_AUTH=true \
  xcode-mcp
```

## Next Steps

- See [README.md](../README.md) for full tool documentation
- See [LANGGRAPH_GUIDE.md](LANGGRAPH_GUIDE.md) for LangGraph workflows
- See [AGENT_GUIDE.md](AGENT_GUIDE.md) for agent usage


