import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Configuration for the Waifu Queue API."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", frozen=True, extra="ignore"
    )

    max_new_tokens: int = Field(
        default=2048, # Default increased significantly for Gemini
        description="Maximum number of new tokens to generate (used for Gemini config if needed).",
    )
    redis_url: str = Field(
        default="redis://localhost:6379", description="URL of the Redis server."
    )

    @classmethod
    def load(cls) -> "Config":
        """Loads the configuration from environment variables and/or a .env file."""
        return cls()