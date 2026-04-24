from app.models.api import DocumentCreateResponse


class InMemoryDocumentRepository:
    def __init__(self) -> None:
        self._documents: dict[str, DocumentCreateResponse] = {}

    async def save(self, document: DocumentCreateResponse) -> None:
        self._documents[document.document_id] = document

    async def get(self, document_id: str) -> DocumentCreateResponse | None:
        return self._documents.get(document_id)


_document_repository = InMemoryDocumentRepository()


def get_document_repository() -> InMemoryDocumentRepository:
    return _document_repository
