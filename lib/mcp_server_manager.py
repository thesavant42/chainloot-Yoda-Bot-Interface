# lib/mcp_server_manager.py

import os
import asyncio
import logging
from typing import Dict, Optional, Any, List
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPServerManager:
    """
    Manages server-side MCP connections and tools.
    This runs MCP servers on the application server, not in the browser.
    """
    
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.tools: Dict[str, Dict[str, Any]] = {}  # tool_name -> {session_name, description, schema}
        self.initialized = False
        self.session_contexts: Dict[str, Any] = {}  # Store context managers
    
    async def initialize(self):
        """Initialize all MCP servers"""
        if self.initialized:
            return
            
        try:
            await self._setup_time_server()
            await self._setup_brave_search_server()
            
            self.initialized = True
            logging.info(f"MCP initialization complete. Available tools: {list(self.tools.keys())}")
            
        except Exception as e:
            logging.error(f"Failed to initialize MCP servers: {e}")
            raise
    
    async def _setup_time_server(self):
        """Setup the time server using proper stdio_client"""
        try:
            server_params = StdioServerParameters(
                command="uvx",
                args=["mcp-server-time"]
            )
            
            # Use stdio_client context manager
            stdio_context = stdio_client(server_params)
            read, write = await stdio_context.__aenter__()
            
            # Store the context for cleanup later
            self.session_contexts['time'] = stdio_context
            
            # Create session with proper streams
            session = ClientSession(read, write)
            await session.__aenter__()
            await session.initialize()
            
            # List available tools
            tool_list = await session.list_tools()
            
            # Store session and tools
            self.sessions["time"] = session
            
            for tool in tool_list.tools:
                self.tools[tool.name] = {
                    "session_name": "time",
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                
            logging.info(f"Time server initialized with tools: {[t.name for t in tool_list.tools]}")
            
        except Exception as e:
            logging.error(f"Failed to setup time server: {e}")
            raise
    
    async def _setup_brave_search_server(self):
        """Setup the Brave Search server using proper stdio_client"""
        try:
            server_params = StdioServerParameters(
                command="npx",
                args=["-y", "@brave/brave-search-mcp-server", "--transport", "stdio"],
                env={"BRAVE_API_KEY": os.environ.get("BRAVE_API_KEY", "")}
            )
            
            # Use stdio_client context manager
            stdio_context = stdio_client(server_params)
            read, write = await stdio_context.__aenter__()
            
            # Store the context for cleanup later
            self.session_contexts['brave_search'] = stdio_context
            
            # Create session with proper streams
            session = ClientSession(read, write)
            await session.__aenter__()
            await session.initialize()
            
            # List available tools
            tool_list = await session.list_tools()
            
            # Store session and tools
            self.sessions["brave_search"] = session
            
            for tool in tool_list.tools:
                self.tools[tool.name] = {
                    "session_name": "brave_search",
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                
            logging.info(f"Brave Search server initialized with tools: {[t.name for t in tool_list.tools]}")
            
        except Exception as e:
            logging.error(f"Failed to setup Brave Search server: {e}")
            raise
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        
        tool_info = self.tools[tool_name]
        session_name = tool_info["session_name"]
        session = self.sessions[session_name]
        
        try:
            result = await session.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            logging.error(f"Failed to call tool {tool_name}: {e}")
            raise
    
    def find_tool_by_capability(self, capability: str) -> Optional[str]:
        """Find a tool by capability (e.g., 'time', 'search')"""
        for tool_name, tool_info in self.tools.items():
            if capability.lower() in tool_name.lower():
                return tool_name
        return None
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return list(self.tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool"""
        return self.tools.get(tool_name)
    
    async def cleanup(self):
        """Clean up all sessions and contexts"""
        try:
            # Close all sessions
            for session_name, session in self.sessions.items():
                try:
                    await session.__aexit__(None, None, None)
                except Exception as e:
                    logging.error(f"Error closing session {session_name}: {e}")
            
            # Close all stdio contexts
            for context_name, context in self.session_contexts.items():
                try:
                    await context.__aexit__(None, None, None)
                except Exception as e:
                    logging.error(f"Error closing context {context_name}: {e}")
            
            self.sessions.clear()
            self.tools.clear()
            self.session_contexts.clear()
            self.initialized = False
            
        except Exception as e:
            logging.error(f"Error during MCP cleanup: {e}")

# Global instance for use throughout the application
mcp_manager = MCPServerManager()