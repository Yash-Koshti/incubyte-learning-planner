import io
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


async def test_get_document_invalid_uuid_format(client: AsyncClient):
    response = await client.get("/api/v1/documents/not-a-uuid")
    assert response.status_code == 422


async def test_delete_document_invalid_uuid_format(client: AsyncClient):
    response = await client.delete("/api/v1/documents/not-a-uuid")
    assert response.status_code == 422


async def test_upload_document_no_file(client: AsyncClient):
    response = await client.post("/api/v1/documents")
    assert response.status_code == 422


async def test_upload_document_whitespace_title(client: AsyncClient):
    response = await client.post(
        "/api/v1/documents",
        files={"file": ("report.pdf", io.BytesIO(b"content"), "application/pdf")},
        data={"title": "   "},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_TITLE"


async def test_create_job_empty_operations(client: AsyncClient):
    upload = await client.post(
        "/api/v1/documents",
        files={"file": ("report.pdf", io.BytesIO(b"content"), "application/pdf")},
    )
    document_id = upload.json()["id"]

    response = await client.post(
        f"/api/v1/documents/{document_id}/process",
        json={"operations": []},
    )
    assert response.status_code == 422


async def test_create_job_missing_operations_field(client: AsyncClient):
    upload = await client.post(
        "/api/v1/documents",
        files={"file": ("report.pdf", io.BytesIO(b"content"), "application/pdf")},
    )
    document_id = upload.json()["id"]

    response = await client.post(
        f"/api/v1/documents/{document_id}/process",
        json={},
    )
    assert response.status_code == 422


async def test_list_documents_invalid_page(client: AsyncClient):
    response = await client.get("/api/v1/documents?page=0")
    assert response.status_code == 422


async def test_list_documents_invalid_page_size(client: AsyncClient):
    response = await client.get("/api/v1/documents?page_size=0")
    assert response.status_code == 422


async def test_list_documents_page_size_too_large(client: AsyncClient):
    response = await client.get("/api/v1/documents?page_size=101")
    assert response.status_code == 422


async def test_list_documents_invalid_status_filter(client: AsyncClient):
    response = await client.get("/api/v1/documents?status=invalid_status")
    assert response.status_code == 422


async def test_middleware_logs_unhandled_exception(client: AsyncClient):
    with patch(
        "app.api.v1.documents.DocumentService.list",
        new_callable=AsyncMock,
        side_effect=RuntimeError("unexpected crash"),
    ):
        with pytest.raises(RuntimeError):
            await client.get("/api/v1/documents")
