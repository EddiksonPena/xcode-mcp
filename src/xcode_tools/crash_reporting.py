"""Crash reporting and symbolication tools."""

import subprocess
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional


def symbolicate_crash_log(crash_path: str, dSYM_path: Optional[str] = None, app_path: Optional[str] = None) -> Dict[str, Any]:
    """Symbolicate crash log using atos or symbolicatecrash."""
    crash_file = Path(crash_path)
    if not crash_file.exists():
        return {"success": False, "error": f"Crash log not found: {crash_path}"}
    
    try:
        # Try using symbolicatecrash first (more comprehensive)
        symbolicate_script = Path("/Applications/Xcode.app/Contents/SharedFrameworks/DVTFoundation.framework/Versions/A/Resources/symbolicatecrash")
        
        if symbolicate_script.exists():
            cmd = [str(symbolicate_script), str(crash_file)]
            if dSYM_path:
                cmd.extend(["-d", dSYM_path])
            if app_path:
                cmd.extend(["-o", app_path])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                env={"DEVELOPER_DIR": "/Applications/Xcode.app/Contents/Developer"}
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "symbolicated_log": result.stdout,
                    "method": "symbolicatecrash"
                }
        
        # Fallback to atos for basic symbolication
        crash_content = crash_file.read_text()
        
        # Extract addresses and binary names
        address_pattern = r'(\w+)\s+(\w+)\s+(0x[0-9a-fA-F]+)'
        matches = re.findall(address_pattern, crash_content)
        
        if matches and dSYM_path:
            symbolicated_lines = []
            for match in matches[:10]:  # Limit to first 10 for performance
                binary_name, _, address = match
                try:
                    atos_result = subprocess.run(
                        ["atos", "-o", dSYM_path, "-l", address],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if atos_result.returncode == 0:
                        symbolicated_lines.append(atos_result.stdout.strip())
                except Exception:
                    pass
            
            return {
                "success": True,
                "symbolicated_lines": symbolicated_lines,
                "method": "atos",
                "note": "Partial symbolication. Use symbolicatecrash for full symbolication."
            }
        
        return {
            "success": False,
            "error": "Could not symbolicate. dSYM path required for atos method."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def analyze_crash_log(crash_path: str) -> Dict[str, Any]:
    """Analyze crash log and extract key information."""
    crash_file = Path(crash_path)
    if not crash_file.exists():
        return {"success": False, "error": f"Crash log not found: {crash_path}"}
    
    try:
        content = crash_file.read_text()
        
        # Extract crash information
        crash_info = {
            "exception_type": None,
            "exception_message": None,
            "crashed_thread": None,
            "binary_images": [],
            "threads": []
        }
        
        # Find exception type
        exception_match = re.search(r'Exception Type:\s*(.+)', content)
        if exception_match:
            crash_info["exception_type"] = exception_match.group(1).strip()
        
        # Find exception message
        message_match = re.search(r'Exception Message:\s*(.+)', content)
        if message_match:
            crash_info["exception_message"] = message_match.group(1).strip()
        
        # Find crashed thread
        thread_match = re.search(r'Crashed Thread:\s*(\d+)', content)
        if thread_match:
            crash_info["crashed_thread"] = int(thread_match.group(1))
        
        # Extract binary images
        binary_section = False
        for line in content.splitlines():
            if "Binary Images:" in line:
                binary_section = True
                continue
            if binary_section and line.strip():
                if re.match(r'0x[0-9a-fA-F]+\s+', line):
                    crash_info["binary_images"].append(line.strip())
        
        # Count threads
        thread_count = len(re.findall(r'Thread \d+:', content))
        crash_info["thread_count"] = thread_count
        
        return {
            "success": True,
            "crash_info": crash_info,
            "summary": {
                "exception": crash_info["exception_type"],
                "crashed_thread": crash_info["crashed_thread"],
                "total_threads": thread_count
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_crash_reports(device_id: Optional[str] = None) -> Dict[str, Any]:
    """Get crash reports from device or simulator."""
    try:
        if device_id:
            # Get crashes from specific device
            result = subprocess.run(
                ["xcrun", "devicectl", "device", "diagnose", "crashes", "--device", device_id],
                capture_output=True,
                text=True,
                timeout=60
            )
        else:
            # Get crashes from default location
            crash_dir = Path.home() / "Library" / "Logs" / "DiagnosticReports"
            crashes = []
            
            if crash_dir.exists():
                for crash_file in crash_dir.glob("*.crash"):
                    crashes.append({
                        "path": str(crash_file),
                        "name": crash_file.name,
                        "modified": crash_file.stat().st_mtime
                    })
                
                crashes.sort(key=lambda x: x["modified"], reverse=True)
            
            return {
                "success": True,
                "crashes": crashes[:20],  # Limit to 20 most recent
                "count": len(crashes)
            }
        
        if result.returncode == 0:
            return {
                "success": True,
                "output": result.stdout
            }
        else:
            return {"success": False, "error": result.stderr}
    except FileNotFoundError:
        # Fallback to manual directory scan
        crash_dir = Path.home() / "Library" / "Logs" / "DiagnosticReports"
        crashes = []
        
        if crash_dir.exists():
            for crash_file in crash_dir.glob("*.crash"):
                crashes.append({
                    "path": str(crash_file),
                    "name": crash_file.name
                })
        
        return {
            "success": True,
            "crashes": crashes[:20],
            "count": len(crashes),
            "note": "Using directory scan method"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_crash_log(crash_path: str, output_path: str) -> Dict[str, Any]:
    """Export crash log to specified location."""
    crash_file = Path(crash_path)
    if not crash_file.exists():
        return {"success": False, "error": f"Crash log not found: {crash_path}"}
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        import shutil
        shutil.copy2(crash_file, output_file)
        
        return {
            "success": True,
            "exported_to": str(output_file),
            "size_bytes": output_file.stat().st_size
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

