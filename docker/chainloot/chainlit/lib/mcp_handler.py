import chainlit as cl
from typing import Dict, Any, List, Tuple, AsyncGenerator
from mcp import ClientSession
from mcp.types import CallToolResult, TextContent
import logging
import json

logger = logging.getLogger(__name__)

mcp_tools_cache = {}

# Instrument OpenAI client for Chainlit MCP integration
# This enables Chainlit to intercept tool calls in LLM responses
cl.instrument_openai()


def store_mcp_tools(connection_name: str, tools: List[Dict[str, Any]]):
    """Store tools from a connected MCP server in the session"""
    mcp_tools = cl.user_session.get("mcp_tools", {})
    mcp_tools[connection_name] = tools
    cl.user_session.set("mcp_tools", mcp_tools)
    mcp_tools_cache[connection_name] = tools
    logger.info(f"Stored {len(tools)} tools from MCP connection: {connection_name}")


def has_mcp_tools() -> bool:
    """Check if any MCP tools are available"""
    mcp_tools = cl.user_session.get("mcp_tools", {})
    return any(len(tools) > 0 for tools in mcp_tools.values())


def get_mcp_tools_for_llm() -> List[Dict[str, Any]]:
    """Get all MCP tools available (for UI display/context only, NOT for LLM function calling)"""
    mcp_tools = cl.user_session.get("mcp_tools", {})
    all_tools = []
    for connection_tools in mcp_tools.values():
        all_tools.extend(connection_tools)
    return all_tools


