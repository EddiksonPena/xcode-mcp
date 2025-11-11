"""AppleScript and macOS automation tools for Xcode."""

import subprocess
from typing import Dict, Any, Optional


def open_xcode() -> Dict[str, Any]:
    """Launch Xcode app."""
    try:
        subprocess.run(["open", "-a", "Xcode"], check=True, timeout=10)
        return {"success": True, "action": "Xcode launched"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout launching Xcode"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def close_xcode() -> Dict[str, Any]:
    """Quit Xcode."""
    try:
        subprocess.run(["osascript", "-e", 'tell application "Xcode" to quit'], check=True, timeout=10)
        return {"success": True, "action": "Xcode closed"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_new_file(file_name: str) -> Dict[str, Any]:
    """Create a new Swift file in Xcode."""
    script = f'''
    tell application "Xcode"
        activate
        tell application "System Events"
            keystroke "n" using {{command down, shift down}}
            delay 0.5
            keystroke "{file_name}"
            keystroke return
        end tell
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", script], check=True, timeout=10)
        return {"success": True, "file": file_name}
    except Exception as e:
        return {"success": False, "error": str(e)}


def open_recent_project() -> Dict[str, Any]:
    """Open a recent project."""
    script = '''
    tell application "Xcode"
        activate
        tell application "System Events"
            keystroke "o" using command down
        end tell
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", script], check=True, timeout=10)
        return {"success": True, "action": "Recent projects dialog opened"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def trigger_build_button() -> Dict[str, Any]:
    """Simulate clicking Xcode's build button."""
    script = '''
    tell application "Xcode"
        activate
        tell application "System Events"
            keystroke "b" using command down
        end tell
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", script], check=True, timeout=10)
        return {"success": True, "action": "Build triggered"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def show_debug_area() -> Dict[str, Any]:
    """Toggle Debug area visibility."""
    script = '''
    tell application "Xcode"
        activate
        tell application "System Events"
            keystroke "y" using {command down, shift down}
        end tell
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", script], check=True, timeout=10)
        return {"success": True, "action": "Debug area toggled"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def open_preferences() -> Dict[str, Any]:
    """Open Xcode preferences."""
    script = '''
    tell application "Xcode"
        activate
        tell application "System Events"
            keystroke "," using command down
        end tell
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", script], check=True, timeout=10)
        return {"success": True, "action": "Preferences opened"}
    except Exception as e:
        return {"success": False, "error": str(e)}

