"""
Main MCP Server Implementation.

This module serves as the main entry point for the MCP Waifu Queue server,
implementing the core MCP (Model Context Protocol) tools and resources for
asynchronous AI text generation using Redis queues.

The server provides:
- generate_text tool: Accepts prompts and enqueues them for background processing
- job status resource: Allows checking the status and results of submitted jobs

Architecture:
- Uses FastMCP for MCP server implementation
- Integrates with Redis queue system via task_queue module
- Supports configuration loading and logging
- Provides async endpoints for MCP client integration

Usage:
    Run as MCP server using FastMCP or uvicorn:
    uvicorn mcp_waifu_queue.main:app --reload --port 8000
"""

import logging

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context

from mcp_waifu_queue.config import Config
from mcp_waifu_queue.models import GenerateTextRequest, JobStatusResponse
from mcp_waifu_queue.task_queue import q, add_to_queue, get_job_status_from_queue

# --- Configuration and Logging ---
app = FastMCP(name="WaifuQueue")
config = Config.load()
app.config = config

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# --- MCP Tools ---
@app.tool()
async def generate_text(request: GenerateTextRequest, context: Context) -> dict:
    """Generates text based on a prompt, using a Redis queue."""
    job_id = add_to_queue(request.prompt)
    logger.info(f"Enqueued job with ID: {job_id}")
    return {"job_id": job_id}


# --- MCP Resources ---
@app.resource(uri="job://{job_id}")
async def get_job_status(job_id: str) -> JobStatusResponse:
    """Retrieves the status of a job."""
    status, result = get_job_status_from_queue(job_id)
    logger.info(f"Job status for {job_id}: {status}")
    return JobStatusResponse(status=status, result=result)