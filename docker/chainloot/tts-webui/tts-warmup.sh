#!/bin/bash

echo "Starting TTS-WebUI warmup..."

# Generate timestamp for unique text
TIMESTAMP=$(date +"%A, %B %d, %Y")
echo "Warming up TTS model with timestamp: $TIMESTAMP"

# Function to wait for CUDA operations to complete
wait_for_cuda() {
    echo "Waiting for CUDA operations to stabilize..."
    sleep 8
}

# Function to retry operation with backoff
retry_with_backoff() {
    local max_attempts=2
    local delay=5
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo "Attempt $attempt of $max_attempts..."
        if eval "$1"; then
            return 0
        fi
        echo "Attempt $attempt failed, waiting ${delay}s before retry..."
        sleep $delay
        delay=$((delay + 5))
        attempt=$((attempt + 1))
    done
    
    echo "Operation failed after all attempts"
    return 1
}

# Step 1: TTS warmup with simplified parameters to avoid CUDA conflicts
echo "Step 1: TTS warmup (initial model loading may take 60+ seconds)..."
TTS_CMD='curl --silent -X POST "http://localhost:7778/v1/audio/speech" \
    -H "Content-Type: application/json" \
    -d "{\"model\": \"chatterbox\", \"input\": \"Warmup test $TIMESTAMP\", \"voice\": \"voices/chatterbox/yoda.wav\", \"temperature\": 1.0}" \
    --output /tmp/warmup.wav --max-time 180'

if retry_with_backoff "$TTS_CMD"; then
    echo "✓ TTS warmup successful"
    TTS_SUCCESS=true
else
    echo "✗ TTS warmup failed, but continuing startup..."
    TTS_SUCCESS=false
fi

# Wait for CUDA operations to complete and file to be written
wait_for_cuda

# Step 2: STT warmup only if TTS succeeded and file exists
if [ "$TTS_SUCCESS" = true ] && [ -f "/tmp/warmup.wav" ] && [ -s "/tmp/warmup.wav" ]; then
    echo "Step 2: STT warmup (Whisper model loading may take 30+ seconds)..."
    
    STT_CMD='curl --silent -X POST "http://localhost:7778/v1/audio/transcriptions" \
        -H "Content-Type: multipart/form-data" \
        -F "file=@/tmp/warmup.wav" \
        -F "model=openai/whisper-small.en" \
        --max-time 120'
    
    if retry_with_backoff "$STT_CMD"; then
        echo " STT warmup successful"
    else
        echo "STT warmup failed, but TTS is ready"
    fi
else
    echo "Skipping STT warmup due to TTS issues or missing audio file"
fi

# Cleanup
rm -f /tmp/warmup.wav

# Final stabilization wait
wait_for_cuda

echo "TTS-WebUI warmup completed - models should be pre-loaded for faster user responses"