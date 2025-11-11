"""Simulator control tools for Xcode."""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional


def list_devices() -> Dict[str, Any]:
    """List all simulators."""
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        devices_data = json.loads(result.stdout)
        devices = []
        
        for runtime, runtime_devices in devices_data.get("devices", {}).items():
            for device in runtime_devices:
                devices.append({
                    "name": device.get("name"),
                    "udid": device.get("udid"),
                    "state": device.get("state"),
                    "runtime": runtime
                })
        
        return {"success": True, "devices": devices}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_device_types() -> Dict[str, Any]:
    """List device types."""
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devicetypes", "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        device_types = json.loads(result.stdout).get("devicetypes", [])
        return {"success": True, "device_types": device_types}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_simulator(device_name: str, runtime: str) -> Dict[str, Any]:
    """Create a new simulator."""
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "create", device_name, runtime],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        udid = result.stdout.strip()
        return {
            "success": result.returncode == 0,
            "udid": udid,
            "name": device_name
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_simulator(udid: str) -> Dict[str, Any]:
    """Delete a simulator."""
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "delete", udid],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {"success": result.returncode == 0}
    except Exception as e:
        return {"success": False, "error": str(e)}


def boot_simulator(device_name: str) -> Dict[str, Any]:
    """Boot a simulator."""
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "boot", device_name],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return {"success": result.returncode == 0, "device": device_name}
    except Exception as e:
        return {"success": False, "error": str(e)}


def shutdown_simulator(device_name: str) -> Dict[str, Any]:
    """Shut down simulator."""
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "shutdown", device_name],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {"success": result.returncode == 0}
    except Exception as e:
        return {"success": False, "error": str(e)}


def erase_simulator(device_name: str) -> Dict[str, Any]:
    """Erase simulator contents."""
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "erase", device_name],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return {"success": result.returncode == 0}
    except Exception as e:
        return {"success": False, "error": str(e)}


def install_app(app_path: str) -> Dict[str, Any]:
    """Install app on simulator."""
    return {
        "success": False,
        "error": "Device UDID required for installation",
        "note": "Use install_app with device_udid parameter"
    }


def uninstall_app(bundle_id: str) -> Dict[str, Any]:
    """Uninstall app from simulator."""
    return {
        "success": False,
        "error": "Device UDID required",
        "note": "Use uninstall_app with device_udid parameter"
    }


def launch_app(bundle_id: str) -> Dict[str, Any]:
    """Launch app on simulator."""
    return {
        "success": False,
        "error": "Device UDID required",
        "note": "Use launch_app with device_udid parameter"
    }


def terminate_app(bundle_id: str) -> Dict[str, Any]:
    """Terminate simulator app."""
    return {
        "success": False,
        "error": "Device UDID required",
        "note": "Use terminate_app with device_udid parameter"
    }


def open_url(url: str) -> Dict[str, Any]:
    """Open URL in simulator Safari."""
    return {
        "success": False,
        "error": "Device UDID required",
        "note": "Use open_url with device_udid parameter"
    }


def record_video(output_path: str) -> Dict[str, Any]:
    """Record simulator screen to .mov."""
    return {
        "success": False,
        "error": "Device UDID required",
        "note": "Use record_video with device_udid parameter"
    }


def screenshot(output_path: str) -> Dict[str, Any]:
    """Capture simulator screenshot."""
    return {
        "success": False,
        "error": "Device UDID required",
        "note": "Use screenshot with device_udid parameter"
    }

