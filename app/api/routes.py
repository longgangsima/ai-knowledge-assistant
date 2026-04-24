from fastapi import APIRouter, HTTPException, status

from app.db import get_job_repository
from app.models.api import (DocumentCreateRequest, DocumentCreateResponse,
                            HealthResponse, JobResponse)
from app.services.ingestion import IngestionService

router = APIRouter()

ingestion_service = IngestionService()


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
