# Docker Configuration

This folder contains all Docker-related files for the Chainloot Yoda Bot Interface project.

## Files

- `Dockerfile`: Multi-stage Dockerfile for building the Chainlit application container with MCP support.
- `TTS-WebUI.Dockerfile`: Dockerfile for building the TTS-WebUI container with GPU support and extensions.
- `docker-compose.yml`: Orchestrates all services including Chainlit, TTS-WebUI, PostgreSQL, LocalStack, and Ollama.

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