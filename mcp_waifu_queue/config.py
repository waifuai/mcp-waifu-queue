import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Configuration for the Waifu Queue API."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", frozen=True, extra="ignore"
    )

    model_path: str = Field(
        default="distilgpt2", description="Path to the pre-trained language model."
    )
    gpu_service_url: str = Field(
        default="http://localhost:5001",
        description="URL of the GPU service (respond.py).",
    )
    max_new_tokens: int = Field(
        default=20, description="Maximum number of new tokens to generate."
    )
    queue_port: int = Field(
        default=5000, description="Port for the queue service (queue.py)."
    )
    respond_port: int = Field(
        default=5001, description="Port for the response service (respond.py)."
    )
    redis_url: str = Field(
        default="redis://localhost:6379", description="URL of the Redis server."
    )

    @classmethod
    def load(cls) -> "Config":
        """Loads the configuration from environment variables and/or a .env file."""
        return cls()