from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import StreamingResponse

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
async def create_document(
    payload: DocumentCreateRequest,
    background_tasks: BackgroundTasks,
) -> DocumentCreateResponse:
    """Accept a document, return a queued job, and process ingestion in the background."""
    document = await ingestion_service.submit_document(payload)
    background_tasks.add_task(
        ingestion_service.process_document,
        document.document_id,
        document.job_id,
        payload,
    )
    return document

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

@router.post("/ask/stream")
async def get_ask_stream(payload: AskRequest) -> StreamingResponse:
    """Stream an answer as Server-Sent Events."""
    return StreamingResponse(
        ask_service.stream_ask(payload),
        media_type="text/event-stream",
    )
