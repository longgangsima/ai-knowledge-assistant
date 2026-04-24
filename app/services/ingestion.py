from uuid import uuid4

from app.db import get_document_repository, get_job_repository
from app.models.api import (DocumentCreateRequest, DocumentCreateResponse,
                            JobResponse)


class IngestionService:
    async def submit_document(self, payload: DocumentCreateRequest) -> DocumentCreateResponse:
        document_id = str(uuid4())
        job_id = str(uuid4())

        job = JobResponse(
            job_id=job_id,
            document_id=document_id,
            status="queued",
            detail=f"Queued ingestion for document '{payload.title}'.",
        )
        await get_job_repository().save(job)
        
        document = DocumentCreateResponse(
            document_id=document_id,
            job_id=job_id,
            status="queued",
        )
        
        await get_document_repository().save(document)

        return document
