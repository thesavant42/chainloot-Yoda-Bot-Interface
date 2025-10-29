# MCP Integration Plan

## Goal

I want to implement Chainlit's MCP https://docs.chainlit.io/advanced-features/mcp

## MCP - Mondel Context Protocol 
- Enables LLMs to access data hosted by User or external services
- The Model Context Protocol (MCP) allows servers to expose tools that can be invoked by language models. 
- Tools enable models to interact with external systems, such as querying databases, calling APIs, or performing computations. 
- Each tool is uniquely identified by a name and includes metadata describing its schema.
- They are not meant to be installed in the App, or in the Middlewear, but in the User's browser and on their workstation. The React UI widget allows users to select which tools to enable the model to access, and toggle them as needed. Toggling a tool to enabled allows its tools to be advertised to the model. The model discovers the tools as needed based upon their use case.


## Chainlit and MCP

- Chainlit has native integrations for configuring MCP, they are detailed in https://docs.chainlit.io/advanced-features/mcp
- MCP itself, **a model and platform agnostic** standard, is detailed here: https://modelcontextprotocol.io/specification/2025-06-18/server/tools
- MCP is based on JSON RPC, and as such will exoect JSON
- It is the responsibility of the model to generate properly formatted tool requests. It is the app's responsibility to consusme and to create properly formatted tool requests

## Uer Interaction Model

- Tools in MCP are designed to be model-controlled, meaning that the language model can discover and invoke tools automatically based on its contextual understanding and the user’s prompts.
- However, implementations are free to expose tools through any interface pattern that suits their needs—the protocol itself does not mandate any specific user interaction model.

I will avoid copy pasting the whole article, but read this for implementation details: https://docs.chainlit.io/advanced-features/mcp

Basically, the important things to note are that
1. MCP is an open specification and should not be implimented in a vendor-specific way
2. Chainlit does all of the hard work, we just need to integrate the tool calls into the chat message workflow.

Tool responses should not be passed on as is to the user, they are instead treated like system messages or reasoning blocks, collapsed from view of the user. The model interprets the results and then responds in natural language to the user. This also helps unwanted characters avoid being sent to the text-to-speech function.

- An example implementation of MCP in the chainlit cookbook repository - https://github.com/Chainlit/cookbook/tree/main/mcp-linear
    - Dont follow as a recipe, but read for a higher level understanding how how the part fit together.
    - https://raw.githubusercontent.com/Chainlit/cookbook/refs/heads/main/mcp-linear/app.py
    - This example shows how to use the chat message flow to integrate mcp calling
- MCP support through `@cl.on_mcp_connect` and `@cl.on_mcp_disconnect`

## TASK: Create MCP Library

- Should handle all mcp functionality and keep app.py lean
- Should implement tool discovery
- Should NOT try to implement more than the bare mninimum. Let MCP and Chainlit do the work!
- Less is more!
1. Use context7 to update your docs for model context protocol and chainlit
2. Q: What are the touch points that we need to interact with in the application so that our queries become bot tool requests?
    A: Based on analysis of Chainlit's MCP documentation and the cookbook example:
    
    **Primary Touch Points:**
    - **app.py**: Add `@cl.on_mcp_connect` and `@cl.on_mcp_disconnect` handlers to manage MCP connection lifecycle
    - **lib/chat.py**: Modify `ChatProcessor.process_user_input_and_respond()` to:
      - Include MCP tools in LLM calls alongside system messages
      - Handle tool calling responses from the LLM
      - Use `@cl.step(type="tool")` decorated function for tool execution
      - Route tool results back through the LLM for natural language response
    - **User Session**: Store discovered MCP tools using `cl.user_session.get("mcp_tools", {})`
    
    **Message Flow:**
    User Input → LLM (with tools) → Tool Calls (if needed) → Tool Results → LLM (interpret results) → Natural Language Response → TTS

3. The chat logic currently has a function to attempt to "Clean" the output of characters that may be harmful to text to speech audio generation. Be careful that they are not applied to MCP messages, or they will break the formatting/crash the application.
    
    **Critical Note**: MCP tool responses should NOT be processed by TTS. They are intermediate results that the LLM interprets before generating the final user-facing response. Only the final LLM response should go through `process_message_for_tts()`.

