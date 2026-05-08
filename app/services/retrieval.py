import re

from app.models.api import ChunkResponse


class RetrievalService:
    def __init__(self, chunk_repository):
        """Store the repository used as the retrieval candidate source."""
        self.chunk_repository = chunk_repository

    async def retrieve(self, question: str, top_k: int = 3) -> list[ChunkResponse]:
        """Select the most relevant stored chunks for a question."""
        chunks = await self.chunk_repository.list_all()
        question_terms = self._tokenize(question)

        scored_chunks = [
            (self._score(question_terms, chunk.text), chunk)
            for chunk in chunks
        ]
        relevant_chunks = [
            (score, chunk)
            for score, chunk in scored_chunks
            if score > 0
        ]
        ranked_chunks = sorted(
            relevant_chunks,
            key=lambda item: (-item[0], item[1].document_id, item[1].chunk_index),
        )

        return [chunk for _, chunk in ranked_chunks[:top_k]]

    def _tokenize(self, text: str) -> set[str]:
        """Normalize text into unique lowercase terms for simple matching."""
        return set(re.findall(r"\w+", text.lower()))

    def _score(self, question_terms: set[str], chunk_text: str) -> int:
        """Score a chunk by counting keyword overlap with the question."""
        chunk_terms = self._tokenize(chunk_text)
        return len(question_terms.intersection(chunk_terms))
