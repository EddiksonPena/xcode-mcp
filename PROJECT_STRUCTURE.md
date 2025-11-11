# Project Structure

```
xcode-mcp/
├── README.md                    # Main documentation (comprehensive)
├── PROJECT_STRUCTURE.md         # This file
├── .gitignore                   # Git ignore rules
│
├── src/                         # Source code
│   ├── __init__.py
│   ├── unified_mcp_server.py    # Main unified MCP server
│   ├── tool_registry.py         # Tool registration system
│   ├── langgraph_agent.py       # LangGraph agent implementation
│   ├── llm_service.py           # LLM provider abstraction
│   ├── agent_schemas.py         # Agent schema definitions
│   └── xcode_tools/             # Tool implementations
│       ├── __init__.py
│       ├── project.py           # Project management tools
│       ├── build.py             # Build operations
│       ├── testing.py           # Testing tools
│       ├── simulator.py         # Simulator control
│       ├── device.py            # Device management
│       ├── swift.py             # Swift-specific tools
│       ├── git_ci.py            # Git/CI tools
│       ├── diagnostics.py       # Diagnostics tools
│       ├── meta.py              # Meta tools
│       ├── agentic.py           # Agentic tools
│       ├── applescript.py       # AppleScript integration
│       └── llm_config.py        # LLM configuration
│
├── schemas/                     # Schema definitions
│   ├── xcode-mcp-tools.json     # Complete tool schema (94 tools)
│   ├── persona_schemas.json     # Persona schema definition
│   └── persona_examples.json    # Pre-configured personas
│
├── tests/                       # Test suite
│   └── test_unified_server.py   # Comprehensive server tests
│
├── docs/                        # Additional documentation
│   ├── AGENT_GUIDE.md           # Agent usage guide
│   └── LANGGRAPH_GUIDE.md       # LangGraph guide
│
├── examples/                    # Usage examples
│   ├── agent_example.py         # Agent usage example
│   └── langgraph_example.py     # LangGraph example
│
├── archive/                     # Archived files
│   ├── docs/                    # Old documentation files
│   └── deprecated/              # Deprecated code files
│
├── run_unified_mcp.py           # Main server entry point
├── test_mcp_connection.py      # Connection test script
│
├── environment.yml               # Conda environment definition
├── setup.sh                     # Setup script
└── config.example.json          # Example configuration
```

## Key Files

### Main Entry Points
- **`run_unified_mcp.py`** - Use this for Cursor MCP integration
- **`test_mcp_connection.py`** - Test server connectivity

### Core Components
- **`src/unified_mcp_server.py`** - Unified MCP server (combines all capabilities)
- **`src/tool_registry.py`** - Tool registration and execution system
- **`src/langgraph_agent.py`** - LangGraph subagentic implementation

### Configuration
- **`schemas/xcode-mcp-tools.json`** - Complete tool definitions
- **`schemas/persona_schemas.json`** - Persona configuration schema
- **`~/.cursor/mcp.json`** - Cursor MCP configuration (user's home)

### Documentation
- **`README.md`** - Comprehensive project documentation
- **`docs/`** - Additional guides and references

## Deprecated Files

Deprecated files have been moved to `archive/deprecated/`:
- `run_mcp_server.py` - Replaced by `run_unified_mcp.py`
- `run_langgraph_mcp.py` - Replaced by `run_unified_mcp.py`
- `src/server_stdio.py` - Replaced by unified server
- `src/langgraph_mcp_server.py` - Replaced by unified server
- `src/server_mcp.py` - Replaced by unified server
- `src/server_mcp_official.py` - Not used
- `src/server_http.py` - HTTP server (not used for MCP stdio)
- `src/pydantic_ai_agent.py` - Not integrated
- `src/pydantic_ai_agent_simple.py` - Not integrated
- `src/tool_wrapper.py` - Not used

