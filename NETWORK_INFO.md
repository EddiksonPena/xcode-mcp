# Network Connection Information

## Your Device Information

### IP Addresses

  - 192.168.4.208 (inet)
  - 169.254.181.98 (inet)

## Connection URLs

### HTTP Endpoints
  - http://192.168.4.208:8000/mcp
  - http://192.168.4.208:8000/tools
  - http://192.168.4.208:8000/health
  - http://169.254.181.98:8000/mcp
  - http://169.254.181.98:8000/tools
  - http://169.254.181.98:8000/health

### WebSocket Endpoints
  - ws://192.168.4.208:8000/ws
  - ws://169.254.181.98:8000/ws

## Quick Start

1. Start the server:
   ```bash
   conda activate xcode-mcp
   python run_network_server.py
   ```

2. From another device, use one of the URLs above

## Default Port: 8000

To change the port:
   ```bash
   MCP_PORT=8080 python run_network_server.py
   ```

## Network Interfaces

  - lo0:
  - gif0:
  - stf0:
  - anpi0:
  - anpi1:
  - anpi4:
  - anpi2:
  - anpi3:
  - anpi5:
  - en8:

## Firewall Check

If you can't connect, check macOS firewall:
  - System Settings > Network > Firewall
  - Allow incoming connections for Python


## Test Connection

Test from another device:
  ```bash
  # Test HTTP endpoint
  curl http://192.168.4.208:8000/health

  # Test tools list
  curl http://192.168.4.208:8000/tools

  # Test HTTP endpoint
  curl http://169.254.181.98:8000/health

  # Test tools list
  curl http://169.254.181.98:8000/tools

  ```

## Python Client Example

  ```python
  import requests
  BASE_URL = "http://192.168.4.208:8000"
  
  # Health check
  response = requests.get(f"{BASE_URL}/health")
  print(response.json())
  
  # List tools
  response = requests.get(f"{BASE_URL}/tools")
  print(f"Available tools: {response.json()['count']}")
  ```
