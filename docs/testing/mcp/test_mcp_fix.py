#!/usr/bin/env python3
"""
Test script to verify MCP time tool functionality
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.dynamic_mcp_manager import dynamic_mcp_manager

async def test_time_tool():
    """Test the time tool functionality"""
    try:
        print("Testing MCP time tool...")
        
        # Initialize the manager
        await dynamic_mcp_manager.initialize()
        
        # Check if time tool is available
        time_tool = dynamic_mcp_manager.find_tool_by_capability("time")
        if not time_tool:
            print("ERROR: Time tool not found")
            return False
            
        print(f"Found time tool: {time_tool}")
        
        # Call the tool
        result = await dynamic_mcp_manager.call_tool(time_tool, {})
        print(f"Time tool result: {result}")
        
        # Clean up
        await dynamic_mcp_manager.cleanup()
        
        print("Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_time_tool())
    sys.exit(0 if success else 1)