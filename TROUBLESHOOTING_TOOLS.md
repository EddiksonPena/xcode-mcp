# Troubleshooting: Tools Not Showing in Cursor

## ✅ Verification

The tools ARE implemented and registered. If you don't see them in Cursor, it's likely a caching or connection issue.

## 🔧 Quick Fix Steps

### Step 1: Verify Tools Are Available
Run the verification script:
```bash
python verify_tools.py
```

This will confirm all 21 new tools are registered.

### Step 2: Restart MCP Server

#### Option A: Restart Cursor (Recommended)
1. **Quit Cursor completely**: `Cmd+Q` (don't just close the window)
2. **Wait 5-10 seconds**
3. **Reopen Cursor**
4. **Check MCP server status** - Should show GREEN in Cursor's MCP panel

#### Option B: Kill and Restart MCP Process
```bash
# Kill any running MCP server processes
pkill -f "run_unified_mcp.py"

# Restart Cursor (it will auto-start the MCP server)
```

### Step 3: Check MCP Configuration

Verify your `~/.cursor/mcp.json` is correct:
```json
{
  "mcpServers": {
    "xcode-mcp": {
      "command": "/path/to/miniconda3/envs/xcode-mcp/bin/python",
      "args": [
        "/Users/eddiksonpena/Projects/xcode-mcp/run_unified_mcp.py"
      ],
      "env": {
        "DEEPSEEK_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**Important**: Use **absolute paths** for both `command` and `args`.

### Step 4: Check MCP Server Status

In Cursor:
1. Open MCP panel (usually in bottom status bar or sidebar)
2. Look for `xcode-mcp` server
3. Status should be **GREEN** ✅
4. If RED ❌, check the error message

### Step 5: Test MCP Connection

Test the server directly:
```bash
python test_mcp_connection.py
```

## 🔍 Diagnostic Commands

### Check Tool Count
```bash
python -c "from src.tool_registry import get_registry; r = get_registry(); print(f'Tools: {len(r.tools)}')"
```

Expected: **115 tools**

### Check Specific Tool
```bash
python -c "from src.tool_registry import get_registry; r = get_registry(); print('symbolicate_crash_log' in r.tools)"
```

Expected: **True**

### List All New Tools
```bash
python -c "
from src.tool_registry import get_registry
r = get_registry()
new_tools = ['symbolicate_crash_log', 'optimize_images', 'set_simulator_location', 'set_build_number', 'set_version', 'analyze_build_time', 'extract_strings', 'validate_localizations']
for tool in new_tools:
    print(f'{tool}: {\"✅\" if tool in r.tools else \"❌\"}')"
```

## 🐛 Common Issues

### Issue 1: Tools Not Appearing After Update
**Solution**: Restart Cursor completely (Cmd+Q, wait, reopen)

### Issue 2: MCP Server Shows RED
**Causes**:
- Wrong Python path
- Missing dependencies
- Syntax errors in code

**Solution**:
1. Check `~/.cursor/mcp.json` paths are absolute
2. Verify Python environment: `conda activate xcode-mcp && python --version`
3. Test server: `python run_unified_mcp.py` (should not error)

### Issue 3: Only Old Tools Showing
**Cause**: Cursor cached old tool list

**Solution**:
1. Quit Cursor (Cmd+Q)
2. Clear Cursor cache (optional): `rm -rf ~/Library/Application\ Support/Cursor/Cache`
3. Restart Cursor

### Issue 4: Some Tools Missing
**Check**:
1. Run `python verify_tools.py` to see which tools are missing
2. Check if tool is in schema: `grep "tool_name" schemas/xcode-mcp-tools.json`
3. Check if tool implementation exists: `ls src/xcode_tools/*.py`

## 📋 New Tools Checklist

Verify these 21 new tools are available:

### Build Enhancements (5)
- [ ] `set_build_number`
- [ ] `set_version`
- [ ] `analyze_build_time`
- [ ] `increment_build_number` (enhanced)
- [ ] `increment_version_number` (enhanced)

### Crash Reporting (4)
- [ ] `symbolicate_crash_log`
- [ ] `analyze_crash_log`
- [ ] `get_crash_reports`
- [ ] `export_crash_log`

### Asset Management (5)
- [ ] `optimize_images`
- [ ] `generate_app_icons`
- [ ] `validate_asset_catalog`
- [ ] `check_asset_sizes`
- [ ] `manage_color_assets`

### Simulator Enhancements (5)
- [ ] `set_simulator_location`
- [ ] `get_simulator_logs`
- [ ] `list_simulator_apps`
- [ ] `simulate_network_conditions`
- [ ] `clone_simulator`

### Localization (4)
- [ ] `extract_strings`
- [ ] `validate_localizations`
- [ ] `check_localization_coverage`
- [ ] `list_localizations`

## 🚀 Force Refresh

If nothing else works:

1. **Kill all MCP processes**:
   ```bash
   pkill -f "run_unified_mcp.py"
   pkill -f "xcode-mcp"
   ```

2. **Clear Cursor cache** (optional):
   ```bash
   rm -rf ~/Library/Application\ Support/Cursor/Cache
   ```

3. **Restart Cursor**:
   - Quit completely (Cmd+Q)
   - Wait 10 seconds
   - Reopen

4. **Verify MCP server is GREEN** in Cursor

## 📞 Still Not Working?

If tools still don't appear after trying all steps:

1. Run `python verify_tools.py` and share the output
2. Check Cursor's MCP server logs for errors
3. Verify the MCP server path in `~/.cursor/mcp.json` is correct
4. Ensure you're using the latest code (pull latest changes if using git)

## ✅ Expected Result

After restarting Cursor, you should see:
- **115+ tools** in the MCP server
- All 21 new tools available
- MCP server status: **GREEN** ✅

---

**Last Updated**: 2025-01-XX

