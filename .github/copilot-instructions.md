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
### Container Monitoring**: System resources and service availability tracked via MQTT (`lib/container_monitor.py`)

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
- **Monitoring Flow**: Container Monitor → Docker API + System Stats → MQTT Publishing → External Monitoring

## Development Commands

### Local Development
```bash
# Start all services
docker-compose -f docker/chainloot/docker-compose.yml up

# Run with HTTPS (default)
./start.sh https

# Run database migrations
prisma migrate deploy --schema=docker/chainloot/chainlit/database/schema.prisma
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
- **`docker/chainloot/`**: Container orchestration and service-specific configurations
  - **`chainlit/`**: Main application container with source code, configs, and assets
    - **`lib/`**: Core business logic modules (config, MCP, audio processing)
    - **`config/`**: Configuration files (JSON configs, MCP server definitions)
    - **`database/`**: Database schema and migrations (Prisma ORM)
    - **`public/`**: Static assets (avatars, themes)
    - **`ssl/`**: SSL certificates for HTTPS
    - **`uploads/`**: User-uploaded files
  - **`database/`**: PostgreSQL container configuration
  - **`localstack/`**: LocalStack S3 simulation container
  - **`mosquitto/`**: MQTT broker container
  - **`ollama/`**: Ollama LLM container
  - **`tts-webui/`**: TTS-WebUI speech synthesis container
- **`docs/`**: API documentation and research notes
- **`submodules/`**: External dependencies (TTS-WebUI, datalayer)

**Container-Specific Organization**: Each service under `docker/chainloot/` maintains its own folder with Dockerfiles, environment files, and configuration. Do not consolidate or share container-specific files (like requirements.txt or .env files) across services, as this structure preserves isolation and simplifies troubleshooting.

### Code Style Notes
- **No Emojis EVER**: Emojis are strictly forbidden in code, comments, commit messages, documentation, and chat communications
- **Async First**: All I/O operations use async/await
- **Session State**: User preferences stored in `cl.user_session`
- **Monkey Patching**: Custom S3 client injected for LocalStack compatibility
- **Factory Pattern**: `get_active_mcp_manager()` switches between dynamic/legacy MCP

## Workflow Requirements
- **ALWAYS seek explicit approval before editing any files** - discuss design approaches and get confirmation before implementing changes
- **Collaborative design first**: Propose solutions and get feedback before coding
- **No unapproved changes**: Never modify code without explicit user permission

## Communication Guidelines
- **Keep responses brief and concise** while always being accurate
- **Never disagree with the user** - focus on understanding and fulfilling their requests
- **Be helpful and collaborative** in all interactions
- **ALWAYS seek explicit approval before editing any files** - discuss design approaches and get confirmation before implementing changes

## Key Files for Understanding
- `docker/chainloot/chainlit/app.py`: Main application flow and UI orchestration
- `docker/chainloot/chainlit/lib/config_handler.py`: Service client initialization and asset fetching
- `docker/chainloot/chainlit/lib/mcp_tool_processor.py`: Intelligent tool selection and execution
- `docker/chainloot/chainlit/lib/dynamic_mcp_manager.py`: Modern MCP server management
- `docker/chainloot/chainlit/config/config.json`: Authoritative configuration source
- `docker/chainloot/docker-compose.yml`: Service orchestration and networking
- `docker/chainloot/chainlit/database/schema.prisma`: Data model for conversation persistence