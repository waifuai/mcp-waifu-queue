import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Configuration for the Waifu Queue API."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", frozen=True, extra="ignore"
    )

    max_new_tokens: int = Field(
        default=2048,
        description="Maximum number of new tokens to generate (used for provider config if needed).",
    )
    redis_url: str = Field(
        default="redis://localhost:6379", description="URL of the Redis server."
    )
    default_provider: str = Field(
        default="openrouter",
        description="Default LLM provider to use when not overridden by env. Supported: openrouter, gemini.",
    )
    request_timeout_seconds: int = Field(
        default=60,
        description="HTTP request timeout for providers that use HTTP clients.",
    )

    @classmethod
    def load(cls) -> "Config":
        """Loads the configuration from environment variables and/or a .env file."""
        # Allow explicit override via PROVIDER env var while still keeping Pydantic immutability.
        cfg = cls()
        provider_env = os.getenv("PROVIDER")
        if provider_env and provider_env.strip():
            # Create a new instance with overridden provider to honor frozen dataclass
            return cls.model_construct(
                max_new_tokens=cfg.max_new_tokens,
                redis_url=cfg.redis_url,
                default_provider=provider_env.strip().lower(),
                request_timeout_seconds=cfg.request_timeout_seconds,
            )
        return cfg