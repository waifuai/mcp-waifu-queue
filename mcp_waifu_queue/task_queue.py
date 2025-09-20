"""
Redis Queue Management Module.

This module provides functionality for managing the Redis job queue system used
for asynchronous AI text generation requests. It integrates with the RQ (Redis Queue)
library to handle job enqueuing, status tracking, and result retrieval.

Key Features:
- Job enqueuing for text generation requests
- Job status tracking (queued, processing, completed, failed, unknown)
- Result retrieval from completed jobs
- Integration with Redis for persistent job storage
- Connection management using configuration settings

Functions:
- add_to_queue(): Enqueues a prompt for background processing
- get_job_status_from_queue(): Retrieves job status and results

Dependencies:
- redis: Redis client for connection management
- rq: Redis Queue for job management
- logging: For operation logging
- config: For Redis URL configuration
- utils: For the actual prediction function

The queue uses a TTL (Time To Live) of 3600 seconds (1 hour) for job results
to prevent indefinite storage of generated text.
"""

import logging
import requests
import redis
from rq import Queue
from rq.job import Job

from mcp_waifu_queue.config import Config
from mcp_waifu_queue.utils import call_predict_response

config = Config.load()

logging.basicConfig(level=logging.INFO)

conn = redis.from_url(config.redis_url)
q = Queue(connection=conn)


def add_to_queue(prompt: str) -> str:
    """Adds a text generation request to the Redis queue."""
    job = q.enqueue_call(func=call_predict_response, args=(prompt,), result_ttl=3600)
    return job.id

def get_job_status_from_queue(job_id: str) -> tuple[str, str | None]:
    """Retrieves the status and result (if available) of a job."""
    job = Job.fetch(job_id, connection=conn)
    if job.is_finished:
        return "completed", job.result
    elif job.is_failed:
        return "failed", None  # Or perhaps return the exception details
    elif job.is_queued:
        return "queued", None
    elif job.is_started:
        return "processing", None
    else:
        return "unknown", None