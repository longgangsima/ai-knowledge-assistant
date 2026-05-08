from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ask_stream_returns_answer_chunks_citations_and_done() -> None:
    create_response = client.post(
        "/documents",
        json={
            "title": "Streaming Notes",
            "content": (
                "Streaming improves perceived latency by returning partial output."
                "\n\n"
                "Batch responses wait until the full answer is complete."
            ),
            "source": "day-05-test",
        },
    )
    document_id = create_response.json()["document_id"]

    response = client.post(
        "/ask/stream",
        json={"question": "How does streaming improve latency?"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    body = response.text
    assert "event: answer_chunk" in body
    assert "Streaming " in body or "streaming " in body
    assert "event: citation" in body
    assert document_id in body
    assert "day-05-test" in body
    assert "event: done" in body


def test_ask_stream_returns_fallback_chunk_and_done_when_no_context_matches() -> None:
    response = client.post(
        "/ask/stream",
        json={"question": "xylophonium qwertyasdf"},
    )

    assert response.status_code == 200

    body = response.text
    assert "event: answer_chunk" in body
    assert '"text": "I "' in body
    assert '"text": "context "' in body
    assert '"text": "documents. "' in body
    assert "event: citation" not in body
    assert "event: done" in body
