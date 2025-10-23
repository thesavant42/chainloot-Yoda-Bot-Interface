#!/bin/bash

# Copy voices from mounted location to expected location
echo "Copying voices to TTS-WebUI..."
# Find all .wav files in subdirectories and copy them to the main chatterbox directory
find /app/tts-webui/voices/chatterbox/ -name "*.wav" -exec cp {} /app/tts-webui/voices/chatterbox/ \;

# Start TTS-WebUI server in background
python3 server.py --docker &

# Wait for server to start and API to be ready
echo "Waiting for TTS-WebUI to start..."
sleep 15

# Check if the OpenAI TTS API is responding
echo "Checking if TTS-WebUI API is responding..."
if curl -f http://localhost:7778/v1/audio/voices/chatterbox --max-time 10 --silent --show-error > /dev/null; then
    echo "TTS-WebUI API is responding correctly"
else
    echo "TTS-WebUI API health check failed"
fi

# Keep the container running
wait