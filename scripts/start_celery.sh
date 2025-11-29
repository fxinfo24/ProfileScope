#!/bin/bash
# Start Celery Worker and Flower Monitoring for ProfileScope

echo "🚀 Starting ProfileScope Real-Time Processing Pipeline"
echo "====================================================="

# Load environment variables
source .env

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis not running. Please start Redis server first:"
    echo "   macOS: brew services start redis"
    echo "   Linux: sudo systemctl start redis"
    echo "   Docker: docker run -d -p 6379:6379 redis:alpine"
    exit 1
fi

echo "✅ Redis server is running"

# Activate virtual environment
source venv/bin/activate

# Start Celery worker in background
echo "🔄 Starting Celery worker..."
celery -A app.core.tasks worker --loglevel=info --queues=analysis,vision,reports,data &
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
echo "   • vision    - Computer vision image processing"
echo "   • reports   - Report generation"
echo "   • data      - Data collection tasks"
echo ""
echo "To stop services:"
echo "   kill $CELERY_PID $FLOWER_PID"
echo "   or run: scripts/stop_celery.sh"

# Wait for user interrupt
echo "Press Ctrl+C to stop all services..."
wait