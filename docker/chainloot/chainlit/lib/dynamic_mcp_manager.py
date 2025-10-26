# lib/dynamic_mcp_manager.py

import json
import os
import asyncio
import logging
from typing import Dict, Optional, Any, List
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class DynamicMCPManager:
    """
    Dynamic MCP Server Manager with configuration-driven setup.
    Implements proper tool discovery and standardized server management.
    """
    
    def __init__(self, config_file: str = "config/mcp_servers.json"):
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.sessions: Dict[str, ClientSession] = {}
        self.tools: Dict[str, Dict[str, Any]] = {}  # tool_name -> {server_name, description, schema}
        self.session_contexts: Dict[str, Any] = {}
        self.initialized = False
        self._initialization_lock = asyncio.Lock()
        self._initializing = False
        
    def load_config(self) -> Dict[str, Any]:
        """Load MCP server configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
                
            # Environment variable substitution
            self._substitute_env_vars(self.config)
            
            logging.info(f"Loaded MCP configuration: {len(self.config.get('servers', {}))} servers defined")
            return self.config
            
        except FileNotFoundError:
            logging.error(f"MCP config file not found: {self.config_file}")
            return {}
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in MCP config: {e}")
            return {}
            
    def _substitute_env_vars(self, obj: Any) -> None:
        """Recursively substitute ${VAR} with environment variables"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    env_var = value[2:-1]
                    obj[key] = os.environ.get(env_var, "")
                elif isinstance(value, (dict, list)):
                    self._substitute_env_vars(value)
        elif isinstance(obj, list):
            for item in obj:
                self._substitute_env_vars(item)
                
    async def initialize(self) -> None:
        """Initialize all configured MCP servers with dynamic discovery"""
        async with self._initialization_lock:
            if self.initialized:
                logging.info("MCP servers already initialized, skipping...")
                return
                
            if self._initializing:
                logging.info("MCP initialization already in progress, waiting...")
                return
                
            self._initializing = True
            
            try:
                # Load configuration
                config = self.load_config()
                if not config:
                    logging.warning("No MCP configuration loaded")
                    return
                    
                servers = config.get("servers", {})
                if not servers:
                    logging.warning("No servers defined in MCP configuration")
                    return
                    
                logging.info(f"Starting dynamic MCP initialization for {len(servers)} servers...")
                
                # Initialize each server dynamically
                for server_name, server_config in servers.items():
                    try:
                        await self._setup_server(server_name, server_config)
                    except Exception as e:
                        logging.error(f"Failed to initialize {server_name}: {e}")
                        # Continue with other servers
                        
                self.initialized = True
                tool_count = len(self.tools)
                server_count = len(self.sessions)
                logging.info(f"Dynamic MCP initialization complete: {server_count} servers, {tool_count} tools")
                
            except Exception as e:
                logging.error(f"Failed to initialize MCP servers: {e}")
                await self.cleanup()
                raise
            finally:
                self._initializing = False
                
    async def _setup_server(self, server_name: str, server_config: Dict[str, Any]) -> None:
        """Dynamically set up a single MCP server using configuration"""
        try:
            # Extract server parameters
            command = server_config.get("command")
            args = server_config.get("args", [])
            env = server_config.get("env", {})
            description = server_config.get("description", f"MCP server: {server_name}")
            
            if not command:
                raise ValueError(f"No command specified for server {server_name}")
                
            logging.info(f"Initializing {server_name}: {command} {' '.join(args)}")
            
            # Create server parameters
            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=env
            )
            
            # Set up stdio connection
            stdio_context = stdio_client(server_params)
            read, write = await stdio_context.__aenter__()
            
            # Store context for cleanup
            self.session_contexts[server_name] = stdio_context
            
            # Create and initialize session
            session = ClientSession(read, write)
            await session.__aenter__()
            await session.initialize()
            
            # Store session
            self.sessions[server_name] = session
            
            # Discover tools dynamically
            await self._discover_tools(server_name, session, description)
            
            logging.info(f"Successfully initialized {server_name}")
            
        except Exception as e:
            logging.error(f"Failed to setup server {server_name}: {e}")
            # Clean up partial resources
            await self._cleanup_server(server_name)
            raise
            
    async def _discover_tools(self, server_name: str, session: ClientSession, server_description: str) -> None:
        """Discover and catalog tools from an MCP server"""
        try:
            # Use standard MCP tool discovery
            tool_list = await session.list_tools()
            
            discovered_tools = []
            for tool in tool_list.tools:
                tool_info = {
                    "server_name": server_name,
                    "description": tool.description or f"Tool from {server_name}",
                    "input_schema": tool.inputSchema,
                    "server_description": server_description
                }
                
                self.tools[tool.name] = tool_info
                discovered_tools.append(tool.name)
                
            logging.info(f"Discovered {len(discovered_tools)} tools from {server_name}: {discovered_tools}")
            
        except Exception as e:
            logging.error(f"Failed to discover tools from {server_name}: {e}")
            raise
            
    async def _cleanup_server(self, server_name: str) -> None:
        """Clean up resources for a specific server"""
        try:
            if server_name in self.sessions:
                await self.sessions[server_name].__aexit__(None, None, None)
                del self.sessions[server_name]
                
            if server_name in self.session_contexts:
                await self.session_contexts[server_name].__aexit__(None, None, None)
                del self.session_contexts[server_name]
                
        except Exception as e:
            logging.error(f"Error cleaning up server {server_name}: {e}")
            
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a dynamically discovered tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
            
        tool_info = self.tools[tool_name]
        server_name = tool_info["server_name"]
        
        if server_name not in self.sessions:
            raise ValueError(f"Server {server_name} not available")
            
        session = self.sessions[server_name]
        
        try:
            result = await session.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            logging.error(f"Failed to call tool {tool_name} on {server_name}: {e}")
            raise
            
    def find_tool_by_capability(self, capability: str) -> Optional[str]:
        """Find a tool by capability (e.g., 'time', 'search', 'git')"""
        capability_lower = capability.lower()
        
        # Direct matches
        for tool_name in self.tools:
            if capability_lower in tool_name.lower():
                return tool_name
                
        # Server name matches
        for tool_name, tool_info in self.tools.items():
            server_name = tool_info.get("server_name", "")
            if capability_lower in server_name.lower():
                return tool_name
                
        # Description matches
        for tool_name, tool_info in self.tools.items():
            description = tool_info.get("description", "").lower()
            if capability_lower in description:
                return tool_name
                
        return None
        
    def get_available_tools(self) -> List[str]:
        """Get list of all discovered tools"""
        return list(self.tools.keys())
        
    def get_servers(self) -> List[str]:
        """Get list of active servers"""
        return list(self.sessions.keys())
        
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a tool"""
        return self.tools.get(tool_name)
        
    def get_server_tools(self, server_name: str) -> List[str]:
        """Get all tools provided by a specific server"""
        return [
            tool_name for tool_name, tool_info in self.tools.items()
            if tool_info["server_name"] == server_name
        ]
        
    async def reload_config(self) -> None:
        """Hot reload configuration (if enabled)"""
        if not self.config.get("discovery", {}).get("enable_hot_reload", False):
            logging.info("Hot reload disabled in configuration")
            return
            
        logging.info("Hot reloading MCP configuration...")
        await self.cleanup()
        self.initialized = False
        await self.initialize()
        
    async def cleanup(self) -> None:
        """Clean up all servers and resources"""
        try:
            for server_name in list(self.sessions.keys()):
                await self._cleanup_server(server_name)
                
            self.tools.clear()
            self.initialized = False
            self._initializing = False
            
            logging.info("MCP cleanup completed")
            
        except Exception as e:
            logging.error(f"Error during MCP cleanup: {e}")

# Global instance for use throughout the application
dynamic_mcp_manager = DynamicMCPManager()