# Multi-stage Dockerfile for Chainlit app with MCP support on Debian slim
FROM python:3.11-slim AS builder

# Install build dependencies (added libssl-dev for SSL support during build)
RUN apt-get update && apt-get install -y gcc libffi-dev libssl-dev && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip cache purge && pip install --no-cache-dir -r requirements.txt

# Install uv for MCP servers (required for MCP tool usage as per README)
RUN pip install uv

# Final stage
FROM python:3.11-slim

# Install runtime dependencies (added curl for health checks, nodejs/npm for potential front-end if needed, bash and passwd for user management)
RUN apt-get update && apt-get install -y nodejs npm curl bash passwd && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set work directory
WORKDIR /app

# Copy app code (includes app.py, .env, etc.)
COPY . .

# Copy and make executable the startup script
COPY start.sh .
RUN chmod +x start.sh

# Install MCP servers explicitly (Python via uv, npm via npm install -g)
RUN uv tool install mcp-server-time && \
    uv tool install mcp-server-fetch && \
    uv tool install mcp-server-git && \
    uv tool install wikipedia-mcp && \
    npm install -g @brave/brave-search-mcp-server && \
    npm install -g @modelcontextprotocol/server-memory && \
    npm install -g @modelcontextprotocol/server-sequential-thinking && \
    npm install -g @kimtaeyoon83/mcp-server-youtube-transcript

# Pre-download the sentiment analysis model to avoid runtime downloads
RUN python -c "from transformers import pipeline; pipeline('text-classification', model='joeddav/distilbert-base-uncased-go-emotions-student')"

# Set PATH to include MCP tool locations
ENV PATH="/root/.local/bin:/usr/local/bin:$PATH"

# Create a non-root user for security (per Docker best practices)
RUN useradd --create-home --shell /bin/bash appuser && chown -R appuser:appuser /app

# Expose ports (8000 for HTTP, 8443 for HTTPS; Chainlit default is 8000)
EXPOSE 8000 8443

# Health check to ensure the HTTPS server is running (default mode)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -k -f https://localhost:8443/health || exit 1

# Command to run both HTTP and HTTPS servers
CMD ["./start.sh"]