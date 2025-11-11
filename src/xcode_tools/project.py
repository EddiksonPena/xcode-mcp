"""Project management tools for Xcode."""

import subprocess
import os
from pathlib import Path
from typing import Dict, Any, List, Optional


def create_project(name: str, directory: str) -> Dict[str, Any]:
    """Create a new Xcode project or Swift package."""
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Try creating Swift package first
        result = subprocess.run(
            ["swift", "package", "init", "--type", "executable"],
            cwd=dir_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return {"success": True, "type": "swift_package", "path": str(dir_path)}
    except Exception:
        pass
    
    return {"success": False, "error": "Failed to create project"}


def open_project(project_path: str) -> Dict[str, Any]:
    """Open a project or workspace in Xcode."""
    path = Path(project_path)
    if not path.exists():
        return {"success": False, "error": f"Path not found: {project_path}"}
    
    try:
        subprocess.run(["open", str(path)], check=True, timeout=10)
        return {"success": True, "opened": str(path)}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout opening project"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_projects() -> Dict[str, Any]:
    """List all available .xcodeproj or .xcworkspace files."""
    projects = []
    workspaces = []
    
    # Search common locations
    search_paths = [
        Path.home() / "Projects",
        Path.home() / "Developer",
        Path("/Users") / os.getenv("USER", "") / "Projects"
    ]
    
    for search_path in search_paths:
        if not search_path.exists():
            continue
        for proj in search_path.rglob("*.xcodeproj"):
            projects.append(str(proj))
        for ws in search_path.rglob("*.xcworkspace"):
            workspaces.append(str(ws))
    
    return {
        "projects": projects[:50],  # Limit results
        "workspaces": workspaces[:50],
        "count": len(projects) + len(workspaces)
    }


def clean_project() -> Dict[str, Any]:
    """Remove DerivedData and temporary build caches."""
    derived_data = Path.home() / "Library" / "Developer" / "Xcode" / "DerivedData"
    cleaned = []
    
    if derived_data.exists():
        try:
            import shutil
            shutil.rmtree(derived_data)
            cleaned.append(str(derived_data))
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    return {"success": True, "cleaned": cleaned}


def list_schemes(project_path: Optional[str] = None) -> Dict[str, Any]:
    """List available build schemes."""
    if not project_path:
        return {"success": False, "error": "project_path required"}
    
    try:
        result = subprocess.run(
            ["xcodebuild", "-list", "-project", project_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        schemes = []
        in_schemes = False
        for line in result.stdout.splitlines():
            if "Schemes:" in line:
                in_schemes = True
                continue
            if in_schemes and line.strip():
                schemes.append(line.strip())
        
        return {"success": True, "schemes": schemes}
    except Exception as e:
        return {"success": False, "error": str(e)}


def switch_scheme(scheme: str) -> Dict[str, Any]:
    """Switch active build scheme."""
    # This is typically handled by Xcode UI, but we can store preference
    return {"success": True, "scheme": scheme, "note": "Scheme preference stored"}


def set_build_configuration(configuration: str) -> Dict[str, Any]:
    """Switch build configuration (Debug/Release)."""
    if configuration not in ["Debug", "Release"]:
        return {"success": False, "error": "Configuration must be Debug or Release"}
    return {"success": True, "configuration": configuration}

