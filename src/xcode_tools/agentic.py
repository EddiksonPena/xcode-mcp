"""Agentic AI and reasoning tools for Xcode MCP."""

from typing import Dict, Any, Optional
from ..llm_service import get_llm_service


def suggest_tests_for_code(code: Optional[str] = None, language: str = "swift") -> Dict[str, Any]:
    """Suggest tests for given code."""
    if not code:
        return {"success": False, "error": "Code is required"}
    
    try:
        llm = get_llm_service()
        system_prompt = f"You are an expert {language} test engineer. Generate comprehensive unit tests for the provided code."
        suggestions = llm.generate(
            f"Suggest unit tests for this {language} code:\n\n{code}",
            system_prompt
        )
        
        return {
            "success": True,
            "suggestions": suggestions,
            "provider": llm.current_provider,
            "model": llm.current_model
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def analyze_performance_profile(profile_path: Optional[str] = None) -> Dict[str, Any]:
    """Summarize Instruments performance logs."""
    if not profile_path:
        return {"success": False, "error": "Profile path required"}
    
    from pathlib import Path
    profile_file = Path(profile_path)
    if not profile_file.exists():
        return {"success": False, "error": f"Profile file not found: {profile_path}"}
    
    try:
        # Read profile content (simplified - real implementation would parse Instruments format)
        content = profile_file.read_text()[:4000]  # Limit size
        
        llm = get_llm_service()
        system_prompt = "You are a performance analysis expert. Analyze Instruments performance profiles and identify bottlenecks."
        analysis = llm.generate(
            f"Analyze this performance profile and identify bottlenecks:\n\n{content}",
            system_prompt
        )
        
        return {
            "success": True,
            "analysis": analysis,
            "provider": llm.current_provider,
            "model": llm.current_model
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def explain_build_failure(build_log: Optional[str] = None) -> Dict[str, Any]:
    """Summarize build failure causes."""
    if not build_log:
        from .diagnostics import view_build_logs
        log_result = view_build_logs()
        if log_result.get("success"):
            build_log = log_result.get("content", "")
        else:
            return {"success": False, "error": "No build log available"}
    
    try:
        llm = get_llm_service()
        system_prompt = "You are an expert build engineer. Analyze build failures and identify root causes."
        explanation = llm.generate(
            f"Explain why this build failed and identify the root cause:\n\n{build_log[:4000]}",
            system_prompt
        )
        
        return {
            "success": True,
            "explanation": explanation,
            "provider": llm.current_provider,
            "model": llm.current_model
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def recommend_next_action(context: Optional[str] = None) -> Dict[str, Any]:
    """Suggest next command or fix."""
    if not context:
        context = "No specific context provided. Suggest general next steps for iOS development."
    
    try:
        llm = get_llm_service()
        system_prompt = "You are an expert iOS/macOS development assistant. Suggest the next logical action based on context."
        recommendation = llm.generate(
            f"Based on this context, what should be the next action?\n\n{context}",
            system_prompt
        )
        
        return {
            "success": True,
            "recommendation": recommendation,
            "provider": llm.current_provider,
            "model": llm.current_model
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def memory_summarize_recent_activity() -> Dict[str, Any]:
    """Store and recall recent build/test summaries."""
    return {
        "success": True,
        "note": "Memory storage requires database integration (Mem0, ChromaDB, etc.)",
        "hint": "Consider implementing with ChromaDB or Mem0 for persistent memory"
    }

