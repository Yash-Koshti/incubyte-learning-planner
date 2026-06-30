import io

from httpx import AsyncClient


async def _upload_document(client: AsyncClient) -> str:
    response = await client.post(
        "/api/v1/documents",
        files={"file": ("report.pdf", io.BytesIO(b"pdf content"), "application/pdf")},
        data={"title": "Test Report"},
    )
    assert response.status_code == 201
    return response.json()["id"]


async def _create_job(
    client: AsyncClient, document_id: str, operations: list[str]
) -> str:
    response = await client.post(
        f"/api/v1/documents/{document_id}/process",
        json={"operations": operations},
    )
    assert response.status_code == 202
    return response.json()["job_id"]


async def test_create_job_success(client: AsyncClient):
    document_id = await _upload_document(client)
    response = await client.post(
        f"/api/v1/documents/{document_id}/process",
        json={"operations": ["extract_text", "generate_summary"]},
    )
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "pending"
    assert "job_id" in body


async def test_create_job_starts_temporal_workflow(
    client: AsyncClient, mock_temporal_client
):
    document_id = await _upload_document(client)
    job_id = await _create_job(client, document_id, ["extract_text"])
    mock_temporal_client.start_workflow.assert_awaited_once()
    call_args = mock_temporal_client.start_workflow.call_args
    assert call_args.kwargs["id"] == f"doc-processing-{job_id}"


async def test_create_job_document_not_found(client: AsyncClient):
    response = await client.post(
        "/api/v1/documents/00000000-0000-0000-0000-000000000000/process",
        json={"operations": ["extract_text"]},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"


async def test_create_job_invalid_operation(client: AsyncClient):
    document_id = await _upload_document(client)
    response = await client.post(
        f"/api/v1/documents/{document_id}/process",
        json={"operations": ["invalid_op"]},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "UNSUPPORTED_OPERATION"


async def test_get_job_status_pending(client: AsyncClient):
    document_id = await _upload_document(client)
    job_id = await _create_job(client, document_id, ["extract_text"])
    response = await client.get(f"/api/v1/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "pending"


async def test_get_job_not_found(client: AsyncClient):
    response = await client.get("/api/v1/jobs/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "JOB_NOT_FOUND"


async def test_get_results_job_not_completed(client: AsyncClient):
    document_id = await _upload_document(client)
    job_id = await _create_job(client, document_id, ["extract_text"])
    response = await client.get(f"/api/v1/jobs/{job_id}/results")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "JOB_NOT_COMPLETED"


async def test_get_results_job_not_found(client: AsyncClient):
    response = await client.get(
        "/api/v1/jobs/00000000-0000-0000-0000-000000000000/results"
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "JOB_NOT_FOUND"
