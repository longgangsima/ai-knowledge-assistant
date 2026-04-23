from collections.abc import AsyncIterator

from app.models.api import AskRequest, AskResponse, Citation


class ChatService:
    async def answer(self, payload: AskRequest) -> AskResponse:
        return AskResponse(
            answer=f"Stub answer for: {payload.question}",
            citations=[
                Citation(
                    document_id="stub-document",
                    snippet="Retrieval and generation are not implemented yet.",
                )
            ],
        )

    async def stream_answer(self, payload: AskRequest) -> AsyncIterator[str]:
        chunks = [
            "event: message\ndata: Stub streaming response",
            f"event: message\ndata: Question: {payload.question}",
            "event: done\ndata: [DONE]",
        ]
        for chunk in chunks:
            yield f"{chunk}\n\n"
