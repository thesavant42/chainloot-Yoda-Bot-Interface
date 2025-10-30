
# Example MCP Flow for Chainlit Applications

This is an example flow, fully functional of mcp tool calling using chainlit and lm studio (ollama will also be compatible)

Don't copy as is, but review the analysis to incorporate these patterns into the main chainlit application logic.

This is a section by section walthrough of the code at https://github.com/AI-Engineer-Skool/local-ai-mcp-chainlit/blob/main/app.py. The entire code is pasted in full at the botto of the report.

## Section 1: Import and Setup

```python
from openai import AsyncOpenAI
import chainlit as cl
from typing import Dict, Any, List
from mcp import ClientSession
from mcp.types import CallToolResult, TextContent

LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
LM_STUDIO_API_KEY = "lm-studio"
client = AsyncOpenAI(base_url=LM_STUDIO_BASE_URL, api_key=LM_STUDIO_API_KEY)

cl.instrument_openai()

settings = {
    "model": "local-model",
    "temperature": 0.3,
    "stream": True,
}

mcp_tools_cache = {}

```


### What's happening here:

1. Creates an AsyncOpenAI client but points it to LM Studio (not OpenAI) at localhost:1234/v1
2. cl.instrument_openai() - This is the CRITICAL line. It tells Chainlit to intercept ALL calls to the AsyncOpenAI - client and:
    - Capture outgoing requests
    - Capture responses
    - When tool_calls appear in responses, automatically route them through Chainlit's MCP system
3. stream: True in settings - ALWAYS streams responses
4. mcp_tools_cache - Local dict to track which tools came from which MCP connection

## SECTION 2: Chat Start Handler

```python
@cl.on_chat_start
async def start():
    cl.user_session.set(
        "message_history",
        [
            {
                "role": "system",
                "content": "You are a helpful AI assistant running locally via LM Studio. You can access tools using MCP servers.",
            }
        ],
    )

    await cl.Message(
        content="Welcome! I'm using a local model running in LM Studio with MCP integration. Make sure that: \n"
        "1. LM Studio is running \n"
        "2. A default model is loaded \n"
        "3. The LM Studio server has started \n"
    ).send()
```

### What's happening:

- 1. @cl.on_chat_start - This fires when a user opens a new chat session
- 2. message_history - Initialized with a system prompt that tells the model "you can access tools using MCP servers"
- 3. cl.user_session.set() - Stores the message history in the session so it persists across messages
- 4. Sends a welcome message to the user

### Key point: 
The system prompt explicitly tells the LLM that tools are available. This is important because without this, the model won't even try to use tools.

## SECTION 3: MCP Connection Handler

```python
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

```

### What's happening:


- 1. @cl.on_mcp_connect - Fires when an MCP server connects
session.list_tools() - Asks the MCP server "what tools do you have?"
- 2. Extracts each tool's name, description, and input_schema (how to call it)
- 3. Stores tools in two places:
        - mcp_tools_cache[connection.name] - for quick lookup
        - cl.user_session.get("mcp_tools") - so they persist across messages

**Key:** Tools are now available in the session

**Key point:** By the time a user sends a message, all connected MCP servers have already registered their tools.

## SECTION 4: MCP Disconnect Handler

```python @cl.on_mcp_disconnect
async def on_mcp_disconnect(name: str, session: ClientSession):
    if name in mcp_tools_cache:
        del mcp_tools_cache[name]

    mcp_tools = cl.user_session.get("mcp_tools", {})
    if name in mcp_tools:
        del mcp_tools[name]
        cl.user_session.set("mcp_tools", mcp_tools)

    await cl.Message(f"Disconnected from MCP server: {name}").send()

```

### What's happening:

- @cl.on_mcp_disconnect - Fires when an MCP server disconnects
- Removes that server's tools from both the cache and the session
- Notifies the user

**Key point:** Simple cleanup. Tools from that MCP server are no longer available.

## SECTION 5: Execute Tool (The MCP Bridge)

