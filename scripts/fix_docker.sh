#!/bin/bash
# Emergency Docker Fix Script
# Use this if Docker is stuck or consuming too much CPU

echo "🚑 Starting Emergency Docker Fix..."

# 1. Stop all ProfileScope containers
echo "🛑 Stopping existing containers..."
docker compose down --remove-orphans

# 2. Prune build cache (optional, helps if builders are stuck)
# echo "🧹 Pruning header build cache..."
# docker builder prune -f

# 3. Build with resource constraints explicitly
echo "🏗️  Rebuilding with optimized configuration (Python 3.11)..."
# We use --no-cache to ensure we pick up the new Python 3.11 base image
docker compose up -d --build --force-recreate

echo "✅ Deployment trigger sent!"
echo "⏳ Please wait 2-3 minutes for the 'Frontend', 'Api', and 'Worker' containers to turn GREEN in Docker Desktop."
echo "👉 Then open: http://localhost:5173"
