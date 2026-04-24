from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok"]


class DocumentCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    source: str | None = Field(default=None, max_length=500)


class DocumentCreateResponse(BaseModel):
    document_id: str
    job_id: str
    status: Literal["queued"]


class JobResponse(BaseModel):
    job_id: str
    document_id: str
    status: Literal["queued", "processing", "completed", "failed"]
    detail: str

