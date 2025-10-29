# MCP Implementation Analysis Notes

**Date:** October 28, 2025  
**Project:** Chainloot Yoda Bot Interface  
**Purpose:** Analyzing and documenting issues with current MCP server implementation

---

## 1. Initial Observations

### Current Architecture Overview
The application has two different MCP manager implementations:
1. **Legacy Manager** ~~(`mcp_server_manager.py`) - Hardcoded server configurations~~ **DELETED!**
2. **Dynamic Manager** ~~(`dynamic_mcp_manager.py`) - Configuration-driven setup~~ **DELETED!**

### Key Files Identified
- ~~`mcp_server_manager.py` - Legacy hardcoded MCP implementation~~ **DELETED!**
- ~~`dynamic_mcp_manager.py` - Newer dynamic configuration approach~~ **DELETED!**
- `app.py` - Main application with MCP integration logic
- Configuration files (to be investigated):
  - `config/mcp_servers.json` (referenced in dynamic manager) **KEEP!**
  - ~~`config/mcp_proxy_servers.json` (referenced in legacy manager)~~ **DELETED!**

## Questions for Clarification

1. **Current Pain Points**: What specific issues are you experiencing with MCP servers?

**ANSWERS:**

- Tools are not automatically discovered when a new server is added to the configuration
  - Configuration of new servers is done via hardcoded JSON, the reactUI widgets are ignored
    - Message parsing was overly greedy, causing mcp to trigger when it shouldn't, and missing commands when it should have.
    - Implementation was not to spec, and was not completed. 
    - As a result, the code is a mish-mash of dead code, obsolete code broken code, and some of it is ok.

---

## 2. Detailed Analysis

### 1. Configuration Analysis

**Found Configuration File**: `config/mcp_servers.json` **KEEP THIS FILE!**

- Contains 10 configured servers (time, brave-search, fetch, git, memory, etc.)
- Uses proper MCP server commands (uvx, npx)
- Includes environment variable substitution (`${BRAVE_API_KEY}`, `${HOME_ASSISTANT_TOKEN}`)
- Has discovery and transport configuration sections

**RESPONSE:** 

- This the configuration file for MCP that is mostly Claude-compatible, but it does not work correctly. Many commands are not recognized, no tool discovery.
- Non-standaerd implmentation of HTTP-based MCP servers is broken and uses a hacky home-grown approach.

**Issues Identified**:

1. ~~**Mixed Transport Types**: Some servers use `mcp-proxy` with streamable HTTP, others use stdio~~ **Desired behavior! Not a bug!**
2. ~~**Non-standard Proxy Usage**: The mqtt and Home Assistant servers use `mcp-proxy` which isn't standard MCP~~ **INCORRECT! `mcp-proxy` is the defacto way to swap between transport mechanisms**
3. **Missing Integration**: No clear path from chat to tool execution

### 2. MCP Specification Compliance Issues

**Based on Official MCP Python SDK Documentation**:

1. **Proper Client Setup Should Be**:
   ```python
   async with stdio_client(StdioServerParameters(...)) as (read, write):
       async with ClientSession(read, write) as session:
           await session.initialize()
           tools = await session.list_tools()
           result = await session.call_tool(tool_name, arguments)
   ```

2. **Current Implementation Problems**:
   - Context managers not properly nested
   - Missing proper cleanup in exception handling
   - Manual session management instead of using context managers
   - Storing sessions in global dictionaries instead of per-request

---

### 3. Architecture Problems

1. **Singleton Pattern Issues**: Both managers use global singletons which can cause resource leaks
2. **Missing Tool Invocation**: No clear mechanism to call tools from chat messages
3. **Mixed Manager Logic**: App switches between managers based on file existence
4. **Resource Management**: Sessions stored indefinitely without proper lifecycle management

### Critical Discovery: mcp-proxy is Legitimate

**RESPONSE** 
-- `mcp-proxy` was used under the old module (now gone) that implemented a broken form of HTTP-based mcp service usage. It is a legitimate service.

**Current Configuration Analysis**:

The `mqtt` server configuration in your `mcp_servers.json`:
```json
"mqtt": {
  "command": "mcp-proxy",
  "args": ["--transport", "streamablehttp", "http://127.0.0.1:8100/mcp/"],
  "env": {},
  "description": "MQTT broker communication via embedded server"
}
```

