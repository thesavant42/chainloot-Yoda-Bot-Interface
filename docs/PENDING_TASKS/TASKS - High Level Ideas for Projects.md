TASKS - High Level Ideas for Projects



# Project: LLM Provider Wizard

##  Add Ollama as a server provider options

## Description

Currently I have ollama installed in the stack but am still configured for LM Studio. It's time to add some flexibility into the server options.

Ollama connectivity PoC:
    - docs\testing\ollama_test.py
    - docs\testing\list_ollama_models.py

 ## Goal; A provider selector offering lm studio, (as it's currently configured), or Ollama. 
- SubGoal is to remove LM Studio from my personal architecture, but not remove support for it. I will still run both services in parallel for a while.
- Stretch goal: download new models from app

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




# Project: Saving Time with Persistent cache for installations/builds

- Things like packages that we rebuild by hand everytime
- Installations take a REALLY long time to complete, most of it is rebuilding packages we know will buid.
- An installation cache would be choice.

## Task: Websocket Streaming Audio

- Streaming audio is supported by Chainlit since 2.0.0 and we should implement it. 
- I've begun some cursory research, detailed here: docs\streaming_audio_research.md
- Check out this proof of concept, Helm, which uses streaming audio + post processing effects to make voices in chainloot sound like IronMan and C3PO robots:
  - lib/Helm/helm-README.md
  - lib/Helm/helm_optimized.py

### Open Questions: 
Q:
A:

Notes:

Progress:

# Project: App Modular Restructuring

The main app.py is at time of writing approximately 570 lines of code, give or take. It began as a mostly succinct piece of elegant code, as the features have expanded, so too has the clutter.

## Task: Refactor

Design a refactor of app.py, so that:
- The app logic is mostly imports and includes, setting up definitions, glue logic and an entry point. 

Many best practices recommend keeping python limited to about 100 lines of code before refactoring becomes necessary. Refactoring into smaller modules also limits the blast radius of software errors.

### Open Questions

Q: What best practices do you recommend for slimming down a chainlit applicatoin?
A:

Q: Is it possible/practical/clever/stupid to make each @cl. object in the app it's own submodule .py file, in a lib folder?
A:

### Feedback: 

Notes:

Progress: