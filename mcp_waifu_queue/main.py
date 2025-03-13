import logging

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.context import Context

from mcp_waifu_queue.config import Config
from mcp_waifu_queue.models import GenerateTextRequest, JobStatusResponse
from mcp_waifu_queue.queue import q, add_to_queue, get_job_status_from_queue

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
async def get_job_status(job_id: str, context: Context) -> JobStatusResponse:
    """Retrieves the status of a job."""
    status, result = get_job_status_from_queue(job_id)
    logger.info(f"Job status for {job_id}: {status}")
    return JobStatusResponse(status=status, result=result)