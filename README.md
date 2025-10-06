
## Chainloot 

 ### Custom front-end interface to chat with AI-powered Yoda animatronic
 utilizing: 
     - Speech Recognition
     - Text To Speech
     - Voice Cloning
     - Tool usage

[![A preview of the YouTube Short](https://img.youtube.com/vi/jfygCYoRjw8/0.jpg)](https://youtube.com/shorts/jfygCYoRjw8) [![A preview of the YouTube Short](https://img.youtube.com/vi/E_Typ3TmwVw/0.jpg)](https://youtube.com/shorts/E_Typ3TmwVw)



And runs 100% locally, on consumer grade hardware (RTX 4070, 12 Gigs of VRAM)

## Goal 

Goal is to unify and simplify the architecture required to run the Robot. The dream is real time conversational AI.

[![Project Homepage](/docs/pics/scumandvillainy.jpg)](https://hackaday.io/project/195655-hacking-seasonal-yoda)


- [x] Should support hot swapping of different models hosted on LM Studio
- [x] Should support TTS-WebUI API Integration
    - [x] Reasoning should be a checkbox toggle, disabled by default
- [x] Should have widgets to adjust sampler settings for text response on the fly
- [x] Should have widgets to adjust sampler settings for speech on the fly
- [x] Should be able to select from available voices via a drop-down selector text-input
- [x] Should support a prompt catalog for hot swapping "roles", AI assistant vs. roleplaying character
- [x] Should support character profiles, to change the chat participants
- [x] Should Integrate Whisper-like ASR (Automatic Speech Recognition)
- [ ] Should support multi-modal functionality, for image recognition and tool usage.

## Status

10-03-20205

Latest commit: Transcription via microphone widget is complete.

![demo](https://github.com/thesavant42/chainloot/blob/main/docs/pics/demo.png?raw=true)

- Firmware: https://github.com/thesavant42/y0da

---

### Homepage

- https://hackaday.io/project/195655-hacking-seasonal-yoda

### Endpoints

 - OpenAI-Compatible Text to Speech  (TTS) API: 	http://192.168.1.98:7778/v1/audio/speech
 - OpenAI-Compatible Whisper (STT) API: 			http://192.168.1.98:7778/v1/audio/transcriptions
 - TTS-WebUI Audio Models List (chatterbox)	    	http://192.168.1.98:7778/v1/audio/models
 - List Voices API (chatterbox-tts):				http://192.168.1.98:7778/v1/audio/voices
 - LM Studio - List Models (LM Studio api):         http://192.168.1.98:1234/api/v0/models
 - LM Studio - (OpenAPI) Chat Completion API:       http://192.168.1.98:1234/v1

### Docs

 - SwaggerDoc:								        http://192.168.1.98:7778/docs#/
 - OpenAPI JSON:							        http://192.168.1.98:7778/openapi.json
 - Gradio UI for TTS-WebUI:	    			        http://192.168.1.98:7770/
 - Gradio UI API Doc:						        http://192.168.1.98:7770/openapi.json
 - React UI for TTS-WebUI:					        http://192.168.1.98:3000/

### Windows-curl friendly TTS Test string

```
 curl -X POST http://192.168.1.98:7778/v1/audio/speech -H "Content-Type: application/json" -d '{"model":"chatterbox","input":"Hello world! This is a streaming test.","voice":"random","stream":true}' --proxy http://127.0.0.1:8080
 ```



![model_settings](https://github.com/thesavant42/chainloot/blob/main/docs/pics/model-settings.png?raw=true)

## Structure

chainlit/ Top Level Directory
- docs/                             # Folder for documentation and support files, API schema docs
- docs/chainlit-docs/
- docs/tts-webui-apis/              # OpenAPI docs for Chatterbox, TTS-WebUI
- ./README.md                       # This file
- ./app.py                          # Man chainlit app code
- ./.env                            # API keys go here (if needed)

[![A preview of the YouTube Short](https://img.youtube.com/vi/PvwhKqiAzew/0.jpg)](https://youtube.com/shorts/PvwhKqiAzew) 

### Chainlit Docs

- https://docs.chainlit.io/get-started/overview

### TTS-WebUI

- https://github.com/rsxdalv/TTS-WebUI

[![A preview of the YouTube Short](https://img.youtube.com/vi/sbZzu1HrOTU/0.jpg)](https://youtube.com/shorts/sbZzu1HrOTU) [![A preview of the YouTube Short](https://img.youtube.com/vi/jSkOm2LKjzg/0.jpg)](https://youtube.com/shorts/jSkOm2LKjzg) 
