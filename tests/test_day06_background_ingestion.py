import asyncio

from app.db import get_job_repository
from app.models.api import DocumentCreateRequest
from app.services.ingestion import IngestionService


def test_submit_document_creates_queued_job_before_processing() -> None:
    service = IngestionService()
    payload = DocumentCreateRequest(
        title="Background Notes",
        content="Background workflows keep request paths fast.",
        source="day-06-test",
    )

    response = asyncio.run(service.submit_document(payload))
    job = asyncio.run(get_job_repository().get(response.job_id))

    assert response.status == "queued"
    assert job is not None
    assert job.status == "queued"
    assert job.document_id == response.document_id


def test_process_document_marks_job_completed() -> None:
    service = IngestionService()
    payload = DocumentCreateRequest(
        title="Completed Notes",
        content="Queued jobs become completed after processing.",
        source="day-06-test",
    )

    response = asyncio.run(service.submit_document(payload))
    asyncio.run(service.process_document(response.document_id, response.job_id, payload))
    job = asyncio.run(get_job_repository().get(response.job_id))

    assert job is not None
    assert job.status == "completed"
    assert job.detail.startswith("Completed ingestion")


def test_process_document_marks_job_failed_when_processing_errors(monkeypatch) -> None:
    service = IngestionService()
    payload = DocumentCreateRequest(
        title="Failed Notes",
        content="This document will fail during processing.",
        source="day-06-test",
    )

    async def fail_store_chunks(document_id, payload):
        raise RuntimeError("embedding provider unavailable")

    monkeypatch.setattr(service, "_store_chunks", fail_store_chunks)

    response = asyncio.run(service.submit_document(payload))
    asyncio.run(service.process_document(response.document_id, response.job_id, payload))
    job = asyncio.run(get_job_repository().get(response.job_id))

    assert job is not None
    assert job.status == "failed"
    assert "embedding provider unavailable" in job.detail
