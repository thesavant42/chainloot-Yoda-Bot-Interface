#!/bin/bash

# Function to cleanup background processes
cleanup() {
    echo "Shutting down services..."
    if [ ! -z "$CHAINLIT_PID" ]; then
        echo "Stopping Chainlit server (PID: $CHAINLIT_PID)..."
        kill $CHAINLIT_PID 2>/dev/null
    fi
    if [ ! -z "$MQTT_PID" ]; then
        echo "Stopping MQTT MCP server (PID: $MQTT_PID)..."
        kill $MQTT_PID 2>/dev/null
    fi
    # Remove cron job
    echo "Removing container monitoring cron job..."
    rm -f /etc/cron.d/container_monitor
    service cron reload 2>/dev/null || true
    exit 0
}

# Set up signal handlers for cleanup
trap cleanup SIGTERM SIGINT

# Run database migrations
echo "Running database migrations..."
prisma migrate deploy --schema=./database/schema.prisma
echo "Generating Prisma client..."
prisma generate --schema=./database/schema.prisma

# Start MQTT MCP server in background
echo "Starting MQTT MCP server on port 8100..."
mqtt-mcp &
MQTT_PID=$!
echo "MQTT MCP server started with PID: $MQTT_PID"

# Give MQTT server a moment to start up
sleep 3

# Start cron daemon for container monitoring
echo "Starting cron daemon for container monitoring..."
service cron start

# Add cron job to run container monitor every 5 minutes
echo "Setting up container monitoring cron job..."
echo "*/5 * * * * /usr/local/bin/python3 /app/lib/container_monitor_script.py >> /app/container_monitor.log 2>&1" > /etc/cron.d/container_monitor
echo "*/5 * * * * /usr/local/bin/python3 /app/lib/system_monitor_script.py >> /app/system_monitor.log 2>&1" >> /etc/cron.d/container_monitor
chmod 0644 /etc/cron.d/container_monitor
crontab /etc/cron.d/container_monitor

# Run initial container monitoring
echo "Running initial container monitoring..."
chmod +x /app/lib/container_monitor_script.py
/usr/local/bin/python3 /app/lib/container_monitor_script.py

# Run initial system monitoring
echo "Running initial system monitoring..."
chmod +x /app/lib/system_monitor_script.py
/usr/local/bin/python3 /app/lib/system_monitor_script.py

# Default mode is https
MODE="${1:-https}"

if [ "$MODE" = "http" ]; then
    echo "Starting HTTP server on port 8000"
    chainlit run app.py --host 0.0.0.0 --port 8000 &
    CHAINLIT_PID=$!
    wait $CHAINLIT_PID
elif [ "$MODE" = "https" ]; then
    echo "Starting HTTPS server on port 8443"
    chainlit run app.py --host 0.0.0.0 --port 8443 --ssl-cert /app/ssl/chainloot-cert.pem --ssl-key /app/ssl/chainloot-key.pem &
    CHAINLIT_PID=$!
    wait $CHAINLIT_PID
elif [ "$MODE" = "both" ]; then
    echo "Starting both HTTP (8000) and HTTPS (8443) servers"
    chainlit run app.py --host 0.0.0.0 --port 8443 --ssl-cert /app/ssl/chainloot-cert.pem --ssl-key /app/ssl/chainloot-key.pem &
    CHAINLIT_PID=$!
    wait $CHAINLIT_PID
else
    echo "Invalid mode: $MODE. Use 'http', 'https', or 'both'"
    cleanup
    exit 1
fi