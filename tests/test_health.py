from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_document_returns_queued_job_shape() -> None:
    response = client.post(
        "/documents",
        json={
            "title": "Behavior Prep Notes",
            "content": "Tell me about a time you improved reliability in production.",
            "source": "local-notes",
        },
    )

    payload = response.json()

    assert response.status_code == 202
    assert payload["status"] == "queued"
    assert isinstance(payload["document_id"], str)
    assert isinstance(payload["job_id"], str)


def test_get_job_returns_previously_created_job() -> None:
    create_response = client.post(
        "/documents",
        json={
            "title": "Behavior Prep Notes",
            "content": "Tell me about a time you improved reliability in production.",
            "source": "local-notes",
        },
    )

    created_payload = create_response.json()
    job_id = created_payload["job_id"]
    document_id = created_payload["document_id"]

    job_response = client.get(f"/jobs/{job_id}")
    job_payload = job_response.json()

    assert job_response.status_code == 200
    assert job_payload["job_id"] == job_id
    assert job_payload["document_id"] == document_id
    assert job_payload["status"] == "queued"


def test_get_job_returns_404_for_unknown_job() -> None:
    response = client.get("/jobs/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {"detail": "Job not found."}
