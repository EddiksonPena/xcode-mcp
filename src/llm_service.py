"""LLM service supporting multiple providers (Ollama, DeepSeek, OpenAI-compatible)."""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum
import requests


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OLLAMA = "ollama"
    DEEPSEEK = "deepseek"
    OPENAI = "openai"


class LLMService:
    """Unified LLM service with provider abstraction."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize LLM service with configuration."""
        if config_path is None:
            config_path = Path.home() / ".xcode-mcp" / "llm_config.json"
        
        self.config_path = config_path
        self.config = self._load_config()
        self.current_provider = self.config.get("provider", "ollama")
        self.current_model = self.config.get("model", "qwen3-coder:30b")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load LLM configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    default_config = self._get_default_config()
                    default_config.update(config)
                    return default_config
            except Exception:
                pass
        
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "provider": "ollama",
            "model": "qwen3-coder:30b",
            "ollama": {
                "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            },
            "deepseek": {
                "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
                "base_url": "https://api.deepseek.com/v1"
            },
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "base_url": "https://api.openai.com/v1"
            }
        }
    
    def _save_config(self):
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)
    
    def set_provider(self, provider: str, model: Optional[str] = None):
        """Switch LLM provider and optionally model."""
        if provider not in [p.value for p in LLMProvider]:
            raise ValueError(f"Unsupported provider: {provider}")
        
        self.current_provider = provider
        if model:
            self.current_model = model
        
        self.config["provider"] = provider
        self.config["model"] = self.current_model
        self._save_config()
    
    def get_available_models(self, provider: Optional[str] = None) -> List[str]:
        """Get list of available models for a provider."""
        provider = provider or self.current_provider
        
        if provider == LLMProvider.OLLAMA.value:
            try:
                import ollama
                models = ollama.list()
                return [model["name"] for model in models.get("models", [])]
            except Exception:
                return ["qwen3-coder:30b", "qwen2.5-coder:32b", "llama3.2", "llama3.1", "mistral", "codellama"]
        
        elif provider == LLMProvider.DEEPSEEK.value:
            return [
                "deepseek-chat",
                "deepseek-coder",
                "deepseek-reasoner"
            ]
        
        elif provider == LLMProvider.OPENAI.value:
            return [
                "gpt-4",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
                "gpt-4o"
            ]
        
        return []
    
    def _call_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call Ollama API."""
        try:
            import ollama
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = ollama.chat(
                model=self.current_model,
                messages=messages
            )
            
            return response["message"]["content"]
        except ImportError:
            # Fallback to HTTP API
            base_url = self.config.get("ollama", {}).get("base_url", "http://localhost:11434")
            url = f"{base_url}/api/chat"
            
            payload = {
                "model": self.current_model,
                "messages": [
                    {"role": "system", "content": system_prompt or "You are a helpful coding assistant."},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            }
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()["message"]["content"]
    
    def _call_deepseek(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call DeepSeek API."""
        api_key = self.config.get("deepseek", {}).get("api_key") or os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DeepSeek API key not configured. Set DEEPSEEK_API_KEY environment variable.")
        
        base_url = self.config.get("deepseek", {}).get("base_url", "https://api.deepseek.com/v1")
        url = f"{base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.current_model,
            "messages": messages,
            "temperature": 0.7
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    
    def _call_openai(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call OpenAI-compatible API."""
        try:
            from openai import OpenAI
            
            api_key = self.config.get("openai", {}).get("api_key") or os.getenv("OPENAI_API_KEY")
            base_url = self.config.get("openai", {}).get("base_url", "https://api.openai.com/v1")
            
            client = OpenAI(api_key=api_key, base_url=base_url)
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.current_model,
                messages=messages,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except ImportError:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using current provider."""
        if self.current_provider == LLMProvider.OLLAMA.value:
            return self._call_ollama(prompt, system_prompt)
        elif self.current_provider == LLMProvider.DEEPSEEK.value:
            return self._call_deepseek(prompt, system_prompt)
        elif self.current_provider == LLMProvider.OPENAI.value:
            return self._call_openai(prompt, system_prompt)
        else:
            raise ValueError(f"Unknown provider: {self.current_provider}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current LLM service status."""
        return {
            "provider": self.current_provider,
            "model": self.current_model,
            "available_models": self.get_available_models(),
            "config_path": str(self.config_path)
        }


# Global LLM service instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create the global LLM service."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

