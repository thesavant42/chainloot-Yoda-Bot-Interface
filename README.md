# Chainloot
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/thesavant42/chainloot-Yoda-Bot-Interface)
## Custom Front-End Interface to Chat with AI-Powered Yoda Animatronic

### Utilizing:
- **Speech Recognition**
- **Text To Speech**
- **Voice Cloning**
- **MCP Tool Usage**

 - **DeepWiki: https://deepwiki.com/thesavant42/chainloot-Yoda-Bot-Interface**

![demo](https://github.com/thesavant42/chainloot/blob/main/docs/pics/landingpage.png?raw=true)

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

## Latest Update

### Docker Ready
- Overhauled the README.md, which was getting cluttered
- Massive rstructure of Docker and app folders, I expect there are bugs I don't know about yet.
  - But so far, "It works in my setup(tm)"  
- Ollama backend enabled by default, still need to download a model. I'm testing with phi4-mini, it can use tools, it's small.
- Also training phi3 on Yoda-speak
  
Service autostart for API has been sorted, no longer need to manually start the first time.  
  

- Firmware: [https://github.com/thesavant42/y0da](https://github.com/thesavant42/y0da)

---

### Homepage

- [https://hackaday.io/project/195655-hacking-seasonal-yoda](https://hackaday.io/project/195655-hacking-seasonal-yoda)

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

**chainloot**

  `docker/`         - Docker Configs for App & Infrastructure
  `docs/`           - Folder for documentation and support files, API schema docs
  `submodules/`     - Dependancy Submodules
  `CHANGELOG.md`    - Sometimes it is even kept up to date. Not now though.
  `FAQ.md`          - You've got questions? Me too.
  `INSTALLATION.md` - Probably accurate installation instructions
  `LICENSE`         - Do whatever but don't blame me.
  `MEDIA.md`        - Multimedia of the Robot
  `README.md`       - That's me!


### Chainlit Docs

- [https://docs.chainlit.io/get-started/overview](https://docs.chainlit.io/get-started/overview)

### TTS-WebUI

- [https://github.com/rsxdalv/TTS-WebUI](https://github.com/rsxdalv/TTS-WebUI)
