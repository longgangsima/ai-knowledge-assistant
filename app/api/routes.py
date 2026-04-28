from fastapi import APIRouter, HTTPException, status

from app.db import get_chunk_repository, get_job_repository
from app.models.api import (AskRequest, AskResponse, DocumentCreateRequest,
                            DocumentCreateResponse, HealthResponse,
                            JobResponse)
from app.services.ask import AskService
from app.services.chat import ChatService
from app.services.ingestion import IngestionService
from app.services.retrieval import RetrievalService

router = APIRouter()

ingestion_service = IngestionService()
retrieval_service = RetrievalService(get_chunk_repository())
chat_service = ChatService()
ask_service = AskService(retrieval_service, chat_service)

@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return a minimal liveness response for the API."""
    return HealthResponse(status="ok")


@router.post("/documents", response_model=DocumentCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_document(payload: DocumentCreateRequest) -> DocumentCreateResponse:
    """Accept a document submission and enqueue the ingestion workflow."""
    return await ingestion_service.submit_document(payload)

@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str) -> JobResponse:
    """Return the saved ingestion job status or a 404 when it is unknown."""
    job = await get_job_repository().get(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    return job

@router.post("/ask", response_model=AskResponse)
async def get_ask(payload: AskRequest) -> AskResponse:
    """Answer a question using retrieved chunks and source citations."""
    return await ask_service.ask(payload)
