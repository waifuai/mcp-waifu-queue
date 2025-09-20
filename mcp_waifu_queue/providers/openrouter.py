# mcp_waifu_queue/providers/openrouter.py
# Minimal OpenRouter client kept separate for potential direct imports if needed.

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import requests


OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_OPENROUTER_MODEL = "deepseek/deepseek-chat-v3-0324:free"
OPENROUTER_API_KEY_FILE_PATH = Path.home() / ".api-openrouter"
MODEL_FILE_PATH = Path.home() / ".model-openrouter"


def _read_single_line(path: Path) -> Optional[str]:
    try:
        if path.is_file():
            val = path.read_text(encoding="utf-8").strip()
            return val or None
    except Exception:
        return None
    return None


def resolve_model() -> str:
    return _read_single_line(MODEL_FILE_PATH) or DEFAULT_OPENROUTER_MODEL


def resolve_api_key() -> Optional[str]:
    env_key = os.getenv("OPENROUTER_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()
    return _read_single_line(OPENROUTER_API_KEY_FILE_PATH)


def generate(prompt: str, model: Optional[str] = None, timeout: int = 60) -> str:
    api_key = resolve_api_key()
    if not api_key:
        raise RuntimeError("OpenRouter API key not available via env or ~/.api-openrouter")

    payload = {
        "model": model or resolve_model(),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    resp = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"OpenRouter non-200: {resp.status_code} body: {resp.text[:500]}")

    data = resp.json()
    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError("OpenRouter response missing choices")
    content = (choices[0].get("message", {}).get("content") or "").strip()
    if not content:
        raise RuntimeError("OpenRouter response empty content")
    return content