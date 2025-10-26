#!/bin/bash
# PediAssist Start Script

set -e

echo "Starting PediAssist..."

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
elif [ -f .env.development ]; then
    export $(cat .env.development | grep -v '^#' | xargs)
fi

# Create necessary directories
mkdir -p data logs cache

# Start services
echo "Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Check health
echo "Checking service health..."
docker-compose ps

echo "PediAssist is starting up!"
echo "Application will be available at: http://localhost:8000"
echo "Grafana dashboard: http://localhost:3000"
echo "Prometheus metrics: http://localhost:9090"
echo ""
echo "Use 'docker-compose logs -f pediassist' to view application logs"
echo "Use 'docker-compose down' to stop all services"
