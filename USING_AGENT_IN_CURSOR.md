# Using LangGraph Agent in Cursor

## ✅ Agent Status: WORKING

The LangGraph agent is fully functional and ready to use in Cursor!

---

## 🚀 Quick Start

### Method 1: Direct Agent Invocation

Simply ask Cursor to use the agent:

```
Use langgraph_agent to check my Xcode development environment
```

```
Use langgraph_agent with prompt "List all my Xcode projects and check if Xcode CLI is installed"
```

### Method 2: Workflow Execution

For multi-step workflows:

```
Use langgraph_workflow to:
1. Clean the build
2. Build my project
3. Run all tests
4. Generate a test report
```

### Method 3: Check Agent Status

```
Use langgraph_status to see what the agent can do
```

---

## 📝 Example Prompts

### Environment Setup
```
Use langgraph_agent to verify my development environment:
- Check Xcode CLI installation
- List available simulators
- Verify LLM service is running
```

### Build & Test
```
Use langgraph_workflow to:
1. Clean previous builds
2. Build the project
3. Run all tests
4. Generate coverage report
```

### Debugging
```
Use langgraph_agent to help me debug this build error:
[paste error message]
```

### Project Management
```
Use langgraph_agent to:
- List all Xcode projects
- Check project schemes
- Verify build configurations
```

---

## 🎯 What the Agent Can Do

The agent has access to **8 key Xcode tools**:
1. `list_projects` - List Xcode projects
2. `check_xcode_cli` - Verify Xcode CLI
3. `list_devices` - List simulators
4. `list_schemes` - List build schemes
5. `get_llm_status` - Check LLM service
6. `build_project` - Build projects
7. `run_tests` - Run tests
8. `boot_simulator` - Boot simulators

The agent can:
- ✅ Execute multiple tools in sequence
- ✅ Reason about which tools to use
- ✅ Maintain context across steps
- ✅ Provide natural language responses
- ✅ Handle errors and retry logic

---

## 🔧 Advanced Usage

### Custom Model

You can specify a different model:

```
Use langgraph_agent with prompt "Check my Xcode setup" and model "ollama:qwen3-coder:30b"
```

### With Persona

Use specialized personas for different tasks:

```
Use langgraph_agent with prompt "Optimize my build settings" and persona "build-optimizer"
```

Available personas:
- `senior-ios-architect` - Architecture decisions
- `swift-mentor` - Learning and guidance
- `build-optimizer` - Build performance
- `test-specialist` - Testing strategies

### Workflow with Context

Provide additional context:

```
Use langgraph_workflow with workflow "Build and test" and context {"project_path": "/path/to/project.xcodeproj", "scheme": "MyApp"}
```

---

## 📊 Agent Capabilities

### What It Does Well
- ✅ Multi-step task execution
- ✅ Tool orchestration
- ✅ Error handling
- ✅ Context management
- ✅ Natural language responses

### Current Limitations
- ⚠️  Has access to 8 tools (can be expanded)
- ⚠️  Requires LLM service (DeepSeek/Ollama/OpenAI)
- ⚠️  May take 10-30 seconds for complex tasks

---

## 🧪 Testing the Agent

### Test Scripts

Run these to verify the agent:

```bash
# Quick test
python test_agent_mcp.py

# Detailed test with full output
python test_agent_detailed.py
```

### Manual Test in Cursor

1. **Open Cursor**
2. **Ask Cursor**:
   ```
   Use langgraph_agent to check if Xcode CLI tools are installed
   ```
3. **Wait for response** (10-30 seconds)
4. **Verify** it executed tools and provided a response

---

## 🐛 Troubleshooting

### Agent Not Responding

1. **Check LangGraph is installed**:
   ```bash
   python -c "import langgraph; print('✅ Installed')"
   ```

2. **Check LLM service**:
   - DeepSeek: Verify `DEEPSEEK_API_KEY` in `mcp.json`
   - Ollama: Ensure Ollama is running locally
   - OpenAI: Verify `OPENAI_API_KEY` is set

3. **Check agent status**:
   ```
   Use langgraph_status
   ```

### Agent Returns Errors

1. **Check tool availability**:
   ```bash
   python -c "from src.tool_registry import get_registry; r = get_registry(); print(len(r.tools))"
   ```
   Should show 115+

2. **Check Xcode CLI**:
   ```bash
   xcodebuild -version
   ```

3. **Review agent logs** in Cursor's MCP panel

### Slow Response Times

- Normal: 10-30 seconds for complex tasks
- If >60 seconds: Check LLM service connection
- Simple tasks: 5-10 seconds

---

## 💡 Best Practices

### 1. Be Specific
❌ "Help me with my project"  
✅ "Use langgraph_agent to list all Xcode projects and check build configurations"

### 2. Break Down Complex Tasks
❌ "Set up my entire development environment"  
✅ "Use langgraph_workflow to: 1. Check Xcode CLI 2. List simulators 3. Verify tools"

### 3. Use Workflows for Multi-Step
For tasks with clear steps, use `langgraph_workflow`:
```
Use langgraph_workflow to:
1. Clean build
2. Build project
3. Run tests
4. Generate report
```

### 4. Check Status First
If unsure, check agent status:
```
Use langgraph_status
```

---

## 🎓 Example Workflows

### Complete Development Setup
```
Use langgraph_agent to set up my development environment:
1. Verify Xcode CLI is installed
2. List all available simulators
3. Check if I have any Xcode projects
4. Verify the LLM service is working
```

### Pre-Release Checklist
```
Use langgraph_workflow to:
1. Increment version number
2. Clean build
3. Build release configuration
4. Run full test suite
5. Generate test coverage report
6. Create git tag
```

### Debug Build Failure
```
Use langgraph_agent to help debug this build error:
[error message]

The agent should:
1. Parse the error
2. Explain what's wrong
3. Suggest fixes
4. Verify the fix works
```

---

## 📈 Performance Tips

1. **Use direct tools for simple tasks** (faster)
2. **Use agent for complex, multi-step tasks** (more intelligent)
3. **Provide context** to reduce agent steps
4. **Use workflows** for predictable sequences

---

## ✅ Verification Checklist

- [x] LangGraph installed
- [x] Agent can be created
- [x] MCP tools registered
- [x] Agent responds to prompts
- [x] Tools are executed correctly
- [x] Natural language responses work

---

## 🚀 Next Steps

1. **Try it in Cursor**: Use the example prompts above
2. **Experiment**: Try different prompts and workflows
3. **Provide feedback**: Let us know what works well
4. **Request features**: Suggest new agent capabilities

---

**The agent is ready to use! Just ask Cursor to use `langgraph_agent` or `langgraph_workflow`.**

---

**Last Updated**: 2025-01-XX  
**Agent Status**: ✅ Fully Operational

