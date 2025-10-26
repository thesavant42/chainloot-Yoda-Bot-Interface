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
        self._initialization_lock = asyncio.Lock()  # Prevent concurrent initialization
        self._initializing = False  # Track if initialization is in progress
    
    async def initialize(self):
        """Initialize all MCP servers (singleton pattern with proper async locking)"""
        async with self._initialization_lock:
            if self.initialized:
                logging.info("MCP servers already initialized, skipping...")
                return
                
            if self._initializing:
                logging.info("MCP initialization already in progress, waiting...")
                return
                
            self._initializing = True
            
            try:
                logging.info("Starting MCP server initialization...")
                await self._setup_time_server()
                await self._setup_brave_search_server()
                await self._setup_fetch_server()
                await self._setup_git_server()
                await self._setup_memory_server()
                await self._setup_sequential_thinking_server()
                await self._setup_youtube_transcript_server()
                await self._setup_wikipedia_server()
                await self._setup_proxy_servers()  # Add proxy servers from config
                
                self.initialized = True
                logging.info(f"MCP initialization complete. Available tools: {list(self.tools.keys())}")
                
            except Exception as e:
                logging.error(f"Failed to initialize MCP servers: {e}")
                # Clean up partial initialization
                await self.cleanup()
                raise
            finally:
                self._initializing = False
    
    async def _setup_time_server(self):
        """Setup the time server using proper stdio_client"""
        try:
            server_params = StdioServerParameters(
                command="uvx",
                args=["mcp-server-time"]
            )
            
            # Use stdio_client as async context manager
            stdio_context = stdio_client(server_params)
            read, write = await stdio_context.__aenter__()
            
            # Store the context for cleanup later
            self.session_contexts['time'] = stdio_context
            
            # Create session with proper streams
            session = ClientSession(read, write)
            await session.__aenter__()
            
            # Store session for cleanup
            self.sessions["time"] = session
            
            # Initialize after storing (prevents partial cleanup issues)
            await session.initialize()
            
            # List available tools
            tool_list = await session.list_tools()
            
            for tool in tool_list.tools:
                self.tools[tool.name] = {
                    "session_name": "time",
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                
            logging.info(f"Time server initialized with tools: {[t.name for t in tool_list.tools]}")
            
        except Exception as e:
            logging.error(f"Failed to setup time server: {e}")
            # Clean up partially created resources
            if 'time' in self.session_contexts:
                try:
                    await self.session_contexts['time'].__aexit__(None, None, None)
                    del self.session_contexts['time']
                except:
                    pass
            if 'time' in self.sessions:
                try:
                    await self.sessions['time'].__aexit__(None, None, None)
                    del self.sessions['time']
                except:
                    pass
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
    
    async def _setup_fetch_server(self):
        """Setup the fetch server for web content retrieval"""
        try:
            server_params = StdioServerParameters(
                command="uvx",
                args=["mcp-server-fetch"]
            )
            
            stdio_context = stdio_client(server_params)
            read, write = await stdio_context.__aenter__()
            self.session_contexts['fetch'] = stdio_context
            
            session = ClientSession(read, write)
            await session.__aenter__()
            await session.initialize()
            
            tool_list = await session.list_tools()
            self.sessions["fetch"] = session
            
            for tool in tool_list.tools:
                self.tools[tool.name] = {
                    "session_name": "fetch",
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                
            logging.info(f"Fetch server initialized with tools: {[t.name for t in tool_list.tools]}")
            
        except Exception as e:
            logging.error(f"Failed to setup fetch server: {e}")
            # Don't raise - continue with other servers
    
    async def _setup_git_server(self):
        """Setup the git server for repository operations"""
        try:
            server_params = StdioServerParameters(
                command="uvx",
                args=["mcp-server-git"]
            )
            
            stdio_context = stdio_client(server_params)
            read, write = await stdio_context.__aenter__()
            self.session_contexts['git'] = stdio_context
            
            session = ClientSession(read, write)
            await session.__aenter__()
            await session.initialize()
            
            tool_list = await session.list_tools()
            self.sessions["git"] = session
            
            for tool in tool_list.tools:
                self.tools[tool.name] = {
                    "session_name": "git",
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                
            logging.info(f"Git server initialized with tools: {[t.name for t in tool_list.tools]}")
            
        except Exception as e:
            logging.error(f"Failed to setup git server: {e}")
            # Don't raise - continue with other servers
    
    async def _setup_memory_server(self):
        """Setup the memory server for persistent conversation memory"""
        try:
            server_params = StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-memory"],
                env={"MEMORY_FILE_PATH": "memory.json"}
            )
            
            stdio_context = stdio_client(server_params)
            read, write = await stdio_context.__aenter__()
            self.session_contexts['memory'] = stdio_context
            
            session = ClientSession(read, write)
            await session.__aenter__()
            await session.initialize()
            
            tool_list = await session.list_tools()
            self.sessions["memory"] = session
            
            for tool in tool_list.tools:
                self.tools[tool.name] = {
                    "session_name": "memory",
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                
            logging.info(f"Memory server initialized with tools: {[t.name for t in tool_list.tools]}")
            
        except Exception as e:
            logging.error(f"Failed to setup memory server: {e}")
            # Don't raise - continue with other servers
    
    async def _setup_sequential_thinking_server(self):
        """Setup the sequential thinking server for step-by-step reasoning"""
        try:
            server_params = StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-sequential-thinking"]
            )
            
            stdio_context = stdio_client(server_params)
            read, write = await stdio_context.__aenter__()
            self.session_contexts['sequential_thinking'] = stdio_context
            
            session = ClientSession(read, write)
            await session.__aenter__()
            await session.initialize()
            
            tool_list = await session.list_tools()
            self.sessions["sequential_thinking"] = session
            
            for tool in tool_list.tools:
                self.tools[tool.name] = {
                    "session_name": "sequential_thinking",
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                
            logging.info(f"Sequential thinking server initialized with tools: {[t.name for t in tool_list.tools]}")
            
        except Exception as e:
            logging.error(f"Failed to setup sequential thinking server: {e}")
            # Don't raise - continue with other servers
    
    async def _setup_youtube_transcript_server(self):
        """Setup the YouTube transcript server for video transcript extraction"""
        try:
            server_params = StdioServerParameters(
                command="npx",
                args=["-y", "@kimtaeyoon83/mcp-server-youtube-transcript"]
            )
            
            stdio_context = stdio_client(server_params)
            read, write = await stdio_context.__aenter__()
            self.session_contexts['youtube_transcript'] = stdio_context
            
            session = ClientSession(read, write)
            await session.__aenter__()
            await session.initialize()
            
            tool_list = await session.list_tools()
            self.sessions["youtube_transcript"] = session
            
            for tool in tool_list.tools:
                self.tools[tool.name] = {
                    "session_name": "youtube_transcript",
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                
            logging.info(f"YouTube transcript server initialized with tools: {[t.name for t in tool_list.tools]}")
            
        except Exception as e:
            logging.error(f"Failed to setup YouTube transcript server: {e}")
            # Don't raise - continue with other servers
    
    async def _setup_wikipedia_server(self):
        """Setup the Wikipedia server for encyclopedia lookup"""
        try:
            server_params = StdioServerParameters(
                command="wikipedia-mcp",
                args=[]
            )
            
            stdio_context = stdio_client(server_params)
            read, write = await stdio_context.__aenter__()
            self.session_contexts['wikipedia'] = stdio_context
            
            session = ClientSession(read, write)
            await session.__aenter__()
            await session.initialize()
            
            tool_list = await session.list_tools()
            self.sessions["wikipedia"] = session
            
            for tool in tool_list.tools:
                self.tools[tool.name] = {
                    "session_name": "wikipedia",
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                
            logging.info(f"Wikipedia server initialized with tools: {[t.name for t in tool_list.tools]}")
            
        except Exception as e:
            logging.error(f"Failed to setup Wikipedia server: {e}")
            # Don't raise - continue with other servers
    
    async def _setup_proxy_servers(self):
        """Setup proxy servers from mcp_proxy_servers.json"""
        try:
            import json
            import os
            
            proxy_config_path = "config/mcp_proxy_servers.json"
            if not os.path.exists(proxy_config_path):
                logging.info("No proxy server config found, skipping proxy servers")
                return
                
            with open(proxy_config_path, 'r') as f:
                proxy_config = json.load(f)
                
            # Environment variable substitution
            def substitute_env_vars(obj):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                            env_var = value[2:-1]
                            obj[key] = os.environ.get(env_var, "")
                        elif isinstance(value, (dict, list)):
                            substitute_env_vars(value)
                elif isinstance(obj, list):
                    for item in obj:
                        substitute_env_vars(item)
            
            substitute_env_vars(proxy_config)
            
            mcp_servers = proxy_config.get("mcpServers", {})
            if not mcp_servers:
                logging.info("No proxy servers defined in config")
                return
                
            logging.info(f"Setting up {len(mcp_servers)} proxy servers from config")
            
            for server_name, server_config in mcp_servers.items():
                try:
                    await self._setup_single_proxy_server(server_name, server_config)
                except Exception as e:
                    logging.error(f"Failed to setup proxy server {server_name}: {e}")
                    # Continue with other servers
                    
        except Exception as e:
            logging.error(f"Failed to setup proxy servers: {e}")
    
    async def _setup_single_proxy_server(self, server_name: str, server_config: dict):
        """Setup a single proxy server using mcp-proxy"""
        try:
            env = server_config.get("env", {})
            sse_url = env.get("SSE_URL")
            api_token = env.get("API_ACCESS_TOKEN")
            
            if not sse_url:
                raise ValueError(f"No SSE_URL specified for proxy server {server_name}")
                
            # Set up mcp-proxy command
            command = "mcp-proxy"
            args = [sse_url]
            
            # Add API token to environment if provided
            proxy_env = os.environ.copy()
            if api_token:
                proxy_env["API_ACCESS_TOKEN"] = api_token
                
            logging.info(f"Initializing proxy server {server_name}: {command} {' '.join(args)}")
            
            # Set up stdio connection
            stdio_context = stdio_client(StdioServerParameters(
                command=command,
                args=args,
                env=proxy_env
            ))
            read, write = await stdio_context.__aenter__()
            
            # Store context for cleanup
            self.session_contexts[server_name] = stdio_context
            
            # Create session
            session = ClientSession(read, write)
            await session.__aenter__()
            await session.initialize()
            
            # Store session
            self.sessions[server_name] = session
            
            # List available tools
            tool_list = await session.list_tools()
            
            for tool in tool_list.tools:
                self.tools[tool.name] = {
                    "session_name": server_name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                
            logging.info(f"Proxy server {server_name} initialized with tools: {[t.name for t in tool_list.tools]}")
            
        except Exception as e:
            logging.error(f"Failed to setup proxy server {server_name}: {e}")
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