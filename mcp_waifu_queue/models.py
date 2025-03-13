from pydantic import BaseModel, Field
from typing import Optional


class GenerateTextRequest(BaseModel):
    """Request model for the generate_text tool."""

    prompt: str = Field(..., description="The input text prompt.")


class JobStatusResponse(BaseModel):
    """Response model for the get_job_status resource."""

    status: str = Field(..., description="The status of the job (queued, processing, completed, failed).")
    result: Optional[str] = Field(None, description="The generated text, if the job is completed.")