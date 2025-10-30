# Chainloot Yoda Bot Interface - AI Agent Instructions

## Project Overview
**Chainloot** is a real-time conversational AI system built around a Yoda animatronic robot. The stack combines Chainlit (chat UI), TTS-WebUI (voice synthesis), Ollama/LM Studio (LLM backends), and an extensive MQTT-based telemetry system. The architecture prioritizes **real-time performance** and **local deployment** on consumer GPU hardware.

## Architecture & Service Dependencies

### Core Stack
- **Frontend**: Chainlit (Python) - Chat UI with MCP tool integration
- **LLM Backends**: Ollama (default) + LM Studio (OpenAI-compatible CHAT APIs but NOT OpenAI Tool Functions! Convert those to MCP and remove them from the code base.)  
- **Voice Stack**: TTS-WebUI (voice synthesis) + Whisper (speech recognition)
- **Message Bus**: Mosquitto MQTT broker with emotion telemetry
- **Data Layer**: PostgreSQL + LocalStack S3 (file storage)

### Service URLs (Docker Internal)
```
Chainlit:     http://localhost:8100, https://localhost:8443
TTS-WebUI:    http://tts-webui:7778 (API), http://localhost:7770 (UI)
Ollama:       http://ollama:11434
LM Studio:    http://192.168.1.98:1234/v1 (external host)
MQTT:         mosquitto:1883 (yoda/yoda auth)
PostgreSQL:   postgres:5432
LocalStack:   localstack:4566
```

## Critical Development Patterns

### MCP Integration (Model Context Protocol)
** CRITICAL: This project uses MCP (Model Context Protocol), NOT OpenAI tool functions!**

**Architecture Flow:**
```
LLM Response → Chainlit (detects tools) → MCP JSON-RPC → call_mcp_tool() → MCP Server
```

**Key Rules:**
- ✅ ALL tool handling goes through `lib/mcp_handler.py` 
- ✅ Chainlit automatically converts MCP

### MQTT Telemetry System
Real-time emotion and system monitoring via hierarchical MQTT topics:

```python
# Emotion publishing (automatic during chat)
/chainloot/persona/{persona}/feelings  # Emotion weights + dominant emotion
/chainloot/persona/{persona}/status    # online/idle/offline

# System monitoring (container_monitor.py)
/chainloot/system/containers/{name}/*  # All Docker container stats
/chainloot/system/services/{name}/*    # Service availability
```

**Key Pattern**: All MQTT messages use QoS 1, retain=True, with expiry intervals for TTL.

### Character Profile System
Personas defined in `lib/bot_config.py` with voice mapping in `config/config.json`:

```python
# Profile structure (authoritative - no defaults)
PROFILE_DEFAULTS = {
    "Yoda": {
        "system_prompt": "Yoda-speak responses...",
        "default_voice": "voices/chatterbox/yoda.wav"
    }
}
# Voice mapping in config.json
"profile_voices": {
    "Yoda": "voices/chatterbox/11.wav",
    "Stark": "voices/chatterbox/stark.wav"
}
```

### Docker Build Optimization
Uses BuildKit with aggressive caching - **ALWAYS update requirements before code copy**:

```dockerfile
# ✅ Correct order - dependencies first, code last
COPY requirements*.txt ./
RUN uv pip install --no-cache -r requirements-chainlit.txt
# Heavy MCP server installations here
COPY . .  # Code copy happens last for cache efficiency
```

## Essential File Structure

```
docker/chainloot/chainlit/          # Main Chainlit application
├── app.py                          # Entry point with MCP event handlers
├── lib/
│   ├── chat.py                     # Core chat processing (simplified for MCP)
│   ├── mcp_handler.py              # 🔧 ALL MCP tool logic (store_mcp_tools only)
│   ├── mqtt_publisher.py           # MQTT telemetry publishing
│   ├── container_monitor.py        # Docker stats → MQTT pipeline
│   ├── feels_classifier.py         # 28-emotion sentiment analysis
│   └── config_handler.py           # Provider switching (Ollama/LM Studio)
├── config/
│   ├── config.json                 # Runtime settings (voices, models, temps)
└── chainlit.Dockerfile             # Build with UV package manager
```

## Critical Development Workflows

**CRITICAL DEVELOPER INSTRUCTION**

This project uses an OpenAI-compatible chat client (chat.completions.create) to get LLM responses, but it uses a standard tool implementation called MCP (Model Context Protocol).

**DO NOT implement or use OpenAI Tool functions.**

ALL tool handling logic is located in lib/mcp_handler.py.

ALL tool calls from the LLM must be passed to the call_mcp_tool function.

### Docker Development Loop
```bash
# Standard rebuild (fast with caching)
cd docker/chainloot
docker-compose build chainlit && docker-compose up -d chainlit

# Full clean rebuild (when dependencies change)  
docker-compose down chainlit
docker builder prune -f
docker-compose build --no-cache chainlit
docker-compose up -d chainlit

# View logs for debugging
docker-compose logs -f chainlit
```

### Configuration Switching
Provider switching between Ollama/LM Studio via `config.json`:
```json
{
  "provider": "ollama",                    // or "lm-studio"  
  "last_used_model": "phi-4-mini",         // Must exist in provider
  "lm_studio_base_url": "http://192.168.1.98:1234/v1"
}
```

## Performance & Debugging

### Latency Optimization Focus Areas
1. **TTS Pipeline**: `lib/tts_response.py` - audio streaming + effects processing
2. **LLM Calls**: Provider selection affects response time (Ollama vs LM Studio)
3. **MQTT Publishing**: Async emotion analysis in `lib/message_processor.py`

### Common Issues
- **S3 Client Patch**: `app.py` applies monkey-patch before imports (LocalStack compatibility)
- **Voice Validation**: TTS-WebUI must be running for voice dropdown population  
- **Model Selection**: Invalid models auto-correct to first available on session start
- **MQTT Auth**: Default credentials `yoda/yoda` in Mosquitto setup

### Key Debugging Commands
```bash
# Check service health
docker-compose ps

# Test TTS API directly  
curl -X POST http://localhost:7778/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"model":"chatterbox","input":"test","voice":"stark"}'

# MQTT message monitoring
docker exec -it chainloot-mosquitto-1 mosquitto_sub -t "/chainloot/#" -u yoda -P yoda

# Ollama model management
docker exec -it chainloot-ollama-1 ollama list
docker exec -it chainloot-ollama-1 ollama pull phi4-mini
```

## Integration Boundaries
- **MCP Tools**: JSON-RPC via Chainlit (not OpenAI functions)
- **MQTT Telemetry**: Pub/sub for emotions, system stats, presence
- **Voice Synthesis**: REST API to TTS-WebUI (chatterbox model)
- **LLM Providers**: OpenAI-compatible Chat APIs (auto-detected model lists)