```python
@cl.step(type="tool")
async def execute_tool(tool_name: str, tool_input: Dict[str, Any]):
    print("Executing tool:", tool_name)
    print("Tool input:", tool_input)
    mcp_name = None
    mcp_tools = cl.user_session.get("mcp_tools", {})

    for conn_name, tools in mcp_tools.items():
        if any(tool["name"] == tool_name for tool in tools):
            mcp_name = conn_name
            break

    if not mcp_name:
        return {"error": f"Tool '{tool_name}' not found in any connected MCP server"}

    mcp_session, _ = cl.context.session.mcp_sessions.get(mcp_name)

    try:
        result = await mcp_session.call_tool(tool_name, tool_input)
        return result
    except Exception as e:
        return {"error": f"Error calling tool '{tool_name}': {str(e)}"}
```

### What's happening:

- @cl.step(type="tool") - Wraps this as a visible "tool execution" step in Chainlit
- Find which MCP server has this tool - loops through all stored MCP tools to find which one has the requested tool name
- cl.context.session.mcp_sessions.get(mcp_name) - Gets the MCP ClientSession for that server
- await mcp_session.call_tool(tool_name, tool_input) - THE KEY LINE. Actually executes the tool via MCP protocol
- Returns the result (or error if something fails)

**Key point: This is the BRIDGE between LM Studio's tool request and the actual MCP server. When the LLM says "call this tool", this function executes it.

## SECTION 6: Helper Functions

```python
async def format_tools_for_openai(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    openai_tools = []

    for tool in tools:
        openai_tool = {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"],
            },
        }
        openai_tools.append(openai_tool)

    return openai_tools
```
### What's happening:

- Converts MCP tool format → OpenAI tool format
- MCP has name, description, inputSchema
- OpenAI expects type: "function" with nested function: { name, description, parameters }

```python
def format_calltoolresult_content(result):
    """Extract text content from a CallToolResult object."""
    text_contents = []

    if isinstance(result, CallToolResult):
        for content_item in result.content:
            if isinstance(content_item, TextContent):
                text_contents.append(content_item.text)

    if text_contents:
        return "\n".join(text_contents)
    return str(result)
```

### What's happening:

- MCP tool results come back as CallToolResult objects with a list of content items
- Some might be TextContent, some might be other types
- This extracts just the text and joins it
- Used later when formatting the tool result to send back to the LLM

## SECTION 7: The Main Message Handler - PART A (Setup)

```python
@cl.on_message
async def on_message(message: cl.Message):
    message_history = cl.user_session.get("message_history", [])
    message_history.append({"role": "user", "content": message.content})

    try:
        # Initial message for the first assistant response
        initial_msg = cl.Message(content="")
        await initial_msg.send()

        mcp_tools = cl.user_session.get("mcp_tools", {})
        all_tools = []
        for connection_tools in mcp_tools.values():
            all_tools.extend(connection_tools)

        chat_params = {**settings}
        if all_tools:
            openai_tools = await format_tools_for_openai(all_tools)
            chat_params["tools"] = openai_tools
            chat_params["tool_choice"] = "auto"
            print("Tools passed:", openai_tools)
```

### What's happening:

- `@cl.on_message` - Fires when user sends a message
- Get message history from the session and add the user's new message to it
- Create an empty message to stream the response into
- Gather ALL tools from all connected MCP servers into one list
- Format tools for OpenAI - convert from MCP format to OpenAI format
- Add tools to the LLM request params:
    - "tools": openai_tools - here are the tools available
    - "tool_choice": "auto" - let the model decide if it needs to call a tool

**Key point:** Tools are now being SENT to the LLM. The model will see them and CAN choose to use them.

## SECTION 7B: The Streaming Loop - THE CRITICAL PART

```python
        stream = await client.chat.completions.create(
            messages=message_history, **chat_params
        )

        initial_response = ""
        tool_calls = []

        async for chunk in stream:
            delta = chunk.choices[0].delta
            print(delta)

            if token := delta.content or "":
                initial_response += token
                await initial_msg.stream_token(token)

            if delta.tool_calls:
                for tool_call in delta.tool_calls:
                    tc_id = tool_call.index
                    if tc_id >= len(tool_calls):
                        tool_calls.append({"name": "", "arguments": ""})

                    if tool_call.function.name:
                        tool_calls[tc_id]["name"] = tool_call.function.name

                    if tool_call.function.arguments:
                        tool_calls[tc_id]["arguments"] += tool_call.function.arguments
```

**THIS IS THE KEY DIFFERENCE. Let me break it down slowly:**

