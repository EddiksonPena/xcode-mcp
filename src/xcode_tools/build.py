"""Build, archive, and packaging tools for Xcode."""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional


def build_project(project_path: str, scheme: str) -> Dict[str, Any]:
    """Build a project using xcodebuild."""
    try:
        result = subprocess.run(
            [
                "xcodebuild",
                "-project", project_path,
                "-scheme", scheme,
                "build"
            ],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Build timeout (10 minutes)"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def build_workspace(workspace_path: str, scheme: str) -> Dict[str, Any]:
    """Build a workspace and scheme."""
    try:
        result = subprocess.run(
            [
                "xcodebuild",
                "-workspace", workspace_path,
                "-scheme", scheme,
                "build"
            ],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Build timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def clean_build(project_path: Optional[str] = None) -> Dict[str, Any]:
    """Clean build artifacts."""
    cmd = ["xcodebuild", "clean"]
    if project_path:
        if project_path.endswith(".xcworkspace"):
            cmd.extend(["-workspace", project_path])
        else:
            cmd.extend(["-project", project_path])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return {
            "success": result.returncode == 0,
            "output": result.stdout
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def archive_project(scheme: str, archive_path: str) -> Dict[str, Any]:
    """Create an .xcarchive."""
    archive_dir = Path(archive_path)
    archive_dir.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        result = subprocess.run(
            [
                "xcodebuild",
                "archive",
                "-scheme", scheme,
                "-archivePath", archive_path
            ],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        return {
            "success": result.returncode == 0,
            "archive_path": archive_path,
            "output": result.stdout
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_ipa(archive_path: str, export_plist: str, export_path: str) -> Dict[str, Any]:
    """Export .ipa from archive."""
    try:
        result = subprocess.run(
            [
                "xcodebuild",
                "-exportArchive",
                "-archivePath", archive_path,
                "-exportPath", export_path,
                "-exportOptionsPlist", export_plist
            ],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        return {
            "success": result.returncode == 0,
            "export_path": export_path,
            "output": result.stdout
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def analyze_build(project_path: Optional[str] = None) -> Dict[str, Any]:
    """Run static analysis."""
    cmd = ["xcodebuild", "analyze"]
    if project_path:
        if project_path.endswith(".xcworkspace"):
            cmd.extend(["-workspace", project_path])
        else:
            cmd.extend(["-project", project_path])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {
            "success": result.returncode == 0,
            "analysis": result.stdout
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def increment_build_number(project_path: Optional[str] = None) -> Dict[str, Any]:
    """Increment build number automatically using agvtool."""
    try:
        cmd = ["agvtool", "next-version", "-all"]
        if project_path:
            project_dir = Path(project_path).parent
            result = subprocess.run(
                cmd,
                cwd=str(project_dir),
                capture_output=True,
                text=True,
                timeout=30
            )
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Extract new version from output
            new_version = None
            for line in result.stdout.splitlines():
                if "Setting version" in line or "new version" in line.lower():
                    import re
                    match = re.search(r'(\d+)', line)
                    if match:
                        new_version = match.group(1)
            
            return {
                "success": True,
                "new_build_number": new_version,
                "output": result.stdout
            }
        else:
            return {"success": False, "error": result.stderr}
    except FileNotFoundError:
        return {"success": False, "error": "agvtool not found. Install Xcode Command Line Tools."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def increment_version_number(project_path: Optional[str] = None) -> Dict[str, Any]:
    """Increment version number in Info.plist using agvtool."""
    try:
        cmd = ["agvtool", "next-version", "-all"]
        if project_path:
            project_dir = Path(project_path).parent
            result = subprocess.run(
                cmd,
                cwd=str(project_dir),
                capture_output=True,
                text=True,
                timeout=30
            )
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return {
                "success": True,
                "output": result.stdout
            }
        else:
            return {"success": False, "error": result.stderr}
    except FileNotFoundError:
        return {"success": False, "error": "agvtool not found. Install Xcode Command Line Tools."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def set_build_number(project_path: str, build_number: str) -> Dict[str, Any]:
    """Set specific build number."""
    try:
        cmd = ["agvtool", "new-version", "-all", build_number]
        project_dir = Path(project_path).parent
        result = subprocess.run(
            cmd,
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "success": result.returncode == 0,
            "build_number": build_number,
            "output": result.stdout if result.returncode == 0 else result.stderr
        }
    except FileNotFoundError:
        return {"success": False, "error": "agvtool not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def set_version(project_path: str, version: str) -> Dict[str, Any]:
    """Set specific version number."""
    try:
        cmd = ["agvtool", "new-marketing-version", version]
        project_dir = Path(project_path).parent
        result = subprocess.run(
            cmd,
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "success": result.returncode == 0,
            "version": version,
            "output": result.stdout if result.returncode == 0 else result.stderr
        }
    except FileNotFoundError:
        return {"success": False, "error": "agvtool not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def analyze_build_time(project_path: Optional[str] = None) -> Dict[str, Any]:
    """Analyze build duration from build logs."""
    derived_data = Path.home() / "Library" / "Developer" / "Xcode" / "DerivedData"
    
    if not derived_data.exists():
        return {"success": False, "error": "DerivedData not found"}
    
    # Find most recent build log
    log_files = list(derived_data.rglob("*.log"))
    if not log_files:
        return {"success": False, "error": "No build logs found"}
    
    latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
    
    try:
        content = latest_log.read_text()
        import re
        
        # Look for build time patterns
        time_patterns = [
            r'BUILD SUCCEEDED.*?(\d+\.\d+)s',
            r'Total time: (\d+\.\d+)',
            r'Build time: (\d+\.\d+)',
        ]
        
        build_time = None
        for pattern in time_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                build_time = float(match.group(1))
                break
        
        # Count targets built
        target_count = len(re.findall(r'=== BUILD TARGET', content))
        
        return {
            "success": True,
            "build_time_seconds": build_time,
            "targets_built": target_count,
            "log_file": str(latest_log)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def verify_code_signing() -> Dict[str, Any]:
    """Verify provisioning profiles and signing certificates."""
    try:
        result = subprocess.run(
            ["security", "find-identity", "-v", "-p", "codesigning"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        certificates = []
        for line in result.stdout.splitlines():
            if line.strip():
                certificates.append(line.strip())
        
        return {
            "success": True,
            "certificates": certificates
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_xcode_cli() -> Dict[str, Any]:
    """Verify Xcode command-line tools are installed."""
    try:
        result = subprocess.run(
            ["xcodebuild", "-version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        version = result.stdout.strip() if result.returncode == 0 else "Unknown"
        return {
            "success": result.returncode == 0,
            "version": version,
            "installed": result.returncode == 0
        }
    except Exception as e:
        return {"success": False, "error": str(e), "installed": False}