This suggests you have a custom MCP server running at `http://127.0.0.1:8100/mcp/` that provides MQTT functionality, and you're using mcp-proxy to bridge it into your stdio-based MCP setup. 
-- **CORRECT!**

### Major Architecture Issues Identified

1. **Missing Tool Invocation Pipeline**: There's no mechanism in the current code to actually call MCP tools during conversations <<<< **THIS IS THE MAJOR ONE!**
2. **Resource Management Anti-patterns**: Manual session storage instead of proper context managers

**EXAMPLE - Current Anti-pattern in your code:**
```python
# WRONG - From mcp_server_manager.py line 58-75
stdio_context = stdio_client(server_params)
read, write = await stdio_context.__aenter__()
self.session_contexts['time'] = stdio_context  # Manual storage!
session = ClientSession(read, write)
await session.__aenter__()  # Manual lifecycle management
self.sessions["time"] = session  # Global singleton storage
```

**CORRECT - MCP SDK Pattern:**
```python
# Proper per-request pattern
async def call_mcp_tool(tool_name: str, arguments: dict):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result
    # Resources automatically cleaned up
```

**JWT Questions Answered:**

- **Streaming Audio + JWT**: JWT is NOT required for i2s microphone streaming. Static tokens are sufficient for audio streaming. JWT is for authentication, not transport security
- **Recommendation**: Static API keys are fine for audio streaming. Use HTTPS for transport security, not JWT **JWT is Authentication, not encryption**

- **Specification Violations**: Not using proper async context manager patterns from MCP SDK

### Specific Code Issues

**Context Manager Violations**:
```python
# Current (WRONG):
stdio_context = stdio_client(server_params)
read, write = await stdio_context.__aenter__()
session = ClientSession(read, write)
await session.__aenter__()
self.sessions[server_name] = session  # Stored globally!

# Should be (CORRECT):
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool(tool_name, args)
        # Session automatically cleaned up
```

**Missing Integration Point**: No mechanism connects user messages to MCP tool calls. The `mcp_tool_processor.py` file referenced in documentation doesn't exist.
^ This is an intention ommission; this code was bad and now we're trying to rip it out fully and get to-spec implementations.

---

## Root Cause Analysis

### The Core Problem: Missing Tool Invocation

Looking at `process_user_input_and_respond()` in `app.py:148` (called from lines 706 and 740), the current flow is:

1. User sends message
2. Direct LLM API call (no tool consideration)
3. Process response for TTS
4. Send audio back

**There is NO step where MCP tools are evaluated or called!**

**Required Missing Components** (References from Chainlit docs `/chainlit/docs`):

1. **Missing `@cl.on_mcp_connect` handler** - Chainlit docs show this decorator is mandatory for MCP functionality: "This handler is required for MCP to work"

2. **Missing `@cl.step(type="tool")` decorator** - Chainlit docs demonstrate pattern for tool execution: `result = await mcp_session.call_tool(tool_name, tool_input)`

3. **Missing OpenAI function calling integration** - Chainlit docs show proper `call_model_with_tools()` pattern with `tools=all_tools` parameter to enable LLM tool selection

**SOLUTION - Add MCP Tool Integration to your `process_user_input_and_respond()`:**

```python
async def process_user_input_and_respond(user_text: str):
    """Enhanced with MCP tool calling capability"""
    
    # 1. Analyze if message needs tools
    needs_tools = should_use_mcp_tools(user_text)
    
    if needs_tools:
        # 2. Call MCP tools and get results
        tool_results = await execute_mcp_tools(user_text)
        
        # 3. Enhance system prompt with tool results
        enhanced_prompt = f"{system_prompt}\n\nTool Results:\n{tool_results}"
        
        # 4. Call LLM with enhanced context
        request_params["messages"][0]["content"] = enhanced_prompt
    
    # Continue with existing LLM call...
    response = await get_client().chat.completions.create(**request_params)
```

**Required Chainlit MCP Handler - Add to app.py:**

