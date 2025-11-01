#!/bin/bash

# Check if voices directory has content, no need to copy if already present
if [ ! "$(ls -A /app/tts-webui/voices/chatterbox/*.wav 2>/dev/null)" ]; then
    echo "Copying voices to TTS-WebUI..."
    # Only copy if voices directory is empty or missing files
    find /app/mounted-voices/chatterbox/ -name "*.wav" -exec cp {} /app/tts-webui/voices/chatterbox/ \; 2>/dev/null || echo "No external voices to copy"
else
    echo "Voice files already present, skipping copy"
fi

# Start TTS-WebUI server in background
python3 server.py --docker &

# Wait for server to start and API to be ready
echo "Waiting for TTS-WebUI to start..."
sleep 15

# Check if the OpenAI TTS API is responding
echo "Checking if TTS-WebUI API is responding..."
if curl -f http://localhost:7778/v1/audio/voices/chatterbox --max-time 10 --silent --show-error > /dev/null; then
    echo "TTS-WebUI API is responding correctly"
    
    # Run warmup script
    echo "Running TTS-WebUI warmup..."
    /app/host-scripts/tts-warmup.sh
else
    echo "TTS-WebUI API health check failed"
fi

# Keep the container running
wait