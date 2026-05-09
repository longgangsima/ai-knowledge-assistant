import asyncio
import logging

from app.db import get_chunk_repository, get_job_repository
from app.models.api import AskRequest, DocumentCreateRequest
from app.services.ask import AskService
from app.services.chat import ChatService
from app.services.ingestion import IngestionService
from app.services.retrieval import RetrievalService


def _log_events(caplog) -> set[str]:
    return {
        record.event
        for record in caplog.records
        if hasattr(record, "event")
    }


def test_ingestion_logs_job_lifecycle_events(caplog) -> None:
    caplog.set_level(logging.INFO)
    service = IngestionService()
    payload = DocumentCreateRequest(
        title="Day 7 Observability Notes",
        content="Observability makes background jobs easier to debug.",
        source="day-07-test",
    )

    response = asyncio.run(service.submit_document(payload))
    asyncio.run(service.process_document(response.document_id, response.job_id, payload))
    job = asyncio.run(get_job_repository().get(response.job_id))

    assert job is not None
    assert job.status == "completed"
    assert {
        "ingestion_queued",
        "ingestion_processing",
        "ingestion_completed",
    }.issubset(_log_events(caplog))

    completed_record = next(
        record
        for record in caplog.records
        if getattr(record, "event", None) == "ingestion_completed"
    )
    assert completed_record.job_id == response.job_id
    assert completed_record.document_id == response.document_id
    assert completed_record.duration_ms >= 0


def test_ask_logs_retrieval_and_completion_events(caplog) -> None:
    caplog.set_level(logging.INFO)
    ingestion_service = IngestionService()
    payload = DocumentCreateRequest(
        title="Day 7 Ask Notes",
        content="Observabilityneedle helps trace retrieval behavior.",
        source="day-07-test",
    )
    document = asyncio.run(ingestion_service.submit_document(payload))
    asyncio.run(
        ingestion_service.process_document(
            document.document_id,
            document.job_id,
            payload,
        )
    )
    ask_service = AskService(
        RetrievalService(get_chunk_repository()),
        ChatService(),
    )

    response = asyncio.run(
        ask_service.ask(AskRequest(question="observabilityneedle"))
    )

    assert response.citations
    assert {
        "retrieval_completed",
        "ask_retrieval_completed",
        "ask_completed",
    }.issubset(_log_events(caplog))

    ask_completed_record = next(
        record
        for record in caplog.records
        if getattr(record, "event", None) == "ask_completed"
    )
    assert ask_completed_record.retrieved_chunk_count >= 1
    assert ask_completed_record.citation_count >= 1
    assert ask_completed_record.duration_ms >= 0


def test_stream_ask_logs_completion_event(caplog) -> None:
    caplog.set_level(logging.INFO)
    ingestion_service = IngestionService()
    payload = DocumentCreateRequest(
        title="Day 7 Stream Notes",
        content="Streamobservability helps explain incremental delivery.",
        source="day-07-test",
    )
    document = asyncio.run(ingestion_service.submit_document(payload))
    asyncio.run(
        ingestion_service.process_document(
            document.document_id,
            document.job_id,
            payload,
        )
    )
    ask_service = AskService(
        RetrievalService(get_chunk_repository()),
        ChatService(),
    )

    async def collect_stream() -> list[str]:
        return [
            event
            async for event in ask_service.stream_ask(
                AskRequest(question="streamobservability")
            )
        ]

    events = asyncio.run(collect_stream())

    assert any("event: done" in event for event in events)
    assert "ask_stream_completed" in _log_events(caplog)

    stream_completed_record = next(
        record
        for record in caplog.records
        if getattr(record, "event", None) == "ask_stream_completed"
    )
    assert stream_completed_record.answer_chunk_count >= 1
    assert stream_completed_record.citation_count >= 1
    assert stream_completed_record.duration_ms >= 0
