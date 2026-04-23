# AI Knowledge Assistant

Backend-first AI systems project designed to demonstrate:

- Python backend service design
- retrieval-augmented generation foundations
- streaming responses
- background ingestion workflows
- observability and operational hardening

## Initial Scope

The first scaffold focuses on a minimal but interview-relevant service shape:

- `GET /health`
- `POST /documents`
- `GET /jobs/{job_id}`
- `POST /ask`
- `POST /ask/stream`

This version is intentionally backend-first. The goal is to establish a clean service boundary before adding vector storage, model integrations, and richer worker infrastructure.

## Planned Stack

- FastAPI
- Pydantic
- Uvicorn
- Background task abstraction
- Embedding and LLM provider abstractions
- Pluggable document store and vector store interfaces

## Project Layout

```text
app/
  api/              # Route modules and request handlers
  core/             # Settings and app-wide configuration
  db/               # Repository and storage abstractions
  models/           # Pydantic schemas and domain types
  observability/    # Logging and metrics helpers
  services/         # RAG, ingestion, and chat orchestration
  workers/          # Background job execution seam
tests/              # Test suite
```

## Next Steps

1. Add Python packaging and dependencies.
2. Implement in-memory repositories for documents and jobs.
3. Add chunking, embedding, and retrieval services.
4. Wire OpenAI-compatible providers behind interfaces.
5. Add structured logs, retries, and rate limiting.
# ai-knowledge-assistant
