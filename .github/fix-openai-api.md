NOTE: The kokoro tts api extension was recently renamed to the openai api extension. Yoummay find it referred to either way in documentation.

You're asking about how to programmatically enable the **OpenAI API Extension** also known as the **Kokoro TTS API extension** (which provides OpenAI-compatible API endpoints) to start automatically during an unattended installation of TTS-WebUI.<cite />

## Answer

The Kokoro TTS API is an extension that needs to be installed and configured to run on startup.<cite /> Based on the codebase, here's how to enable it programmatically:

### 1. Install the Extension

The Kokoro TTS API extension is defined in `extensions.json` as `extension_kokoro_tts_api`. [1](#0-0)  You need to ensure this extension is installed during your unattended setup by including it in your installation requirements.

### 2. Configuration Approach

The extension system uses the `config.json` file to manage which extensions are disabled. [2](#0-1)  By default, extensions that are installed are enabled unless they appear in the `disabled` list.

For an unattended install, you should:

**Create or modify `config.json`** in the root directory (of the tts-webui container)with the extension NOT in the disabled list:

```json
{
  "extensions": {
    "disabled": []
  }
}
```

This ensures the Kokoro TTS API extension will load when the server starts. [3](#0-2) 

### 3. Automated Installation

For a fully unattended installation, you would need to:

1. **Install the extension package** via pip during setup:
   ```bash
   pip install git+https://github.com/rsxdalv/extension_kokoro_tts_api@main
   ```

2. **Ensure `config.json` exists** with the extension enabled (not in the disabled list)

3. **Start the server** with `python server.py` [4](#0-3) 

The server will automatically load all installed extensions that aren't disabled when it starts. [5](#0-4) 

## Notes

- The Kokoro TTS API extension is classified as a "tools" extension [6](#0-5) , so it will appear in the Tools tab of the interface
- The extension provides OpenAI-compatible endpoints at `http://localhost:7778/v1/audio/speech` as mentioned in the README [7](#0-6) 
- The extension system automatically handles loading during server startup through the `handle_extension_class()` function [8](#0-7) 
- There's no specific "auto-start API server" configuration visible in the codebase - the extension needs to be manually started from the UI after the server loads, or you would need to modify the extension itself to auto-start its API server

Wiki pages you might want to explore:
- [Core Architecture (rsxdalv/TTS-WebUI)](/wiki/rsxdalv/TTS-WebUI#3)
- [Server and Main Application (rsxdalv/TTS-WebUI)](/wiki/rsxdalv/TTS-WebUI#3.1)
- [User Interfaces (rsxdalv/TTS-WebUI)](/wiki/rsxdalv/TTS-WebUI#4)

### Citations

**File:** extensions.json (L617-630)
```json
            "package_name": "extension_kokoro_tts_api",
            "name": "Kokoro TTS API",
            "version": "0.0.1",
            "requirements": "git+https://github.com/rsxdalv/extension_kokoro_tts_api@main",
            "description": "Kokoro TTS API is a text-to-speech model by hexgrad",
            "extension_type": "interface",
            "extension_class": "tools",
            "author": "hexgrad",
            "extension_author": "rsxdalv",
            "license": "MIT",
            "website": "https://huggingface.co/hexgrad/Kokoro-82M",
            "extension_website": "https://github.com/rsxdalv/extension_kokoro_tts_api",
            "extension_platform_version": "0.0.1"
        },
```

**File:** tts_webui/config/load_config.py (L39-42)
```python
    "extensions": {
        "disabled": [],
    },
}
```

**File:** tts_webui/config/load_config.py (L45-53)
```python
def load_config():
    if os.path.exists("config.json"):
        with open("config.json", "r") as infile:
            return json.load(infile)
    else:
        print("Config file not found. Creating default config.")
        with open("config.json", "w") as outfile:
            json.dump(default_config, outfile, indent=2)
        return default_config
```

**File:** documentation/manual_installation.md (L112-115)
```markdown
Run the server:
```bash
python server.py
```
```

**File:** README.md (L263-272)
```markdown
1. Install the Kokoro TTS API extension  
   ![kokoro-tts-api-extension](./documentation/screenshots/kokoro-tts-api-extension.png)
2. Start the API and test it with Python Requests
 
   *(OpenAI client might not be installed thus the Test with Python OpenAI client might fail)*

3. Once you can see the audio generates successfully, go to Silly Tavern, and add a new TTS API
   Default provider endpoint: `http://localhost:7778/v1/audio/speech`
   ![silly-tavern-tts-api](./documentation/screenshots/silly-tavern-tts-api.png)
4. Test it out!
```
