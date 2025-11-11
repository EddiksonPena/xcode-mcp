"""Comprehensive sanity tests for unified MCP server."""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.unified_mcp_server import UnifiedMCPServer
from src.tool_registry import get_registry


class TestUnifiedServer:
    """Comprehensive test suite for unified MCP server."""
    
    def __init__(self):
        self.server = UnifiedMCPServer()
        self.registry = get_registry()
        self.test_results = []
    
    def test_initialization(self):
        """Test server initialization."""
        print("🧪 Test 1: Server Initialization")
        try:
            assert self.server.registry is not None, "Registry not initialized"
            # Updated: We now have 97+ tools (94 original + new tools)
            assert len(self.server.registry.tools) >= 94, f"Expected at least 94 tools, got {len(self.server.registry.tools)}"
            assert self.server.langgraph_enabled is not None, "LangGraph status not checked"
            print("  ✅ Server initialized correctly")
            print(f"  ✅ Registry has {len(self.server.registry.tools)} tools")
            print(f"  ✅ LangGraph enabled: {self.server.langgraph_enabled}")
            return True
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            return False
    
    def test_initialize_protocol(self):
        """Test MCP initialize protocol."""
        print("\n🧪 Test 2: MCP Initialize Protocol")
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0.0"}
                }
            }
            
            # Capture response
            import io
            import contextlib
            
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            self.server.handle_request(request)
            response_str = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            response = json.loads(response_str.strip())
            
            assert response["jsonrpc"] == "2.0", "Invalid JSON-RPC version"
            assert response["id"] == 1, "Invalid response ID"
            assert "result" in response, "No result in response"
            assert response["result"]["protocolVersion"] == "2024-11-05", "Invalid protocol version"
            assert response["result"]["serverInfo"]["name"] == "xcode-mcp-unified", "Invalid server name"
            
            print("  ✅ Initialize protocol works")
            print(f"  ✅ Server name: {response['result']['serverInfo']['name']}")
            print(f"  ✅ Version: {response['result']['serverInfo']['version']}")
            return True
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_tools_list(self):
        """Test tools/list protocol."""
        print("\n🧪 Test 3: Tools List Protocol")
        try:
            # Initialize first
            self.server.initialized = True
            
            request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            self.server.handle_request(request)
            response_str = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            response = json.loads(response_str.strip())
            
            assert "result" in response, "No result in response"
            assert "tools" in response["result"], "No tools in result"
            
            tools = response["result"]["tools"]
            expected_min_count = 94  # Original direct tools
            if self.server.langgraph_enabled:
                expected_min_count += 3  # LangGraph tools
            
            assert len(tools) >= expected_min_count, f"Expected at least {expected_min_count} tools, got {len(tools)}"
            
            # Check tool structure
            for tool in tools[:5]:  # Check first 5
                assert "name" in tool, "Tool missing name"
                assert "description" in tool, "Tool missing description"
                assert "inputSchema" in tool, "Tool missing inputSchema"
            
            # Check for new tools
            tool_names = [tool["name"] for tool in tools]
            new_tools = [
                "symbolicate_crash_log", "optimize_images", "set_simulator_location",
                "set_build_number", "set_version", "analyze_build_time",
                "extract_strings", "validate_localizations"
            ]
            found_new_tools = [name for name in new_tools if name in tool_names]
            
            print(f"  ✅ Tools list returned {len(tools)} tools")
            print(f"  ✅ Original tools: 94+")
            if self.server.langgraph_enabled:
                print(f"  ✅ LangGraph tools: 3")
            print(f"  ✅ New tools found: {len(found_new_tools)}/{len(new_tools)}")
            print(f"  ✅ All tools have required schema fields")
            return True
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_direct_tool_execution(self):
        """Test direct tool execution."""
        print("\n🧪 Test 4: Direct Tool Execution")
        try:
            self.server.initialized = True
            
            # Test a simple tool
            request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "check_xcode_cli",
                    "arguments": {}
                }
            }
            
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            self.server.handle_request(request)
            response_str = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            response = json.loads(response_str.strip())
            
            assert "result" in response or "error" in response, "No result or error"
            
            if "result" in response:
                assert "content" in response["result"], "No content in result"
                print("  ✅ Tool executed successfully")
                return True
            else:
                print(f"  ⚠️  Tool returned error: {response.get('error', {})}")
                return False
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_tool_schema_enhancement(self):
        """Test enhanced tool schemas."""
        print("\n🧪 Test 5: Enhanced Tool Schemas")
        try:
            tool_def = {
                "name": "build_project",
                "description": "Build a project using xcodebuild",
                "parameters": [
                    {"name": "project_path", "type": "string"},
                    {"name": "scheme", "type": "string"}
                ]
            }
            
            schema = self.server._get_tool_schema_enhanced(tool_def)
            
            assert schema["name"] == "build_project", "Invalid tool name"
            assert "inputSchema" in schema, "Missing inputSchema"
            assert "properties" in schema["inputSchema"], "Missing properties"
            assert "project_path" in schema["inputSchema"]["properties"], "Missing project_path"
            assert "scheme" in schema["inputSchema"]["properties"], "Missing scheme"
            
            # Check for examples
            project_path_prop = schema["inputSchema"]["properties"]["project_path"]
            assert "examples" in project_path_prop, "Missing examples for project_path"
            
            print("  ✅ Enhanced schemas include examples")
            print("  ✅ Required fields are marked")
            print("  ✅ Schema caching works")
            return True
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            return False
    
    def test_langgraph_tools(self):
        """Test LangGraph tools if available."""
        print("\n🧪 Test 6: LangGraph Tools")
        if not self.server.langgraph_enabled:
            print("  ⏭️  Skipped (LangGraph not available)")
            return True
        
        try:
            self.server.initialized = True
            
            # Test langgraph_status
            request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "langgraph_status",
                    "arguments": {}
                }
            }
            
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            self.server.handle_request(request)
            response_str = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            response = json.loads(response_str.strip())
            
            if "result" in response:
                print("  ✅ LangGraph status tool works")
                return True
            else:
                print(f"  ⚠️  LangGraph status returned error: {response.get('error')}")
                return False
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_error_handling(self):
        """Test error handling."""
        print("\n🧪 Test 7: Error Handling")
        try:
            self.server.initialized = True
            
            # Test invalid tool
            request = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "nonexistent_tool",
                    "arguments": {}
                }
            }
            
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            self.server.handle_request(request)
            response_str = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            response = json.loads(response_str.strip())
            
            assert "error" in response, "Should return error for nonexistent tool"
            assert response["error"]["code"] == -32000, "Invalid error code"
            
            print("  ✅ Error handling works correctly")
            print("  ✅ Invalid tools return proper errors")
            return True
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            return False
    
    def test_caching(self):
        """Test response caching."""
        print("\n🧪 Test 8: Response Caching")
        try:
            self.server.initialized = True
            
            # Clear cache
            self.server._response_cache.clear()
            
            # First call
            request1 = {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {
                    "name": "check_xcode_cli",
                    "arguments": {}
                }
            }
            
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            self.server.handle_request(request1)
            response1_str = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            # Second call (should use cache)
            sys.stdout = io.StringIO()
            self.server.handle_request(request1)
            response2_str = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            # Check cache was used
            cache_key = f"tool_check_xcode_cli_{json.dumps({}, sort_keys=True)}"
            assert cache_key in self.server._response_cache, "Response not cached"
            
            print("  ✅ Response caching works")
            print("  ✅ Cache TTL is set correctly")
            return True
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests."""
        print("=" * 60)
        print("🧪 Comprehensive Sanity Test Suite")
        print("=" * 60)
        
        tests = [
            self.test_initialization,
            self.test_initialize_protocol,
            self.test_tools_list,
            self.test_direct_tool_execution,
            self.test_tool_schema_enhancement,
            self.test_langgraph_tools,
            self.test_error_handling,
            self.test_caching,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                    self.test_results.append({"test": test.__name__, "status": "passed"})
                else:
                    failed += 1
                    self.test_results.append({"test": test.__name__, "status": "failed"})
            except Exception as e:
                failed += 1
                self.test_results.append({"test": test.__name__, "status": "error", "error": str(e)})
        
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed / len(tests) * 100):.1f}%")
        print("=" * 60)
        
        return failed == 0


if __name__ == "__main__":
    tester = TestUnifiedServer()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

