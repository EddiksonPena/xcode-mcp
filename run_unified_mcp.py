#!/usr/bin/env python3
"""Entry point script for unified MCP server."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run
from src.unified_mcp_server import UnifiedMCPServer

if __name__ == "__main__":
    server = UnifiedMCPServer()
    server.run()

