# lib/mcp_handler.py
"""
MCP (Model Context Protocol) Handler for Chainlit Application
Handles MCP tool discovery and formatting for LLM consumption.
"""

import chainlit as cl
import logging
import json

logger = logging.getLogger(__name__)


def store_mcp_tools(connection_name: str, tools: list) -> None:
    """Store MCP tools in user session for reference"""
    mcp_tools = cl.user_session.get("mcp_tools", {})
    mcp_tools[connection_name] = tools
    cl.user_session.set("mcp_tools", mcp_tools)
    logger.info(f"Stored {len(tools)} MCP tools for connection: {connection_name}")


def has_mcp_tools() -> bool:
    """Check if any MCP tools are available"""
    mcp_tools = cl.user_session.get("mcp_tools", {})
    total_tools = sum(len(tools) for tools in mcp_tools.values())
    return total_tools > 0


def get_mcp_tools_for_llm() -> list:
    """
    Get all MCP tools formatted for OpenAI-compatible tool calling.
    Returns list of tools in OpenAI function calling format.
    """
    mcp_tools = cl.user_session.get("mcp_tools", {})
    tools = []
    
    for connection_name, tool_list in mcp_tools.items():
        for tool in tool_list:
            # Convert MCP tool schema to OpenAI function format
            tool_def = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"]
                }
            }
            tools.append(tool_def)
    
    if tools:
        logger.info(f"Prepared {len(tools)} MCP tools for LLM: {[t['function']['name'] for t in tools]}")
    
    return tools


async def execute_mcp_tool(tool_name: str, tool_arguments: dict) -> str:
    """
    Execute an MCP tool by routing to the appropriate MCP session.
    
    Args:
        tool_name: Name of the tool to execute
        tool_arguments: Arguments to pass to the tool
    
    Returns:
        Tool execution result as string
    """
    # Find which MCP connection owns this tool
    mcp_tools = cl.user_session.get("mcp_tools", {})
    mcp_connection_name = None
    
    for connection_name, tool_list in mcp_tools.items():
        if any(tool["name"] == tool_name for tool in tool_list):
            mcp_connection_name = connection_name
            break
    
    if not mcp_connection_name:
        error_msg = f"Tool '{tool_name}' not found in any MCP connection"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    
    # Get the MCP session for this connection
    mcp_sessions = cl.context.session.mcp_sessions
    if mcp_connection_name not in mcp_sessions:
        error_msg = f"MCP session '{mcp_connection_name}' not found"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})
    
    mcp_session, _ = mcp_sessions[mcp_connection_name]
    
    try:
        logger.info(f"Executing MCP tool '{tool_name}' from connection '{mcp_connection_name}' with args: {tool_arguments}")
        result = await mcp_session.call_tool(tool_name, tool_arguments)
        logger.info(f"Tool '{tool_name}' executed successfully")
        return json.dumps(result) if not isinstance(result, str) else result
    except Exception as e:
        error_msg = f"Error executing tool '{tool_name}': {str(e)}"
        logger.error(error_msg, exc_info=True)
        return json.dumps({"error": error_msg})