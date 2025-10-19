#!/bin/bash

# Start TTS-WebUI server in background
python3 server.py --docker &

# Wait for server to start
echo "Waiting for TTS-WebUI to start..."
sleep 10

# Try to activate the API service
echo "Activating TTS-WebUI API service..."

# First, check if the service checkbox needs to be set
curl -X POST http://localhost:3000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"data":[true],"event_data":null,"fn_index":242,"trigger_id":731,"session_hash":"7sfcr5kua3p"}' \
  --max-time 5 --silent --show-error

# Then activate the service
curl -X POST http://localhost:3000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"data":["0.0.0.0",7778],"event_data":null,"fn_index":241,"trigger_id":729,"session_hash":"7sfcr5kua3p"}' \
  --max-time 10 --silent --show-error

echo "TTS-WebUI API activation attempted. Checking if port 7778 is responding..."

# Wait a bit more for activation
sleep 5

# Test if the API is now responding
if curl -f http://localhost:7778/health --max-time 5 --silent --show-error; then
    echo "TTS-WebUI API successfully activated on port 7778"
else
    echo "TTS-WebUI API activation may have failed, but continuing..."
fi

# Keep the container running
wait