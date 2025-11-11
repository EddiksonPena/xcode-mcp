# Testing the Agent in Cursor - Quick Guide

## ✅ Agent is Working!

The LangGraph agent has been tested and is fully functional. Here's how to use it in Cursor:

---

## 🎯 Quick Test Commands

### Test 1: Simple Agent Check
**In Cursor, type:**
```
Use langgraph_agent to check if Xcode CLI tools are installed
```

**Expected**: Agent will execute `check_xcode_cli` tool and respond.

### Test 2: Multi-Step Task
**In Cursor, type:**
```
Use langgraph_agent to:
1. Check Xcode CLI installation
2. List available simulators
3. List Xcode projects
```

**Expected**: Agent executes multiple tools and provides a summary.

### Test 3: Workflow Execution
**In Cursor, type:**
```
Use langgraph_workflow to:
1. Check Xcode CLI
2. List projects
3. List simulators
```

**Expected**: Workflow executes all steps automatically.

### Test 4: Check Agent Status
**In Cursor, type:**
```
Use langgraph_status
```

**Expected**: Returns agent capabilities and status.

---

## 📋 What Happens When You Use the Agent

1. **Cursor sends request** to MCP server
2. **MCP server routes** to LangGraph agent
3. **Agent analyzes** the prompt
4. **Agent decides** which tools to use
5. **Agent executes** tools in sequence
6. **Agent provides** natural language response
7. **Cursor displays** the response to you

---

## 🔍 Verification Steps

### Step 1: Verify MCP Server is Running
1. Open Cursor
2. Check MCP panel (bottom status bar)
3. Look for `xcode-mcp` server
4. Status should be **GREEN** ✅

### Step 2: Test Agent Status
Type in Cursor:
```
Use langgraph_status
```

Should return:
- Agent type: LangGraph
- Available tools: 115
- LangGraph enabled: true

### Step 3: Test Simple Agent Call
Type in Cursor:
```
Use langgraph_agent with prompt "Check if Xcode CLI tools are installed"
```

Should:
- Execute within 10-30 seconds
- Return a response about Xcode CLI status
- Show which tools were used

---

## 🎓 Example Use Cases

### Use Case 1: Environment Verification
```
Use langgraph_agent to verify my Xcode development environment is set up correctly
```

### Use Case 2: Project Discovery
```
Use langgraph_agent to find all my Xcode projects and show their schemes
```

### Use Case 3: Build & Test Workflow
```
Use langgraph_workflow to:
1. Clean the build
2. Build the project
3. Run tests
4. Show results
```

### Use Case 4: Debugging Help
```
Use langgraph_agent to help me understand this build error: [paste error]
```

---

## ⚡ Quick Reference

### Agent Tool Syntax
```
Use langgraph_agent with prompt "your task here"
```

### Workflow Tool Syntax
```
Use langgraph_workflow with workflow "step 1, step 2, step 3"
```

### Status Check
```
Use langgraph_status
```

---

## 🐛 If It Doesn't Work

### Check 1: MCP Server Status
- Should be GREEN in Cursor
- If RED, check `~/.cursor/mcp.json` configuration

### Check 2: LangGraph Installation
```bash
conda activate xcode-mcp
python -c "import langgraph; print('✅ Installed')"
```

### Check 3: LLM Service
- DeepSeek: Check `DEEPSEEK_API_KEY` in `mcp.json`
- Ollama: Ensure Ollama is running (`ollama list`)

### Check 4: Test Locally
```bash
cd /Users/eddiksonpena/Projects/xcode-mcp
python test_agent_mcp.py
```

Should show: ✅ All agent tests passed!

---

## 💡 Pro Tips

1. **Be specific** in your prompts for better results
2. **Use workflows** for predictable multi-step tasks
3. **Check status first** if unsure about agent capabilities
4. **Wait 10-30 seconds** for agent responses (it's thinking!)
5. **Provide context** when possible (project paths, scheme names, etc.)

---

## ✅ Test Results

From our testing:
- ✅ Agent initializes correctly
- ✅ MCP protocol works
- ✅ Tools are executed
- ✅ Responses are generated
- ✅ Status check works
- ✅ Workflows execute

**The agent is ready to use in Cursor!**

---

**Try it now**: Just type one of the test commands above in Cursor!

