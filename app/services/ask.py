import json
import logging
from collections.abc import AsyncIterator
from time import perf_counter
from typing import Any

from app.models.api import AskRequest, AskResponse, Citation

logger = logging.getLogger(__name__)


class AskService:
    def __init__(self, retrieval_service, chat_service):
        """Store the retrieval and answer-generation services for /ask."""
        self.retrieval_service = retrieval_service
        self.chat_service = chat_service

    async def ask(self, payload: AskRequest) -> AskResponse:
        """Run the full ask flow: retrieve context, generate answer, and cite sources."""
        started_at = perf_counter()
        logger.info(
            "ask started",
            extra={
                "event": "ask_started",
                "status": "started",
            },
        )

        chunks = await self.retrieval_service.retrieve(payload.question)
        retrieval_duration_ms = round((perf_counter() - started_at) * 1000, 2)
        logger.info(
            "ask retrieval completed",
            extra={
                "event": "ask_retrieval_completed",
                "status": "completed",
                "retrieved_chunk_count": len(chunks),
                "duration_ms": retrieval_duration_ms,
            },
        )

        answer = await self.chat_service.generate_answer(payload.question, chunks)
        citations = self._build_citations(chunks)
        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        logger.info(
            "ask completed",
            extra={
                "event": "ask_completed",
                "question": payload.question,
                "retrieved_chunk_count": len(chunks),
                "citation_count": len(citations),
                "status": "completed",
                "duration_ms": duration_ms,
            },
        )

        return AskResponse(answer=answer, citations=citations)

    async def stream_ask(self, payload: AskRequest) -> AsyncIterator[str]:
        """Stream answer chunks, citations, and a completion event as SSE messages."""
        started_at = perf_counter()
        answer_chunk_count = 0

        logger.info(
            "ask stream started",
            extra={
                "event": "ask_stream_started",
                "status": "started",
            },
        )

        chunks = await self.retrieval_service.retrieve(payload.question)
        logger.info(
            "ask stream retrieval completed",
            extra={
                "event": "ask_stream_retrieval_completed",
                "status": "completed",
                "retrieved_chunk_count": len(chunks),
                "duration_ms": round((perf_counter() - started_at) * 1000, 2),
            },
        )

        async for text in self.chat_service.stream_answer(payload.question, chunks):
            answer_chunk_count += 1
            yield self._format_sse(
                "answer_chunk",
                {
                    "type": "answer_chunk",
                    "text": text,
                },
            )

        citations = self._build_citations(chunks)
        for citation in citations:
            yield self._format_sse(
                "citation",
                {
                    "type": "citation",
                    "citation": citation.model_dump(),
                },
            )

        yield self._format_sse(
            "done",
            {
                "type": "done",
            },
        )
        logger.info(
            "ask stream completed",
            extra={
                "event": "ask_stream_completed",
                "status": "completed",
                "retrieved_chunk_count": len(chunks),
                "answer_chunk_count": answer_chunk_count,
                "citation_count": len(citations),
                "duration_ms": round((perf_counter() - started_at) * 1000, 2),
            },
        )

    def _build_citations(self, chunks) -> list[Citation]:
        """Build stable citation records from retrieved chunks."""
        return [
            Citation(
                document_id=chunk.document_id,
                chunk_id=chunk.chunk_id,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                source=self._get_source(chunk.metadata),
            )
            for chunk in chunks
        ]

    def _format_sse(self, event: str, data: dict[str, Any]) -> str:
        """Format one Server-Sent Event message."""
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    def _get_source(self, metadata: dict[str, str | int | float] | None) -> str | None:
        """Extract a stable citation source from chunk metadata when available."""
        if metadata is None:
            return None

        source = metadata.get("source")
        if isinstance(source, str) and source:
            return source

        return None
