# Streaming MCP Implementation

## Overview
This document describes the implementation of streaming MCP patterns into the Chainlit app, based on the walkthrough patterns from the example MCP flow application.

## What Changed

### 1. **Streaming Architecture** (`lib/mcp_handler.py`)

Added two new classes/functions for handling streaming:

#### `StreamingToolCallAccumulator` Class
Handles the complexity of tool calls arriving incrementally in streaming chunks:
- Tool names arrive in early chunks
- Arguments arrive as partial JSON strings across multiple chunks
- Must accumulate arguments with `+=` operator (not replacement)
- Tracks completion status (both name and arguments present)

```python
# Example: How tool calls arrive in chunks
Chunk 1: {"tool_calls": [{"index": 0, "function": {"name": "get_weather"}}]}
Chunk 2: {"tool_calls": [{"index": 0, "function": {"arguments": "{\"loc"}}]}
Chunk 3: {"tool_calls": [{"index": 0, "function": {"arguments": "ation\": \"NYC\"}"}}]}
# After all chunks: tool_calls[0] = {"name": "get_weather", "arguments": "{\"location\": \"NYC\"}"}
```

#### `stream_llm_response()` Function
Async generator that wraps the LLM client streaming:
- Enables `stream: True` in request parameters
- Iterates through chunks as they arrive
- Uses `StreamingToolCallAccumulator` to accumulate tool calls
- Yields tuples of `(text_token, tool_calls)` for real-time processing
- Handles exceptions gracefully

### 2. **Streaming Chat Processing** (`lib/chat.py`)

Completely refactored `ChatProcessor.process_user_input_and_respond()` to implement streaming:

#### Key Changes:
1. **Streaming Message Creation**: Creates empty message immediately, streams tokens into it
2. **Token-by-Token Output**: User sees text appearing word-by-word in real-time
3. **Streaming Loop**: Consumes from `stream_llm_response()` generator
4. **Tool Call Handling**: Tools that arrive in streaming chunks are accumulated and processed
5. **Agentic Loop**: After each tool execution, makes follow-up LLM call with tool results in context
6. **Real-time Feedback**: User sees tools being executed in steps

#### Control Flow:
```
User sends message
    ↓
Initialize streaming message
    ↓
Stream from LLM (text + tool calls)
    ├─ Text arrives? → Stream token to UI
    ├─ Tool complete? → Add to history, execute via MCP
    │   ├─ Display tool result
    │   ├─ Add result to history
    │   └─ Loop back for follow-up response
    └─ No tool calls? → Break from loop
        ↓
Process response for TTS (emotion analysis)
    ↓
Generate audio response
```

## Performance Benefits

1. **Perceived Responsiveness**: Users see text appearing immediately rather than waiting for entire response
2. **Better UX**: Tool execution is visible step-by-step
3. **Network Efficiency**: Streaming uses chunked transfer encoding (more efficient than waiting for full response)
4. **Memory**: Chunks are processed and discarded, not accumulated in memory

## Integration with Your Infrastructure

### Works With:
- ✅ **MQTT Telemetry**: Emotion publishing happens AFTER full response is ready (no conflicts)
- ✅ **TTS Pipeline**: Uses complete response, so timing unchanged
- ✅ **Tool Execution**: MCP tools executed within streaming loop (immediate feedback)
- ✅ **Multiple Providers**: Works with both Ollama and LM Studio (streaming support universal)

### Example Conversation Flow:

```
User: "What's the weather in NYC and what's a good restaurant there?"

[Streaming starts immediately]
Assistant: "I'll help you find the weather and restaurant..."
[text streams as it arrives]

[LLM detects need for tools]
Tool Execution Step: "Executing tool: get_weather with input: {"location": "NYC"}"
Tool Result: "73°F and sunny in NYC"

[Tool result added to history, follow-up LLM call made]
[More streaming...]
Tool Execution Step: "Executing tool: find_restaurant with input: {"city": "NYC"}"
Tool Result: "Top rated: Eleven Madison Park, Alinea"

[Final response streams]
"Based on the weather (73°F sunny), I'd recommend..."
[complete response]

[TTS generates audio]
[User hears audio response]
```

## Code Quality Improvements

1. **Better Error Handling**: Streaming errors caught and logged with context
2. **Performance Logging**: Each iteration logged with latency measurements
3. **Clearer Control Flow**: Agentic loop logic more explicit with comments
4. **Type Hints**: Added `AsyncGenerator`, `Tuple` types for better IDE support

## Breaking Changes

**None.** The streaming implementation is backward compatible:
- Existing session values work unchanged
- MQTT publishing continues as before
- TTS response generation identical
- Tool execution format unchanged (still uses MCP protocol)

## Testing Recommendations

1. **Basic Streaming**: Send simple text message, verify tokens appear incrementally
2. **With Tools**: Send message that triggers tool calls, verify:
   - Tool execution step appears in UI
   - Tool results display correctly
   - Follow-up response streams properly
3. **Error Cases**: 
   - Disconnect provider mid-stream (error handling)
   - Tool execution failure (proper error message in history)
4. **Performance**: 
   - Compare response time before/after (should be similar)
   - Check memory usage during long responses (should be flat)

## Example: Before vs After

### Before (Non-Streaming)
```
User types message
[Wait 2-3 seconds]
[Entire response appears at once]
User reads response
[Audio plays]
```

### After (Streaming)
```
User types message
[Immediately see first tokens appearing]
[Text streams word-by-word]
[If tools needed, see execution steps in real-time]
[See tool results as they arrive]
[Hear audio from complete response]
```

## Files Modified

1. **`lib/mcp_handler.py`**
   - Added `StreamingToolCallAccumulator` class
   - Added `stream_llm_response()` async generator
   - Added type hints for better tooling

2. **`lib/chat.py`**
   - Imported `stream_llm_response` from `mcp_handler`
   - Refactored `process_user_input_and_respond()` to use streaming
   - Improved logging throughout
   - Better documentation of control flow

## Migration Notes

If you have custom integrations that call `process_user_input_and_respond()`:
- No changes needed - the function signature is identical
- The implementation is now async streaming internally
- All existing behavior (MQTT, TTS, tools) works the same

## Future Improvements

1. **Streaming TTS**: Could stream audio chunks during text generation (advanced)
2. **Token Counting**: Add token usage logging from streaming responses
3. **Cancellation**: Add support for canceling in-progress streams
4. **Parallel Tool Execution**: Execute multiple non-dependent tools simultaneously

---

**Implementation Date**: October 30, 2025
**Based On**: Walkthrough.md example patterns
**Status**: Ready for testing
