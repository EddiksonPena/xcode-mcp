"""Entry point for running MCP server as module."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import and run unified server
from src.unified_mcp_server import UnifiedMCPServer

if __name__ == "__main__":
    server = UnifiedMCPServer()
    server.run()

