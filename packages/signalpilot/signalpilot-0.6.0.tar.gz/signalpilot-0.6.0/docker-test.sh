#!/bin/bash
# SignalPilot CLI - Docker Testing Script

set -e

echo "🐳 SignalPilot CLI - Docker Test Environment"
echo "============================================"
echo ""

# Build the Docker image
echo "📦 Building Docker image..."
docker compose build

# Start the container
echo "🚀 Starting container..."
docker compose up -d

# Wait for container to be ready
sleep 2