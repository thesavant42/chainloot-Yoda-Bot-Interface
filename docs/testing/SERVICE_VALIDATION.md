# Service Validation Checklist

This document provides a comprehensive checklist to validate that all Chainloot Yoda Bot Interface services are running correctly and properly configured.

## Prerequisites

- Docker and Docker Compose installed
- Project cloned and configured
- Services started with: `docker-compose -f docker/docker-compose.yml -p chainloot-yoda-bot-interface up -d`

## Service Status Validation

### 1. Container Status Check
Verify all containers are running with correct names:

```bash
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
```

Expected output should include:
- `chainloot-yoda-bot-interface-chainlit-1` - Chainlit app (healthy)
- `chainloot-yoda-bot-interface-postgres-1` - PostgreSQL database
- `chainloot-yoda-bot-interface-tts-webui-1` - TTS-WebUI service
- `chainloot-yoda-bot-interface-localstack-1` - LocalStack S3 storage
- `chainloot-yoda-bot-interface-ollama-1` - Ollama LLM service

### 2. Service Grouping Validation
All containers should be prefixed with `chainloot-yoda-bot-interface-` to ensure proper grouping and avoid conflicts.

### 3. Port Accessibility Check

#### Chainlit Web Interface
```bash
curl -I http://localhost:8000
# Should return HTTP 200 or redirect to HTTPS
curl -I https://localhost:8443
# Should return HTTP 200 (may require accepting self-signed certificate)
```

#### PostgreSQL Database
```bash
docker exec chainloot-yoda-bot-interface-postgres-1 pg_isready -h localhost -p 5432 -U root
# Should return: localhost:5432 - accepting connections
```

#### TTS-WebUI
```bash
curl -I http://localhost:7778
# Should return HTTP 200
```

#### LocalStack S3 Storage
```bash
curl -I http://localhost:4567/_localstack/health
# Should return HTTP 200 with JSON health status
```

#### Ollama API
```bash
curl http://localhost:11434/api/tags
# Should return JSON with available models
```

### 4. Datalayer (LocalStack) Write Access Validation

#### Bucket Existence
```bash
docker exec chainloot-yoda-bot-interface-localstack-1 awslocal s3 ls
# Should show: my-bucket
```

#### Write Test
```bash
# Create test file
docker exec chainloot-yoda-bot-interface-localstack-1 sh -c "echo 'validation test' > validation.txt"

# Upload to bucket
docker exec chainloot-yoda-bot-interface-localstack-1 awslocal s3 cp validation.txt s3://my-bucket/validation.txt
# Should show: upload: ./validation.txt to s3://my-bucket/validation.txt
```

#### Read Test
```bash
# List bucket contents
docker exec chainloot-yoda-bot-interface-localstack-1 awslocal s3 ls s3://my-bucket/
# Should show: validation.txt file

# Download and verify
docker exec chainloot-yoda-bot-interface-localstack-1 awslocal s3 cp s3://my-bucket/validation.txt downloaded.txt
docker exec chainloot-yoda-bot-interface-localstack-1 cat downloaded.txt
# Should show: validation test
```

### 5. Ollama Model Validation

#### Available Models
```bash
docker exec chainloot-yoda-bot-interface-ollama-1 ollama list
# Should show installed models (e.g., phi4-mini:latest, llama2:7b)
```

#### Model Persistence
```bash
ls -la ollama_data/models/blobs/
# Should show large model files (.bin, etc.) indicating models are persisted
```

### 6. Application Functionality Test

#### Web Interface Access
1. Open browser to `https://localhost:8443`
2. Accept self-signed certificate if prompted
3. Should load Chainlit interface
4. Select a profile (Yoda/AI/Stark)
5. Settings gear should be visible and functional

#### Provider Switching Test
1. Click settings gear
2. Change LLM Provider from current to other option
3. Model dropdown should update with provider-specific models
4. Select a model and send a test message
5. Should receive AI response

#### TTS Functionality Test (Optional)
1. Send a message
2. Audio playback should work
3. Voice selection should be available in settings

## Troubleshooting

### If containers aren't running:
```bash
docker-compose -f docker/docker-compose.yml -p chainloot-yoda-bot-interface up -d
```

### If LocalStack bucket missing:
```bash
docker exec chainloot-yoda-bot-interface-localstack-1 awslocal s3 mb s3://my-bucket
```

### If Ollama models missing:
```bash
docker exec chainloot-yoda-bot-interface-ollama-1 ollama pull phi4-mini:latest
docker-compose -f docker/docker-compose.yml -p chainloot-yoda-bot-interface restart chainlit
```

### If app shows model errors:
- Check provider setting in `config/config.json`
- Ensure selected model exists for that provider
- Restart Chainlit: `docker-compose restart chainlit`

## Success Criteria

All services should be:
- ✅ Running with `chainloot-yoda-bot-interface-` prefix
- ✅ Accessible on expected ports
- ✅ LocalStack S3 bucket readable/writable
- ✅ Ollama models available and persisted
- ✅ Chainlit web interface functional
- ✅ Provider switching working
- ✅ No port conflicts or service grouping issues

When all checks pass, the Chainloot Yoda Bot Interface is fully operational.