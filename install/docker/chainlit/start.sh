#!/bin/bash

# Run database migrations
echo "Running database migrations..."
prisma migrate deploy --schema=install/database/schema.prisma
echo "Generating Prisma client..."
prisma generate --schema=install/database/schema.prisma

# Default mode is https
MODE="${1:-https}"

if [ "$MODE" = "http" ]; then
    echo "Starting HTTP server on port 8000"
    chainlit run app.py --host 0.0.0.0 --port 8000
elif [ "$MODE" = "https" ]; then
    echo "Starting HTTPS server on port 8443"
    chainlit run app.py --host 0.0.0.0 --port 8443 --ssl-cert /app/ssl/chainloot-cert.pem --ssl-key /app/ssl/chainloot-key.pem
elif [ "$MODE" = "both" ]; then
    echo "Starting both HTTP (8000) and HTTPS (8443) servers"
    chainlit run app.py --host 0.0.0.0 --port 8443 --ssl-cert /app/ssl/chainloot-cert.pem --ssl-key /app/ssl/chainloot-key.pem &
    wait
else
    echo "Invalid mode: $MODE. Use 'http', 'https', or 'both'"
    exit 1
fi