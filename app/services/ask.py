import json
from collections.abc import AsyncIterator
from typing import Any

from app.models.api import AskRequest, AskResponse, Citation


class AskService:
    def __init__(self, retrieval_service, chat_service):
        """Store the retrieval and answer-generation services for /ask."""
        self.retrieval_service = retrieval_service
        self.chat_service = chat_service

    async def ask(self, payload: AskRequest) -> AskResponse:
        """Run the full ask flow: retrieve context, generate answer, and cite sources."""
        chunks = await self.retrieval_service.retrieve(payload.question)
        answer = await self.chat_service.generate_answer(payload.question, chunks)
        citations = self._build_citations(chunks)

        return AskResponse(answer=answer, citations=citations)

    async def stream_ask(self, payload: AskRequest) -> AsyncIterator[str]:
        """Stream answer chunks, citations, and a completion event as SSE messages."""
        chunks = await self.retrieval_service.retrieve(payload.question)

        async for text in self.chat_service.stream_answer(payload.question, chunks):
            yield self._format_sse(
                "answer_chunk",
                {
                    "type": "answer_chunk",
                    "text": text,
                },
            )

        for citation in self._build_citations(chunks):
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
