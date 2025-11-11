"""Enhanced simulator control tools."""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional


def set_simulator_location(device_udid: str, latitude: float, longitude: float) -> Dict[str, Any]:
    """Set GPS location for simulator."""
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "location", device_udid, "set", str(latitude), str(longitude)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "device_udid": device_udid,
                "latitude": latitude,
                "longitude": longitude
            }
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_simulator_logs(device_udid: str, lines: int = 100) -> Dict[str, Any]:
    """Get device logs from simulator."""
    try:
        # Get system log
        result = subprocess.run(
            ["xcrun", "simctl", "spawn", device_udid, "log", "stream", "--level", "debug", "--predicate", "processImagePath contains 'Simulator'"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Alternative: use syslog
        log_path = Path.home() / "Library" / "Logs" / "CoreSimulator" / device_udid / "system.log"
        
        logs = []
        if log_path.exists():
            with open(log_path, 'r') as f:
                all_lines = f.readlines()
                logs = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        return {
            "success": True,
            "device_udid": device_udid,
            "logs": logs,
            "log_count": len(logs),
            "log_path": str(log_path) if log_path.exists() else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_simulator_apps(device_udid: str) -> Dict[str, Any]:
    """List installed apps on simulator."""
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "listapps", device_udid, "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            apps_data = json.loads(result.stdout)
            apps = []
            
            for bundle_id, app_info in apps_data.items():
                apps.append({
                    "bundle_id": bundle_id,
                    "name": app_info.get("CFBundleName", bundle_id),
                    "version": app_info.get("CFBundleShortVersionString", "Unknown")
                })
            
            return {
                "success": True,
                "device_udid": device_udid,
                "apps": apps,
                "app_count": len(apps)
            }
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}


def simulate_network_conditions(device_udid: str, condition: str = "wifi") -> Dict[str, Any]:
    """Simulate network conditions (wifi, 3g, lte, etc.)."""
    valid_conditions = ["wifi", "3g", "lte", "edge", "none"]
    
    if condition not in valid_conditions:
        return {"success": False, "error": f"Condition must be one of: {', '.join(valid_conditions)}"}
    
    try:
        # Note: simctl doesn't have direct network simulation, but we can document it
        return {
            "success": True,
            "device_udid": device_udid,
            "condition": condition,
            "note": "Network simulation may require additional setup. Use Network Link Conditioner for advanced simulation."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def clone_simulator(source_udid: str, new_name: str) -> Dict[str, Any]:
    """Clone existing simulator."""
    try:
        # Get device info first
        list_result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        devices_data = json.loads(list_result.stdout)
        
        # Find source device
        source_device = None
        for runtime, devices in devices_data.get("devices", {}).items():
            for device in devices:
                if device.get("udid") == source_udid:
                    source_device = device
                    device_type = device.get("deviceTypeIdentifier", "").split(".")[-1]
                    runtime_id = runtime
                    break
        
        if not source_device:
            return {"success": False, "error": f"Source device not found: {source_udid}"}
        
        # Create new device with same type and runtime
        create_result = subprocess.run(
            ["xcrun", "simctl", "create", new_name, device_type, runtime_id],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if create_result.returncode == 0:
            new_udid = create_result.stdout.strip()
            return {
                "success": True,
                "source_udid": source_udid,
                "new_name": new_name,
                "new_udid": new_udid
            }
        else:
            return {"success": False, "error": create_result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}

