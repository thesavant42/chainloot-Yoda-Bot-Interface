# lib/mcp_handler.py
"""
Minimal MCP (Model Context Protocol) Handler for Chainlit Application
Just the essentials to get MCP working.
"""

import chainlit as cl
import json


def store_mcp_tools(connection_name: str, tools: list) -> None:
    """Store MCP tools in user session"""
    mcp_tools = cl.user_session.get("mcp_tools", {})
    mcp_tools[connection_name] = tools
    cl.user_session.set("mcp_tools", mcp_tools)


def get_all_mcp_tools() -> list:
    """Get all MCP tools flattened for LLM"""
    mcp_tools = cl.user_session.get("mcp_tools", {})
    return [tool for tools in mcp_tools.values() for tool in tools]


def find_mcp_for_tool(tool_name: str) -> str:
    """Find which MCP connection owns a tool"""
    mcp_tools = cl.user_session.get("mcp_tools", {})
    for connection_name, tools in mcp_tools.items():
        for tool in tools:
            if tool.get("name") == tool_name:
                return connection_name
    return None


async def call_mcp_tool(tool_name: str, tool_input: dict) -> str:
    """Execute MCP tool and return result"""
    # Find connection
    mcp_name = find_mcp_for_tool(tool_name)
    if not mcp_name:
        return json.dumps({"error": f"Tool {tool_name} not found"})
    
    # Get session and call tool
    mcp_session, _ = cl.context.session.mcp_sessions.get(mcp_name)
    if not mcp_session:
        return json.dumps({"error": f"Session for {mcp_name} not found"})
    
    try:
        result = await mcp_session.call_tool(tool_name, tool_input)
        return result if isinstance(result, str) else json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})