# MCP Implementation Task List

**Reference Document:** `MCP_ANALYSIS_NOTES.md`  
**Date:** October 28, 2025  
**Approach:** Clean slate implementation (delete broken code, fresh start)

**CRITICAL INSTRUCTION: Always use Context7 tools for API verification before implementing any code patterns.**

---

## Phase 1: Clean House FIRST

### 1.1 Backup Critical Configuration
- [x] Copy `config/mcp_servers.json` to backup location outside git


### 1.2 Complete MCP Code Removal
- [ ] Remove all MCP imports from `app.py` and modules
- [ ] Delete any `get_active_mcp_manager()` calls
- [ ] Remove MCP session variables from `cl.user_session`
- [ ] Search and remove MCP references in comments
- [ ] Remove MCP error handling code

### 1.3 Documentation Purge  
- [ ] Delete `config/serverside-mcp-features.md`
- [ ] Clean MCP references from README files
- [ ] Remove MCP TODOs from existing task lists

**Phase 1 Complete When:**  Application runs without MCP errors, no MCP code remains

---

## Phase 2: Fresh Implementation

### 2.1 Context Refresh (MANDATORY: Use Context7)
- [ ] **Use Context7:** Get latest Chainlit MCP documentation
  - [ ] Verify `@cl.on_mcp_connect` current syntax
  - [ ] Check `@cl.step(type="tool")` patterns  
  - [ ] Confirm `config.toml` MCP section format
- [ ] **Use Context7:** Review `chainlit/cookbook/mcp-linear/app.py` for patterns

### 2.2 Minimal MCP Setup
- [ ] Add required MCP handlers to clean `app.py`:
  ```python
  @cl.on_mcp_connect
  @cl.step(type="tool")
  ```
- [ ] Verify `config.toml` has MCP enabled
- [ ] Add `mcp-proxy` to `allowed_executables` if needed
- [ ] Test MCP UI appears in Chainlit

### 2.3 Configuration Restoration
- [ ] Restore MCP server definitions from backup
- [ ] Test each server configuration individually
- [ ] Verify environment variables substitute correctly

**Phase 2 Complete When:** MCP servers connect via UI, tools discovered and stored

---

## Phase 3: LLM Integration

### 3.1 API Context Refresh (MANDATORY: Use Context7)
- [ ] **Use Context7:** Get current OpenAI function calling patterns
- [ ] **Use Context7:** Verify Chainlit LLM integration best practices
- [ ] **Use Context7:** Check MCP tool formatting for LLM consumption

### 3.2 LLM Flow Integration
- [ ] Update `process_user_input_and_respond()` (app.py:148) with:
  - [ ] MCP tool retrieval from user session
  - [ ] OpenAI function calling format conversion
  - [ ] Tool result integration into LLM context
- [ ] Add tool execution via `@cl.step(type="tool")`
- [ ] Test end-to-end: user message → tool selection → execution → response

**Phase 3 Complete When:** Conversational flow works with MCP tools, TTS processes tool results

---

## Success Criteria

**WORKING:** Clean MCP implementation following official patterns  
**WORKING:** Tool discovery and execution via Chainlit UI  
**WORKING:** LLM automatically selects and uses appropriate tools  
**WORKING:** End-to-end conversation flow with tool integration  

---

## Key Implementation Notes

- **Root Cause:** Missing `@cl.on_mcp_connect` and `@cl.step(type="tool")` handlers in `app.py`
- **Current Status:** 90% infrastructure complete, missing application integration
- **Critical Gap:** `process_user_input_and_respond()` bypasses MCP entirely
- **Architecture:** Use Chainlit native MCP support, delete custom managers
- **Reference:** See `MCP_ANALYSIS_NOTES.md` for detailed technical analysis

**REMINDER: Always use Context7 for API verification before coding.**