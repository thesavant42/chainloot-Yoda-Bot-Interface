# MCP Implementation Analysis - CONDENSED

**Date:** October 28, 2025  
**Project:** Chainloot Yoda Bot Interface  
**Status:** Ready for Clean Slate Implementation

---

## Executive Summary

**Problem**: MCP servers configured but not working due to missing application handlers  
**Root Cause**: No tool invocation pipeline in `app.py` - tools discovered but never called  
**Solution**: Delete broken custom code, implement standard Chainlit MCP handlers  
**Risk**: LOW - Config already correct, just need 2 missing functions

---

## Current State Analysis

### What Works
- WORKING: MCP enabled in `.chainlit/config.toml` 
- WORKING: Server definitions in `config/mcp_servers.json` (10 servers configured)
- WORKING: Environment variable substitution working
- WORKING: Security allowlist configured (`npx`, `uvx`, `mcp-proxy`)

### What's Broken
- MISSING: No `@cl.on_mcp_connect` handler in `app.py`
- MISSING: No `@cl.step(type="tool")` handler in `app.py` 
- BROKEN: `process_user_input_and_respond()` bypasses MCP entirely
- DELETED: ~~Custom MCP managers deleted (good!)~~

### Core Problem
```python
# Current flow in app.py:148
async def process_user_input_and_respond(user_text: str):
    # 1. User message
    # 2. Direct LLM call (NO TOOLS!)
    # 3. TTS processing
    # 4. Audio response
    # MCP tools are NEVER consulted or executed
```

---

## Implementation Plan

### Phase 1: Clean Slate
1. **Backup** `config/mcp_servers.json` 
2. **Delete** all remaining MCP code from `app.py`
3. **Remove** MCP references from documentation

### Phase 2: Minimal Implementation  
1. **Add** required handlers to `app.py`:
   ```python
   @cl.on_mcp_connect
   async def on_mcp_connect(connection, session):
       # Store tools in user session
   
   @cl.step(type="tool") 
   async def call_tool(tool_use):
       # Execute MCP tools
   ```
2. **Test** basic tool discovery via Chainlit UI

### Phase 3: LLM Integration
1. **Update** `process_user_input_and_respond()` to include tools
2. **Add** OpenAI function calling workflow
3. **Test** end-to-end tool execution

---

## Reference Implementation

**From Chainlit cookbook `/chainlit/cookbook/mcp-linear/app.py`:**

```python
import json
from mcp import ClientSession
import chainlit as cl

@cl.on_mcp_connect
async def on_mcp(connection, session: ClientSession):
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
    tool_name = tool_use.name
    tool_input = tool_use.input
    
    mcp_tools = cl.user_session.get("mcp_tools", {})
    for connection_name, tools in mcp_tools.items():
        if any(tool.get("name") == tool_name for tool in tools):
            mcp_session, _ = cl.context.session.mcp_sessions.get(connection_name)
            return await mcp_session.call_tool(tool_name, tool_input)
    
    return json.dumps({"error": f"Tool {tool_name} not found"})

# In LLM call:
mcp_tools = cl.user_session.get("mcp_tools", {})
all_tools = [tool for tools in mcp_tools.values() for tool in tools]
response = await llm_client.chat.completions.create(messages=messages, tools=all_tools)
```

---

## TODO Checklist

### Phase 1: Clean House
- [ ] Backup `config/mcp_servers.json`
- [ ] Remove MCP imports from `app.py`  
- [ ] Delete MCP functions from application code
- [ ] Clean MCP references from documentation

### Phase 2: Fresh Implementation
- [ ] Use Context7 to get latest Chainlit MCP docs
- [ ] Add `@cl.on_mcp_connect` handler to `app.py`
- [ ] Add `@cl.step(type="tool")` handler to `app.py`
- [ ] Test MCP UI and tool discovery

### Phase 3: Integration  
- [ ] Update `process_user_input_and_respond()` with tools
- [ ] Add OpenAI function calling workflow
- [ ] Test end-to-end tool execution with TTS

**Success Criteria**: User can ask "What time is it?" and get a response using MCP time server

---

## Key Files

- `docker/chainloot/chainlit/app.py` - Needs MCP handlers (lines 148, 706, 740)
- `docker/chainloot/chainlit/config/mcp_servers.json` - Keep this! (working config)
- `docker/chainloot/chainlit/.chainlit/config.toml` - Already correct

**Next Action**: Start Phase 1 cleanup