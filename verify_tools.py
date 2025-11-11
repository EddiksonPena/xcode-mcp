#!/usr/bin/env python3
"""Verify that all new tools are available in the MCP server."""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.unified_mcp_server import UnifiedMCPServer
from src.tool_registry import get_registry

def main():
    print("=" * 60)
    print("🔍 Xcode MCP Tools Verification")
    print("=" * 60)
    
    # Check registry
    print("\n1. Checking Tool Registry...")
    registry = get_registry()
    registry_tools = registry.list_tools()
    print(f"   ✅ Registry has {len(registry_tools)} tools")
    
    # Check MCP server
    print("\n2. Checking MCP Server...")
    server = UnifiedMCPServer()
    server.initialized = True
    
    import io
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    request = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'tools/list'
    }
    server.handle_request(request)
    response_str = sys.stdout.getvalue()
    sys.stdout = old_stdout
    
    response = json.loads(response_str.strip())
    mcp_tools = response.get('result', {}).get('tools', [])
    mcp_tool_names = [t['name'] for t in mcp_tools]
    
    print(f"   ✅ MCP server returns {len(mcp_tools)} tools")
    
    # Check for new tools
    print("\n3. Checking New Tools...")
    new_tools = [
        # Build enhancements
        'set_build_number', 'set_version', 'analyze_build_time',
        'increment_build_number', 'increment_version_number',
        # Crash reporting
        'symbolicate_crash_log', 'analyze_crash_log', 'get_crash_reports', 'export_crash_log',
        # Asset management
        'optimize_images', 'generate_app_icons', 'validate_asset_catalog', 
        'check_asset_sizes', 'manage_color_assets',
        # Simulator enhancements
        'set_simulator_location', 'get_simulator_logs', 'list_simulator_apps',
        'simulate_network_conditions', 'clone_simulator',
        # Localization
        'extract_strings', 'validate_localizations', 
        'check_localization_coverage', 'list_localizations',
    ]
    
    found_in_registry = []
    found_in_mcp = []
    missing = []
    
    for tool in new_tools:
        in_registry = tool in [t['name'] for t in registry_tools]
        in_mcp = tool in mcp_tool_names
        
        if in_registry:
            found_in_registry.append(tool)
        if in_mcp:
            found_in_mcp.append(tool)
        if not in_registry or not in_mcp:
            missing.append(tool)
    
    print(f"\n   Registry: {len(found_in_registry)}/{len(new_tools)} new tools found")
    print(f"   MCP Server: {len(found_in_mcp)}/{len(new_tools)} new tools found")
    
    if missing:
        print(f"\n   ⚠️  Missing tools: {missing}")
    else:
        print(f"\n   ✅ All {len(new_tools)} new tools are available!")
    
    # Show sample of new tools
    print("\n4. Sample of New Tools Available:")
    for tool in new_tools[:10]:
        if tool in mcp_tool_names:
            print(f"   ✅ {tool}")
    
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print(f"Total tools in registry: {len(registry_tools)}")
    print(f"Total tools in MCP server: {len(mcp_tools)}")
    print(f"New tools implemented: {len(new_tools)}")
    print(f"New tools in registry: {len(found_in_registry)}")
    print(f"New tools in MCP: {len(found_in_mcp)}")
    
    if len(found_in_mcp) == len(new_tools):
        print("\n✅ All tools are properly registered and available!")
        print("\n💡 If you don't see them in Cursor:")
        print("   1. Restart Cursor completely (Cmd+Q)")
        print("   2. Wait 5 seconds")
        print("   3. Reopen Cursor")
        print("   4. Check MCP server status (should be GREEN)")
    else:
        print("\n⚠️  Some tools may not be properly registered")
    
    return len(found_in_mcp) == len(new_tools)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

