#!/usr/bin/env python3
"""Test script to verify MCP server connection."""

import json
import subprocess
import sys
import time

def test_mcp_server():
    """Test the MCP server connection."""
    print("🧪 Testing MCP Server Connection...")
    print("=" * 60)
    
    # Command from mcp.json
    cmd = [
        'bash', '-c',
        'cd /Users/eddiksonpena/Projects/xcode-mcp && source "$(conda info --base)/etc/profile.d/conda.sh" && conda activate xcode-mcp && python /Users/eddiksonpena/Projects/xcode-mcp/run_unified_mcp.py'
    ]
    
    print(f"📋 Command: {' '.join(cmd[:3])}...")
    print()
    
    # Start server
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    print("✅ Server process started")
    print()
    
    # Test 1: Initialize
    print("Test 1: Initialize")
    init_req = json.dumps({
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'initialize',
        'params': {
            'protocolVersion': '2024-11-05',
            'capabilities': {},
            'clientInfo': {'name': 'test', 'version': '1.0.0'}
        }
    }) + '\n'
    
    proc.stdin.write(init_req)
    proc.stdin.flush()
    time.sleep(0.3)
    
    output = proc.stdout.readline()
    if output:
        try:
            resp = json.loads(output.strip())
            if 'result' in resp:
                server_name = resp['result'].get('serverInfo', {}).get('name', 'unknown')
                tools = resp['result'].get('serverInfo', {}).get('features', {}).get('direct_tools', 0)
                print(f"  ✅ Initialize successful")
                print(f"  ✅ Server: {server_name}")
                print(f"  ✅ Direct tools: {tools}")
            else:
                print(f"  ❌ Error: {resp.get('error', {})}")
                return False
        except Exception as e:
            print(f"  ❌ Parse error: {e}")
            print(f"  Raw: {output[:200]}")
            return False
    else:
        stderr = proc.stderr.read(500)
        print(f"  ❌ No response")
        if stderr:
            print(f"  Stderr: {stderr}")
        return False
    
    # Send initialized notification
    notif = json.dumps({
        'jsonrpc': '2.0',
        'method': 'notifications/initialized'
    }) + '\n'
    proc.stdin.write(notif)
    proc.stdin.flush()
    time.sleep(0.2)
    
    # Test 2: List tools
    print()
    print("Test 2: List Tools")
    tools_req = json.dumps({
        'jsonrpc': '2.0',
        'id': 2,
        'method': 'tools/list'
    }) + '\n'
    
    proc.stdin.write(tools_req)
    proc.stdin.flush()
    time.sleep(0.3)
    
    output = proc.stdout.readline()
    if output:
        try:
            resp = json.loads(output.strip())
            if 'result' in resp:
                tools = resp['result'].get('tools', [])
                print(f"  ✅ Tools list successful")
                print(f"  ✅ Total tools: {len(tools)}")
                print(f"  ✅ First tool: {tools[0]['name'] if tools else 'none'}")
                print(f"  ✅ Last tool: {tools[-1]['name'] if tools else 'none'}")
            else:
                print(f"  ❌ Error: {resp.get('error', {})}")
                return False
        except Exception as e:
            print(f"  ❌ Parse error: {e}")
            return False
    else:
        print(f"  ❌ No response")
        return False
    
    # Cleanup
    proc.terminate()
    try:
        proc.wait(timeout=1)
    except:
        proc.kill()
    
    print()
    print("=" * 60)
    print("✅ All tests passed! Server is working correctly.")
    print()
    print("💡 If Cursor shows RED, try:")
    print("   1. Restart Cursor completely")
    print("   2. Check Cursor logs for errors")
    print("   3. Verify conda environment is accessible")
    
    return True

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)