1. `stream = await client.chat.completions.create(...)` - Makes the API call. Because `stream: True`, it returns a stream, not a complete response.
2. `async for chunk in stream`: - ITERATES through each chunk as it arrives. This is streaming.
3. `delta = chunk.choices[0].delta` - Each chunk has a delta object with PARTIAL changes
    - Not the full message
    - Just the new part
4. `if token := delta.content or ""`: - Checks if this chunk has text content
    - If yes, accumulate it into `initial_response`
    - Stream it to the UI with `await initial_msg.stream_token(token)`
    - This makes text appear word-by-word
5. `if delta.tool_calls`: - THE CRITICAL CHECK. Only in STREAMING do tool calls arrive in `delta.tool_calls`
    - In a non-streaming response, tool calls are in the final `message.tool_calls`
    - In streaming, they arrive incrementally across chunks
    - Tool calls can be PARTIAL (function name and arguments arrive in separate chunks)
6. `tc_id = tool_call.index` - Tool calls are numbered (0, 1, 2, etc.)
    - If this is the first chunk of a tool call, create a new entry
    - `if tc_id >= len(tool_calls): tool_calls.append({"name": "", "arguments": ""})`
7. `if tool_call.function.name`: - If this chunk has the function name, store it
8. `if tool_call.function.arguments`: - If this chunk has arguments, ACCUMULATE them
    `tool_calls[tc_id]["arguments"] += tool_call.function.arguments` - NOTE THE `+=`
    - Arguments arrive as strings, one piece at a time
    - You have to concatenate them together

**Key point:** This is why your non-streaming approa

## SECTION 8: After Streaming Ends - Add Initial Response to History

```python
        # First, update message history with the initial response
        if initial_response.strip():
            message_history.append({"role": "assistant", "content": initial_response})
```

### What's happening:

- After the stream finishes, if the assistant produced any text (not just tool calls), add it to message history
- This creates the conversational record

## SECTION 9: Tool Execution Phase - THE LOOP

```python
        # Process tool calls if any
        if tool_calls:
            for tool_call in tool_calls:
                tool_name = tool_call["name"]
                try:
                    import json

                    tool_args = json.loads(tool_call["arguments"])
```

### What's happening:

- If the LLM made any tool calls during streaming, process each one
- Extract the tool name and arguments
- `json.loads(tool_call["arguments"])` - The arguments came in as a JSON STRING from the LLM
    - Parse it into a Python dict so we can pass it to the tool

# Section 9B: Add Tool Call to History

```python
                    # Add the tool call to message history
                    message_history.append(
                        {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": f"call_{len(message_history)}",
                                    "type": "function",
                                    "function": {
                                        "name": tool_name,
                                        "arguments": tool_call["arguments"],
                                    },
                                }
                            ],
                        }
                    )
```

### What's happening:

- Add a message to history that says "the assistant called this tool"
- Format it in OpenAI's conversation format:
    "role": "assistant"
    "content": None (no text, just a tool call)
    "tool_calls" array with the function name and arguments
- This creates the proper conversation record so the LLM knows it made this call

## 9C Execute the tool via MCP

```python
                    # Execute the tool in a step
                    with cl.Step(name=f"Executing tool: {tool_name}", type="tool"):
                        tool_result = await execute_tool(tool_name, tool_args)
```

### What's happening:

- `cl.Step(name=..., type="tool")` - Creates a visible step in Chainlit showing tool execution
- `await execute_tool(tool_name, tool_args)` - Calls the function we defined earlier
    - This finds the right MCP server
    - Calls mcp_session.call_tool(tool_name, tool_args)
    - Returns the result

## SECTION 9D: Format and Display Tool Result

```python
                    # Format the tool result content
                    tool_result_content = format_calltoolresult_content(tool_result)

                    # Display the tool result to the user
                    tool_result_msg = cl.Message(
                        content=f"Tool Result from {tool_name}:\n{tool_result_content}",
                        author="Tool",
                    )
                    await tool_result_msg.send()
```

### What's happening:

- `format_calltoolresult_content(tool_result)` - Extract text from the MCP CallToolResult
- Send a message to the user showing what the tool returned
- `author="Tool"` - makes it clear this came from a tool, not the assistant

## 9E: Add tool result to history

```python
                    # Add the tool result to message history
                    message_history.append(
                        {
                            "role": "tool",
                            "tool_call_id": f"call_{len(message_history)-1}",
                            "content": tool_result_content,
                        }
                    )
```

