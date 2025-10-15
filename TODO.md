# Feature: Docker Container

Goal is to architect a system to containerize the chainlit app, and to unify all of the docker containers into a single Dockerfile. This will group the containers together in Docker Desktop and tie them together for administration convenience.

## TASK: Use MCP tools for context7 and Deepwiki: Look up current documentation for chainlit and docker desktop.

It's time to containerize development into something portable and robust. To do that we will dockerify.

### Docker Host:

- Docker Desktop for Windows, WSL2 Backend Host, GPU Enabled
- Docker Host: 192.168.1.98
- Docker Port to map: Host Post:42420 Container Port: (Whatever chainlit is running on)
  - Considerations: In order for the browser to allow access to the Microphone, the app needs be accessed via a loopback address (localhost) or over HTTPS. Self-signed certificates are fine.

I'd like to try and keep the app as performant as possible so a light weight container would probably be ideal.

- Build off an existing Chainlit base image (e.g., `python:3.11-slim` or official Chainlit if available) to avoid reinventing wheels, but customize for MCP stdio servers (which require `uvx` and specific tools like [`mcp-server-time`](/c:/Users/jbras/AppData/Local/Packages/PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0/LocalCache/local-packages/Python313/site-packages/mcp/__init__.py )). 
The app's server-side MCP initialization (app.py lines 84+) and multiple services suggest a custom multi-stage Dockerfile for efficiency.

- Use a lightweight Linux base like Ubuntu 22.04 or Alpine for WSL2 compatibility and GPU support. 
-- Alpine is smaller and faster due to musl libc and fewer default packages, but may require more setup for complex dependencies (e.g., glibc-based tools). 
-- Ubuntu offers broader compatibility and pre-installed tools, but is larger. 

For this project, Alpine is preferable for performance if dependencies align; otherwise, use Ubuntu for simplicity. # Agreed 100%

- Ensure it supports Python, Node.js (if needed for Chainlit), and MCP dependencies. 
- Avoid Windows containers to match the WSL2 backend.

- Use Docker Compose for orchestration:
    - Define services for 
        - Chainlit, datalayer, 
        - TTS/STT, 
        - and Ollama in a single `docker-compose.yml`. 
    - Network them via Docker's internal bridge (e.g., expose datalayer on a container port, connect via service names). 
        - This unifies management without merging images.

-  The TTS/STT server, the datalayer, ollama, and chainlit, are all components of this application that are all hosted on Docker, but all of them are individually managed services. 
-  It makes sense to design a unified continer setup that manages all of the components together.

### Effort involves: 

(1) Creating a multi-service Compose file with shared volumes for data persistence (e.g., uploads/, .chainlit/). 
(2) Configuring environment variables (from .env) for inter-service communication. 
(3) Handling GPU passthrough for Ollama. 
 -- This should be done already, but let' test it
 -- A: Agreed, verify existing GPU setup in Ollama container before proceeding.
(4) Ensuring MCP servers run in the Chainlit container without conflicts. 


### Estimated: 1-2 weeks for setup/testing, focusing on performance.
-- Response: That's a lont longer than I was anticipating. 
-- Let's stagger it into stages so that we don't need 100% completion in order for the system to be useful.
-- A: Stagger into stages: 
    Stage 1 - Containerize Chainlit with basic MCP. 
    Stage 2 - Integrate datalayer and TTS/STT. 
    Stage 3 - Add Ollama and optimizations. Each stage testable independently.


### Server-side MCP modules: Additional OS considerations:
 - Install `uvx` (via pip or apt) and MCP server packages in the container. 
 - Ensure stdio-based servers (lib/mcp_server_manager.py lines 61+) have access to shell commands. 
 - No special OS needs beyond Python/Linux, but test for WSL2 compatibility.

### Optimizations: 

- (1) Use host networking mode for low-latency inter-container comms.
    -- This is a good idea but will require careful planning
    -- A: Plan involves mapping ports explicitly in Compose to avoid conflicts; test incrementally.
- (2) Enable GPU sharing for Ollama via `--gpus all`. 
    -- DONE!
- (3) Shared tmpfs volumes for fast I/O. 
- (4) Resource limits (CPU/memory) to prevent bottlenecks. 
    -- Let's not worty about setting limits, let's just build it working first
    -- A: Focus on functionality first; add limits in later iterations if needed.
- (5) Pre-initialize MCP on startup (app.py lines 84+) to reduce runtime overhead.


### Reqiurements: 

- If you need to edit a file and I haven't yet said to, you must ask first. 
- Don't assume anything, this is complicated stuff.

- [x] Phase 01: Chainlit frontend app running in a container with existing datalayer

- [ ] Phase 02: Unification of services
    - [ ] https://github.com/rsxdalv/TTS-WebUI?tab=readme-ov-file
        - [ ] will need to map voices directory
    - [ ] https://github.com/Chainlit/chainlit-datalayer
    - [ ] https://hub.docker.com/r/ollama/ollama
        - [ ] will need to map models folder
    - [ ] All containers should be set to automatically restart unless stopped


- [ ] Final Phase: Optimizations