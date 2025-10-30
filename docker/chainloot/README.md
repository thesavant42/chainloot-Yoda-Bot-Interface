# ./docker/

## Top level

### Significant Cleanups!

The app infrastructure layout has undergone a significant change, as a result, there will likekly be bugs.

This document supercedes all others that conflict. This is the source of truth for Chainloot's Docker setup.

 - Each container gets: 
    1. their own folder, 
    2. their own env file, 
    3. their own docker file

## Folder Layout Rules
 - Each container gets their own requirements.txt file, and should not be concerned with sharing package requirements.
 - Do not restructure this folder
 - Do not create new requirements.txt

### Container Folders

# Main Frontend App
./chainlit/

## Persistence / Datalayer
./database/
./localstack-init/

# Emotional Classifier + Messaging
./mosquitto/

# Model servering
./ollama/

 # TTS, STT
./tts-webui/

### Files
# High Level Project Compose
docker-compose.yml

# PIP Cache Proxy Setup
pip.conf

# This file you are reading
README.md