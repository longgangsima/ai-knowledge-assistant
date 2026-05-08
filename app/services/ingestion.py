from typing import Literal
from uuid import uuid4

from app.db import (get_chunk_repository, get_document_repository,
                    get_job_repository)
from app.models.api import (ChunkResponse, DocumentCreateRequest,
                            DocumentCreateResponse, JobResponse)
from app.providers.embedding import MockEmbeddingProvider
from app.services.chunk import ChunkService
from app.services.embedding import EmbeddingService


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

    async def process_document(
        self,
        document_id: str,
        job_id: str,
        payload: DocumentCreateRequest,
    ) -> None:
        await self._update_job(
            job_id=job_id,
            document_id=document_id,
            status="processing",
            detail=f"Processing ingestion for document '{payload.title}'.",
        )

        try:
            await self._store_chunks(document_id, payload)
        except Exception as exc:
            await self._update_job(
                job_id=job_id,
                document_id=document_id,
                status="failed",
                detail=f"Failed ingestion for document '{payload.title}': {exc}",
            )
            return

        await self._update_job(
            job_id=job_id,
            document_id=document_id,
            status="completed",
            detail=f"Completed ingestion for document '{payload.title}'.",
        )

    async def _store_chunks(
        self,
        document_id: str,
        payload: DocumentCreateRequest,
    ) -> None:
        chunks = ChunkService().split_text_into_chunks(payload.content)
        embedding_provider = MockEmbeddingProvider()
        embedding_service = EmbeddingService(embedding_provider)

        for chunk_index, chunk_text in enumerate(chunks):
            vectors = await embedding_service.get_vector(chunk_text)
            chunk = ChunkResponse(
                chunk_id=str(uuid4()),
                document_id=document_id,
                chunk_index=chunk_index,
                text=chunk_text,
                embedding=vectors,
                metadata={
                    "title": payload.title,
                    "source": payload.source or "",
                },
            )

            await get_chunk_repository().save(chunk)

    async def _update_job(
        self,
        job_id: str,
        document_id: str,
        status: Literal["queued", "processing", "completed", "failed"],
        detail: str,
    ) -> None:
        job = JobResponse(
            job_id=job_id,
            document_id=document_id,
            status=status,
            detail=detail,
        )

        await get_job_repository().save(job)
