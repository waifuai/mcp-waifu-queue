"""
Redis Queue Worker Process.

This module implements the RQ (Redis Queue) worker process that continuously
monitors the Redis queue for incoming text generation jobs and executes them
using the utility functions defined in utils.py.

Key Features:
- Continuous job processing from Redis queue
- Automatic job dequeuing and execution
- Error handling and logging for worker failures
- Configuration-based Redis connection
- Integration with RQ for job management

Architecture:
- Uses RQ Worker class for queue monitoring
- Connects to Redis using configuration settings
- Listens to the 'default' queue for incoming jobs
- Executes jobs by calling call_predict_response from utils.py
- Provides logging for monitoring and debugging

Usage:
Run this script as a separate process to start the worker:
    python -m mcp_waifu_queue.worker

The worker should run continuously alongside the MCP server. It will:
1. Connect to Redis using the configured URL
2. Monitor the 'default' queue for new jobs
3. Execute jobs by calling the prediction functions
4. Handle errors gracefully and log them
5. Continue processing until manually stopped

Dependencies:
- redis: Redis client for connection management
- rq: Redis Queue for worker implementation
- logging: For operation logging and error reporting
- config: For Redis URL and configuration loading
"""

import logging
import redis
from rq import Worker, Queue, Connection

from mcp_waifu_queue.config import Config

config = Config.load()

listen = ['default']

conn = redis.from_url(config.redis_url)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        try:
            worker.work()
        except Exception as e:
            logging.exception("Worker failed to start")