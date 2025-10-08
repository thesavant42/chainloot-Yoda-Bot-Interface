## Chainloot

### Custom Front-End Interface to Chat with AI-Powered Yoda Animatronic

Utilizing:
- Speech Recognition
- Text To Speech
- Voice Cloning
- MCP Tool Usage

![demo](https://github.com/thesavant42/chainloot/blob/main/docs/pics/landingpage.png?raw=true)

[![A preview of the YouTube Short](https://img.youtube.com/vi/jfygCYoRjw8/0.jpg)](https://youtube.com/shorts/jfygCYoRjw8)
[![A preview of the YouTube Short](https://img.youtube.com/vi/E_Typ3TmwVw/0.jpg)](https://youtube.com/shorts/E_Typ3TmwVw)

And runs 100% locally, on consumer-grade hardware (RTX 4070, 12GB VRAM).

## Goal

The goal is to unify and simplify the architecture required to run the robot. The dream is real-time conversational AI.

[![Project Homepage](/docs/pics/scumandvillainy.jpg)](https://hackaday.io/project/195655-hacking-seasonal-yoda)

- [x] Should support hot swapping of different models hosted on LM Studio
- [x] Should support TTS-WebUI API Integration
    - [x] Reasoning should be a checkbox toggle, disabled by default
- [x] Should have widgets to adjust sampler settings for text response on the fly
- [x] Should have widgets to adjust sampler settings for speech on the fly
- [x] Should be able to select from available voices via a drop-down selector text-input
- [x] Should support a prompt catalog for hot swapping "roles", AI assistant vs. roleplaying character
- [x] Should support character profiles, to change the chat participants
- [x] Should integrate Whisper-like ASR (Automatic Speech Recognition)
- [ ] Should support multi-modal functionality, for image recognition and tool usage

## Status
**10-06-2025 **
Beta Release 0.1 is Live! Check the releases tag, ->
This release implements Character Profiles, you can hot swap between Yoda, C3PO, and Tony Stark. They each have their own system prompts and voice presets that will persist (I hope).

- Standard edition, Master Yoda

![model_settings](https://github.com/thesavant42/chainloot/blob/main/docs/pics/selected-yoda.png?raw=true)

- C3PO

![model_settings](https://github.com/thesavant42/chainloot/blob/main/docs/pics/selected-3po.png?raw=true)

- Stark

![model_settings](https://github.com/thesavant42/chainloot/blob/main/docs/pics/selected-stark.png?raw=true)

**10-03-2025**

Latest commit: Transcription via microphone widget is complete.

![demo](https://github.com/thesavant42/chainloot/blob/main/docs/pics/demo.png?raw=true)

- Firmware: [https://github.com/thesavant42/y0da](https://github.com/thesavant42/y0da)

---

### Homepage

- [https://hackaday.io/project/195655-hacking-seasonal-yoda](https://hackaday.io/project/195655-hacking-seasonal-yoda)

### Endpoints

- **OpenAI-Compatible Text to Speech (TTS) API:**  
  `http://192.168.1.98:7778/v1/audio/speech`
- **OpenAI-Compatible Whisper (STT) API:**  
  `http://192.168.1.98:7778/v1/audio/transcriptions`
- **TTS-WebUI Audio Models List (chatterbox):**  
  `http://192.168.1.98:7778/v1/audio/models`
- **List Voices API (chatterbox-tts):**  
  `http://192.168.1.98:7778/v1/audio/voices`
- **LM Studio - List Models (LM Studio API):**  
  `http://192.168.1.98:1234/api/v0/models`
- **LM Studio - (OpenAPI) Chat Completion API:**  
  `http://192.168.1.98:1234/v1`

### Docs

- **SwaggerDoc:**  
  [http://192.168.1.98:7778/docs#/](http://192.168.1.98:7778/docs#/)
- **OpenAPI JSON:**  
  [http://192.168.1.98:7778/openapi.json](http://192.168.1.98:7778/openapi.json)
- **Gradio UI for TTS-WebUI:**  
  [http://192.168.1.98:7770/](http://192.168.1.98:7770/)
- **Gradio UI API Doc:**  
  [http://192.168.1.98:7770/openapi.json](http://192.168.1.98:7770/openapi.json)
- **React UI for TTS-WebUI:**  
  [http://192.168.1.98:3000/](http://192.168.1.98:3000/)

### Windows-curl Friendly TTS Test String

```sh
curl -X POST http://192.168.1.98:7778/v1/audio/speech -H "Content-Type: application/json" -d '{"model":"chatterbox","input":"Hello world! This is a streaming test.","voice":"random","stream":true}'
```

![model_settings](https://github.com/thesavant42/chainloot/blob/main/docs/pics/model-settings.png?raw=true)

## Structure

**chainlit/** Top Level Directory
- `docs/` — Folder for documentation and support files, API schema docs
- `docs/chainlit-docs/`
- `docs/tts-webui-apis/` — OpenAPI docs for Chatterbox, TTS-WebUI
- `README.md` — This file
- `app.py` — Main chainlit app code
- `.env` — API keys go here (if needed)

[![A preview of the YouTube Short](https://img.youtube.com/vi/PvwhKqiAzew/0.jpg)](https://youtube.com/shorts/PvwhKqiAzew)

### Chainlit Docs

- [https://docs.chainlit.io/get-started/overview](https://docs.chainlit.io/get-started/overview)

### TTS-WebUI

- [https://github.com/rsxdalv/TTS-WebUI](https://github.com/rsxdalv/TTS-WebUI)

[![A preview of the YouTube Short](https://img.youtube.com/vi/sbZzu1HrOTU/0.jpg)](https://youtube.com/shorts/sbZzu1HrOTU)
[![A preview of the YouTube Short](https://img.youtube.com/vi/jSkOm2LKjzg/0.jpg)](https://youtube.com/shorts/jSkOm2LKjzg)