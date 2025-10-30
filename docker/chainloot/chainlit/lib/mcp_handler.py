# lib/mcp_handler.py
"""
MCP (Model Context Protocol) Handler for Chainlit Application
Chainlit handles MCP automatically - we just store tool metadata for reference.
"""

import chainlit as cl
import logging

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