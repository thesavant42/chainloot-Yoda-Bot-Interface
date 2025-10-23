# CHANGELOG

## Status

**10-16-2025**

- ✅ Fixed port conflict issues with TTS-WebUI
- ✅ Added Prisma CLI to Dockerfile to resolve database client generation warnings
- ✅ Enabled GPU acceleration on all containers (chainlit, ollama, tts-webui)
- ✅ Fixed voice fetching with retry logic for TTS-WebUI startup timing
- ✅ All containers healthy and app fully functional

### Complete MCP Server Catalog

- 1. Time Server (mcp-server-time)
- 2. Brave Search Server (@brave/brave-search-mcp-server)
- 3. Fetch Server (mcp-server-fetch)
- 4. Git Server (mcp-server-git)
- 5. Memory Server (@modelcontextprotocol/server-memory)
- 6. Sequential Thinking Server (@modelcontextprotocol/server-sequential-thinking)
- 7. YouTube Transcript Server (@kimtaeyoon83/mcp-server-youtube-transcript)
- 8. Wikipedia Server (wikipedia-mcp)

See the full readme for mcp docs\serverside-mcp-features.md

**10-06-2025**

Beta Release 0.1 is Live! Check the releases tag, ->
This release implements Character Profiles, you can hot swap between Yoda, C3PO, and Tony Stark. They each have their own system prompts and voice presets that will persist (I hope).

- Standard edition, Master Yoda
- C3PO
- Stark

![model_settings](https://github.com/thesavant42/chainloot/blob/main/docs/pics/selected-stark.png?raw=true)

**10-03-2025**

Latest commit: Transcription via microphone widget is complete.

![demo](https://github.com/thesavant42/chainloot/blob/main/docs/pics/demo.png?raw=true)
