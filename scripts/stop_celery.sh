#!/bin/bash
# Stop Celery Worker and Flower Monitoring

echo "🛑 Stopping ProfileScope Real-Time Processing Pipeline"
echo "===================================================="

# Stop Celery workers
echo "Stopping Celery workers..."
pkill -f "celery.*worker" 

# Stop Flower monitoring
echo "Stopping Flower monitoring..."
pkill -f "celery.*flower"

# Stop any remaining celery processes
echo "Cleaning up remaining processes..."
pkill -f celery

echo "✅ All Celery services stopped"