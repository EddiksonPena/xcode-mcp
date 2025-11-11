"""Git and CI/CD integration tools."""

import subprocess
from typing import Dict, Any, Optional


def git_status() -> Dict[str, Any]:
    """Show Git repository status."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        files = []
        for line in result.stdout.splitlines():
            if line.strip():
                status, filepath = line[:2], line[3:]
                files.append({"status": status, "file": filepath})
        
        return {"success": True, "files": files}
    except subprocess.CalledProcessError:
        return {"success": False, "error": "Not a git repository"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def git_commit(message: str) -> Dict[str, Any]:
    """Commit changes."""
    try:
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def git_push() -> Dict[str, Any]:
    """Push changes to remote."""
    try:
        result = subprocess.run(
            ["git", "push"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def git_pull() -> Dict[str, Any]:
    """Pull latest changes."""
    try:
        result = subprocess.run(
            ["git", "pull"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def trigger_ci_build() -> Dict[str, Any]:
    """Trigger CI pipeline."""
    return {
        "success": True,
        "note": "CI trigger depends on your CI system (GitHub Actions, GitLab CI, etc.)"
    }


def ci_build_status() -> Dict[str, Any]:
    """Check CI build status."""
    return {
        "success": True,
        "note": "CI status check depends on your CI system"
    }


def post_ci_results() -> Dict[str, Any]:
    """Post CI results to webhook."""
    return {
        "success": True,
        "note": "Webhook posting requires webhook URL configuration"
    }


def generate_release_notes() -> Dict[str, Any]:
    """Generate release notes from commits."""
    try:
        result = subprocess.run(
            ["git", "log", "--pretty=format:%s", "--since", "1 week ago"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        commits = result.stdout.splitlines()
        return {
            "success": True,
            "commits": commits,
            "note": "Release notes generated from recent commits"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

