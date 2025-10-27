FROM python:3.13.3-slim-bookworm

# Install required packages
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install aiohttp
RUN pip install aiohttp

# Create app directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/history /app/logs /app/images /app/sounds

# Copy application files
COPY gpu-monitor/gpu-stats.html /app/
COPY gpu-monitor/monitor_gpu.sh /app/
COPY gpu-monitor/server.py /app/
COPY gpu-monitor/images/ /app/images/
COPY gpu-monitor/sounds/ /app/sounds/

# Make scripts executable
RUN chmod +x /app/monitor_gpu.sh

# Expose port for web server
EXPOSE 8081

# Start the application
CMD ["./monitor_gpu.sh"]