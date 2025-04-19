import logging
# Removed requests import
# Removed GPUServiceError class
# Removed config import as it's not used here anymore

# Import the actual prediction function
from mcp_waifu_queue.respond import predict_response

logger = logging.getLogger(__name__)

# This function now directly calls the local predict_response function.
def call_predict_response(prompt: str) -> str:
    """
    Calls the Gemini prediction function directly.

    Args:
        prompt: The input prompt string.

    Returns:
        The generated text response.

    Raises:
        RuntimeError: If the underlying predict_response fails.
    """
    logger.info(f"Worker calling predict_response for prompt: '{prompt[:50]}...'")
    try:
        # Directly call the function from respond.py
        result = predict_response(prompt)
        logger.info(f"predict_response returned: '{result[:50]}...'")
        return result
    except Exception as e:
        # Log the error and re-raise it so RQ marks the job as failed
        logger.error(f"Error calling predict_response: {e}", exc_info=True)
        # Re-raising the original exception or a new one to signal failure
        raise # Reraises the caught exception