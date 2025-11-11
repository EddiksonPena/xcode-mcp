"""LangGraph agent for Xcode development with subagentic MCP support."""

import sys
from pathlib import Path
from typing import Any, Dict, List, TypedDict, Annotated, Sequence
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from langgraph.graph import StateGraph, END
    from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage
    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI
    from langchain_ollama import ChatOllama
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    # Create dummy types for when LangGraph is not available
    BaseMessage = object
    StateGraph = object
    END = None
    HumanMessage = object
    AIMessage = object
    ToolMessage = object
    tool = lambda *args, **kwargs: lambda f: f
    ChatOpenAI = object
    ChatOllama = object
    print("⚠️  LangGraph not installed. Install with: pip install langgraph langchain langchain-core langchain-openai langchain-ollama")

from src.tool_registry import get_registry


if LANGGRAPH_AVAILABLE:
    class AgentState(TypedDict):
        """State for the LangGraph agent."""
        messages: Annotated[Sequence[BaseMessage], "add_messages"]
        tool_results: List[Dict[str, Any]]
        current_task: str
        context: Dict[str, Any]
else:
    # Dummy class when LangGraph is not available
    class AgentState(TypedDict):
        """State for the LangGraph agent (dummy when LangGraph not available)."""
        messages: List[Dict[str, Any]]
        tool_results: List[Dict[str, Any]]
        current_task: str
        context: Dict[str, Any]


class XcodeLangGraphAgent:
    """LangGraph agent for Xcode development automation."""
    
    def __init__(self, model: str = "ollama:qwen3-coder:30b", system_prompt: str = None):
        """Initialize the LangGraph agent.
        
        Args:
            model: Model identifier (e.g., 'ollama:qwen3-coder:30b', 'openai:gpt-4')
            system_prompt: Custom system prompt
        """
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph is not installed. Install with: pip install langgraph langchain langchain-core")
        
        self.registry = get_registry()
        self.model = model
        
        # Default system prompt
        default_prompt = """You are an expert iOS and macOS development assistant. 
You have access to 94 Xcode automation tools through the MCP protocol.
Always use the appropriate tools to help developers with their tasks.
Provide clear explanations of what you're doing and why."""
        
        self.system_prompt = system_prompt or default_prompt
        self.llm = self._create_llm()
        self.tools = self._create_tools()
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.graph = self._create_graph()
    
    def _create_llm(self):
        """Create the LLM instance."""
        if ":" in self.model:
            provider, model_name = self.model.split(":", 1)
        else:
            provider = "ollama"
            model_name = self.model
        
        if provider == "ollama":
            return ChatOllama(model=model_name, temperature=0.7)
        elif provider == "openai":
            import os
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set")
            return ChatOpenAI(model=model_name, api_key=api_key, temperature=0.7)
        elif provider == "deepseek":
            import os
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY not set")
            return ChatOpenAI(
                model=model_name,
                base_url="https://api.deepseek.com/v1",
                api_key=api_key,
                temperature=0.7
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _create_tools(self) -> List:
        """Create LangChain tools from MCP tool registry."""
        from langchain_core.tools import tool
        
        tools = []
        
        # Register key tools as examples
        key_tools = [
            "list_projects",
            "check_xcode_cli",
            "list_devices",
            "list_schemes",
            "get_llm_status",
            "build_project",
            "run_tests",
            "boot_simulator",
        ]
        
        for tool_name in key_tools:
            tool_def = self.registry.tools.get(tool_name)
            if tool_def:
                tool_func = self.registry.get_tool_implementation(tool_name)
                if tool_func:
                    # Create LangChain tool wrapper
                    desc = tool_def.get("description", "")
                    
                    # Create a closure to capture tool_name and tool_func
                    def make_tool(name, func, description):
                        @tool
                        def tool_wrapper(**kwargs):
                            """Tool wrapper for MCP tool execution."""
                            result = func(**kwargs)
                            return json.dumps(result.get("result", {}) if isinstance(result, dict) else result, indent=2)
                        tool_wrapper.__name__ = name
                        tool_wrapper.__doc__ = description or f"Execute {name} tool"
                        return tool_wrapper
                    
                    tools.append(make_tool(tool_name, tool_func, desc))
        
        return tools
    
    def _create_graph(self):
        """Create the LangGraph workflow."""
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph is not installed")
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("agent", self._agent_node)
        graph.add_node("tools", self._tools_node)
        
        # Set entry point
        graph.set_entry_point("agent")
        
        # Add edges
        graph.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        graph.add_edge("tools", "agent")
        
        return graph.compile()
    
    def _agent_node(self, state: AgentState) -> AgentState:
        """Agent node that processes messages."""
        messages = state["messages"]
        response = self.llm_with_tools.invoke(messages)
        # Append response to existing messages
        new_messages = list(messages) + [response]
        return {"messages": new_messages}
    
    def _tools_node(self, state: AgentState) -> AgentState:
        """Tools node that executes tool calls."""
        messages = state["messages"]
        last_message = messages[-1]
        
        tool_results = state.get("tool_results", [])
        
        # Check if last message has tool calls
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                tool_name = tool_call.get("name") or tool_call.get("function", {}).get("name", "")
                tool_args = tool_call.get("args") or json.loads(tool_call.get("function", {}).get("arguments", "{}"))
                
                # Find and execute tool
                tool_func = None
                for tool in self.tools:
                    if tool.name == tool_name:
                        # Execute the tool
                        try:
                            result = tool.invoke(tool_args)
                            tool_results.append({
                                "tool": tool_name,
                                "result": result,
                                "success": True
                            })
                            
                            # Add tool message
                            tool_call_id = tool_call.get("id") or f"call_{tool_name}_{len(tool_results)}"
                            messages.append(ToolMessage(
                                content=str(result),
                                tool_call_id=tool_call_id
                            ))
                        except Exception as e:
                            tool_results.append({
                                "tool": tool_name,
                                "result": None,
                                "error": str(e),
                                "success": False
                            })
                        break
        
        return {"messages": messages, "tool_results": tool_results}
    
    def _should_continue(self, state: AgentState) -> str:
        """Determine if we should continue or end."""
        messages = state["messages"]
        if not messages:
            return "end"
        
        last_message = messages[-1]
        
        # Check if last message has tool calls
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
        
        # Also check for function calls (alternative format)
        if hasattr(last_message, "function_calls") and last_message.function_calls:
            return "continue"
        
        return "end"
    
    async def run(self, prompt: str) -> Dict[str, Any]:
        """Run the agent with a prompt.
        
        Args:
            prompt: User prompt or question
            
        Returns:
            Agent response with state
        """
        initial_state = {
            "messages": [HumanMessage(content=prompt)],
            "tool_results": [],
            "current_task": prompt,
            "context": {}
        }
        
        result = await self.graph.ainvoke(initial_state)
        return result
    
    def run_sync(self, prompt: str) -> Dict[str, Any]:
        """Run the agent synchronously.
        
        Args:
            prompt: User prompt or question
            
        Returns:
            Agent response with state
        """
        import asyncio
        return asyncio.run(self.run(prompt))


# Convenience function
def create_langgraph_agent(model: str = "ollama:qwen3-coder:30b", system_prompt: str = None) -> XcodeLangGraphAgent:
    """Create a LangGraph agent for Xcode development.
    
    Args:
        model: Model identifier
        system_prompt: Custom system prompt
        
    Returns:
        XcodeLangGraphAgent instance
    """
    return XcodeLangGraphAgent(model=model, system_prompt=system_prompt)

