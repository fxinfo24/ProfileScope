#!/bin/bash
# Start Celery Worker and Flower Monitoring for ProfileScope
# This script is for LOCAL DEVELOPMENT only
# For Railway production, workers are deployed as separate services

echo "🚀 Starting ProfileScope Real-Time Processing Pipeline"
echo "====================================================="

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "⚠️  Warning: .env file not found, using system environment"
fi

# Check if Redis is running
echo "Checking Redis connection..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis not running. Please start Redis server first:"
    echo ""
    echo "   macOS:   brew services start redis"
    echo "   Linux:   sudo systemctl start redis"
    echo "   Docker:  docker run -d -p 6379:6379 redis:alpine"
    echo ""
    echo "Or set REDIS_URL in .env to use remote Redis service."
    exit 1
fi

echo "✅ Redis server is running"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found at ./venv"
    echo "Proceeding with system Python..."
fi

# Start Celery worker in background
echo "🔄 Starting Celery worker..."
celery -A app.core.tasks worker --loglevel=info --queues=analysis &
CELERY_PID=$!

# Start Flower monitoring dashboard
echo "🌸 Starting Flower monitoring dashboard..."
celery -A app.core.tasks flower --port=5555 &
FLOWER_PID=$!

echo ""
echo "✅ Real-Time Processing Pipeline Started!"
echo ""
echo "📊 Monitoring Dashboard: http://localhost:5555"
echo "🔄 Celery Worker PID: $CELERY_PID"
echo "🌸 Flower Monitor PID: $FLOWER_PID"
echo ""
echo "📋 Available Queues:"
echo "   • analysis  - Main profile analysis tasks"
# Note: only the `analysis` queue is implemented in this repository's current Celery worker.
# Other queues are placeholders for future expansion.
# echo "   • vision    - Computer vision image processing"
# echo "   • reports   - Report generation"
# echo "   • data      - Data collection tasks"
echo ""
echo "To stop services:"
echo "   kill $CELERY_PID $FLOWER_PID"
echo "   or run: scripts/stop_celery.sh"

# Wait for user interrupt
echo "Press Ctrl+C to stop all services..."
wait