### What's happening:

- Add the tool result to the conversation history
- Format: `"role": "tool"` with the result content
- This is in OpenAI's format for tool results in conversations

## SECTION 10: Follow-up Response

```python
                    # Create a new message for the follow-up response
                    follow_up_msg = cl.Message(content="")
                    await follow_up_msg.send()

                    # Stream the follow-up response
                    follow_up_stream = await client.chat.completions.create(
                        messages=message_history, **settings
                    )

                    follow_up_text = ""
                    async for chunk in follow_up_stream:
                        if token := chunk.choices[0].delta.content or "":
                            follow_up_text += token
                            await follow_up_msg.stream_token(token)

                    # Add the follow-up response to message history
                    message_history.append(
                        {"role": "assistant", "content": follow_up_text}
                    )
```

### What's happening:

- After a tool finishes, the LLM might want to say something about the result
- Make ANOTHER streaming call to LM Studio with the UPDATED message history
    - History now includes: initial response → tool call → tool result
- Stream the follow-up response the same way as before
- Add it to message history

**Key point:** This is the agentic loop. If the tool result triggers more tool calls, they get processed again. It continues until the LLM decides to just respond with text.a

SECTION 11: Save Updated History

```python
        # Update the session message history
        cl.user_session.set("message_history", message_history)

    except Exception as e:
        error_message = f"Error: {str(e)}"
        await cl.Message(content=error_message).send()
```        

### What's happening:

- Save the updated message history back to the session
- If anything errors, catch it and show the user

## Summary: The Flow
- User sends message → added to history
- Fetch all MCP tools → format for OpenAI
- Stream response from LLM with tools available
- Iterate chunks checking for delta.tool_calls
- For each tool call:
    - Add to history
    - Execute via MCP
    - Add result to history
    - Get follow-up response
- Save updated history

The magic: `cl.instrument_openai()` + streaming + manual `delta.tool_calls` parsing + `session.call_tool()`

Appendix A:

The full applicaiton, ready to run, from github.


