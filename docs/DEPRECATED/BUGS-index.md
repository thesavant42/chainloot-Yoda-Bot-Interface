
## Multiple instances of spacy: 3.6.0 and 3.6.1 (Blocking chatterbox?)
Lines 45-58

Notes: 


## No Cuda Toolkit: Ollama (CRITICAL)
Lines 59-77

Notes: 
- Added GPU passthrough to docker-compose.yml for Ollama container
- Added deploy.resources.reservations.devices with nvidia driver
- This should enable CUDA support for LLM inference

## Prisma error: Unsupported Engine.  Prisma only supports Node.js >= 16.13.
Lines 78-150

Notes: 
- Updated Dockerfile to install Node.js 20.18.0 using nvm
- Added proper PATH configuration for newer Node.js
- This should fix Prisma CLI and MCP server compatibility issues

## OpenAI API does not start enabled (Critical)
Lines 151-157

Notes: See "fix-openai-api.md"

## Node errors affect MCP Services
Lines 158-298

Notes: 
- Node.js upgrade to 20.18.0 should resolve ES6+ syntax errors
- MCP servers require Node.js >= 18 for modern JavaScript features
- This should fix the "Unexpected token '?'" and engine compatibility errors

## Home Assistant MCP fails to load
Lines 299-318

Notes: 

## Chatterbox dependancies install failure (CRITICAL)
Lines 339-391

Notes: 

## Kokoro Extension Installation causes exceptions (CRITICAL)
Lines 392-512

Notes: 
- Custom TTS-WebUI build now includes kokoro extension and its dependencies
- This should resolve the "Kokoro extension is not installed" ImportError
- OpenAI API extension should now work properly

## No cuda detected on tts-webui container (CRITICAL)
Lines 513-539

Notes: 
- Created custom TTS-WebUI.Dockerfile based on nvidia/cuda:12.8.0 base image
- Added GPU passthrough to docker-compose.yml for TTS-WebUI container
- Installed all required TTS extensions including kokoro, bark-voice-clone, rvc, etc.
- This should provide CUDA support and all necessary extensions for TTS generation


## Unhandled Exception: TTS voices empty
Lines 319-338

Notes: 

## Bug: "available_voices is empty. Ensure TTS voices are fetched before starting the chat."
Lines 1-44

Notes: 

## I am not concerned about bark at this phase.

### Bark Voices exception
Lines 540-569

Notes: 

### Bark Extension Exception (harmless)
570-END

Notes: 