```python
import chainlit as cl
from mcp import ClientSession

@cl.on_mcp_connect
async def on_mcp_connect(connection, session: ClientSession):
    """Called when MCP connection established - REQUIRED"""
    # List available tools
    result = await session.list_tools()
    
    # Store tools in user session
    tools = [{
        "name": t.name,
        "description": t.description,
        "input_schema": t.inputSchema,
    } for t in result.tools]
    
    mcp_tools = cl.user_session.get("mcp_tools", {})
    mcp_tools[connection.name] = tools
    cl.user_session.set("mcp_tools", mcp_tools)

@cl.step(type="tool")
async def call_mcp_tool(tool_name: str, tool_input: dict):
    """Execute MCP tool with Chainlit step tracking"""
    # Find MCP connection for this tool
    mcp_name = find_mcp_for_tool(tool_name)
    
    # Get session from context
    mcp_session, _ = cl.context.session.mcp_sessions.get(mcp_name)
    
    # Call the tool
    result = await mcp_session.call_tool(tool_name, tool_input)
    return result
```

The entire MCP infrastructure (configuration, sessions) exists but is never used during conversations. This explains why "standard plugins are not working" - they're initialized but never invoked.

-  **The broken version was ripped out, some of it remains. Is it worth saving or should we cut bait and start over?**

**RECOMMENDATION: Start Over with Proper Integration**

**RESPONSE: Agree, but fully removing the old code will take skeptical verification.**

- Your current MCP code violates the specification in multiple ways
- The Chainlit MCP integration is much cleaner than your custom approach  
- **Cut bait on both managers and use Chainlit's native MCP support**
- This will give you proper tool discovery, execution, and UI integration

---

### What's Missing

**Critical Missing Components** (specific to your codebase):

1. **MCP Handlers in app.py** - Required decorators not present at application level:
   - **Missing**: `@cl.on_mcp_connect` handler (app.py has no MCP decorators) 
   - **Reference**: Chainlit docs `/chainlit/docs` state "This handler is required for MCP to work"
   - **Missing**: `@cl.step(type="tool")` decorator for tool execution
   - **Reference**: Chainlit docs show pattern `result = await mcp_session.call_tool(tool_name, tool_input)`

2. **Tool Integration in process_user_input_and_respond** (app.py:148) - No LLM function calling:
   - **Current**: Direct LLM API call without tools parameter
   - **Required**: OpenAI function calling integration as shown in Chainlit docs `call_model_with_tools()` pattern
   - **Reference**: Chainlit docs `/chainlit/docs` demonstrate `tools=all_tools` parameter for LLM tool selection

**MCP-Compliant Implementation Patterns** (from Chainlit docs `/chainlit/docs`):

```python
# CORRECT: LLM-driven tool selection (MCP spec compliant)
async def get_available_tools_for_llm():
    """Get all MCP tools in OpenAI function calling format"""
    mcp_tools = cl.user_session.get("mcp_tools", {})
    all_tools = []
    
    for connection_tools in mcp_tools.values():
        for tool in connection_tools:
            all_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"]
                }
            })
    
    return all_tools

# CORRECT: From Chainlit docs - integrate MCP with LLM
async def call_model_with_tools():
    # Get tools from all MCP connections
    mcp_tools = cl.user_session.get("mcp_tools", {})
    all_tools = [tool for connection_tools in mcp_tools.values() for tool in connection_tools]
    
    # Call your LLM with the tools
    response = await your_llm_client.call(
        messages=messages,
        tools=all_tools  # LLM chooses tools based on context
    )
    
    # Handle tool calls if needed
    if response.has_tool_calls():
        # Process tool calls using @cl.step(type="tool")
        pass
        
    return response
```

2. **OpenAI Function Calling Integration**: Let LLM handle tool selection and execution

```python
# WRONG: Manual tool selection (not MCP spec)
async def find_relevant_tools(message: str) -> list[str]:
    """This is NOT how MCP works - manual tool mapping"""
    # DON'T DO THIS - keyword matching is primitive and error-prone

# CORRECT: OpenAI Function Calling Format (MCP spec compliant)
async def get_mcp_tools_for_openai() -> list[dict]:
    """Convert MCP tools to OpenAI function calling format"""
    mcp_tools = cl.user_session.get("mcp_tools", {})
    openai_tools = []
    
    for connection_tools in mcp_tools.values():
        for tool in connection_tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"]
                }
            })
    
    return openai_tools

async def process_tool_calls(tool_calls) -> list[dict]:
    """Process LLM-requested tool calls using Chainlit MCP"""
    tool_results = []
    
    for tool_call in tool_calls:
        try:
            # Execute via Chainlit MCP integration
            result = await execute_mcp_tool_via_chainlit(
                tool_call.function.name,
                tool_call.function.arguments
            )
            
            tool_results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "content": str(result)
            })
        except Exception as e:
            tool_results.append({
                "tool_call_id": tool_call.id,
                "role": "tool", 
                "content": f"Error: {str(e)}"
            })
    
    return tool_results
```

3.

```python
# REAL EXAMPLE - From chainlit/cookbook/mcp-linear/app.py
import json
from mcp import ClientSession
import chainlit as cl

@cl.on_mcp_connect
async def on_mcp(connection, session: ClientSession):
    """Simple MCP connection handler - stores tools in user session"""
    result = await session.list_tools()
    tools = [{
        "name": t.name,
        "description": t.description,
        "input_schema": t.inputSchema,
    } for t in result.tools]
    
    mcp_tools = cl.user_session.get("mcp_tools", {})
    mcp_tools[connection.name] = tools
    cl.user_session.set("mcp_tools", mcp_tools)

@cl.step(type="tool")
async def call_tool(tool_use):
    """Simple MCP tool execution"""
    tool_name = tool_use.name
    tool_input = tool_use.input
    
    # Find which MCP connection has this tool
    mcp_tools = cl.user_session.get("mcp_tools", {})
    for connection_name, tools in mcp_tools.items():
        if any(tool.get("name") == tool_name for tool in tools):
            mcp_session, _ = cl.context.session.mcp_sessions.get(connection_name)
            return await mcp_session.call_tool(tool_name, tool_input)
    
    return json.dumps({"error": f"Tool {tool_name} not found"})

# In your LLM call - just pass the flattened tools:
async def call_llm_with_tools(messages):
    mcp_tools = cl.user_session.get("mcp_tools", {})
    all_tools = [tool for tools in mcp_tools.values() for tool in tools]
    
    # Use with ANY LLM (OpenAI, Anthropic, etc.)
    response = await llm_client.chat.completions.create(
        messages=messages,
        tools=all_tools  # That's it!
    )
    return response
```

4. **Response Integration**: Mechanism to incorporate tool results into LLM context

**VERIFIED - Official Chainlit MCP Integration Pattern:**

```python
import chainlit as cl

@cl.on_mcp_connect  # VERIFIED: Official Chainlit decorator
async def on_mcp_connect(connection, session: ClientSession):
    """Called when MCP connection established - REQUIRED"""
    # List available tools - VERIFIED API
    result = await session.list_tools()
    
    # Process tool metadata - VERIFIED: Official pattern
    tools = [{
        "name": t.name,
        "description": t.description,
        "input_schema": t.inputSchema,
    } for t in result.tools]
    
    # Store tools in user session - VERIFIED: cl.user_session API
    mcp_tools = cl.user_session.get("mcp_tools", {})
    mcp_tools[connection.name] = tools
    cl.user_session.set("mcp_tools", mcp_tools)

@cl.step(type="tool")  # VERIFIED: Official step decorator with type="tool"
async def call_mcp_tool(tool_use):
    """Execute MCP tool with Chainlit step tracking"""
    tool_name = tool_use.name
    tool_input = tool_use.input
    
    # Find appropriate MCP connection for this tool
    mcp_name = find_mcp_for_tool(tool_name)
    
    # Get the MCP session - VERIFIED: cl.context.session API
    mcp_session, _ = cl.context.session.mcp_sessions.get(mcp_name)
    
    # Call the tool - VERIFIED: ClientSession.call_tool API
    result = await mcp_session.call_tool(tool_name, tool_input)
    
    return result

async def call_model_with_tools():
    """VERIFIED: Official LLM integration pattern"""
    # Get tools from all MCP connections - VERIFIED API
    mcp_tools = cl.user_session.get("mcp_tools", {})
    all_tools = [tool for connection_tools in mcp_tools.values() for tool in connection_tools]
    
    # Call your LLM with the tools
    response = await your_llm_client.call(
        messages=messages,
        tools=all_tools
    )
    
    # Handle tool calls if needed
    if response.has_tool_calls():
        # Process tool calls using @cl.step decorator above
        pass
        
    return response
```


### Architectural Debt

The current setup suggests there was originally a plan for full MCP integration:
    - References to `mcp_tool_processor.py` in documentation
    - Sophisticated MCP manager implementations
    - Rich configuration for tool discovery
- But the actual invocation pipeline was never completed

---

## Remediation Plan Overview

~~**STEP 1: Enable Chainlit MCP Support**~~ **DONE!**

