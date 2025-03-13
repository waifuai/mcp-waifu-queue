#!/bin/bash
set -e

# Activate the virtual environment
source venv/bin/activate

# Check if Redis is already running
if redis-cli ping > /dev/null 2>&1; then
  echo "Redis server is already running."
else
  # Start Redis server
  echo "Starting Redis server"
  redis-server --daemonize yes
fi

# Start worker.py
echo "Starting worker.py"
nohup python3 mcp_waifu_queue/worker.py &

# Start queue service
echo "Starting queue service"
FLASK_APP=mcp_waifu_queue/queue.py FLASK_ENV=production QUEUE_PORT=${QUEUE_PORT:-5000} nohup flask run --host=0.0.0.0 --port=${QUEUE_PORT} &

# Start response service
echo "Starting response service"
FLASK_APP=mcp_waifu_queue/respond.py FLASK_ENV=production RESPOND_PORT=${RESPOND_PORT:-5001} nohup flask run --host=0.0.0.0 --port=${RESPOND_PORT} &

echo "Services started."
