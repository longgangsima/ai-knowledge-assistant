from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ask_returns_answer_with_citations_from_retrieved_chunks() -> None:
    create_response = client.post(
        "/documents",
        json={
            "title": "Reliability Notes",
            "content": (
                "Production reliability improved after adding retries and alerts."
                "\n\n"
                "Frontend polish focused on spacing and typography."
            ),
            "source": "day-04-test",
        },
    )
    document_id = create_response.json()["document_id"]

    ask_response = client.post(
        "/ask",
        json={"question": "How did reliability improve?"},
    )
    payload = ask_response.json()

    assert ask_response.status_code == 200
    assert "Production reliability improved" in payload["answer"]
    assert payload["citations"]
    assert payload["citations"][0]["document_id"] == document_id
    assert payload["citations"][0]["chunk_index"] == 0
    assert "Production reliability improved" in payload["citations"][0]["text"]
    assert payload["citations"][0]["source"] == "day-04-test"


def test_ask_returns_empty_citations_when_no_context_matches() -> None:
    response = client.post(
        "/ask",
        json={"question": "zzzz unmatched query"},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["answer"] == "I could not find relevant context in the stored documents."
    assert payload["citations"] == []
