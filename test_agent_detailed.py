#!/usr/bin/env python3
"""Detailed test of LangGraph agent showing full responses."""

import json
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.unified_mcp_server import UnifiedMCPServer


def test_agent_detailed():
    """Test agent with detailed output."""
    print("=" * 70)
    print("🤖 LangGraph Agent - Detailed Test")
    print("=" * 70)
    
    server = UnifiedMCPServer()
    server.initialized = True
    
    # Test prompt
    test_prompt = "Check if Xcode CLI tools are installed and list available simulators"
    
    print(f"\n📝 Test Prompt:")
    print(f"   '{test_prompt}'")
    print(f"\n⏳ Executing agent...")
    print(f"   (This simulates what Cursor does when you use langgraph_agent)")
    print()
    
    import io
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "langgraph_agent",
            "arguments": {
                "prompt": test_prompt
            }
        }
    }
    
    try:
        server.handle_request(request)
        response_str = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        response = json.loads(response_str.strip())
        
        if "result" in response:
            result_data = json.loads(response["result"]["content"][0]["text"])
            
            print("=" * 70)
            print("✅ AGENT RESPONSE")
            print("=" * 70)
            
            print(f"\n📊 Execution Summary:")
            print(f"   Steps executed: {result_data.get('steps_executed', 0)}")
            print(f"   Messages: {result_data.get('messages_count', 0)}")
            
            # Show tool results
            tool_results = result_data.get('tool_results', [])
            if tool_results:
                print(f"\n🔧 Tools Used:")
                for i, tr in enumerate(tool_results, 1):
                    tool_name = tr.get('tool', 'unknown')
                    success = tr.get('success', False)
                    status = "✅" if success else "❌"
                    print(f"   {i}. {status} {tool_name}")
            
            # Show full response
            response_text = result_data.get('response', '')
            if response_text:
                print(f"\n💬 Agent Response:")
                print("-" * 70)
                # Pretty print the response
                lines = response_text.split('\n')
                for line in lines[:50]:  # First 50 lines
                    print(f"   {line}")
                if len(lines) > 50:
                    print(f"   ... ({len(lines) - 50} more lines)")
                print("-" * 70)
            
            return True
        else:
            sys.stdout = old_stdout
            error = response.get('error', {})
            print(f"❌ Error: {error.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        sys.stdout = old_stdout
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_agent_detailed()

