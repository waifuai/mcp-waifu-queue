# mcp_waifu_queue/respond.py
# Provider-dispatching text generation with OpenRouter default and Gemini fallback.

import logging
import os
from pathlib import Path
from typing import Optional

from mcp_waifu_queue.config import Config

# Lazy imports inside providers to avoid hard dependency failures during import time
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Provider constants
PROVIDER_OPENROUTER = "openrouter"
PROVIDER_GEMINI = "gemini"

# Model config file locations
MODEL_FILE_OPENROUTER = Path.home() / ".model-openrouter"
MODEL_FILE_GEMINI = Path.home() / ".model-gemini"

def _read_single_line(path: Path) -> Optional[str]:
    try:
        if path.is_file():
            val = path.read_text(encoding="utf-8").strip()
            return val or None
    except Exception as e:
        logger.warning(f"Failed reading {path}: {e}")
    return None

def _resolve_model_for(provider: str) -> Optional[str]:
    if provider == PROVIDER_OPENROUTER:
        return _read_single_line(MODEL_FILE_OPENROUTER) or "deepseek/deepseek-chat-v3-0324:free"
    if provider == PROVIDER_GEMINI:
        return _read_single_line(MODEL_FILE_GEMINI) or "gemini-2.5-pro"
    return None

def _select_provider(cfg: Config) -> str:
    # Env override already applied in Config.load; still honor explicit env if present
    env_provider = os.getenv("PROVIDER")
    provider = (env_provider or cfg.default_provider or PROVIDER_OPENROUTER).strip().lower()
    if provider not in (PROVIDER_OPENROUTER, PROVIDER_GEMINI):
        logger.warning(f"Unknown provider '{provider}', falling back to '{PROVIDER_OPENROUTER}'")
        return PROVIDER_OPENROUTER
    return provider

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

def _predict_with_gemini(prompt: str, model: str, max_tokens: int) -> str:
    from google import genai

    # Auth precedence:
    # 1) GEMINI_API_KEY
    # 2) GOOGLE_API_KEY
    # 3) ~/.api-gemini
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key or not key.strip():
        key = _read_single_line(Path.home() / ".api-gemini")

    if not key:
        raise RuntimeError("Gemini API key not available via env or ~/.api-gemini")

    client = genai.Client(api_key=key)
    generation_config = {"max_output_tokens": max_tokens}
    resp = client.models.generate_content(
        model=model,
        contents=prompt,
        generation_config=generation_config,
    )
    text = getattr(resp, "text", None)
    if not text:
        candidates = getattr(resp, "candidates", None)
        if not candidates:
            feedback = getattr(resp, "prompt_feedback", None)
            block_reason = getattr(feedback, "block_reason", "Unknown")
            raise RuntimeError(f"Gemini response blocked or empty. Reason: {block_reason}")
        try:
            first = candidates[0]
            content = getattr(first, "content", None)
            parts = getattr(content, "parts", None) if content else None
            if parts:
                maybe_text = "".join(getattr(p, "text", "") for p in parts if hasattr(p, "text"))
                text = maybe_text or None
        except Exception:
            text = None

    if not text:
        raise RuntimeError("Gemini response contained no text.")
    return text

def predict_response(prompt: str) -> str:
    """
    Generates a response for a given prompt using selected provider.
    Default provider is OpenRouter unless overridden by PROVIDER env or config.default_provider.
    """
    cfg = Config.load()
    provider = _select_provider(cfg)
    model = _resolve_model_for(provider)

    logger.info(f"Provider '{provider}' selected; model '{model}'")

    if provider == PROVIDER_OPENROUTER:
        try:
            return _predict_with_openrouter(prompt, model=model or "deepseek/deepseek-chat-v3-0324:free", timeout=cfg.request_timeout_seconds)
        except Exception as e:
            logger.error(f"OpenRouter failed: {e}", exc_info=True)
            # Fallback to Gemini
            try:
                gem_model = _resolve_model_for(PROVIDER_GEMINI) or "gemini-2.5-pro"
                return _predict_with_gemini(prompt, model=gem_model, max_tokens=cfg.max_new_tokens)
            except Exception as ge:
                logger.error(f"Gemini fallback failed: {ge}", exc_info=True)
                raise RuntimeError(f"All providers failed: OpenRouter error: {e} ; Gemini error: {ge}")
    elif provider == PROVIDER_GEMINI:
        try:
            return _predict_with_gemini(prompt, model=model or "gemini-2.5-pro", max_tokens=cfg.max_new_tokens)
        except Exception as e:
            logger.error(f"Gemini failed: {e}", exc_info=True)
            # Fallback to OpenRouter
            try:
                or_model = _resolve_model_for(PROVIDER_OPENROUTER) or "deepseek/deepseek-chat-v3-0324:free"
                return _predict_with_openrouter(prompt, model=or_model, timeout=cfg.request_timeout_seconds)
            except Exception as oe:
                logger.error(f"OpenRouter fallback failed: {oe}", exc_info=True)
                raise RuntimeError(f"All providers failed: Gemini error: {e} ; OpenRouter error: {oe}")
    else:
        # Safety: unknown provider, try OpenRouter then Gemini
        try:
            return _predict_with_openrouter(prompt, model="deepseek/deepseek-chat-v3-0324:free", timeout=cfg.request_timeout_seconds)
        except Exception as e:
            logger.error(f"OpenRouter failed under unknown provider: {e}", exc_info=True)
            try:
                return _predict_with_gemini(prompt, model="gemini-2.5-pro", max_tokens=cfg.max_new_tokens)
            except Exception as ge:
                logger.error(f"Gemini fallback failed under unknown provider: {ge}", exc_info=True)
                raise RuntimeError(f"All providers failed under unknown provider: OR: {e} ; Gemini: {ge}")