"""Tool registry that dynamically loads tools from JSON schema and maps them to Python functions."""

import json
import re
import importlib
from pathlib import Path
from typing import Dict, Any, Callable, Optional


def load_json_with_comments(file_path: Path) -> Dict[str, Any]:
    """Load JSON file, removing JavaScript-style comments if present."""
    content = file_path.read_text(encoding='utf-8')
    
    # First try loading as regular JSON (for clean files)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    
    # If that fails, try removing comments (for files with comments)
    # Remove single-line comments (// ...)
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
    # Remove multi-line comments (/* ... */)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    # Remove control characters except newlines, tabs, and carriage returns
    content = ''.join(char if char.isprintable() or char in '\n\t\r' else ' ' for char in content)
    return json.loads(content)


class ToolRegistry:
    """Registry that maps tool names to their implementations."""
    
    def __init__(self, schema_path: Optional[Path] = None):
        """Initialize registry and load tool schema."""
        if schema_path is None:
            schema_path = Path(__file__).parent.parent / "schemas" / "xcode-mcp-tools.json"
        
        self.schema_path = schema_path
        self.schema = load_json_with_comments(schema_path)
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.implementations: Dict[str, Callable] = {}
        self._load_tool_definitions()
        self._load_implementations()
    
    def _load_tool_definitions(self):
        """Load tool definitions from JSON schema."""
        for tool_def in self.schema.get("tools", []):
            tool_name = tool_def.get("name")
            if tool_name:
                self.tools[tool_name] = tool_def
    
    def _load_implementations(self):
        """Dynamically import and register tool implementations from xcode_tools modules."""
        try:
            from . import xcode_tools
        except ImportError:
            # Running as script, use absolute import
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent))
            import xcode_tools
        
        tool_modules = [
            xcode_tools.project,
            xcode_tools.build,
            xcode_tools.testing,
            xcode_tools.simulator,
            xcode_tools.device,
            xcode_tools.swift,
            xcode_tools.git_ci,
            xcode_tools.diagnostics,
            xcode_tools.meta,
            xcode_tools.agentic,
            xcode_tools.applescript,
            xcode_tools.llm_config,
            xcode_tools.crash_reporting,
            xcode_tools.assets,
            xcode_tools.simulator_enhanced,
            xcode_tools.localization,
        ]
        
        for module in tool_modules:
            # Register all functions from the module
            for attr_name in dir(module):
                if not attr_name.startswith("_") and attr_name in self.tools:
                    attr = getattr(module, attr_name)
                    if callable(attr):
                        self.implementations[attr_name] = attr
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get schema definition for a tool."""
        return self.tools.get(tool_name)
    
    def get_tool_implementation(self, tool_name: str) -> Optional[Callable]:
        """Get implementation function for a tool."""
        return self.implementations.get(tool_name)
    
    def list_tools(self) -> list[Dict[str, Any]]:
        """List all available tools with their schemas."""
        return list(self.tools.values())
    
    def register_implementation(self, tool_name: str, func: Callable):
        """Manually register a tool implementation."""
        self.implementations[tool_name] = func
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool with given parameters."""
        impl = self.get_tool_implementation(tool_name)
        if impl is None:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not implemented"
            }
        
        try:
            result = impl(**kwargs)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Global registry instance
_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    """Get or create the global tool registry."""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry

