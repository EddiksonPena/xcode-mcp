#!/usr/bin/env python3
"""Test the LangGraph agent through MCP protocol (simulating Cursor)."""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.unified_mcp_server import UnifiedMCPServer


def test_agent_via_mcp():
    """Test LangGraph agent through MCP protocol."""
    print("=" * 60)
    print("🧪 Testing LangGraph Agent via MCP Protocol")
    print("=" * 60)
    
    # Initialize server
    server = UnifiedMCPServer()
    
    # Step 1: Initialize MCP connection
    print("\n1️⃣  Initializing MCP connection...")
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "cursor-test", "version": "1.0.0"}
        }
    }
    
    import io
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    server.handle_request(init_request)
    init_response_str = sys.stdout.getvalue()
    sys.stdout = old_stdout
    
    init_response = json.loads(init_response_str.strip())
    print(f"   ✅ Initialized: {init_response.get('result', {}).get('serverInfo', {}).get('name')}")
    print(f"   ✅ LangGraph enabled: {server.langgraph_enabled}")
    
    if not server.langgraph_enabled:
        print("\n   ⚠️  LangGraph not available. Install with:")
        print("      pip install langgraph langchain langchain-core langchain-openai langchain-ollama")
        return False
    
    # Step 2: Check agent status
    print("\n2️⃣  Checking LangGraph agent status...")
    server.initialized = True
    
    status_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "langgraph_status",
            "arguments": {}
        }
    }
    
    sys.stdout = io.StringIO()
    server.handle_request(status_request)
    status_response_str = sys.stdout.getvalue()
    sys.stdout = old_stdout
    
    status_response = json.loads(status_response_str.strip())
    
    if "result" in status_response:
        status_data = json.loads(status_response["result"]["content"][0]["text"])
        print(f"   ✅ Agent type: {status_data.get('agent_type')}")
        print(f"   ✅ Available tools: {status_data.get('available_tools')}")
        print(f"   ✅ LangGraph enabled: {status_data.get('langgraph_enabled')}")
    else:
        print(f"   ❌ Error: {status_response.get('error')}")
        return False
    
    # Step 3: Test simple agent prompt
    print("\n3️⃣  Testing LangGraph agent with simple prompt...")
    print("   Prompt: 'Check if Xcode CLI tools are installed'")
    
    agent_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "langgraph_agent",
            "arguments": {
                "prompt": "Check if Xcode CLI tools are installed and list available simulators"
            }
        }
    }
    
    print("   ⏳ Executing agent (this may take 10-30 seconds)...")
    sys.stdout = io.StringIO()
    
    try:
        server.handle_request(agent_request)
        agent_response_str = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        agent_response = json.loads(agent_response_str.strip())
        
        if "result" in agent_response:
            result_data = json.loads(agent_response["result"]["content"][0]["text"])
            print(f"   ✅ Agent executed successfully!")
            print(f"   ✅ Steps executed: {result_data.get('steps_executed', 0)}")
            print(f"   ✅ Messages: {result_data.get('messages_count', 0)}")
            
            # Show response preview
            response_text = result_data.get('response', '')
            if response_text:
                preview = response_text[:200] + "..." if len(response_text) > 200 else response_text
                print(f"\n   📝 Response preview:")
                print(f"   {preview}")
            
            return True
        else:
            error = agent_response.get('error', {})
            print(f"   ❌ Error: {error.get('message', 'Unknown error')}")
            print(f"   Code: {error.get('code', 'N/A')}")
            return False
            
    except Exception as e:
        sys.stdout = old_stdout
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Test workflow
    print("\n4️⃣  Testing LangGraph workflow...")
    print("   Workflow: 'List projects and check Xcode CLI'")
    
    workflow_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "langgraph_workflow",
            "arguments": {
                "workflow": "1. Check Xcode CLI installation 2. List available Xcode projects"
            }
        }
    }
    
    print("   ⏳ Executing workflow (this may take 10-30 seconds)...")
    sys.stdout = io.StringIO()
    
    try:
        server.handle_request(workflow_request)
        workflow_response_str = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        workflow_response = json.loads(workflow_response_str.strip())
        
        if "result" in workflow_response:
            workflow_data = json.loads(workflow_response["result"]["content"][0]["text"])
            print(f"   ✅ Workflow executed successfully!")
            print(f"   ✅ Steps executed: {workflow_data.get('steps_executed', 0)}")
            print(f"   ✅ Success: {workflow_data.get('success', False)}")
            return True
        else:
            error = workflow_response.get('error', {})
            print(f"   ❌ Error: {error.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        sys.stdout = old_stdout
        print(f"   ❌ Exception: {e}")
        return False


def main():
    """Run agent tests."""
    try:
        success = test_agent_via_mcp()
        
        print("\n" + "=" * 60)
        if success:
            print("✅ All agent tests passed!")
            print("\n💡 To use in Cursor:")
            print("   1. Restart Cursor (Cmd+Q, wait, reopen)")
            print("   2. Ask Cursor: 'Use langgraph_agent to check my Xcode setup'")
            print("   3. Or: 'Use langgraph_workflow to build and test my project'")
        else:
            print("❌ Some tests failed. Check errors above.")
        print("=" * 60)
        
        return success
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

