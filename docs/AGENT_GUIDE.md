# PydanticAI Agent Guide for Xcode MCP

This guide explains how to use the PydanticAI agent with the Xcode MCP tools.

## Overview

The PydanticAI agent provides a natural language interface to all 94 Xcode MCP tools. It uses structured schemas (Pydantic models) to ensure type-safe tool calls and responses.

## Installation

```bash
conda activate xcode-mcp
pip install pydantic-ai
```

## Quick Start

```python
from src.pydantic_ai_agent import create_xcode_agent

# Create agent with default persona
agent = create_xcode_agent(model="ollama:qwen3-coder:30b")

# Run a task
result = agent.run_sync("List all available Xcode projects")
print(result.data)
```

## Available Models

### Ollama (Local)
```python
agent = create_xcode_agent(model="ollama:qwen3-coder:30b")
```

### DeepSeek (Cloud)
```python
# Set DEEPSEEK_API_KEY environment variable first
agent = create_xcode_agent(model="deepseek:deepseek-coder")
```

### OpenAI (Cloud)
```python
# Set OPENAI_API_KEY environment variable first
agent = create_xcode_agent(model="openai:gpt-4")
```

## Custom Persona

You can customize the agent's persona:

```python
custom_prompt = """You are a senior iOS architect specializing in:
- Clean architecture and SOLID principles
- Performance optimization
- Test-driven development

Always suggest best practices and explain your reasoning."""

agent = create_xcode_agent(
    model="ollama:qwen3-coder:30b",
    system_prompt=custom_prompt
)
```

## Example Use Cases

### 1. Project Management
```python
# List projects
result = agent.run_sync("Show me all Xcode projects")

# Open a project
result = agent.run_sync("Open the project at /path/to/MyApp.xcodeproj")

# List schemes
result = agent.run_sync("What build schemes are available?")
```

### 2. Build & Testing
```python
# Build a project
result = agent.run_sync("Build the MyApp scheme in Debug configuration")

# Run tests
result = agent.run_sync("Run all tests for the MyAppTests scheme")

# Check build status
result = agent.run_sync("What was the last build duration?")
```

### 3. Simulator Management
```python
# List simulators
result = agent.run_sync("Show me all available iOS simulators")

# Boot a simulator
result = agent.run_sync("Boot the iPhone 15 Pro simulator")

# Install app
result = agent.run_sync("Install MyApp.app on the booted simulator")
```

### 4. Debugging & Analysis
```python
# Explain build error
result = agent.run_sync("""
I got this build error:
[error message here]

Can you explain what's wrong and suggest a fix?
""")

# Analyze performance
result = agent.run_sync("Analyze the Instruments trace at /path/to/trace.trace")
```

### 5. Complex Workflows
```python
# Multi-step task
result = agent.run_sync("""
I need to:
1. Clean the build
2. Build the project
3. Run all tests
4. Generate a test report

Please execute these steps and report the results.
""")
```

## Structured Responses

The agent uses Pydantic models for structured responses. See `src/agent_schemas.py` for all available schemas:

- `ProjectInfo` - Project information
- `SchemeInfo` - Build scheme details
- `DeviceInfo` - Simulator/device information
- `BuildInfo` - Build results
- `TestResult` - Test execution results
- `LLMStatus` - LLM service status

## Tool Schemas

All 94 tools have detailed schemas with:
- Parameter descriptions
- Type validation
- Example values
- Required vs optional fields

See `src/agent_schemas.py` for complete schema definitions.

## Error Handling

```python
try:
    result = agent.run_sync("Build the project")
    if result.data.get("success"):
        print("✅ Build succeeded")
    else:
        print(f"❌ Build failed: {result.data.get('error')}")
except Exception as e:
    print(f"Error: {e}")
```

## Async Usage

For async applications:

```python
import asyncio

async def main():
    agent = create_xcode_agent()
    result = await agent.run("List all projects")
    print(result.data)

asyncio.run(main())
```

## Available Tools

The agent has access to all 94 Xcode MCP tools:

- **Project Management**: create_project, open_project, list_projects, etc.
- **Build & Archive**: build_project, archive_project, export_ipa, etc.
- **Testing**: run_tests, run_ui_tests, generate_test_report, etc.
- **Simulator**: list_devices, boot_simulator, install_app, etc.
- **Device Management**: list_connected_devices, pair_device, etc.
- **Swift Tools**: run_swift_script, compile_swift_file, etc.
- **Git & CI/CD**: git_status, git_commit, trigger_ci_build, etc.
- **LLM Tools**: set_llm_provider, get_llm_status, etc.
- **Agentic AI**: suggest_tests_for_code, explain_build_failure, etc.

## Best Practices

1. **Be Specific**: Provide clear, specific instructions
2. **Use Context**: Reference previous results in follow-up questions
3. **Check Results**: Always verify tool execution results
4. **Handle Errors**: Implement proper error handling
5. **Use Structured Queries**: Leverage the agent's understanding of schemas

## Troubleshooting

### Agent not responding
- Check that the LLM service is running (Ollama) or API keys are set
- Verify the model name is correct
- Check agent logs for errors

### Tools not working
- Ensure Xcode command-line tools are installed
- Verify project paths are correct
- Check file permissions

### Import errors
- Make sure you're in the conda environment: `conda activate xcode-mcp`
- Verify all dependencies are installed: `pip install -r requirements.txt`

## Next Steps

- See `examples/agent_example.py` for more examples
- Check `src/agent_schemas.py` for all available schemas
- Review `src/pydantic_ai_agent.py` for agent implementation details

