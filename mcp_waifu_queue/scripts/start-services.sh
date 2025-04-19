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
nohup python3 -m mcp_waifu_queue.worker & # Use python -m for module execution

# Removed queue service start
# Removed response service start

echo "Worker service started."
