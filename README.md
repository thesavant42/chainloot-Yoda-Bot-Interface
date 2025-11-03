# Chainloot
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/thesavant42/chainloot-Yoda-Bot-Interface)


<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [Chainloot](#chainloot)
    - [Custom Front-End Interface to Chat with AI-Powered Yoda Animatronic](#custom-front-end-interface-to-chat-with-ai-powered-yoda-animatronic)
      - [Utilizing:](#utilizing)
    - [Goal](#goal)
  - [Latest Update](#latest-update)
    - [Docker Ready](#docker-ready)
    - [Structure](#structure)
  - [Links](#links)
    - [Homepage](#homepage)
    - [Firmware:](#firmware)
    - [Docs](#docs)
    - [Chainlit Docs](#chainlit-docs)
    - [TTS-WebUI](#tts-webui)

<!-- /code_chunk_output -->



### Custom Front-End Interface to Chat with AI-Powered Yoda Animatronic

#### Utilizing:

| **Speech Recognition**  | **Text To Speech**  |
|---|---|
| **Voice Cloning**  | **MCP Tool Usage**  |

- **And runs 100% locally, on consumer-grade hardware (RTX 4070, 12GB VRAM).**
 - **DeepWiki: https://deepwiki.com/thesavant42/chainloot-Yoda-Bot-Interface**




![demo](https://github.com/thesavant42/chainloot/blob/main/docs/pics/landingpage.png?raw=true)

### Goal

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

**FEATURE** Language Overhaul for Yoda! - Smarter Yoda-speak translations.
**FEATURE** Pre-warm the voice models  - Shorter time waiting for models to load

- Previous attempts to train a language model were time-expensive and didn't yield results I was happy with. Training limited me to models that were compatible with that LORA and even with the trained additions, the performance was closer to *Shakespeare* than Yoda.
- Following those, I attempted a purely prompt-based approach. This worked better than the tuning but still not consistent, and was still impacted by which model family was used.
- **New hotness**: Yoda-Translator - Use SpaCy to parse the messages before sending and then reshuffle them into "Object-Subject-Verb syntax.
  - Used https://github.com/thesavant42/yoda-translator
    - Which is based off of **https://github.com/haohangxu/yoda-translator**
- https://spacy.io/models/en#en_core_web_sm     
- This approach will work with any model or any text input for that matter. 
- An added bonus is that it only applies to Master Yoda, and his Chain of Thought no longer has to be Yodish. 
  - It was causing issues with reasoning and MCP.
- **Significant user experience improvements** by implementing a warmup function for Text to Speech and Speech to text, which uses TTS to speak the current date and time to STT, which keeps them in memory.
- GPU Tracking via Docker Container

### Docker Ready
- Overhauled the README.md, which was getting cluttered
- Massive rstructure of Docker and app folders, 
  - I expect there are bugs I don't know about yet.
  - But so far, "*It works in my setup(tm)*"  
- Ollama backend enabled by default, still need to download a model. I'm testing with phi4-mini, it can use tools, it's small.
- ~~Also training phi3 on Yoda-speak~~ New solution is way better
  
**Service autostart for API has been sorted, no longer need to manually start the first time.**  
  

---


![model_settings](https://github.com/thesavant42/chainloot/blob/main/docs/pics/model-settings.png?raw=true)

### Structure

**chainloot**

- `docker/chainloot/` - Complete Docker orchestration for the Yoda Bot ecosystem
  - `chainlit/` - Chainlit web interface with chat UI and persona system
  - `tts-webui/` - TTS-WebUI service with Chatterbox voice models and warmup system  
  - `ollama/` - Local LLM hosting with model management
  - `database/` - Data persistence and storage
  - `gpu-monitor/` - CUDA/GPU monitoring and diagnostics
  - `mosquitto/` - MQTT broker for device communication
  - `localstack/` - AWS service emulation for local development
  - `docker-compose.yml` - Multi-service orchestration configuration
- `docs/` - Project documentation and development tracking
  - `BUGS/` - Active bug tracking and investigation reports
  - `COMPLETED_TASKS/` - Completed feature implementations and fixes
  - `IN_PROGRESS_TASKS/` - Current development work and research
  - `UNSTARTED_TASKS/` - Planned features and improvement ideas
  - `RESEARCH/` - Technical research and proof-of-concepts
  - `testing/` - Test scripts and validation procedures
- `submodules/` - Git submodules for external dependencies
  - `chainlit-datalayer/` - Data layer integration for Chainlit
  - `tts-webui/` - TTS-WebUI upstream integration
- `testing/` - Integration tests and system validation
- `backups/` - Configuration and data backups
- `.data/` - Runtime data and temporary files
- `INSTALLATION.md` - Setup and deployment instructions
- `LICENSE` - MIT License - Do whatever but don't blame me
- `MEDIA.md` - Photos, videos, and multimedia of the robot
- `README.md` - That's me!


## Links
### Homepage

- [https://hackaday.io/project/195655-hacking-seasonal-yoda](https://hackaday.io/project/195655-hacking-seasonal-yoda)

### Firmware: 
- [https://github.com/thesavant42/y0da](https://github.com/thesavant42/y0da)

### Docs
- Check out the docs folder!

### Chainlit Docs

- [https://docs.chainlit.io/get-started/overview](https://docs.chainlit.io/get-started/overview)

### TTS-WebUI

- [https://github.com/rsxdalv/TTS-WebUI](https://github.com/rsxdalv/TTS-WebUI)
