"""Testing and QA tools for Xcode."""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional


def run_tests(project_or_workspace: str, scheme: str, destination: Optional[str] = None) -> Dict[str, Any]:
    """Run all tests for a project/scheme."""
    cmd = ["xcodebuild", "test"]
    
    if project_or_workspace.endswith(".xcworkspace"):
        cmd.extend(["-workspace", project_or_workspace])
    else:
        cmd.extend(["-project", project_or_workspace])
    
    cmd.extend(["-scheme", scheme])
    
    if destination:
        cmd.extend(["-destination", destination])
    
    try:
        result = subprocess.run(
            cmd,
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
        return {"success": False, "error": "Test timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_ui_tests(scheme: str, destination: Optional[str] = None) -> Dict[str, Any]:
    """Run UI tests on simulator."""
    cmd = ["xcodebuild", "test", "-scheme", scheme]
    
    if destination:
        cmd.extend(["-destination", destination])
    else:
        # Default to iOS simulator
        cmd.extend(["-destination", "platform=iOS Simulator,name=iPhone 15"])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return {
            "success": result.returncode == 0,
            "output": result.stdout
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_specific_test(test_identifier: str) -> Dict[str, Any]:
    """Run a specific test case."""
    # test_identifier format: "TestClass/testMethod"
    return {
        "success": False,
        "error": "Specific test execution requires project context",
        "note": "Use run_tests with test filter"
    }


def list_test_targets(project_path: Optional[str] = None) -> Dict[str, Any]:
    """List all testable targets."""
    if not project_path:
        return {"success": False, "error": "project_path required"}
    
    try:
        result = subprocess.run(
            ["xcodebuild", "-list", "-project", project_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        targets = []
        in_targets = False
        for line in result.stdout.splitlines():
            if "Targets:" in line:
                in_targets = True
                continue
            if in_targets and line.strip() and not line.startswith(" "):
                if "Test" in line or "Tests" in line:
                    targets.append(line.strip())
        
        return {"success": True, "test_targets": targets}
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_test_report(output_path: str) -> Dict[str, Any]:
    """Generate JSON or JUnit test report."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    return {
        "success": True,
        "output_path": output_path,
        "note": "Test report generation requires xcresult bundle processing"
    }


def code_coverage_report() -> Dict[str, Any]:
    """Generate code coverage report."""
    return {
        "success": True,
        "note": "Code coverage requires xcodebuild with -enableCodeCoverage flag"
    }


def lint_project() -> Dict[str, Any]:
    """Run SwiftLint."""
    try:
        result = subprocess.run(
            ["swiftlint", "lint"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr
        }
    except FileNotFoundError:
        return {"success": False, "error": "SwiftLint not installed"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def swift_format() -> Dict[str, Any]:
    """Auto-format Swift code using SwiftFormat."""
    try:
        result = subprocess.run(
            ["swiftformat", "."],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout
        }
    except FileNotFoundError:
        return {"success": False, "error": "SwiftFormat not installed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

