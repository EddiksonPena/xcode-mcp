# LangGraph Subagentic MCP Guide

This guide explains how to use the LangGraph agent as a subagentic MCP server for complex Xcode development workflows.

## Overview

The LangGraph MCP server provides a stateful, multi-step agent that can:
- Execute complex workflows with multiple tool calls
- Maintain context across steps
- Reason about task decomposition
- Orchestrate multiple Xcode tools in sequence

## Architecture

```
┌─────────────────────────────────┐
│   Cursor / MCP Client           │
└──────────────┬──────────────────┘
               │
               │ MCP Protocol (JSON-RPC)
               │
┌──────────────▼──────────────────┐
│   LangGraph MCP Server           │
│   (xcode-langgraph-mcp)          │
└──────────────┬──────────────────┘
               │
               │ Tool Calls
               │
┌──────────────▼──────────────────┐
│   Xcode MCP Tools (94 tools)     │
│   - list_projects                │
│   - build_project                │
│   - run_tests                    │
│   - ...                          │
└──────────────────────────────────┘
```

## Installation

```bash
conda activate xcode-mcp
pip install langgraph langchain langchain-core langchain-openai langchain-ollama
```

## MCP Configuration

The LangGraph MCP server is already configured in `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "xcode-langgraph-mcp": {
      "command": "bash",
      "args": [
        "-c",
        "cd /path/to/xcode-mcp && conda activate xcode-mcp && python run_langgraph_mcp.py"
      ],
      "env": {
        "DEEPSEEK_API_KEY": "your-key"
      }
    }
  }
}
```

## Available Tools

The LangGraph MCP server exposes 3 tools:

### 1. `langgraph_agent`
Execute a natural language prompt with the LangGraph agent.

**Parameters:**
- `prompt` (required): Natural language task description
- `model` (optional): Model override (default: "ollama:qwen3-coder:30b")

**Example:**
```json
{
  "name": "langgraph_agent",
  "arguments": {
    "prompt": "List all Xcode projects and check if Xcode CLI is installed"
  }
}
```

### 2. `langgraph_workflow`
Execute a multi-step workflow using LangGraph state machine.

**Parameters:**
- `workflow` (required): Workflow description
- `context` (optional): Additional context object

**Example:**
```json
{
  "name": "langgraph_workflow",
  "arguments": {
    "workflow": "Build project, run tests, generate report",
    "context": {
      "project_path": "/path/to/project.xcodeproj",
      "scheme": "MyApp"
    }
  }
}
```

### 3. `langgraph_status`
Get status of the LangGraph agent.

**Example:**
```json
{
  "name": "langgraph_status",
  "arguments": {}
}
```

## Usage in Cursor

### Basic Usage

Ask Cursor to use the LangGraph agent:

```
Use the langgraph_agent tool to help me set up my iOS development environment
```

### Multi-Step Workflows

```
Use langgraph_workflow to:
1. Clean the build
2. Build the project
3. Run all tests
4. Generate a test report
```

### Complex Reasoning

```
I need to debug a build failure. Use langgraph_agent to:
1. Analyze the build logs
2. Identify the error
3. Suggest a fix
4. Verify the fix works
```

## LangGraph Workflow

The agent uses a state machine with these nodes:

1. **Agent Node**: Processes user input and decides on actions
2. **Tools Node**: Executes tool calls
3. **Conditional Edges**: Routes based on whether tools are needed

### State Structure

```python
class AgentState(TypedDict):
    messages: Sequence[BaseMessage]  # Conversation history
    tool_results: List[Dict]         # Tool execution results
    current_task: str                 # Current task description
    context: Dict[str, Any]           # Additional context
```

## Example Workflows

### 1. Project Setup Verification

```python
from src.langgraph_agent import create_langgraph_agent

agent = create_langgraph_agent()

result = agent.run_sync("""
Verify my Xcode development environment:
1. Check Xcode CLI installation
2. List available projects
3. Check simulator availability
4. Verify LLM service is running
""")
```

### 2. Build and Test Pipeline

```python
result = agent.run_sync("""
Execute a complete build and test pipeline:
1. Clean previous builds
2. Build the project
3. Run all tests
4. Generate test coverage report
5. Summarize results
""")
```

### 3. Debug Workflow

```python
result = agent.run_sync("""
I'm getting a build error. Help me:
1. Parse the error from build logs
2. Explain what's wrong
3. Suggest a fix
4. Verify the fix
""")
```

## Integration with Main MCP

The LangGraph MCP server works alongside the main `xcode-mcp` server:

- **xcode-mcp**: Direct tool access (94 tools)
- **xcode-langgraph-mcp**: Subagentic workflows (3 tools that orchestrate the 94)

You can use both in Cursor:
- Use `xcode-mcp` for direct, single tool calls
- Use `xcode-langgraph-mcp` for complex, multi-step workflows

## Advanced Features

### Custom Workflows

Create custom LangGraph workflows:

```python
from src.langgraph_agent import XcodeLangGraphAgent

agent = XcodeLangGraphAgent(
    model="deepseek:deepseek-coder",
    system_prompt="You are a senior iOS architect..."
)

# Custom workflow
result = agent.run_sync("Your custom workflow here")
```

### State Inspection

Inspect the agent state:

```python
result = agent.run_sync("List projects")

# Access state
messages = result["messages"]
tool_results = result["tool_results"]
context = result["context"]
```

### Error Handling

```python
try:
    result = agent.run_sync("Complex workflow")
    if result.get("tool_results"):
        print("✅ Workflow completed")
    else:
        print("⚠️  No tools were called")
except Exception as e:
    print(f"❌ Error: {e}")
```

## Best Practices

1. **Use LangGraph for Complex Tasks**: Multi-step workflows benefit from state management
2. **Use Direct MCP for Simple Tasks**: Single tool calls are faster via `xcode-mcp`
3. **Provide Context**: Include relevant information in your prompts
4. **Monitor State**: Check `tool_results` to verify execution
5. **Handle Errors**: Implement proper error handling for production use

## Troubleshooting

### Agent not responding
- Check that LangGraph is installed: `pip list | grep langgraph`
- Verify the model is accessible (Ollama running, API keys set)
- Check MCP server logs

### Tools not executing
- Verify `xcode-mcp` server is running (LangGraph depends on it)
- Check tool registry is loaded correctly
- Review agent state for errors

### State issues
- Clear state between unrelated workflows
- Use context to maintain information across steps
- Check message history for debugging

## Next Steps

- See `examples/langgraph_example.py` for more examples
- Review `src/langgraph_agent.py` for implementation details
- Check `src/langgraph_mcp_server.py` for MCP server code