```python
from openai import AsyncOpenAI
import chainlit as cl
from typing import Dict, Any, List
from mcp import ClientSession
from mcp.types import CallToolResult, TextContent

LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
LM_STUDIO_API_KEY = "lm-studio"
client = AsyncOpenAI(base_url=LM_STUDIO_BASE_URL, api_key=LM_STUDIO_API_KEY)

cl.instrument_openai()

settings = {
    "model": "local-model",
    "temperature": 0.3,
    "stream": True,
}

mcp_tools_cache = {}


@cl.on_chat_start
async def start():
    cl.user_session.set(
        "message_history",
        [
            {
                "role": "system",
                "content": "You are a helpful AI assistant running locally via LM Studio. You can access tools using MCP servers.",
            }
        ],
    )

    await cl.Message(
        content="Welcome! I'm using a local model running in LM Studio with MCP integration. Make sure that: \n"
        "1. LM Studio is running \n"
        "2. A default model is loaded \n"
        "3. The LM Studio server has started \n"
    ).send()


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
    print("Executing tool:", tool_name)
    print("Tool input:", tool_input)
    mcp_name = None
    mcp_tools = cl.user_session.get("mcp_tools", {})

    for conn_name, tools in mcp_tools.items():
        if any(tool["name"] == tool_name for tool in tools):
            mcp_name = conn_name
            break

    if not mcp_name:
        return {"error": f"Tool '{tool_name}' not found in any connected MCP server"}

    mcp_session, _ = cl.context.session.mcp_sessions.get(mcp_name)

    try:
        result = await mcp_session.call_tool(tool_name, tool_input)
        return result
    except Exception as e:
        return {"error": f"Error calling tool '{tool_name}': {str(e)}"}


async def format_tools_for_openai(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    openai_tools = []

    for tool in tools:
        openai_tool = {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"],
            },
        }
        openai_tools.append(openai_tool)

    return openai_tools


def format_calltoolresult_content(result):
    """Extract text content from a CallToolResult object.

    The MCP CallToolResult contains a list of content items,
    where we want to extract text from TextContent type items.
    """
    text_contents = []

    if isinstance(result, CallToolResult):
        for content_item in result.content:
            # This script only supports TextContent but you can implement other CallToolResult types
            if isinstance(content_item, TextContent):
                text_contents.append(content_item.text)

    if text_contents:
        return "\n".join(text_contents)
    return str(result)


@cl.on_message
async def on_message(message: cl.Message):
    message_history = cl.user_session.get("message_history", [])
    message_history.append({"role": "user", "content": message.content})

    try:
        # Initial message for the first assistant response
        initial_msg = cl.Message(content="")
        await initial_msg.send()

        mcp_tools = cl.user_session.get("mcp_tools", {})
        all_tools = []
        for connection_tools in mcp_tools.values():
            all_tools.extend(connection_tools)

        chat_params = {**settings}
        if all_tools:
            openai_tools = await format_tools_for_openai(all_tools)
            chat_params["tools"] = openai_tools
            chat_params["tool_choice"] = "auto"
            print("Tools passed:", openai_tools)
        stream = await client.chat.completions.create(
            messages=message_history, **chat_params
        )

        initial_response = ""
        tool_calls = []

        async for chunk in stream:
            delta = chunk.choices[0].delta
            print(delta)

            if token := delta.content or "":
                initial_response += token
                await initial_msg.stream_token(token)

            if delta.tool_calls:
                for tool_call in delta.tool_calls:
                    tc_id = tool_call.index
                    if tc_id >= len(tool_calls):
                        tool_calls.append({"name": "", "arguments": ""})

                    if tool_call.function.name:
                        tool_calls[tc_id]["name"] = tool_call.function.name

                    if tool_call.function.arguments:
                        tool_calls[tc_id]["arguments"] += tool_call.function.arguments

        # First, update message history with the initial response
        if initial_response.strip():
            message_history.append({"role": "assistant", "content": initial_response})

        # Process tool calls if any
        if tool_calls:
            for tool_call in tool_calls:
                tool_name = tool_call["name"]
                try:
                    import json

                    tool_args = json.loads(tool_call["arguments"])

                    # Add the tool call to message history
                    message_history.append(
                        {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": f"call_{len(message_history)}",
                                    "type": "function",
                                    "function": {
                                        "name": tool_name,
                                        "arguments": tool_call["arguments"],
                                    },
                                }
                            ],
                        }
                    )

                    # Execute the tool in a step
                    with cl.Step(name=f"Executing tool: {tool_name}", type="tool"):
                        tool_result = await execute_tool(tool_name, tool_args)

                    # Format the tool result content
                    tool_result_content = format_calltoolresult_content(tool_result)

                    # Display the tool result to the user
                    tool_result_msg = cl.Message(
                        content=f"Tool Result from {tool_name}:\n{tool_result_content}",
                        author="Tool",
                    )
                    await tool_result_msg.send()

                    # Add the tool result to message history
                    message_history.append(
                        {
                            "role": "tool",
                            "tool_call_id": f"call_{len(message_history)-1}",
                            "content": tool_result_content,
                        }
                    )

                    # Create a new message for the follow-up response
                    follow_up_msg = cl.Message(content="")
                    await follow_up_msg.send()

                    # Stream the follow-up response
                    follow_up_stream = await client.chat.completions.create(
                        messages=message_history, **settings
                    )

                    follow_up_text = ""
                    async for chunk in follow_up_stream:
                        if token := chunk.choices[0].delta.content or "":
                            follow_up_text += token
                            await follow_up_msg.stream_token(token)

                    # Add the follow-up response to message history
                    message_history.append(
                        {"role": "assistant", "content": follow_up_text}
                    )

                except Exception as e:
                    error_msg = f"Error executing tool {tool_name}: {str(e)}"
                    error_message = cl.Message(content=error_msg)
                    await error_message.send()

        # Update the session message history
        cl.user_session.set("message_history", message_history)

    except Exception as e:
        error_message = f"Error: {str(e)}"
        await cl.Message(content=error_message).send()

        troubleshooting = (
            "Troubleshooting tips:\n"
            "1. Verify LM Studio is running\n"
            "2. Check that a model is loaded\n"
            "3. Confirm the LM Studio server is started on port 1234\n"
            "4. Make sure the model supports the OpenAI chat completions API format with tools"
        )
        await cl.Message(content=troubleshooting).send()


if __name__ == "__main__":
    print("Starting Chainlit app with LM Studio and MCP integration...")
```
