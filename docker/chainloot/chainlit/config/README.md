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

**Settings not persisting**:
- Ensure the application has write permissions to config files
- Check that the config path in `app.py` matches the actual file location
- Verify the application can restart successfully
