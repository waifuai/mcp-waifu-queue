import logging
import requests
from mcp_waifu_queue.config import Config

class GPUServiceError(Exception):
    """Custom exception for GPU service errors."""
    pass

config = Config.load()

# This function calls the GPU service to generate a response for a given prompt.
def call_predict_response(prompt):
    try:
        response = requests.post(f"{config.gpu_service_url}/generate", json={'prompt': prompt})
        response.raise_for_status()
        return response.json()['response']
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling GPU service: {e}")
        # Raise an exception so RQ marks the job as failed
        raise GPUServiceError(f"Error calling GPU service: {e}")