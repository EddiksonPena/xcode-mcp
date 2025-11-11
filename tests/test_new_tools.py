"""Regression tests for newly added tools."""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tool_registry import get_registry


class TestNewTools:
    """Test suite for newly added tools."""
    
    def __init__(self):
        self.registry = get_registry()
        self.test_results = []
    
    def test_build_enhancements(self):
        """Test build enhancement tools."""
        print("\n🧪 Testing Build Enhancement Tools")
        
        tools_to_test = [
            "set_build_number",
            "set_version",
            "analyze_build_time",
            "increment_build_number",
            "increment_version_number"
        ]
        
        passed = 0
        for tool_name in tools_to_test:
            try:
                impl = self.registry.get_tool_implementation(tool_name)
                schema = self.registry.get_tool_schema(tool_name)
                
                assert impl is not None, f"{tool_name} implementation not found"
                assert schema is not None, f"{tool_name} schema not found"
                
                print(f"  ✅ {tool_name} - Implementation and schema found")
                passed += 1
            except Exception as e:
                print(f"  ❌ {tool_name} - Failed: {e}")
        
        return passed == len(tools_to_test)
    
    def test_crash_reporting_tools(self):
        """Test crash reporting tools."""
        print("\n🧪 Testing Crash Reporting Tools")
        
        tools_to_test = [
            "symbolicate_crash_log",
            "analyze_crash_log",
            "get_crash_reports",
            "export_crash_log"
        ]
        
        passed = 0
        for tool_name in tools_to_test:
            try:
                impl = self.registry.get_tool_implementation(tool_name)
                schema = self.registry.get_tool_schema(tool_name)
                
                assert impl is not None, f"{tool_name} implementation not found"
                assert schema is not None, f"{tool_name} schema not found"
                
                print(f"  ✅ {tool_name} - Implementation and schema found")
                passed += 1
            except Exception as e:
                print(f"  ❌ {tool_name} - Failed: {e}")
        
        return passed == len(tools_to_test)
    
    def test_asset_management_tools(self):
        """Test asset management tools."""
        print("\n🧪 Testing Asset Management Tools")
        
        tools_to_test = [
            "optimize_images",
            "generate_app_icons",
            "validate_asset_catalog",
            "check_asset_sizes",
            "manage_color_assets"
        ]
        
        passed = 0
        for tool_name in tools_to_test:
            try:
                impl = self.registry.get_tool_implementation(tool_name)
                schema = self.registry.get_tool_schema(tool_name)
                
                assert impl is not None, f"{tool_name} implementation not found"
                assert schema is not None, f"{tool_name} schema not found"
                
                print(f"  ✅ {tool_name} - Implementation and schema found")
                passed += 1
            except Exception as e:
                print(f"  ❌ {tool_name} - Failed: {e}")
        
        return passed == len(tools_to_test)
    
    def test_simulator_enhancements(self):
        """Test simulator enhancement tools."""
        print("\n🧪 Testing Simulator Enhancement Tools")
        
        tools_to_test = [
            "set_simulator_location",
            "get_simulator_logs",
            "list_simulator_apps",
            "simulate_network_conditions",
            "clone_simulator"
        ]
        
        passed = 0
        for tool_name in tools_to_test:
            try:
                impl = self.registry.get_tool_implementation(tool_name)
                schema = self.registry.get_tool_schema(tool_name)
                
                assert impl is not None, f"{tool_name} implementation not found"
                assert schema is not None, f"{tool_name} schema not found"
                
                print(f"  ✅ {tool_name} - Implementation and schema found")
                passed += 1
            except Exception as e:
                print(f"  ❌ {tool_name} - Failed: {e}")
        
        return passed == len(tools_to_test)
    
    def test_localization_tools(self):
        """Test localization tools."""
        print("\n🧪 Testing Localization Tools")
        
        tools_to_test = [
            "extract_strings",
            "validate_localizations",
            "check_localization_coverage",
            "list_localizations"
        ]
        
        passed = 0
        for tool_name in tools_to_test:
            try:
                impl = self.registry.get_tool_implementation(tool_name)
                schema = self.registry.get_tool_schema(tool_name)
                
                assert impl is not None, f"{tool_name} implementation not found"
                assert schema is not None, f"{tool_name} schema not found"
                
                print(f"  ✅ {tool_name} - Implementation and schema found")
                passed += 1
            except Exception as e:
                print(f"  ❌ {tool_name} - Failed: {e}")
        
        return passed == len(tools_to_test)
    
    def test_resign_app_enhancement(self):
        """Test enhanced resign_app tool."""
        print("\n🧪 Testing Enhanced resign_app Tool")
        
        try:
            impl = self.registry.get_tool_implementation("resign_app")
            schema = self.registry.get_tool_schema("resign_app")
            
            assert impl is not None, "resign_app implementation not found"
            assert schema is not None, "resign_app schema not found"
            
            # Check that provisioning_profile parameter exists
            params = schema.get("parameters", [])
            param_names = [p.get("name") for p in params]
            assert "provisioning_profile" in param_names, "provisioning_profile parameter missing"
            
            print("  ✅ resign_app - Enhanced with provisioning_profile parameter")
            return True
        except Exception as e:
            print(f"  ❌ resign_app - Failed: {e}")
            return False
    
    def test_tool_count(self):
        """Test that all new tools are registered."""
        print("\n🧪 Testing Tool Count")
        
        try:
            all_tools = self.registry.list_tools()
            tool_count = len(all_tools)
            
            # We should have at least 97 tools (94 original + 3+ new)
            assert tool_count >= 97, f"Expected at least 97 tools, got {tool_count}"
            
            print(f"  ✅ Total tools registered: {tool_count}")
            print(f"  ✅ Expected minimum: 97")
            print(f"  ✅ New tools added: {tool_count - 94}")
            
            return True
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all regression tests."""
        print("=" * 60)
        print("🧪 Regression Test Suite for New Tools")
        print("=" * 60)
        
        tests = [
            self.test_build_enhancements,
            self.test_crash_reporting_tools,
            self.test_asset_management_tools,
            self.test_simulator_enhancements,
            self.test_localization_tools,
            self.test_resign_app_enhancement,
            self.test_tool_count,
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
        print("📊 Regression Test Results Summary")
        print("=" * 60)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed / len(tests) * 100):.1f}%")
        print("=" * 60)
        
        return failed == 0


if __name__ == "__main__":
    tester = TestNewTools()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

