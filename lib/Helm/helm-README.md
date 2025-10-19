# Helm - Vintage Voice Effects for Text-to-Speech

Helm is a Python application that adds a classic "vintage doubler" audio effect to text-to-speech voices, giving them a rich, professional sound reminiscent of analog recording equipment.

## What It Does

Helm takes plain text and converts it to speech using character voices (like Iron Man or C-3PO), then applies a sophisticated audio effect that makes the voice sound like it's coming through vintage recording gear. The effect creates a natural doubling with subtle delay and warmth.

## Features

- **Character Voices**: Choose from preset character voices like "stark" (Iron Man) and "C3PO"
- **Vintage Doubler Effect**: Professional audio processing that adds depth and character
- **Optimized Performance**: Smart processing that adapts to audio length for minimal delay
- **Real-time Playback**: Immediate audio output with background effect processing

## Quick Start

### Requirements

- Python 3.7+
- A running TTS-WebUI server (see setup below)
- Required Python packages: `openai`, `pydub`, `sounddevice`, `numpy`

### Installation

1. **Set up TTS-WebUI Server**
   ```bash
   # Youll need to run a TTS-WebUI server on your network
   # See: https://github.com/rsxdalv/tts_webui_extension.openai_tts_api
   # Default server location: http://192.168.1.98:7778
   ```

2. **Install Dependencies**
   ```bash
   pip install openai pydub sounddevice numpy
   ```

3. **Run Helm**
   ```bash
   python helm_optimized.py --input "Hello, world!" --voice stark
   ```

## Usage

### Basic Command

```bash
python helm_optimized.py --input "Your text here" --voice stark
```

### Command Line Options

- `--input`: The text you want to convert to speech (default: "What up, everybody, so glad you're here!")
- `--voice`: Character voice to use. Options: "stark", "C3PO" (default: "stark")

### Examples

**Simple greeting:**
```bash
python helm_optimized.py --input "Hello there!" --voice stark
```

**Longer message:**
```bash
python helm_optimized.py --input "This is a longer message that will demonstrate the background processing for better performance." --voice C3PO
```

**Custom text:**
```bash
python helm_optimized.py --input "I am Iron Man." --voice stark
```

## Configuration

### Server Settings

The script is configured to connect to a TTS-WebUI server. If your server runs on a different address, you'll need to modify the script:

```python
api_key="sk-1234567890"  # API key (usually not needed for local servers)
base_url="http://192.168.1.98:7778/v1"  # Your TTS-WebUI server URL
```

### Audio Settings

The vintage doubler effect uses these default settings:
- **Delay**: 20ms (creates tight doubling)
- **Volume reduction**: -4dB on delayed signal
- **Normalization**: Automatic to prevent clipping

## Performance

Helm automatically optimizes performance based on audio length:

- **Short audio** (< 2 seconds): Processes immediately for fastest response
- **Long audio** (≥ 2 seconds): Uses background processing to start playback sooner

Typical latency: 3-8 seconds depending on text length and server response time.

## Troubleshooting

### "Error connecting to the API"
- Make sure your TTS-WebUI server is running
- Check the server URL in the script matches your setup
- Verify the server is accessible from your network

### "Processing timeout"
- The effect processing took too long and fell back to original audio
- This is normal behavior - you'll still get audio output
- Try shorter text if this happens frequently

### Audio Quality Issues
- Make sure your sound system supports the audio format
- Check that `sounddevice` can access your audio output
- The effect may sound different on different audio systems

### Voice Not Working
- Only "stark" and "C3PO" voices are currently configured
- Check your TTS-WebUI server configuration for available voices

## Technical Details

### Audio Processing
- Input: WAV audio from TTS API
- Effect: 20ms delay with volume reduction and normalization
- Output: Real-time audio playback through system speakers

### Dependencies
- **openai**: For API communication
- **pydub**: Audio processing and effects
- **sounddevice**: Audio playback
- **numpy**: Efficient audio data handling

### Files
- `helm_optimized.py`: Main optimized version (recommended)
- `deprecated/`: Old and experimental versions
  - `helm_streaming.py`: Experimental streaming version (audio quality issues)
  - `helm_soundfile.py`: Alternative using soundfile library
  - `optimized_delay.py`: Utility code for delay processing
- `docs/openapi.json`: API documentation

## Tips

- **Short phrases** work best for real-time conversation
- **Test different voices** to find your preference
- **Monitor the timing output** to understand performance
- **Use the optimized version** (`helm_optimized.py`) for best performance

## License

This project is open source. Check individual file headers for license information.

