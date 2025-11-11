"""Swift and CLI utility tools."""

import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


def run_swift_package_build() -> Dict[str, Any]:
    """Build Swift Package Manager project."""
    try:
        result = subprocess.run(
            ["swift", "build"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_swift_package_test() -> Dict[str, Any]:
    """Run SwiftPM tests."""
    try:
        result = subprocess.run(
            ["swift", "test"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_swift_script(file_path: str) -> Dict[str, Any]:
    """Execute a .swift script."""
    path = Path(file_path)
    if not path.exists():
        return {"success": False, "error": f"File not found: {file_path}"}
    
    try:
        result = subprocess.run(
            ["swift", str(path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def compile_swift_file(file_path: str) -> Dict[str, Any]:
    """Compile a standalone Swift file."""
    path = Path(file_path)
    if not path.exists():
        return {"success": False, "error": f"File not found: {file_path}"}
    
    output_path = path.with_suffix("")
    
    try:
        result = subprocess.run(
            ["swiftc", str(path), "-o", str(output_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return {
            "success": result.returncode == 0,
            "output": str(output_path),
            "stderr": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_docs() -> Dict[str, Any]:
    """Generate documentation via DocC or Jazzy."""
    try:
        # Try DocC first
        result = subprocess.run(
            ["swift", "package", "generate-documentation"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            return {"success": True, "method": "DocC", "output": result.stdout}
    except Exception:
        pass
    
    # Fallback to Jazzy
    try:
        result = subprocess.run(
            ["jazzy"],
            capture_output=True,
            text=True,
            timeout=300
        )
        return {"success": result.returncode == 0, "method": "Jazzy", "output": result.stdout}
    except FileNotFoundError:
        return {"success": False, "error": "DocC or Jazzy not available"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_swift_lint() -> Dict[str, Any]:
    """Run SwiftLint CLI."""
    try:
        result = subprocess.run(
            ["swiftlint"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout
        }
    except FileNotFoundError:
        return {"success": False, "error": "SwiftLint not installed"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def swift_package_dependencies() -> Dict[str, Any]:
    """List SPM dependencies."""
    try:
        result = subprocess.run(
            ["swift", "package", "show-dependencies", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        import json
        deps = json.loads(result.stdout) if result.returncode == 0 else {}
        
        return {
            "success": result.returncode == 0,
            "dependencies": deps
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

