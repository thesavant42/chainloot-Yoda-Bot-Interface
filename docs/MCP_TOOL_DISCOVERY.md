# MCP Tool Discovery and Execution

## Overview

This application implements **MCP (Model Context Protocol) tool discovery** to enable the LLM to automatically discover and use tools from connected MCP servers. This is NOT OpenAI tool functions - it uses the MCP standard protocol.

## Architecture

```
┌─────────────────┐
│  MCP Servers    │  (Context7, Home Assistant, etc.)
│  (SSE/Stdio)    │
└────────┬────────┘
         │
         │ JSON-RPC (tools/list, tools/call)
         │
┌────────▼────────┐
│   Chainlit UI   │
│  @on_mcp_connect│
└────────┬────────┘
         │
         │ Store tools in session
         │
┌────────▼────────┐
│  lib/mcp_handler│
│  - store_mcp_tools()
│  - get_mcp_tools_for_llm()
│  - execute_mcp_tool()
└────────┬────────┘
         │
         │ Tools formatted for LLM
         │
┌────────▼────────┐
│   lib/chat.py   │
│  LLM Request    │
│  with tools=[]  │
└────────┬────────┘
         │
         │ OpenAI-compatible API
         │
┌────────▼────────┐
│  Local Model    │
│ (Ollama/LM      │
│  Studio + MCP)  │
└─────────────────┘
```

## How It Works

### 1. MCP Connection and Tool Discovery

When a user connects an MCP server via the Chainlit UI:

```python
@cl.on_mcp_connect
async def on_mcp_connect(connection, session: ClientSession):
    # Discover available tools from MCP server
    result = await session.list_tools()
    tools = [{
        "name": t.name,
        "description": t.description,
        "input_schema": t.inputSchema,
    } for t in result.tools]
    
    # Store in session
    store_mcp_tools(connection.name, tools)
```

**Location:** `app.py` lines 81-92

### 2. Tool Storage

Tools are stored in the user session keyed by connection name:

```python
{
    "mcp_tools": {
        "context7": [
            {
                "name": "search_docs",
                "description": "Search documentation",
                "input_schema": {...}
            }
        ],
        "home-assistant": [...]
    }
}
```

**Location:** `lib/mcp_handler.py` function `store_mcp_tools()`

### 3. Tool Formatting for LLM

When the LLM is called, tools are retrieved and formatted in OpenAI function calling format:

```python
def get_mcp_tools_for_llm() -> list:
    """Convert MCP tools to OpenAI function format"""
    tools = []
    for connection_name, tool_list in mcp_tools.items():
        for tool in tool_list:
            tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"]
                }
            })
    return tools
```

**Location:** `lib/mcp_handler.py` function `get_mcp_tools_for_llm()`

### 4. LLM Request with Tools

The chat processor adds tools to the LLM request:

```python
request_params = {
    "model": selected_model,
    "messages": messages,
    "temperature": llm_temp,
    "max_tokens": max_tokens,
}

# Add MCP tools if available
mcp_tools = get_mcp_tools_for_llm()
if mcp_tools:
    request_params["tools"] = mcp_tools
    request_params["tool_choice"] = "auto"
```

**Location:** `lib/chat.py` in `ChatProcessor.process_user_input_and_respond()`

### 5. Tool Call Detection and Execution

When the LLM responds with tool calls:

```python
if choice.finish_reason == 'tool_calls':
    tool_calls = choice.message.tool_calls
    
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        
        # Execute via MCP
        tool_result = await execute_mcp_tool(tool_name, tool_args)
        
        # Add result to conversation
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": tool_result
        })
```

**Location:** `lib/chat.py` in the LLM call loop

### 6. Tool Execution Routing

The tool executor finds the correct MCP session and executes:

```python
async def execute_mcp_tool(tool_name: str, tool_arguments: dict) -> str:
    # Find which MCP connection owns this tool
    mcp_connection_name = find_connection_for_tool(tool_name)
    
    # Get the MCP session
    mcp_session, _ = cl.context.session.mcp_sessions[mcp_connection_name]
    
    # Execute via MCP protocol
    result = await mcp_session.call_tool(tool_name, tool_arguments)
    return result
```

**Location:** `lib/mcp_handler.py` function `execute_mcp_tool()`

### 7. Iterative Conversation Loop

The system supports multi-turn tool calling:

1. LLM receives user message + available tools
2. LLM decides to call tool(s)
3. Tools are executed via MCP
4. Results are added to conversation
5. LLM is called again with updated context
6. Repeat until LLM provides final answer (max 5 iterations)

## Configuration

### Enable MCP in Chainlit

File: `.chainlit/config.toml`

```toml
[features.mcp]
enabled = true

[features.mcp.sse]
enabled = true

[features.mcp.stdio]
enabled = true
allowed_executables = ["npx", "uvx", "python"]
```

### Connect MCP Servers

MCP servers are connected via the Chainlit UI:
1. Click "Add MCP Connection" button
2. Choose connection type (SSE or Stdio)
3. Enter server details
4. Tools are automatically discovered

## Key Differences from OpenAI Tool Functions

| Aspect | OpenAI Functions | MCP Tools |
|--------|-----------------|-----------|
| Discovery | Static (hardcoded) | Dynamic (discovered at runtime) |
| Execution | Python functions | JSON-RPC to external servers |
| Protocol | OpenAI-specific | Standardized MCP (JSON-RPC 2.0) |
| Transport | N/A | SSE, HTTP, Stdio |
| Extensibility | Limited to app code | Any MCP-compatible server |

## Debugging

### Enable Debug Logging

The code includes comprehensive logging:

```python
logger.info(f"Stored {len(tools)} MCP tools for connection: {connection_name}")
logger.info(f"Prepared {len(tools)} MCP tools for LLM: {tool_names}")
logger.info(f"Executing MCP tool '{tool_name}' with args: {tool_arguments}")
```

### Check Tool Discovery

In the Chainlit app, after connecting an MCP server, check the logs:

```
INFO: Stored 5 MCP tools for connection: context7
INFO: Added 5 MCP tools to LLM request
```

### Verify Tool Execution

When the LLM calls a tool:

```
INFO: Model requested 1 tool calls
INFO: Executing tool: search_docs
INFO: Tool search_docs executed, result added to conversation
```

## Troubleshooting

### Tools Not Discovered

- Check MCP server is running and accessible
- Verify connection details in UI
- Check `.chainlit/config.toml` has MCP enabled
- Look for errors in `@cl.on_mcp_connect` handler

### LLM Not Using Tools

- Verify `tools` parameter is added to request (check logs)
- Ensure local model platform supports MCP
- Try adding more explicit instructions in system prompt
- Check model supports function calling

### Tool Execution Fails

- Verify MCP session exists in `cl.context.session.mcp_sessions`
- Check tool arguments match input schema
- Review tool error messages in logs
- Test tool execution directly via MCP

## Future Enhancements

- [ ] Persistent conversation history across messages
- [ ] Tool execution visualization in UI
- [ ] Automatic retry on tool failures
- [ ] Tool execution caching
- [ ] Support for streaming tool responses
