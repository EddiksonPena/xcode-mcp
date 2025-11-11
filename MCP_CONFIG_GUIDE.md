# MCP Configuration Guide for xcode-mcp

## Current Configuration

Your `xcode-mcp` server is configured in `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "xcode-mcp": {
      "command": "/Users/eddiksonpena/miniconda3/envs/xcode-mcp/bin/python",
      "args": [
        "-u",
        "/Users/eddiksonpena/Projects/xcode-mcp/run_unified_mcp.py"
      ],
      "env": {
        "DEEPSEEK_API_KEY": "sk-3f7e5496aafd422cb0109bfdc502dd7f",
        "PYTHONPATH": "/Users/eddiksonpena/Projects/xcode-mcp",
        "PYTHONUNBUFFERED": "1",
        "DEFAULT_MODEL": "deepseek:deepseek-coder"
      },
      "description": "Xcode MCP Server - 118 tools for iOS/macOS development"
    }
  }
}
```

## Configuration Options

### Required Settings

#### `command`
The Python interpreter path. Should point to your conda environment:
```json
"command": "/Users/eddiksonpena/miniconda3/envs/xcode-mcp/bin/python"
```

**To find your path:**
```bash
conda activate xcode-mcp
which python
```

#### `args`
The script arguments:
- `-u`: Unbuffered output (important for real-time logs)
- Script path: Absolute path to `run_unified_mcp.py`

### Environment Variables

#### `DEEPSEEK_API_KEY` (Required for LLM features)
API key for DeepSeek (used for error analysis, recommendations):
```json
"DEEPSEEK_API_KEY": "your-api-key-here"
```

**Get your key**: https://platform.deepseek.com/

#### `PYTHONPATH` (Recommended)
Ensures Python can find the project modules:
```json
"PYTHONPATH": "/Users/eddiksonpena/Projects/xcode-mcp"
```

#### `PYTHONUNBUFFERED` (Recommended)
Enables real-time output:
```json
"PYTHONUNBUFFERED": "1"
```

#### `DEFAULT_MODEL` (Optional)
Default LLM model for LangGraph agent:
```json
"DEFAULT_MODEL": "deepseek:deepseek-coder"
```

**Supported formats:**
- `deepseek:deepseek-coder` - DeepSeek Coder
- `ollama:qwen3-coder:30b` - Ollama (requires local Ollama)
- `openai:gpt-4` - OpenAI (requires `OPENAI_API_KEY`)

### Optional Environment Variables

#### For OpenAI Support
```json
"OPENAI_API_KEY": "your-openai-key"
```

#### For Ollama Support
Ensure Ollama is running locally. No API key needed.

#### For Custom Model Selection
```json
"DEFAULT_MODEL": "ollama:qwen3-coder:30b"
```

## Verification

### Check Configuration
```bash
python3 -m json.tool ~/.cursor/mcp.json
```

### Test Server
```bash
cd /Users/eddiksonpena/Projects/xcode-mcp
python run_unified_mcp.py
```

Should see no errors (server waits for stdin).

### Verify in Cursor
1. Open Cursor
2. Check MCP panel (bottom status bar or sidebar)
3. Look for `xcode-mcp` server
4. Status should be **GREEN** ✅

## Troubleshooting

### Server Shows RED

1. **Check Python Path**
   ```bash
   /Users/eddiksonpena/miniconda3/envs/xcode-mcp/bin/python --version
   ```
   Should show Python 3.11+

2. **Check Script Path**
   ```bash
   ls -la /Users/eddiksonpena/Projects/xcode-mcp/run_unified_mcp.py
   ```
   Should exist and be executable

3. **Test Manually**
   ```bash
   /Users/eddiksonpena/miniconda3/envs/xcode-mcp/bin/python -u /Users/eddiksonpena/Projects/xcode-mcp/run_unified_mcp.py
   ```
   Should not error

### Tools Not Showing

1. **Restart Cursor** (Cmd+Q, wait, reopen)
2. **Check Server Status** (should be GREEN)
3. **Verify Tool Count**:
   ```bash
   python -c "from src.tool_registry import get_registry; r = get_registry(); print(len(r.tools))"
   ```
   Should show 115+

### LangGraph Not Working

1. **Check Installation**:
   ```bash
   conda activate xcode-mcp
   python -c "import langgraph; print('✅ Installed')"
   ```

2. **Install if Missing**:
   ```bash
   pip install langgraph langchain langchain-core langchain-openai langchain-ollama
   ```

## Advanced Configuration

### Multiple Environments

If you have multiple Python environments:

```json
{
  "mcpServers": {
    "xcode-mcp-dev": {
      "command": "/path/to/dev/python",
      "args": ["-u", "/path/to/xcode-mcp/run_unified_mcp.py"],
      "env": { ... }
    },
    "xcode-mcp-prod": {
      "command": "/path/to/prod/python",
      "args": ["-u", "/path/to/xcode-mcp/run_unified_mcp.py"],
      "env": { ... }
    }
  }
}
```

### Custom Model Configuration

For different models per use case:

```json
{
  "env": {
    "DEFAULT_MODEL": "deepseek:deepseek-coder",
    "LLM_TEMPERATURE": "0.7",
    "LLM_MAX_TOKENS": "2000"
  }
}
```

## Best Practices

1. **Use Absolute Paths**: Always use absolute paths for `command` and script paths
2. **Keep API Keys Secure**: Don't commit `mcp.json` with real API keys
3. **Version Control**: Use `.cursor/mcp.json.example` for templates
4. **Regular Updates**: Keep the server code updated for new features
5. **Monitor Logs**: Check Cursor's MCP logs for errors

## Configuration Template

```json
{
  "mcpServers": {
    "xcode-mcp": {
      "command": "/absolute/path/to/python",
      "args": [
        "-u",
        "/absolute/path/to/xcode-mcp/run_unified_mcp.py"
      ],
      "env": {
        "DEEPSEEK_API_KEY": "your-key-here",
        "PYTHONPATH": "/absolute/path/to/xcode-mcp",
        "PYTHONUNBUFFERED": "1",
        "DEFAULT_MODEL": "deepseek:deepseek-coder"
      },
      "description": "Xcode MCP Server - 118 tools for iOS/macOS development"
    }
  }
}
```

## What's New in v2.1.0

The configuration now supports:
- ✅ 115 direct tools (up from 94)
- ✅ 3 LangGraph agent tools
- ✅ Crash reporting tools
- ✅ Asset management tools
- ✅ Localization tools
- ✅ Enhanced simulator tools
- ✅ Build enhancement tools

All tools are automatically available once the server is running!

---

**Last Updated**: 2025-01-XX  
**Server Version**: 2.1.0