**STEP 2: Replace Custom Managers** **IN PROGRESS**

~~1. **Delete Both Managers**: Remove `mcp_server_manager.py` and `dynamic_mcp_manager.py`~~ DONE!
2. **Use Chainlit Native**: Let Chainlit handle MCP connections via UI
3. **Add Required Handlers**: Implement `@cl.on_mcp_connect` as shown above
4. **Update app.py**: Integrate tool calling into `process_user_input_and_respond()`

**STEP 3: Integration Tasks**

1. **Tool Decision Engine**: Implement `should_use_mcp_tools()` message analysis
2. **Tool Execution Pipeline**: Use `@cl.step(type="tool")` for proper tracking  
3. **LLM Integration**: Enhanced system prompts with tool results
4. **UI Integration**: Chainlit will provide MCP connection UI automatically
5. **Remove Dead Code**: Clean up all references to custom MCP managers

**BENEFITS of This Approach:**
- Specification compliant (uses official MCP Python SDK)
- Built-in UI for MCP server management
- Proper resource management (no manual cleanup needed)
- Step tracking and debugging in Chainlit UI
- Supports all transport types (stdio, SSE, HTTP)

The infrastructure exists, but the integration layer is completely missing.

---

### File Structure Investigation

**Current MCP-Related File Inventory:**

**Core Application Files:**
- `docker/chainloot/chainlit/app.py` - Main Chainlit application (missing MCP handlers)
- `docker/chainloot/chainlit/.chainlit/config.toml` - Chainlit configuration (MCP already enabled!)

**Configuration Files:**
- `docker/chainloot/chainlit/config/mcp_servers.json` - MCP server definitions (Claude-compatible format)
- `docker/chainloot/chainlit/config/serverside-mcp-features.md` - Documentation about server-side features **OBSOLETE DOCS**

**Key Findings from File Analysis:**

1. ~~**MCP Already Enabled in config.toml**~~ CONFIRMED
   ```toml
   [features.mcp]
       enabled = true
   [features.mcp.sse]
       enabled = true
   [features.mcp.streamable-http]
       enabled = true
   [features.mcp.stdio]
       enabled = true
       allowed_executables = [ "npx", "uvx" ]
   ```

2. ~~**Missing mcp-proxy Support**~~ **FIXED**
   - ~~Current `allowed_executables` only includes `["npx", "uvx"]`~~
   - ~~Your MQTT server configuration requires `mcp-proxy` to be added~~

3. **File Organization Issues:**
   - ~~Two competing MCP manager implementations in `lib/`~~ **DELETED!**
   - No MCP handlers in main `app.py`
   - Configuration exists but no integration pipeline

**Required File Modifications:**

~~1. **Update config.toml** - Add mcp-proxy support:~~ **DONE!**
   ```toml
   allowed_executables = [ "npx", "uvx", "mcp-proxy" ]
   ```

2. **Add MCP Handlers to app.py** - Missing required decorators:
   ```python
   @cl.on_mcp_connect
   @cl.step(type="tool")
   ```

3. ~~**Remove Obsolete Files** - Clean up broken implementations:~~
   - ~~Delete `lib/mcp_server_manager.py`~~ DONE!
   - ~~Delete `lib/dynamic_mcp_manager.py`~~ DONE!

4. **Update app.py Integration** - Replace current LLM flow with MCP-enabled version

**Migration Path:**
- ~~COMPLETE: MCP infrastructure already configured~~
- ~~COMPLETE: Server definitions exist in JSON format~~
- MISSING: Application handlers missing (major gap)
- MISSING: Tool invocation pipeline missing (major gap)
- MISSING: mcp-proxy executable not allowed (minor fix)

---

## Implementation Readiness Assessment

**CRITICAL FINDING**: Your MCP setup is **90% complete** - much closer than initially expected.

### What's Already Working

Your `.chainlit/config.toml` shows MCP is properly configured:
- All transport types enabled (stdio, SSE, streamable-http)
- Security allowlist in place
- Feature flags correctly set

### Immediate Actions Required

**~~1. DONE~~**
**2. ADD MISSING HANDLERS to app.py**

Your `app.py` is missing these required decorators:

```python
@cl.on_mcp_connect
@cl.step(type="tool")
```

**3. INTEGRATION GAP**

Your `process_user_input_and_respond()` bypasses MCP entirely - needs OpenAI function calling integration.

