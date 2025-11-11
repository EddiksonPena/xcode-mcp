"""Example usage of PydanticAI agent for Xcode development."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Note: This example uses PydanticAI agent which is not integrated into MCP
# For MCP usage, use the unified_mcp_server tools directly or langgraph_agent
# from src.pydantic_ai_agent import create_xcode_agent  # Deprecated - not in MCP


async def main():
    """Example agent interactions using LangGraph agent (recommended for MCP)."""
    
    # Use LangGraph agent instead (integrated into MCP)
    from src.langgraph_agent import create_langgraph_agent
    
    print("🤖 Creating LangGraph Xcode development agent...")
    agent = create_langgraph_agent(model="ollama:qwen3-coder:30b")
    
    print("✅ Agent ready\n")
    
    # Example 1: List projects
    print("📋 Example 1: Listing Xcode projects...")
    result = agent.run_sync("List all available Xcode projects in the current directory")
    messages = result.get("messages", [])
    if messages:
        print(f"Response: {messages[-1].content if hasattr(messages[-1], 'content') else messages[-1]}\n")
    
    # Example 2: Check Xcode CLI
    print("🔧 Example 2: Checking Xcode CLI tools...")
    result = agent.run_sync("Verify that Xcode command-line tools are installed")
    messages = result.get("messages", [])
    if messages:
        print(f"Response: {messages[-1].content if hasattr(messages[-1], 'content') else messages[-1]}\n")
    
    # Example 3: List simulators
    print("📱 Example 3: Listing available simulators...")
    result = agent.run_sync("Show me all available iOS simulators")
    messages = result.get("messages", [])
    if messages:
        print(f"Response: {messages[-1].content if hasattr(messages[-1], 'content') else messages[-1]}\n")
    
    # Example 4: Get LLM status
    print("🧠 Example 4: Checking LLM service status...")
    result = agent.run_sync("What is the current LLM provider and model being used?")
    messages = result.get("messages", [])
    if messages:
        print(f"Response: {messages[-1].content if hasattr(messages[-1], 'content') else messages[-1]}\n")
    
    # Example 5: Complex task
    print("🚀 Example 5: Complex development task...")
    result = agent.run_sync("""
    I want to:
    1. List all available build schemes
    2. Check if there are any build errors
    3. Get the status of the LLM service
    
    Please help me with these tasks.
    """)
    messages = result.get("messages", [])
    if messages:
        print(f"Response: {messages[-1].content if hasattr(messages[-1], 'content') else messages[-1]}\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

