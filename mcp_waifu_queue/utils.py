import logging
import requests
from mcp_waifu_queue.config import Config

config = Config.load()

# This function calls the GPU service to generate a response for a given prompt.
def call_predict_response(prompt):
    try:
        response = requests.post(f"{config.gpu_service_url}/generate", json={'prompt': prompt})
        response.raise_for_status()
        return response.json()['response']
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling GPU service: {e}")
        return "Error: Could not connect to the GPU service."