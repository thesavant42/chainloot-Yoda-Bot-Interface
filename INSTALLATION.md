# INSTALLATION.md

## Installation & Setup

### Docker Setup (Recommended)

This project uses Docker Compose for easy deployment with optimized build caching.

#### Prerequisites
- Docker Desktop or Docker Engine
- Docker Compose
- At least 16GB RAM recommended
- NVIDIA GPU with CUDA support (optional, for GPU acceleration)

#### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/thesavant42/chainloot-Yoda-Bot-Interface.git
   cd chainloot-Yoda-Bot-Interface
   ```

2. **Enable BuildKit for faster builds** (add to your shell profile for permanence):
   ```powershell
   # PowerShell
   $env:DOCKER_BUILDKIT=1
   ```

3. **Start all services:**
   ```bash
   # First build (may take 10-15 minutes)
   docker-compose -f install/docker/docker-compose.yml up --build

   # Subsequent runs (much faster due to caching)
   docker-compose -f install/docker/docker-compose.yml up
   ```

4. **Access the application:**
   - **Main App (HTTP):** http://localhost:8000
   - **Main App (HTTPS):** https://localhost:8443
   - **TTS-WebUI (API):** http://localhost:7778
   - **TTS-WebUI (Gradio UI):** http://localhost:7770
   - **TTS-WebUI (React UI):** http://localhost:3000

#### Build Optimization Features

The Docker setup includes advanced caching optimizations:

- **Layer Caching**: Heavy installations (Python packages, MCP servers, ML models) happen before code copy
- **Cache Mounts**: Persistent caches for pip, npm, uv, and Hugging Face downloads
- **BuildKit**: Parallel builds and advanced caching features

**Performance Benefits:**
- First build: ~10-15 minutes
- Code-only changes: ~1-2 minutes (90%+ faster)
- Dependency changes: Still benefit from package caches

#### Docker Commands

```bash
# Start services
docker-compose -f install/docker/docker-compose.yml up -d

# Stop services
docker-compose -f install/docker/docker-compose.yml down

# View logs
docker-compose -f install/docker/docker-compose.yml logs -f

# Rebuild specific service
docker-compose -f install/docker/docker-compose.yml build chainlit

# Clean rebuild (when dependencies change)
docker builder prune -f
docker-compose -f install/docker/docker-compose.yml build --no-cache

# Update services
docker-compose -f install/docker/docker-compose.yml pull
docker-compose -f install/docker/docker-compose.yml up -d
```

#### Environment Configuration

Create a `.env` file in the project root with any required API keys:

```env
# Example environment variables (if needed)
# OPENAI_API_KEY=your_key_here
# BRAVE_API_KEY=your_key_here
```

#### Services Overview

- **Chainlit**: Main conversational AI interface (ports 8000/8443)
- **TTS-WebUI**: Text-to-speech with voice cloning (ports 7778/7770/3000)
- **PostgreSQL**: Database for conversation persistence (port 5432)
- **LocalStack**: AWS S3 simulation for file storage (port 4566)
- **Ollama**: Local LLM runtime (port 11434)

### Manual Setup (Alternative)

If you prefer not to use Docker, you'll need to set up each component manually:

1. **LM Studio**: Run locally on port 1234
2. **TTS-WebUI**: Run locally on ports 7778/7770/3000
3. **PostgreSQL**: Local database setup
4. **Python Environment**: Install dependencies from `install/requirements-*.txt` files

See the individual component documentation for manual setup instructions.
