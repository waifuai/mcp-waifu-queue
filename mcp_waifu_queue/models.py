"""
Pydantic Models for MCP Waifu Queue.

This module defines the Pydantic models used throughout the MCP Waifu Queue system
for request/response validation and serialization. These models ensure type safety
and provide clear interfaces for the MCP tools and resources.

Models Defined:
- GenerateTextRequest: Model for text generation tool requests
- JobStatusResponse: Model for job status resource responses

Key Features:
- Pydantic v2 BaseModel for validation and serialization
- Field descriptions for API documentation
- Optional fields with proper typing
- Integration with FastMCP for automatic validation

Usage:
These models are automatically used by FastMCP when processing MCP tool calls
and resource requests, providing validation and type conversion.
"""

from pydantic import BaseModel, Field
from typing import Optional


class GenerateTextRequest(BaseModel):
    """Request model for the generate_text tool."""

    prompt: str = Field(..., description="The input text prompt.")


class JobStatusResponse(BaseModel):
    """Response model for the get_job_status resource."""

    status: str = Field(..., description="The status of the job (queued, processing, completed, failed).")
    result: Optional[str] = Field(None, description="The generated text, if the job is completed.")