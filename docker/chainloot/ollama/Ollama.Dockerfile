# Custom Ollama Dockerfile with MQTT health reporting support
FROM ollama/ollama:latest

# Install Python and pip for health monitoring
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv && rm -rf /var/lib/apt/lists/*

# Copy the pip configuration file
COPY ../pip.conf /etc/pip.conf

# Set working directory for userland scripts and data
WORKDIR /app
RUN ls
COPY ./ollama/requirements-ollama.txt /app/requirements-ollama.txt

# Create virtual environment for Python packages to avoid system conflicts
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
# Install Python dependencies for health monitoring in virtual environment
RUN pip install -r requirements-ollama.txt && rm requirements-ollama.txt

# Expose Ollama port
EXPOSE 11434
