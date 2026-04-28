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
        citations = [
            Citation(
                document_id=chunk.document_id,
                chunk_id=chunk.chunk_id,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                source=self._get_source(chunk.metadata),
            )
            for chunk in chunks
        ]

        return AskResponse(answer=answer, citations=citations)

    def _get_source(self, metadata: dict[str, str | int | float] | None) -> str | None:
        """Extract a stable citation source from chunk metadata when available."""
        if metadata is None:
            return None

        source = metadata.get("source")
        if isinstance(source, str) and source:
            return source

        return None
