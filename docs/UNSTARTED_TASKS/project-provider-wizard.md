
# Project: LLM Provider Wizard
 
  Add Ollama as a server provider options

## Description

Currently I have ollama installed in the stack but am still configured for LM Studio. It's time to add some flexibility into the server options.

Ollama connectivity PoC:
    - docs/testing/ollama/ollama_test.py
    - docs/testing/ollama/list_ollama_models.py

 ### Goal; A provider selector offering lm studio, (as it's currently configured), or Ollama.

- Configuator to select between different providers
- Ability to configure multiple connection profiles for the same provider type (ie, multiple OpenAI-compatible servers, multiple ollama, etc) 
  - Will need to capture: 
    - API endpoints 
    - Host addresses
    - API credentials 
    - New model names 
    - more?
- SubGoal is to remove LM Studio from my personal architecture, but not remove support for it. 
  - I will still run both services in parallel for a while.
- Stretch goal: download new models from app
  - via the ollama API

## Task

-Design and implement a new workflow to switch between ollama and lm studio models
  - Use Context7 MCP to get the most recent documentation for Ollama, Chainlit, and any other necessary tech
   - Can begin with a json configuration file for servers, and then add a "New Server" Wizard later on
   - Store all json configurations in the new (config) subdirectory.
 - Track your work in THIS DOCUMENT
 - Update documentation after completion

### Passing Test Case:


- No new bugs, no exceptions!
- Should be able to list all models currently in local llama instance
- Should be able to select a model for conversation, via the settings widget in the React UI
    - these settings should persist across application restarts ( widget should write to config/config.json)
- LM Studio / OpenAI Compatible APIs should still continue to function per SOP, with no regressions 

### Open Questions:

Open Questions:

Q: Should we turn this into a connection wizard to add providers? Need to be able to handle API keys, endpoints, metadata.
    -- Store it in a database and generate configuration additions?
    -- Could expand to include any openai-compatible chat completion endpoint
A:

Q: Is Ollama currently forwarding its service port to the LAN? If not, let's make sure that the docker compose forwards that out, so that other containers can make use of ollama. Some kind of a model cache would also probably be a good idea.

A:

### Feedback: 

Notes:

Status:


