# AI Coding Assistant Instructions for Chainloot Yoda Bot Interface

## Project Overview
This is a conversational AI platform built with Chainlit that integrates speech recognition, text-to-speech, and MCP (Model Context Protocol) tools. It supports character profiles (Yoda, AI Assistant, Tony Stark) with distinct voices and personalities, running entirely locally on consumer hardware.

## Architecture Overview

### Core Components
- **Chainlit Frontend** (`app.py`): Main conversational interface with audio handling
- **MCP Tool System**: Server-side tool execution via Model Context Protocol
- **TTS/STT Pipeline**: Speech synthesis/recognition via TTS-WebUI and Whisper
- **Data Layer**: PostgreSQL with Prisma ORM for conversation persistence
- **External Services**: LM Studio (LLM), LocalStack S3 (storage), Ollama (alternative LLM)

### Service Boundaries
- **Audio Processing**: STT → Message Processing → TTS (handled in `lib/stt.py`, `lib/tts.py`)
- **Tool Integration**: MCP servers run server-side, not in browser (`lib/mcp_*_manager.py`)
- **Configuration**: Dynamic MCP setup via `mcp_servers.json` vs legacy hardcoded servers
- **Character Profiles**: Personality switching with voice/prompt persistence (`PROFILE_DEFAULTS`)

## Critical Developer Workflows

### Startup Sequence
1. **MCP Pre-initialization**: Servers start on app launch (not per-chat) for optimal UX
2. **Database Migration**: `prisma migrate deploy` runs before app start
3. **Service Dependencies**: Chainlit waits for TTS-WebUI, PostgreSQL, LocalStack, Ollama

### Audio Pipeline
```python
# STT → Processing → TTS flow (from app.py:390-420)
audio_buffer = handle_audio_end(stt_client, audio_buffer, config["whisper_model"])
processed_message = process_message_for_tts(full_response)  # Sentiment analysis
audio_response = generate_speech(tts_client, text, voice, **tts_config)
```

### MCP Tool Execution
- **Detection**: `tool_processor.should_use_tools()` analyzes messages for tool needs
- **Priority Order**: Time → Search → Fetch → Git → Memory → YouTube → Wikipedia
- **Response Formatting**: All tool outputs cleaned for TTS compatibility

## Project-Specific Patterns

### Configuration Management
- **Single Source of Truth**: `config.json` for all settings, persisted via `on_settings_update()`
- **Profile Voices**: `config["profile_voices"]` maps characters to voice files
- **Environment Variables**: API keys via `.env`, substituted in `mcp_servers.json` as `${VAR}`

### Character Profile System
```python
PROFILE_DEFAULTS = {
    "Yoda": {
        "system_prompt": "You are Yoda, wise Jedi Master. Reply in Yoda-speak...",
        "default_voice": "voices/chatterbox/yoda.wav",
    }
}
```
- **Validation**: Runtime checks ensure selected voices/models exist in available options
- **Persistence**: Voice preferences saved per-profile in `config.json`

### MCP Server Management
- **Dynamic vs Legacy**: `mcp_servers.json` presence determines manager type
- **Tool Discovery**: Automatic capability detection via `find_tool_by_capability()`
- **Error Resilience**: Individual server failures don't crash the application

### Audio Processing Conventions
- **Buffer Handling**: Audio chunks accumulated in `cl.user_session["audio_buffer"]`
- **Safety Filtering**: `scrub_unsafe_characters()` removes problematic content
- **Sentiment Processing**: Messages split by emotion for varied TTS delivery
- **Streaming TTS**: Configurable chunking with `tts_chunked: true`

## Integration Points & Dependencies

### External Services
- **LM Studio** (`http://192.168.1.98:1234`): OpenAI-compatible LLM API
- **TTS-WebUI** (`http://tts-webui:7778`): Speech synthesis with voice cloning
- **Whisper** (`http://192.168.1.98:7778/v1/audio/transcriptions`): Speech recognition
- **LocalStack S3**: File storage simulation for development

### MCP Tool Ecosystem
- **Time Server**: Timezone-aware queries ("What time is it in London?")
- **Brave Search**: Web search with result formatting
- **Git Server**: Repository operations
- **Memory Server**: Conversation persistence
- **YouTube Transcripts**: Video content extraction
- **Wikipedia**: Encyclopedia lookups

### Data Flow Patterns
- **Message Chain**: User Audio → STT → Tool Check → LLM → TTS Processing → Audio Response
- **Settings Sync**: UI changes → `on_settings_update()` → `config.json` persistence
- **Profile Switching**: Character selection → `PROFILE_DEFAULTS` lookup → session state update

## Development Commands

### Local Development
```bash
# Start all services
docker-compose -f docker/docker-compose.yml up

# Run with HTTPS (default)
./start.sh https

# Run database migrations
prisma migrate deploy --schema=database/schema.prisma
prisma generate
```

### Testing MCP Tools
```bash
# Test individual servers
uvx mcp-server-time  # Time utilities
npx @brave/brave-search-mcp-server  # Web search
```

### Configuration
- **Models**: Fetched dynamically from LM Studio API
- **Voices**: Retrieved from TTS-WebUI `/v1/audio/voices/chatterbox`
- **MCP Servers**: Configured in `mcp_servers.json` or fallback to hardcoded

## Common Patterns & Conventions

### Error Handling
- **Graceful Degradation**: MCP failures fall back to basic LLM chat
- **Validation**: Runtime checks for config completeness before chat start
- **Logging**: Performance metrics for LLM/TTS calls with `logger.info(f"PERF: ...")`

### File Organization
- **`lib/`**: Core business logic modules (config, MCP, audio processing)
- **`docs/`**: API documentation and research notes
- **`database/`**: Database schema and migrations (Prisma ORM)
- **`docker/`**: Docker configuration and compose files
- **`public/`**: Static assets (avatars, themes)
- **`submodules/`**: External dependencies (TTS-WebUI, datalayer)

### Code Style Notes
- **Async First**: All I/O operations use async/await
- **Session State**: User preferences stored in `cl.user_session`
- **Monkey Patching**: Custom S3 client injected for LocalStack compatibility
- **No Emojis**: Emojis are not allowed in our code
- **Factory Pattern**: `get_active_mcp_manager()` switches between dynamic/legacy MCP

## Key Files for Understanding
- `app.py`: Main application flow and UI orchestration
- `lib/config_handler.py`: Service client initialization and asset fetching
- `lib/mcp_tool_processor.py`: Intelligent tool selection and execution
- `lib/dynamic_mcp_manager.py`: Modern MCP server management
- `config.json`: Authoritative configuration source
- `docker/docker-compose.yml`: Service orchestration and networking
- `database/schema.prisma`: Data model for conversation persistence