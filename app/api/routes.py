from app.db.repositories import get_job_repository
from app.models.api import (AskRequest, AskResponse, DocumentCreateRequest,
                            DocumentCreateResponse, HealthResponse,
                            JobResponse)
from app.services.chat import ChatService
from app.services.ingestion import IngestionService
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

router = APIRouter()

ingestion_service = IngestionService()
chat_service = ChatService()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/documents", response_model=DocumentCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_document(payload: DocumentCreateRequest) -> DocumentCreateResponse:
    return await ingestion_service.submit_document(payload)


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str) -> JobResponse:
    job = await get_job_repository().get(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    return job


@router.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest) -> AskResponse:
    return await chat_service.answer(payload)


@router.post("/ask/stream")
async def ask_stream(payload: AskRequest) -> StreamingResponse:
    return StreamingResponse(chat_service.stream_answer(payload), media_type="text/event-stream")
