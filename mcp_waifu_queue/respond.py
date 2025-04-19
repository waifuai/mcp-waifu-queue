# mcp_waifu_queue/respond.py
# This file contains the core text generation logic using the Gemini API.

import os
from pathlib import Path # Added for home directory access
import google.generativeai as genai
import logging
# Removed dotenv import

from mcp_waifu_queue.config import Config

config = Config.load()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Gemini API Configuration ---
gemini_model = None
try:
    # Load API key from ~/.api-gemini
    api_key_path = Path.home() / ".api-gemini"
    api_key = None
    if api_key_path.is_file():
        api_key = api_key_path.read_text().strip()
        logger.info(f"Loaded Gemini API key from {api_key_path}")
    else:
        logger.warning(f"API key file not found at {api_key_path}. Attempting to use environment variable GEMINI_API_KEY as fallback.")
        api_key = os.getenv("GEMINI_API_KEY") # Fallback to env var if file not found

    if not api_key:
        logger.error(
            f"Gemini API key not found in {api_key_path} or GEMINI_API_KEY environment variable. Cannot initialize Gemini."
        )
    else:
        genai.configure(api_key=api_key)
        # TODO: Make model name configurable?
        gemini_model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17') # Using 2.5 flash
        logger.info("Gemini API configured successfully with model gemini-2.5-flash-preview-04-17.")
        # Test call to check API key validity (optional, but good for early feedback)
        # try:
        #     gemini_model.generate_content("test", generation_config=genai.types.GenerationConfig(max_output_tokens=5))
        #     logger.info("Gemini API key appears valid.")
        # except Exception as api_test_e:
        #     logger.error(f"Error during Gemini API test call (check API key?): {api_test_e}")
        #     gemini_model = None # Invalidate model if test fails

except Exception as e:
    logger.error(f"Error configuring Gemini API: {e}")
    gemini_model = None # Ensure model is None if setup fails

# --- Text Generation Function ---
def predict_response(prompt: str) -> str:
    """
    Generates a response for a given prompt using the configured Gemini model.

    Args:
        prompt: The input prompt string.

    Returns:
        The generated text response, or an error message string if generation fails.
    """
    logger.info(f"Received prompt for Gemini: '{prompt[:100]}...'") # Log truncated prompt
    if not gemini_model:
        logger.error("Gemini model is not available or not configured correctly.")
        # Raise an exception to signal failure to the RQ worker
        raise RuntimeError("Gemini model not available")

    try:
        # Configure generation parameters
        generation_config = genai.types.GenerationConfig(
            # candidate_count=1, # Default is 1
            # stop_sequences=["\n"], # Example stop sequence
            max_output_tokens=config.max_new_tokens,
            # temperature=0.9, # Example temperature
            # top_p=1, # Example top_p
            # top_k=1 # Example top_k
        )

        # TODO: Add safety_settings if needed
        # safety_settings = [
        #     {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        #     {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        #     {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        #     {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        # ]

        response = gemini_model.generate_content(
            prompt,
            generation_config=generation_config,
            # safety_settings=safety_settings
        )

        # Enhanced error checking based on response structure
        if not response.candidates:
            feedback = response.prompt_feedback
            block_reason = feedback.block_reason if feedback else "Unknown"
            safety_ratings = feedback.safety_ratings if feedback else "N/A"
            logger.warning(
                f"Gemini response blocked or empty. Block Reason: {block_reason}. Safety Ratings: {safety_ratings}"
            )
            # Return a specific message indicating blockage
            return f"AI response generation failed or was blocked. Reason: {block_reason}"

        # Check parts within the first candidate
        candidate = response.candidates[0]
        if not candidate.content or not candidate.content.parts:
             finish_reason = candidate.finish_reason if candidate else "N/A"
             safety_ratings = candidate.safety_ratings if candidate else "N/A"
             logger.warning(
                 f"Gemini response candidate has no content parts. Finish Reason: {finish_reason}. Safety Ratings: {safety_ratings}"
             )
             return "AI response generation resulted in empty content."


        # Assuming response.text provides the combined text of parts
        generated_text = response.text
        logger.info(f"Generated Gemini response: '{generated_text[:100]}...'") # Log truncated response
        return generated_text

    except Exception as e:
        logger.error(f"Error during Gemini API call: {e}", exc_info=True)
        # Raise an exception to signal failure to the RQ worker
        raise RuntimeError(f"Error generating AI response: {e}")

# Note: Removed Flask app logic as this module is now just for the generation function.