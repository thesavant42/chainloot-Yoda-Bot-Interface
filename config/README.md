# Configuration Files

This directory contains all user-editable configuration files for the Chainloot Yoda Bot Interface application.

## Files Overview

### `config.json`
**Purpose**: Main application configuration file containing settings for LLM, TTS, STT, and user preferences.

**Key Settings**:
- **LLM Configuration**: LM Studio URL, API key, temperature, max tokens, selected model
- **TTS Configuration**: TTS-WebUI URL, voice settings, speed, exaggeration, temperature
- **STT Configuration**: Whisper model settings
- **Profile Voices**: Voice mappings for different character profiles (Yoda, AI, Stark)
- **UI Settings**: Reasoning enabled, logging settings

**Modified by**: Chainlit UI settings widget - changes are automatically saved here and persist across application restarts.

**Example**:
```json
{
  "lm_studio_base_url": "http://192.168.1.98:1234/v1",
  "api_key": "lm-studio",
  "last_used_model": "phi-4-mini-instruct",
  "tts_base_url": "http://tts-webui:7778",
  "tts_voice": "voices/chatterbox/yoda.wav",
  "profile_voices": {
    "Yoda": "voices/chatterbox/23.wav",
    "AI": "voices/chatterbox/3po.wav",
    "Stark": "voices/chatterbox/stark.wav"
  }
}
```

### `mcp_servers.json`
**Purpose**: Configuration for Model Context Protocol (MCP) servers that provide additional tools and capabilities.

**Structure**:
- **servers**: Object containing server definitions with command, args, environment variables, and descriptions
- **discovery**: Settings for tool discovery and hot reloading
- **transport**: Connection settings and retry logic

**Current Servers**:
- **time**: Time and date utilities
- **brave-search**: Web search via Brave Search API
- **fetch**: HTTP content fetching
- **git**: Git repository operations
- **memory**: Conversation memory persistence
- **sequential-thinking**: Step-by-step reasoning
- **youtube-transcript**: YouTube video transcripts
- **wikipedia**: Wikipedia encyclopedia lookup
- **Home Assistant**: Smart home integration (optional)

**Modified by**: Manual editing - add/remove MCP servers as needed for additional functionality.

### `mcp_proxy_servers.json`
**Purpose**: Configuration for MCP proxy servers that connect to external MCP services via Server-Sent Events (SSE).

**Structure**:
- **mcpServers**: Object containing proxy server definitions with SSE URLs and authentication tokens

**Current Proxies**:
- **home-assistant**: Local Home Assistant integration
- **hf-mcp-server**: Hugging Face MCP services
- **context7**: Context7.ai MCP services

**Modified by**: Manual editing - configure external MCP services as needed.

## Usage Guidelines

### Editing Configuration Files

1. **Stop the application** before editing configuration files
2. **Use a JSON validator** to ensure syntax correctness
3. **Test changes** by restarting the application
4. **Check logs** for any configuration errors

### Environment Variables

Many configuration values support environment variable substitution using the `${VAR_NAME}` syntax:
- `${BRAVE_API_KEY}` - API key for Brave Search
- `${HOME_ASSISTANT_TOKEN}` - Token for Home Assistant integration
- `${HUGGING_FACE_API}` - API key for Hugging Face services

### Backup and Version Control

- **Backup configs** before making significant changes
- **Version control** these files to track configuration changes
- **Document customizations** for team members

## Troubleshooting

### Common Issues

**Configuration not loading**:
- Check JSON syntax with a validator
- Ensure file permissions allow reading
- Verify file paths are correct

**MCP servers not connecting**:
- Check network connectivity to external services
- Verify API keys and tokens are set
- Review server logs for connection errors

**Settings not persisting**:
- Ensure the application has write permissions to config files
- Check that the config path in `app.py` matches the actual file location
- Verify the application can restart successfully

### Validation Commands

Test configuration loading:
```bash
# Inside container
python3 -c "import json; print('Config valid' if json.load(open('config/config.json')) else 'Invalid')"
```

Check MCP configuration:
```bash
# Inside container
python3 -c "import json; config=json.load(open('config/mcp_servers.json')); print(f'Servers: {len(config.get(\"servers\", {}))}')"
```</content>
<parameter name="filePath">c:\Users\jbras\GitHub\chainloot-Yoda-Bot-Interface\config\README.md