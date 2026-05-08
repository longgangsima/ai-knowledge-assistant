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


class ChunkResponse(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    text: str
    embedding: list[float] | None = None
    metadata: dict[str, str | int | float] | None = None


class VectorResponse(BaseModel):
    val: list[float]


class AskRequest(BaseModel):
    question: str = Field(min_length=1)


class Citation(BaseModel):
    document_id: str
    chunk_id: str
    chunk_index: int
    text: str
    source: str | None = None


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