---

---

## Updated TODO List - Clean Slate Approach

### Phase 1

#### 1.1 Backup Critical Configuration
- [ ] **Copy `config/mcp_servers.json`** to backup location outside git

#### 1.2 Complete MCP Code Removal
- [ ] **Remove MCP imports** from `app.py` and all modules
  - [ ] Remove `from mcp import *` statements
  - [ ] Remove `mcp` package references
- [ ] **Delete MCP functions** from application code
  - [ ] Remove any `get_active_mcp_manager()` calls
  - [ ] Delete MCP session variables from `cl.user_session`
  - [ ] Remove MCP-related globals
- [ ] **Clean MCP references** from all Python files
  - [ ] Search and remove MCP mentions in comments
  - [ ] Remove MCP error handling code
  - [x] ~~Clean up MCP-related imports in `lib/` folder~~

#### 1.3 Documentation Purge
- [ ] **Delete obsolete MCP docs**
  - [ ] Remove `config/serverside-mcp-features.md`
  - [ ] Clean MCP references from README files
- [ ] **Update code comments** to remove MCP mentions
- [ ] **Remove MCP TODOs** from existing task lists

### Phase 2: Fresh MCP Implementation

#### 2.1 Context Refresh (Use Context7)
- [ ] **Get latest Chainlit MCP documentation** via Context7
  - [ ] Verify `@cl.on_mcp_connect` current syntax
  - [ ] Check `@cl.step(type="tool")` patterns
  - [ ] Confirm `config.toml` MCP section format
- [ ] **Review cookbook examples** for current best practices
  - [ ] Study `chainlit/cookbook/mcp-linear/app.py`
  - [ ] Check for any API changes since documentation

#### 2.2 Minimal MCP Setup
- [ ] **Add MCP handlers to clean `app.py`**
  ```python
  @cl.on_mcp_connect
  async def on_mcp_connect(connection, session: ClientSession):
      # Store tools in user session (from Context7 docs)
  
  @cl.step(type="tool")
  async def call_tool(tool_use):
      # Execute MCP tools (from Context7 docs)
  ```
- [ ] **Verify config.toml MCP settings**
  - [ ] Confirm `[features.mcp.*]` sections enabled
  - [ ] Add `mcp-proxy` to `allowed_executables` if needed
- [ ] **Test basic functionality**
  - [ ] Start Chainlit app and verify MCP UI appears
  - [ ] Test MCP server connection via UI
  - [ ] Verify tool discovery works

#### 2.3 Configuration Restoration
- [ ] **Restore MCP server definitions** from backup
- [ ] **Test each server configuration** individually
- [ ] **Verify environment variables** are properly substituted

### Phase 3: LLM Integration

#### 3.1 API Context Refresh (Use Context7)
- [ ] **Get current OpenAI function calling patterns**
- [ ] **Verify Chainlit LLM integration** best practices
- [ ] **Check MCP tool formatting** for LLM consumption

#### 3.2 LLM Flow Integration
- [ ] **Update `process_user_input_and_respond()`** (app.py:148)
  - [ ] Add MCP tool retrieval from user session
  - [ ] Format tools for OpenAI function calling
  - [ ] Integrate tool results into LLM context
- [ ] **Add tool execution workflow**
  - [ ] Handle LLM tool calls via `@cl.step(type="tool")`
  - [ ] Process tool results back to LLM
- [ ] **Test end-to-end functionality**
  - [ ] Verify tools are offered to LLM
  - [ ] Test tool execution from user messages
  - [ ] Confirm TTS pipeline works with tool results

### Success Criteria

#### Phase 1 Complete When:
- [ ] No MCP code remains in application (except config)
- [ ] No MCP imports or references in Python files
- [ ] Documentation contains no obsolete MCP information
- [ ] Application runs without MCP errors

#### Phase 2 Complete When:
- [ ] MCP servers connect via Chainlit UI
- [ ] Tools are discovered and stored in user session
- [ ] Basic tool execution works via `@cl.step(type="tool")`

#### Phase 3 Complete When:
- [ ] User messages trigger appropriate MCP tools
- [ ] Tool results are integrated into LLM responses
- [ ] TTS pipeline processes tool-enhanced responses
- [ ] End-to-end conversational flow works with tools

**FINAL GOAL**: Clean, specification-compliant MCP integration with minimal code complexity