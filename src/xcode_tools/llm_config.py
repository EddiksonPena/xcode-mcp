"""LLM configuration and management tools."""

from typing import Dict, Any, Optional
from ..llm_service import get_llm_service, LLMProvider


def set_llm_provider(provider: str, model: Optional[str] = None) -> Dict[str, Any]:
    """Switch LLM provider and optionally model."""
    try:
        llm = get_llm_service()
        llm.set_provider(provider, model)
        return {
            "success": True,
            "provider": provider,
            "model": llm.current_model,
            "message": f"Switched to {provider} with model {llm.current_model}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_llm_models(provider: Optional[str] = None) -> Dict[str, Any]:
    """List available models for a provider."""
    try:
        llm = get_llm_service()
        models = llm.get_available_models(provider)
        return {
            "success": True,
            "provider": provider or llm.current_provider,
            "models": models
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_llm_status() -> Dict[str, Any]:
    """Get current LLM service status."""
    try:
        llm = get_llm_service()
        return {
            "success": True,
            **llm.get_status()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def test_llm_connection() -> Dict[str, Any]:
    """Test LLM connection with a simple prompt."""
    try:
        llm = get_llm_service()
        response = llm.generate("Say 'Hello' if you can read this.", "You are a test assistant.")
        return {
            "success": True,
            "provider": llm.current_provider,
            "model": llm.current_model,
            "response": response[:100]  # First 100 chars
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "hint": "Check your API keys and network connection"
        }

