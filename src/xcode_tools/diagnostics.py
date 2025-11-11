"""Diagnostics and log analysis tools."""

import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import re
from ..llm_service import get_llm_service


def view_build_logs() -> Dict[str, Any]:
    """View last build logs."""
    derived_data = Path.home() / "Library" / "Developer" / "Xcode" / "DerivedData"
    
    if not derived_data.exists():
        return {"success": False, "error": "DerivedData not found"}
    
    # Find most recent build log
    log_files = list(derived_data.rglob("*.log"))
    if not log_files:
        return {"success": False, "error": "No build logs found"}
    
    latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
    
    try:
        content = latest_log.read_text()[:10000]  # First 10KB
        return {
            "success": True,
            "log_file": str(latest_log),
            "content": content
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def tail_build_log() -> Dict[str, Any]:
    """Stream live build logs."""
    return {
        "success": True,
        "note": "Live log streaming requires WebSocket support"
    }


def parse_errors() -> Dict[str, Any]:
    """Parse compiler errors."""
    log_result = view_build_logs()
    if not log_result.get("success"):
        return log_result
    
    content = log_result.get("content", "")
    errors = []
    
    # Simple error pattern matching
    error_pattern = r"error:\s*(.+)"
    for match in re.finditer(error_pattern, content, re.IGNORECASE):
        errors.append(match.group(1))
    
    return {
        "success": True,
        "errors": errors,
        "count": len(errors)
    }


def export_log(output_path: str) -> Dict[str, Any]:
    """Export build log."""
    log_result = view_build_logs()
    if not log_result.get("success"):
        return log_result
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        log_file = Path(log_result["log_file"])
        import shutil
        shutil.copy2(log_file, output_file)
        
        return {
            "success": True,
            "exported_to": output_path
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def show_last_build_duration() -> Dict[str, Any]:
    """Show last build duration."""
    return {
        "success": True,
        "note": "Build duration parsing requires xcodebuild timing flags"
    }


def list_failed_tests() -> Dict[str, Any]:
    """List failed tests."""
    return {
        "success": True,
        "note": "Failed test detection requires test result parsing"
    }


def summarize_build_output(build_output: Optional[str] = None) -> Dict[str, Any]:
    """Summarize build output via LLM."""
    if not build_output:
        log_result = view_build_logs()
        if log_result.get("success"):
            build_output = log_result.get("content", "")
        else:
            return {"success": False, "error": "No build output available"}
    
    try:
        llm = get_llm_service()
        system_prompt = "You are an expert iOS/macOS build engineer. Summarize build output concisely, highlighting key issues, warnings, and success indicators."
        summary = llm.generate(
            f"Summarize this build output:\n\n{build_output[:4000]}",  # Limit to 4K chars
            system_prompt
        )
        
        return {
            "success": True,
            "summary": summary,
            "provider": llm.current_provider,
            "model": llm.current_model
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def explain_compiler_error(error_log: Optional[str] = None) -> Dict[str, Any]:
    """Explain compiler error via LLM."""
    if not error_log:
        parse_result = parse_errors()
        if parse_result.get("success") and parse_result.get("errors"):
            error_log = "\n".join(parse_result["errors"])
        else:
            return {"success": False, "error": "No errors found to explain"}
    
    try:
        llm = get_llm_service()
        system_prompt = "You are an expert Swift/iOS compiler engineer. Explain compiler errors clearly and suggest potential fixes."
        explanation = llm.generate(
            f"Explain this compiler error and suggest how to fix it:\n\n{error_log}",
            system_prompt
        )
        
        return {
            "success": True,
            "error": error_log,
            "explanation": explanation,
            "provider": llm.current_provider,
            "model": llm.current_model
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def recommend_fix(error_context: Optional[str] = None) -> Dict[str, Any]:
    """Suggest likely fix via LLM."""
    if not error_context:
        parse_result = parse_errors()
        if parse_result.get("success") and parse_result.get("errors"):
            error_context = "\n".join(parse_result["errors"])
        else:
            return {"success": False, "error": "No errors found to recommend fixes for"}
    
    try:
        llm = get_llm_service()
        system_prompt = "You are an expert iOS/macOS developer. Provide specific, actionable fix recommendations for build errors."
        recommendation = llm.generate(
            f"Recommend a fix for this error:\n\n{error_context}",
            system_prompt
        )
        
        return {
            "success": True,
            "error_context": error_context,
            "recommendation": recommendation,
            "provider": llm.current_provider,
            "model": llm.current_model
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