async def format_tools_for_openai(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format MCP tools into OpenAI-compatible tool format for the chat API."""
    openai_tools = []
    for tool in tools:
        openai_tool = {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool.get("input_schema", {}),
            },
        }
        openai_tools.append(openai_tool)
    return openai_tools


def format_calltoolresult_content(result: Any) -> str:
    """Extract text content from an MCP CallToolResult object."""
    text_contents = []
    if isinstance(result, CallToolResult):
        for content_item in result.content:
            if isinstance(content_item, TextContent):
                text_contents.append(content_item.text)
    if text_contents:
        return "\n".join(text_contents)
    return str(result)


async def execute_mcp_tool(tool_name: str, tool_input: Dict[str, Any]) -> Any:
    """Execute an MCP tool via MCP protocol (NOT OpenAI function calling)"""
    return await execute_tool(tool_name, tool_input)


@cl.on_mcp_connect
async def on_mcp_connect(connection, session: ClientSession):
    cl.Message(f"Connected to MCP server: {connection.name}").send()

    try:
        result = await session.list_tools()

        tools = [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.inputSchema,
            }
            for t in result.tools
        ]

        mcp_tools_cache[connection.name] = tools

        mcp_tools = cl.user_session.get("mcp_tools", {})
        mcp_tools[connection.name] = tools
        cl.user_session.set("mcp_tools", mcp_tools)

        await cl.Message(
            f"Found {len(tools)} tools from {connection.name} MCP server."
        ).send()
    except Exception as e:
        await cl.Message(f"Error listing tools from MCP server: {str(e)}").send()


@cl.on_mcp_disconnect
async def on_mcp_disconnect(name: str, session: ClientSession):
    if name in mcp_tools_cache:
        del mcp_tools_cache[name]

    mcp_tools = cl.user_session.get("mcp_tools", {})
    if name in mcp_tools:
        del mcp_tools[name]
        cl.user_session.set("mcp_tools", mcp_tools)

    await cl.Message(f"Disconnected from MCP server: {name}").send()


@cl.step(type="tool")
async def execute_tool(tool_name: str, tool_input: Dict[str, Any]):
    """Execute an MCP tool directly via MCP protocol.
    
    Chainlit's @cl.step decorator automatically handles displaying this
    as a collapsible tool step in the UI with proper formatting.
    """
    logger.info(f"Executing MCP tool: {tool_name} with input: {tool_input}")
    mcp_name = None
    mcp_tools = cl.user_session.get("mcp_tools", {})

    # Find which MCP connection provides this tool
    for conn_name, tools in mcp_tools.items():
        if any(tool["name"] == tool_name for tool in tools):
            mcp_name = conn_name
            break

    if not mcp_name:
        logger.error(f"Tool '{tool_name}' not found in any connected MCP server")
        return {"error": f"Tool '{tool_name}' not found in any connected MCP server"}

    try:
        # Get the MCP session for this connection
        mcp_session_result = cl.context.session.mcp_sessions.get(mcp_name)
        
        if mcp_session_result is None:
            logger.error(f"No MCP session found for connection '{mcp_name}'")
            return {"error": f"No MCP session found for connection '{mcp_name}'"}
        
        # mcp_sessions.get returns a tuple of (session, connection_name)
        mcp_session, _ = mcp_session_result
        
        if mcp_session is None:
            logger.error(f"MCP session is None for connection '{mcp_name}'")
            return {"error": f"MCP session is None for connection '{mcp_name}'"}
        
        # Call the tool via MCP protocol
        logger.info(f"Calling MCP tool '{tool_name}' on connection '{mcp_name}'")
        result = await mcp_session.call_tool(tool_name, tool_input)
        logger.info(f"MCP tool '{tool_name}' executed successfully")
        return result
    except Exception as e:
        logger.error(f"Error calling MCP tool '{tool_name}': {str(e)}", exc_info=True)
        return {"error": f"Error calling tool '{tool_name}': {str(e)}"}


class StreamingToolCallAccumulator:
    """Accumulates streaming tool calls that arrive across multiple chunks."""
    
    def __init__(self):
        self.tool_calls = []
    
    def process_delta(self, delta_tool_calls):
        """Process tool_calls from a streaming delta chunk.
        
        Tool calls arrive incrementally:
        - First chunk: tool[0].function.name
        - Second chunk: tool[0].function.arguments (partial)
        - Later chunks: more arguments (concatenate with +=)
        """
        if not delta_tool_calls:
            return
        
        for delta_tool_call in delta_tool_calls:
            tc_id = delta_tool_call.index
            
            # Ensure we have enough slots in the list
            while tc_id >= len(self.tool_calls):
                self.tool_calls.append({"name": "", "arguments": ""})
            
            # Accumulate function name (usually arrives in first chunk)
            if delta_tool_call.function.name:
                self.tool_calls[tc_id]["name"] = delta_tool_call.function.name
            
            # Accumulate arguments (arrives across multiple chunks, concatenate)
            if delta_tool_call.function.arguments:
                self.tool_calls[tc_id]["arguments"] += delta_tool_call.function.arguments
    
    def get_completed_tool_calls(self):
        """Get tool calls that have both name and arguments."""
        return [tc for tc in self.tool_calls if tc["name"] and tc["arguments"]]


async def stream_llm_response(client, request_params: Dict[str, Any]):
    """Stream an LLM response, yielding text tokens and tool calls.
    
    This is an async generator that yields:
    - Individual text tokens as they arrive (for real-time UI display)
    - After streaming completes: tuple of (text_buffer, tool_calls)
    
    Tool calls are accumulated throughout streaming and yielded as final result.
    This matches the walkthrough pattern of accumulating tools across all chunks.
    """
    accumulator = StreamingToolCallAccumulator()
    text_buffer = ""
    
    # Enable streaming in request params
    request_params["stream"] = True
    
    try:
        stream = await client.chat.completions.create(**request_params)
        
        async for chunk in stream:
            if not chunk.choices:
                continue
            
            delta = chunk.choices[0].delta
            
            # Process text content - yield immediately for UI streaming
            # Handle both content and reasoning_content for SmolLM3 thinking mode
            if delta.content:
                text_buffer += delta.content
                yield ("text", delta.content)  # Yield as text token
            elif hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                text_buffer += delta.reasoning_content
                yield ("text", delta.reasoning_content)  # Yield reasoning content as text
            
            # Accumulate tool calls across all chunks - don't yield yet
            if delta.tool_calls:
                accumulator.process_delta(delta.tool_calls)
        
        # After stream completes, yield all accumulated tool calls
        # This ensures tool calls are only processed when fully complete
        yield ("tool_calls", accumulator.tool_calls)
    
    except Exception as e:
        logger.error(f"Error during LLM streaming: {str(e)}")
        raise


@cl.on_message
async def on_message(message: cl.Message):
    """Handle messages and intercept MCP tool calls from LLM responses.
    
    Chainlit detects tool_calls in LLM responses and this handler
    processes them, executing tools via MCP protocol.
    """
    # This handler is called AFTER the LLM response is generated
    # If the message has tool calls, Chainlit provides them here
    # We delegate the actual chat processing to chat.py
    # Tool execution happens automatically via Chainlit's instrumentation
    pass