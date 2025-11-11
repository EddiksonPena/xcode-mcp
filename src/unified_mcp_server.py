"""Unified MCP server combining direct tools and LangGraph subagentic capabilities."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, List
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tool_registry import get_registry

# Lazy import for LangGraph (optional)
_langgraph_available = None
_langgraph_agent = None


def _check_langgraph():
    """Check if LangGraph is available."""
    global _langgraph_available
    if _langgraph_available is None:
        try:
            from src.langgraph_agent import create_langgraph_agent
            _langgraph_available = True
        except ImportError:
            _langgraph_available = False
    return _langgraph_available


def _get_langgraph_agent(model: str = "ollama:qwen3-coder:30b"):
    """Get or create LangGraph agent (lazy initialization)."""
    global _langgraph_agent
    if _langgraph_available and _langgraph_agent is None:
        try:
            from src.langgraph_agent import create_langgraph_agent
            _langgraph_agent = create_langgraph_agent(model=model)
        except Exception as e:
            print(f"Warning: Could not create LangGraph agent: {e}", file=sys.stderr)
            return None
    return _langgraph_agent


class UnifiedMCPServer:
    """Unified MCP server with both direct tools and subagentic capabilities."""
    
    def __init__(self):
        """Initialize the unified MCP server."""
        self.registry = get_registry()
        self.initialized = False
        self.langgraph_enabled = _check_langgraph()
        self._tool_cache = {}  # Cache for tool schemas
        self._response_cache = {}  # Cache for responses
        self._cache_ttl = 300  # 5 minutes
    
    def send_response(self, id: Optional[str], result: Any = None, error: Optional[Dict] = None):
        """Send JSON-RPC response with optional compression."""
        response = {
            "jsonrpc": "2.0",
        }
        if id is not None:
            response["id"] = id
        
        if error:
            response["error"] = error
        else:
            response["result"] = result
        
        # Optimize response size
        response_str = json.dumps(response, separators=(',', ':'))  # Compact JSON
        sys.stdout.write(response_str + "\n")
        sys.stdout.flush()
    
    def handle_initialize(self, params: Dict, request_id: str):
        """Handle initialize request."""
        self.initialized = True
        capabilities = {
            "tools": {
                "listChanged": False
            }
        }
        
        if self.langgraph_enabled:
            capabilities["experimental"] = {
                "subagentic": True,
                "workflows": True
            }
        
        self.send_response(request_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": capabilities,
            "serverInfo": {
                "name": "xcode-mcp-unified",
                "version": "2.0.0",
                "features": {
                    "direct_tools": len(self.registry.tools),
                    "langgraph_enabled": self.langgraph_enabled,
                    "subagentic_tools": 3 if self.langgraph_enabled else 0
                }
            }
        })
    
    def _get_tool_schema_enhanced(self, tool_def: Dict[str, Any]) -> Dict[str, Any]:
        """Get enhanced tool schema with detailed descriptions."""
        tool_name = tool_def.get("name")
        
        # Check cache
        cache_key = f"schema_{tool_name}"
        if cache_key in self._tool_cache:
            cached_time, cached_schema = self._tool_cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                return cached_schema
        
        tool_schema = {
            "name": tool_name,
            "description": tool_def.get("description", ""),
        }
        
        # Enhanced parameter schemas
        params = tool_def.get("parameters", [])
        properties = {}
        required = []
        
        for param in params:
            param_name = param.get("name")
            param_type = param.get("type", "string")
            
            # Enhanced property definition
            prop_def = {
                "type": param_type,
                "description": param.get("description", f"{param_name} parameter")
            }
            
            # Add examples based on tool name and parameter
            if param_name == "project_path":
                prop_def["examples"] = ["/path/to/MyApp.xcodeproj", "./MyApp.xcodeproj"]
            elif param_name == "scheme":
                prop_def["examples"] = ["MyApp", "MyAppTests"]
            elif param_name == "device_name":
                prop_def["examples"] = ["iPhone 15 Pro", "iPad Pro"]
            elif param_name == "bundle_id":
                prop_def["examples"] = ["com.example.MyApp"]
            elif param_name == "configuration":
                prop_def["enum"] = ["Debug", "Release"]
            
            properties[param_name] = prop_def
            
            # Mark required if not optional
            if param.get("required", True):
                required.append(param_name)
        
        tool_schema["inputSchema"] = {
            "type": "object",
            "properties": properties
        }
        
        if required:
            tool_schema["inputSchema"]["required"] = required
        
        # Cache the schema
        self._tool_cache[cache_key] = (time.time(), tool_schema)
        
        return tool_schema
    
    def handle_tools_list(self, request_id: str):
        """Handle tools/list request - returns all tools including subagentic."""
        tools = []
        
        # Add all 94 direct tools
        for tool_def in self.registry.list_tools():
            tools.append(self._get_tool_schema_enhanced(tool_def))
        
        # Add LangGraph subagentic tools if available
        if self.langgraph_enabled:
            tools.extend([
                {
                    "name": "langgraph_agent",
                    "description": "LangGraph subagentic agent for complex Xcode development workflows. Handles multi-step tasks, reasoning, and tool orchestration with state management.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Natural language prompt describing the task or question. Be specific about what you want to accomplish.",
                                "minLength": 10,
                                "maxLength": 2000,
                                "examples": [
                                    "List all Xcode projects and check if Xcode CLI is installed",
                                    "Set up my development environment: verify Xcode CLI, list projects, check simulators"
                                ]
                            },
                            "model": {
                                "type": "string",
                                "description": "Optional model override. Format: 'provider:model' (e.g., 'ollama:qwen3-coder:30b', 'deepseek:deepseek-coder')",
                                "default": "ollama:qwen3-coder:30b",
                                "examples": ["ollama:qwen3-coder:30b", "deepseek:deepseek-coder", "openai:gpt-4"]
                            },
                            "persona": {
                                "type": "object",
                                "description": "Optional persona configuration (see persona_schemas.json)",
                                "properties": {
                                    "id": {"type": "string"},
                                    "role": {"type": "string"},
                                    "expertise": {"type": "array", "items": {"type": "string"}}
                                }
                            }
                        },
                        "required": ["prompt"]
                    }
                },
                {
                    "name": "langgraph_workflow",
                    "description": "Execute a multi-step Xcode workflow using LangGraph state machine. Automatically orchestrates multiple tools in sequence.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "workflow": {
                                "type": "string",
                                "description": "Workflow description. List steps clearly (e.g., '1. Clean build, 2. Build project, 3. Run tests, 4. Generate report')",
                                "minLength": 10,
                                "maxLength": 1000,
                                "examples": [
                                    "Build project, run tests, generate report",
                                    "1. Clean build 2. Build MyApp scheme 3. Run all tests 4. Generate coverage report"
                                ]
                            },
                            "context": {
                                "type": "object",
                                "description": "Additional context for the workflow (project paths, scheme names, etc.)",
                                "additionalProperties": True,
                                "examples": [
                                    {"project_path": "/path/to/project.xcodeproj", "scheme": "MyApp"},
                                    {"workspace_path": "/path/to/workspace.xcworkspace"}
                                ]
                            },
                            "persona": {
                                "type": "object",
                                "description": "Optional persona configuration"
                            }
                        },
                        "required": ["workflow"]
                    }
                },
                {
                    "name": "langgraph_status",
                    "description": "Get status of LangGraph agent, available workflows, and system capabilities",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ])
        
        self.send_response(request_id, {"tools": tools})
    
    def handle_tools_call(self, params: Dict, request_id: str):
        """Handle tools/call request - routes to direct tools or LangGraph."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            self.send_response(request_id, None, {
                "code": -32602,
                "message": "Invalid params: tool name required"
            })
            return
        
        # Check if it's a LangGraph tool
        if tool_name.startswith("langgraph_"):
            if not self.langgraph_enabled:
                self.send_response(request_id, None, {
                    "code": -32001,
                    "message": "LangGraph not available. Install with: pip install langgraph langchain"
                })
                return
            
            self._handle_langgraph_tool(tool_name, arguments, request_id)
            return
        
        # Handle direct tool call
        # Check cache first
        cache_key = f"tool_{tool_name}_{json.dumps(arguments, sort_keys=True)}"
        if cache_key in self._response_cache:
            cached_time, cached_result = self._response_cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                self.send_response(request_id, cached_result)
                return
        
        # Execute tool
        result = self.registry.execute_tool(tool_name, **arguments)
        
        if not result.get("success"):
            self.send_response(request_id, None, {
                "code": -32000,
                "message": result.get("error", "Tool execution failed")
            })
            return
        
        response = {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result.get("result", {}), separators=(',', ':'))
                }
            ]
        }
        
        # Cache successful responses
        self._response_cache[cache_key] = (time.time(), response)
        
        self.send_response(request_id, response)
    
    def _handle_langgraph_tool(self, tool_name: str, arguments: Dict, request_id: str):
        """Handle LangGraph subagentic tool calls."""
        try:
            if tool_name == "langgraph_agent":
                prompt = arguments.get("prompt")
                if not prompt:
                    raise ValueError("prompt is required")
                
                model = arguments.get("model", "ollama:qwen3-coder:30b")
                persona_config = arguments.get("persona")
                
                # Create agent with optional persona
                from src.langgraph_agent import create_langgraph_agent
                
                if persona_config:
                    # Apply persona if provided
                    system_prompt = self._build_persona_prompt(persona_config)
                    from src.langgraph_agent import create_langgraph_agent
                    agent = create_langgraph_agent(model=model, system_prompt=system_prompt)
                else:
                    agent = _get_langgraph_agent(model)
                
                if agent is None:
                    raise ValueError("LangGraph agent could not be created")
                
                result = agent.run_sync(prompt)
                
                # Extract final response
                messages = result.get("messages", [])
                final_message = messages[-1] if messages else None
                
                response_text = ""
                if final_message:
                    if hasattr(final_message, "content"):
                        response_text = final_message.content
                    else:
                        response_text = str(final_message)
                
                self.send_response(request_id, {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "response": response_text,
                                "tool_results": result.get("tool_results", []),
                                "messages_count": len(messages),
                                "steps_executed": len(result.get("tool_results", []))
                            }, separators=(',', ':'))
                        }
                    ]
                })
            
            elif tool_name == "langgraph_workflow":
                workflow = arguments.get("workflow")
                if not workflow:
                    raise ValueError("workflow is required")
                
                context = arguments.get("context", {})
                persona_config = arguments.get("persona")
                
                model = "ollama:qwen3-coder:30b"
                from src.langgraph_agent import create_langgraph_agent
                if persona_config:
                    system_prompt = self._build_persona_prompt(persona_config)
                    agent = create_langgraph_agent(model=model, system_prompt=system_prompt)
                else:
                    agent = _get_langgraph_agent(model)
                
                if agent is None:
                    raise ValueError("LangGraph agent could not be created")
                
                # Create workflow prompt
                workflow_prompt = f"""Execute this Xcode development workflow:
{workflow}

Context: {json.dumps(context, separators=(',', ':'))}

Break this down into steps and execute them using the available tools. Provide clear progress updates."""
                
                result = agent.run_sync(workflow_prompt)
                
                self.send_response(request_id, {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "workflow": workflow,
                                "result": result,
                                "steps_executed": len(result.get("tool_results", [])),
                                "success": all(tr.get("success", False) for tr in result.get("tool_results", []))
                            }, separators=(',', ':'))
                        }
                    ]
                })
            
            elif tool_name == "langgraph_status":
                agent = _get_langgraph_agent()
                status = {
                    "agent_type": "LangGraph",
                    "model": agent.model if agent else "not_initialized",
                    "available_tools": len(self.registry.tools),
                    "langgraph_tools": len(agent.tools) if agent else 0,
                    "graph_compiled": agent.graph is not None if agent else False,
                    "capabilities": [
                        "Multi-step task execution",
                        "State management",
                        "Tool orchestration",
                        "Reasoning and planning"
                    ],
                    "langgraph_enabled": self.langgraph_enabled
                }
                
                self.send_response(request_id, {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(status, separators=(',', ':'))
                        }
                    ]
                })
            
            else:
                self.send_response(request_id, None, {
                    "code": -32601,
                    "message": f"Unknown LangGraph tool: {tool_name}"
                })
        
        except Exception as e:
            import traceback
            error_msg = str(e)
            self.send_response(request_id, None, {
                "code": -32000,
                "message": f"Tool execution failed: {error_msg}"
            })
            print(f"LangGraph tool error: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
    
    def _build_persona_prompt(self, persona_config: Dict) -> str:
        """Build system prompt from persona configuration."""
        persona_id = persona_config.get("id", "default")
        role = persona_config.get("role", "generalist")
        expertise = persona_config.get("expertise", [])
        behavior_rules = persona_config.get("behavior_rules", [])
        comm_style = persona_config.get("communication_style", {})
        
        prompt_parts = [
            f"You are a {role} specializing in iOS/macOS development.",
            f"Your expertise areas: {', '.join(expertise) if expertise else 'general iOS development'}."
        ]
        
        if behavior_rules:
            prompt_parts.append("Behavioral guidelines:")
            for rule in behavior_rules:
                prompt_parts.append(f"- {rule}")
        
        if comm_style:
            tone = comm_style.get("tone", "professional")
            verbosity = comm_style.get("verbosity", "moderate")
            prompt_parts.append(f"Communication style: {tone}, {verbosity} detail level.")
        
        prompt_parts.append("Use the available Xcode MCP tools to help developers efficiently.")
        
        return "\n".join(prompt_parts)
    
    def handle_request(self, request: Dict):
        """Handle incoming JSON-RPC request."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "initialize":
            self.handle_initialize(params, request_id)
        elif method == "tools/list":
            if not self.initialized:
                self.send_response(request_id, None, {
                    "code": -32002,
                    "message": "Server not initialized"
                })
                return
            self.handle_tools_list(request_id)
        elif method == "tools/call":
            if not self.initialized:
                self.send_response(request_id, None, {
                    "code": -32002,
                    "message": "Server not initialized"
                })
                return
            self.handle_tools_call(params, request_id)
        elif method == "notifications/initialized":
            pass
        else:
            self.send_response(request_id, None, {
                "code": -32601,
                "message": f"Method not found: {method}"
            })
    
    def run(self):
        """Run the unified MCP stdio server."""
        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    self.handle_request(request)
                except json.JSONDecodeError as e:
                    self.send_response(None, None, {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    })
                except Exception as e:
                    import traceback
                    self.send_response(None, None, {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    })
                    print(f"Error: {e}", file=sys.stderr)
                    traceback.print_exc(file=sys.stderr)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Fatal error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    server = UnifiedMCPServer()
    server.run()

