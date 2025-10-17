# Docker Configuration

This folder contains all Docker-related files for the Chainloot Yoda Bot Interface project.

## Files

- `Dockerfile`: Multi-stage Dockerfile for building the Chainlit application container with MCP support.
- `TTS-WebUI.Dockerfile`: Dockerfile for building the TTS-WebUI container with GPU support and extensions.
- `docker-compose.yml`: Orchestrates all services including Chainlit, TTS-WebUI, PostgreSQL, LocalStack, and Ollama.

## Build Optimization

The Dockerfile is optimized for Docker layer caching:

- Python dependencies are installed in a separate builder stage and copied to the final image
- MCP servers and sentiment analysis model are downloaded before copying application code
- Cache mounts are used for pip, uv, npm, and Hugging Face caches
- This allows for faster rebuilds when only application code changes, as the heavy installation steps are cached

### Build Caching Tips

**Enable BuildKit** (recommended for faster builds):
```bash
# Windows PowerShell
$env:DOCKER_BUILDKIT=1
docker-compose -f docker/docker-compose.yml build

# Or set permanently in PowerShell profile:
# Add to $PROFILE: $env:DOCKER_BUILDKIT=1
```

**Use cache-from for incremental builds**:
```bash
# Build using previous image as cache source
docker build --cache-from docker-chainlit:latest -f docker/Dockerfile -t docker-chainlit:latest .
```

**Clean rebuild** (when dependencies change):
```bash
docker builder prune -f  # Clear build cache
docker-compose -f docker/docker-compose.yml build --no-cache
```

## Usage

To start all services:

```bash
docker-compose -f docker/docker-compose.yml up --build
```

To start in detached mode:

```bash
docker-compose -f docker/docker-compose.yml up -d --build
```

To stop services:

```bash
docker-compose -f docker/docker-compose.yml down
```

## Services

- **Chainlit**: Main application on ports 8000 (HTTP) and 8443 (HTTPS)
- **TTS-WebUI**: Text-to-speech interface on ports 7778 (API), 7770 (Gradio), 3000 (UI)
- **PostgreSQL**: Database on port 5432
- **LocalStack**: AWS S3 simulation on port 4566
- **Ollama**: LLM service on port 11434

## Building Individual Services

To build just the Chainlit app:

```bash
docker-compose -f docker/docker-compose.yml build chainlit
```

To build just TTS-WebUI:

```bash
docker-compose -f docker/docker-compose.yml build tts-webui
```

## Volumes

- `tts_models`: Persistent storage for TTS models
- `ollama_data`: Persistent storage for Ollama models
- `./.data/postgres`: PostgreSQL data
- `./localstack-init`: LocalStack initialization scripts
- `./tts_voices`: TTS voice samples
- `./ssl`: SSL certificates
- `./uploads`: User uploads

## Environment

Requires `.env` file in project root with necessary environment variables.

## Links

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [TTS-WebUI](https://github.com/rsxdalv/tts-webui)