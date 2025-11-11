"""Example usage of LangGraph agent for Xcode development."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.langgraph_agent import create_langgraph_agent


async def main():
    """Example LangGraph agent interactions."""
    
    print("🤖 Creating LangGraph Xcode development agent...")
    agent = create_langgraph_agent(model="ollama:qwen3-coder:30b")
    
    print(f"✅ Agent ready\n")
    
    # Example 1: Simple query
    print("📋 Example 1: Simple query...")
    result = await agent.run("List all available Xcode projects")
    print(f"Messages: {len(result.get('messages', []))}")
    print(f"Tool results: {len(result.get('tool_results', []))}")
    print(f"Final message: {result.get('messages', [])[-1] if result.get('messages') else 'None'}\n")
    
    # Example 2: Multi-step workflow
    print("🚀 Example 2: Multi-step workflow...")
    result = await agent.run("""
    I need to:
    1. Check if Xcode CLI tools are installed
    2. List all available simulators
    3. Get the LLM service status
    
    Please execute these steps in order.
    """)
    print(f"Steps executed: {len(result.get('tool_results', []))}")
    print(f"Final state: {result.get('context', {})}\n")
    
    # Example 3: Complex reasoning task
    print("🧠 Example 3: Complex reasoning task...")
    result = await agent.run("""
    I want to set up a new iOS development environment. 
    What steps should I take and can you help me verify each one?
    """)
    print(f"Workflow completed with {len(result.get('tool_results', []))} tool calls\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

