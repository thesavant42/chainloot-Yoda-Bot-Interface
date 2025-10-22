# Custom Ollama Dockerfile with MQTT health reporting support
FROM ollama/ollama:latest

# Set working directory for userland scripts and data
WORKDIR /app

# Install Python dependencies for health monitoring
COPY requirements-ollama.txt .
RUN pip install --no-cache-dir -r requirements-ollama.txt && rm requirements-ollama.txt

# Copy health monitoring script (to be created later)
# COPY health_monitor.py .

# Ensure the health monitor can run
# RUN chmod +x health_monitor.py

# Expose Ollama port
EXPOSE 11434

# Default command (same as base image)
CMD ["ollama", "serve"]