### Testing: I have installed the "everything" mcp server, we can use this to test our integration: https://github.com/modelcontextprotocol/servers/tree/main/src/everything
 - This lets us use diagnostic information
- Ask clarifying questions, let's get this right in the planning phase

## DETAILED IMPLEMENTATION CHECKLIST

### Task 1: Create MCP Library Module
**File**: `lib/mcp_handler.py`
- **Purpose**: Centralize all MCP functionality following single responsibility principle
- **Functions needed**:
  - `store_mcp_tools(connection_name: str, tools: List[Dict])` - Store tools in user session
  - `get_all_mcp_tools() -> List[Dict]` - Retrieve all tools for LLM
  - `find_mcp_for_tool(tool_name: str) -> str` - Find which MCP connection owns a tool
  - `call_mcp_tool(tool_name: str, tool_input: Dict) -> str` - Execute tool via MCP session
- **Citation**: Based on Chainlit MCP docs pattern from `/chainlit/docs`

### Task 2: Add MCP Connection Handlers  
**File**: `app.py`
- **Add handlers**:
  ```python
  @cl.on_mcp_connect
  async def on_mcp_connect(connection, session: ClientSession):
      # List tools, store in session via mcp_handler
  
  @cl.on_mcp_disconnect  
  async def on_mcp_disconnect(name: str, session: ClientSession):
      # Clean up connection tools
  ```
- **Citation**: Required by Chainlit MCP specification `/chainlit/docs` - "This handler is required for MCP to work"

### Task 3: Integrate Tool Calling in Chat Flow
**File**: `lib/chat.py`
- **Modify**: `ChatProcessor.process_user_input_and_respond()`
- **Changes**:
  - Add tools to LLM request: `tools=get_all_mcp_tools()`
  - Handle tool calling responses with while loop (like cookbook example)
  - Use `@cl.step(type="tool")` for tool execution 
  - Route tool results back to LLM for interpretation
- **Citation**: Pattern from `/chainlit/cookbook` MCP Linear example

### Task 4: Prevent TTS Processing of Tool Responses
**File**: `lib/chat.py` 
- **Ensure**: Tool responses don't go through `generate_audio_response()`
- **Method**: Only process final LLM "Assistant" response (after tool calling loop) and after the model has interpreted the results, ok through TTS pipeline
- **Reason**: Tool responses are JSON/structured data, not natural language for users

### Task 5: Test MCP Integration (to be done by User)
- **Using**: "everything" MCP server (already installed)
- **Verify**:
  - Tool discovery works via MCP connection UI
  - Tools appear in LLM context  
  - Tool calling executes without errors
  - Results interpreted correctly by LLM
  - Final response goes through TTS normally
  - No breaking of existing chat functionality

## COMPILATION TESTS (All Passed ✅)

**Navigate to chainlit directory first:**
```powershell
cd "c:\Users\jbras\GitHub\chainloot-Yoda-Bot-Interface\docker\chainloot\chainlit"
```

**Test file compilation:**
```powershell
# Test mcp_handler.py
python -m py_compile lib/mcp_handler.py

# Test chat.py  
python -m py_compile lib/chat.py

# Test app.py
python -m py_compile app.py
```

**Test syntax validation:**
```powershell
# Test mcp_handler.py syntax
python -c "import ast; ast.parse(open('lib/mcp_handler.py').read()); print('MCP handler syntax OK')"

# Test chat.py syntax
python -c "import ast; ast.parse(open('lib/chat.py').read()); print('Chat.py syntax OK')"

# Test app.py syntax  
python -c "import ast; ast.parse(open('app.py').read()); print('App.py syntax OK')"
```

**Test MCP import availability:**
```powershell
python -c "from mcp import ClientSession; print('MCP import successful')"
```

**Results:**
- ✅ All files compile without syntax errors
- ✅ All Python syntax is valid 
- ✅ MCP ClientSession import works correctly
- ✅ Ready for runtime testing

5. Review the document with me
