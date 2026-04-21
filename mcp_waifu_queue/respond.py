"""
AI Provider Dispatch and Text Generation.

This module implements the core text generation functionality for the MCP Waifu Queue
system, providing OpenRouter-based text generation.

Key Features:
- OpenRouter text generation via HTTP API
- Centralized text generation dispatch
- Error handling and logging
- Configuration-driven model selection

Model Configuration:
- OpenRouter models: Configured via ~/.model-openrouter or default 'openrouter/free'

Usage:
This module is used by the RQ worker process through utils.py. The main
entry point is the predict_response() function which handles provider
logic and returns generated text.

Dependencies:
- requests: For OpenRouter API calls
- logging: For operation logging and debugging
- config: For configuration management
"""

# mcp_waifu_queue/respond.py
# OpenRouter-only text generation.

import logging
import os
from pathlib import Path
from typing import Optional

from mcp_waifu_queue.config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Model config file locations
MODEL_FILE_OPENROUTER = Path.home() / ".model-openrouter"

def _read_single_line(path: Path) -> Optional[str]:
    try:
        if path.is_file():
            val = path.read_text(encoding="utf-8").strip()
            return val or None
    except Exception as e:
        logger.warning(f"Failed reading {path}: {e}")
    return None

def _resolve_model() -> str:
    return _read_single_line(MODEL_FILE_OPENROUTER) or "openrouter/free"

def _predict_with_openrouter(prompt: str, model: str, timeout: int) -> str:
    import requests

    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

    # Key resolution precedence:
    # 1) OPENROUTER_API_KEY env
    # 2) ~/.api-openrouter single line
    key = os.getenv("OPENROUTER_API_KEY")
    if not key or not key.strip():
        key_file = Path.home() / ".api-openrouter"
        key = _read_single_line(key_file)

    if not key:
        raise RuntimeError("OpenRouter API key not available via env or ~/.api-openrouter")

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    resp = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=timeout)
    if resp.status_code != 200:
        body = resp.text[:500]
        raise RuntimeError(f"OpenRouter non-200: {resp.status_code} body: {body}")

    data = resp.json()
    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError("OpenRouter response missing choices")
    content = (choices[0].get("message", {}).get("content") or "").strip()
    if not content:
        raise RuntimeError("OpenRouter response empty content")
    return content

def predict_response(prompt: str) -> str:
    """
    Generates a response for a given prompt using OpenRouter.
    """
    cfg = Config.load()
    model = _resolve_model()

    logger.info(f"Using OpenRouter with model '{model}'")

    return _predict_with_openrouter(prompt, model=model or "openrouter/free", timeout=cfg.request_timeout_seconds)
