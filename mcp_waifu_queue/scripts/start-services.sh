#!/bin/bash
# =============================================================================
# MCP Waifu Queue Service Startup Script
# =============================================================================
#
# This script initializes and starts the required services for the MCP Waifu
# Queue system, including Redis and the RQ worker process.
#
# Features:
# - Activates Python virtual environment
# - Checks if Redis is already running and starts it if needed
# - Starts the RQ worker process in the background
# - Provides status messages for each step
#
# Usage:
#   chmod +x ./scripts/start-services.sh
#   ./scripts/start-services.sh
#
# Requirements:
# - Redis server installed and available in PATH
# - Python virtual environment with dependencies installed
# - mcp_waifu_queue package available in Python path
#
# Services Started:
# - Redis server (daemonized)
# - RQ worker (background process)
#
# Note:
# This script is primarily designed for Linux/macOS environments.
# Windows users should start Redis and the worker manually.
# =============================================================================

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
