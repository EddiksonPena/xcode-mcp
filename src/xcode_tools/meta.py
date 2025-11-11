"""Meta and utility tools for MCP server."""

import subprocess
import platform
import sys
from pathlib import Path
from typing import Dict, Any
import shutil


def help() -> Dict[str, Any]:
    """List all available tools."""
    from tool_registry import get_registry
    registry = get_registry()
    tools = registry.list_tools()
    
    tool_names = [tool["name"] for tool in tools]
    return {
        "success": True,
        "tools": tool_names,
        "count": len(tool_names)
    }


def version() -> Dict[str, Any]:
    """Show MCP + Xcode version."""
    try:
        xcode_result = subprocess.run(
            ["xcodebuild", "-version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        xcode_version = xcode_result.stdout.strip() if xcode_result.returncode == 0 else "Unknown"
    except Exception:
        xcode_version = "Unknown"
    
    return {
        "success": True,
        "mcp_version": "1.0.0",
        "xcode_version": xcode_version,
        "python_version": sys.version,
        "platform": platform.system()
    }


def update_mcp() -> Dict[str, Any]:
    """Update MCP server."""
    return {
        "success": True,
        "note": "Update via: git pull && conda env update"
    }


def cleanup_temp_files() -> Dict[str, Any]:
    """Remove temporary build/log files."""
    temp_paths = [
        Path.home() / "Library" / "Developer" / "Xcode" / "DerivedData",
        Path("/tmp") / "xcodebuild-*.log"
    ]
    
    cleaned = []
    for temp_path in temp_paths:
        if temp_path.exists():
            try:
                if temp_path.is_dir():
                    shutil.rmtree(temp_path)
                else:
                    temp_path.unlink()
                cleaned.append(str(temp_path))
            except Exception:
                pass
    
    return {
        "success": True,
        "cleaned": cleaned
    }


def restart_core_services() -> Dict[str, Any]:
    """Restart Xcode daemons."""
    try:
        # Kill Xcode processes
        subprocess.run(["killall", "Xcode"], capture_output=True, timeout=10)
        subprocess.run(["killall", "com.apple.CoreSimulator.CoreSimulatorService"], capture_output=True, timeout=10)
        
        return {
            "success": True,
            "note": "Xcode services restarted"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def ping() -> Dict[str, Any]:
    """Health check for MCP."""
    return {
        "success": True,
        "status": "pong",
        "service": "Xcode MCP Server"
    }


def whoami() -> Dict[str, Any]:
    """Display MCP host info."""
    import getpass
    import socket
    
    return {
        "success": True,
        "hostname": socket.gethostname(),
        "user": getpass.getuser(),
        "platform": platform.system(),
        "platform_version": platform.version()
    }

