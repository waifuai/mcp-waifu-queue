# mcp_waifu_queue/respond.py
# Core text generation logic using the Google GenAI SDK (google-genai).

import os
from pathlib import Path
import logging
from typing import Optional

from google import genai
from mcp_waifu_queue.config import Config

config = Config.load()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-pro"

def _load_api_key() -> Optional[str]:
    """
    Auth precedence:
    1) GEMINI_API_KEY
    2) GOOGLE_API_KEY
    3) ~/.api-gemini (single-line)
    """
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if key:
        return key
    api_key_path = Path.home() / ".api-gemini"
    if api_key_path.is_file():
        try:
            text = api_key_path.read_text(encoding="utf-8").strip()
            if text:
                logger.info(f"Loaded Gemini API key from {api_key_path}")
                return text
        except Exception as e:
            logger.warning(f"Failed reading {api_key_path}: {e}")
    return None

# Initialize client once
_client: Optional[genai.Client] = None
try:
    _key = _load_api_key()
    if not _key:
        logger.error("No Gemini API key found via env or ~/.api-gemini")
    else:
        _client = genai.Client(api_key=_key)
        logger.info("Google GenAI client initialized.")
except Exception as e:
    logger.error(f"Error initializing Google GenAI client: {e}")
    _client = None

def predict_response(prompt: str) -> str:
    """
    Generates a response for a given prompt using Google GenAI SDK.

    Raises RuntimeError when generation cannot proceed.
    """
    logger.info(f"Received prompt for Gemini: '{prompt[:100]}...'")
    if _client is None:
        raise RuntimeError("Gemini client not available")

    try:
        generation_config = {"max_output_tokens": config.max_new_tokens}
        resp = _client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            generation_config=generation_config,
        )

        # The new SDK returns a typed object; prefer aggregated text where available
        text = getattr(resp, "text", None)
        if not text:
            # Fallback: inspect candidates if present
            candidates = getattr(resp, "candidates", None)
            if not candidates:
                feedback = getattr(resp, "prompt_feedback", None)
                block_reason = getattr(feedback, "block_reason", "Unknown")
                logger.warning(
                    f"Gemini response blocked or empty. Block Reason: {block_reason}"
                )
                return f"AI response generation failed or was blocked. Reason: {block_reason}"
            # Try first candidate content parts aggregation
            try:
                first = candidates[0]
                content = getattr(first, "content", None)
                parts = getattr(content, "parts", None) if content else None
                if parts:
                    maybe_text = "".join(getattr(p, "text", "") for p in parts if hasattr(p, "text"))
                    if maybe_text:
                        text = maybe_text
            except Exception:
                pass

        if not text:
            logger.warning("Gemini response contained no text.")
            return "AI response generation resulted in empty content."

        logger.info(f"Generated Gemini response: '{text[:100]}...'")
        return text

    except Exception as e:
        logger.error(f"Error during Gemini API call: {e}", exc_info=True)
        raise RuntimeError(f"Error generating AI response: {e}")