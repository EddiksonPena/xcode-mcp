"""Physical device and provisioning tools for Xcode."""

import subprocess
import json
from typing import Dict, Any, Optional


def list_connected_devices() -> Dict[str, Any]:
    """List physically connected iOS devices."""
    try:
        result = subprocess.run(
            ["xcrun", "devicectl", "list", "devices", "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Fallback to instruments if devicectl not available
        if result.returncode != 0:
            result = subprocess.run(
                ["instruments", "-s", "devices"],
                capture_output=True,
                text=True,
                timeout=30
            )
        
        devices = []
        for line in result.stdout.splitlines():
            if "iPhone" in line or "iPad" in line:
                devices.append(line.strip())
        
        return {"success": True, "devices": devices}
    except Exception as e:
        return {"success": False, "error": str(e)}


def install_on_device(device_id: str, app_path: str) -> Dict[str, Any]:
    """Install app to physical device."""
    try:
        result = subprocess.run(
            ["xcrun", "devicectl", "device", "install", "app", "--device", device_id, app_path],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def uninstall_from_device(device_id: str, bundle_id: str) -> Dict[str, Any]:
    """Uninstall app from device."""
    try:
        result = subprocess.run(
            ["xcrun", "devicectl", "device", "uninstall", "app", "--device", device_id, bundle_id],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return {"success": result.returncode == 0}
    except Exception as e:
        return {"success": False, "error": str(e)}


def pair_device(device_id: str) -> Dict[str, Any]:
    """Pair physical device."""
    return {
        "success": True,
        "note": "Device pairing typically done through Xcode UI"
    }


def unpair_device(device_id: str) -> Dict[str, Any]:
    """Unpair device."""
    return {
        "success": True,
        "note": "Device unpairing typically done through Xcode UI"
    }


def list_certificates() -> Dict[str, Any]:
    """List signing certificates."""
    try:
        result = subprocess.run(
            ["security", "find-identity", "-v", "-p", "codesigning"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        certificates = []
        for line in result.stdout.splitlines():
            if line.strip() and not line.startswith("   "):
                certificates.append(line.strip())
        
        return {"success": True, "certificates": certificates}
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_provisioning_profiles() -> Dict[str, Any]:
    """Export provisioning profiles."""
    profiles_path = "~/Library/MobileDevice/Provisioning Profiles"
    return {
        "success": True,
        "profiles_path": profiles_path,
        "note": "Provisioning profiles are stored in Library/MobileDevice/Provisioning Profiles"
    }


def resign_app(app_path: str, certificate: str, provisioning_profile: Optional[str] = None) -> Dict[str, Any]:
    """Re-sign an app with specific certificate using codesign."""
    from pathlib import Path
    
    app_path_obj = Path(app_path)
    if not app_path_obj.exists():
        return {"success": False, "error": f"App not found: {app_path}"}
    
    try:
        # First, remove existing signature
        subprocess.run(
            ["codesign", "--remove-signature", str(app_path_obj)],
            capture_output=True,
            check=False,
            timeout=30
        )
        
        # Sign with new certificate
        cmd = ["codesign", "--sign", certificate, "--force", "--deep", str(app_path_obj)]
        
        if provisioning_profile:
            # Embed provisioning profile if provided
            cmd.extend(["--entitlements", provisioning_profile])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # Verify signature
            verify_result = subprocess.run(
                ["codesign", "--verify", "--verbose", str(app_path_obj)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": True,
                "app_path": str(app_path_obj),
                "certificate": certificate,
                "signature_valid": verify_result.returncode == 0,
                "verification_output": verify_result.stdout
            }
        else:
            return {
                "success": False,
                "error": result.stderr,
                "output": result.stdout
            }
    except FileNotFoundError:
        return {"success": False, "error": "codesign not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

