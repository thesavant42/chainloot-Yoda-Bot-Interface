# Helm - Audio Effects Processing Instructions

## Project Overview
Helm is a real-time audio processing module that applies vintage "doubler" effects to text-to-speech audio generated from OpenAI-compatible APIs. The core challenge is **latency optimization** - the current audio pipeline introduces significant delay that impacts real-time usage.

## Architecture & Data Flow
1. **API Request**: Text → OpenAI-compatible TTS API (`http://192.168.1.98:7778/v1`) → Raw WAV audio stream
2. **Audio Processing**: Raw audio → pydub processing → "vintage doubler" effect → numpy array
3. **Playback**: numpy array → sounddevice → speakers

## Critical Performance Patterns

### Audio Pipeline (helm.py)
- **Streaming Response**: Always use `client.audio.speech.with_streaming_response.create()` to minimize initial latency
- **Fixed Model**: Must use `model="global_preset"` - this maps to character presets configured server-side
- **Character Voices**: Current working voices are "stark" and "C3PO" (specified via `voice` parameter)
- **Memory Processing**: Audio stays in-memory using `io.BytesIO()` - avoid filesystem I/O for performance

### Doubler Effect Implementation
```python
# Standard pattern for vintage doubler effect
delay_ms = 20  # Fixed 20ms delay for tight doubling
delayed_audio = AudioSegment.silent(duration=delay_ms) + original_audio
delayed_audio = delayed_audio - 4  # -4dB volume reduction
doubled_audio = original_audio.overlay(delayed_audio)
doubled_audio = doubled_audio.normalize()  # Prevent digital clipping
```

### Audio Format Handling
- **Input Format**: Always request `response_format="wav"` from API
- **Sample Processing**: Convert pydub → numpy with proper dtype inference based on `sample_width`
- **Playback**: Use `sounddevice.play()` with `blocking=True` for synchronous playback

## Performance Optimization Focus
- **Primary Goal**: Reduce overall latency without server-side changes
- **Known Bottleneck**: Audio effect processing adds significant overhead to otherwise fast character voice
- **Clipping Issue**: Doubling process doubles amplitude, causing static when exceeding noise floor

## Dependencies & Environment
- **Core Libraries**: `openai`, `pydub`, `sounddevice`, `numpy`
- **Audio Backend**: Uses sounddevice for robust cross-platform audio playback
- **API Integration**: Communicates with `tts_webui_extension.openai_tts_api` backend

## External API Contract
- **Endpoint**: `/v1/audio/speech` (see `docs/openapi.json` for full schema)
- **Required Fields**: `model`, `input`, `voice`
- **Character Mapping**: Voice names map to server-configured presets (e.g., "stark" → Iron Man settings)
- **Legacy References**: May see "kokoro" references from previous API version - leave unchanged

## Development Workflow
- **Testing**: Run with `python helm.py --input "test text" --voice stark`
- **Voice Options**: Use `--voice` parameter to switch between "stark" and "C3PO"
- **Audio Output**: Current version plays directly through speakers (no file export by default)

## Performance Investigation Areas
When optimizing latency, focus on:
1. Audio processing pipeline efficiency (pydub operations)
2. Memory allocation patterns in numpy conversion
3. Streaming vs. buffered processing approaches
4. Effect algorithm optimization while preserving audio quality