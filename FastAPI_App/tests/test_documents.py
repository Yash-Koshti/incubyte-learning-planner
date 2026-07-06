import io

from httpx import AsyncClient


async def test_upload_document_success(client: AsyncClient):
    response = await client.post(
        "/api/v1/documents",
        files={"file": ("report.pdf", io.BytesIO(b"pdf content"), "application/pdf")},
        data={"title": "Q4 Report", "description": "Annual report"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "report.pdf"
    assert body["status"] == "uploaded"
    assert body["title"] == "Q4 Report"
    assert "id" in body


async def test_upload_document_unsupported_file_type(client: AsyncClient):
    response = await client.post(
        "/api/v1/documents",
        files={
            "file": (
                "malware.exe",
                io.BytesIO(b"bad content"),
                "application/octet-stream",
            )
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


async def test_upload_document_empty_title_rejected(client: AsyncClient):
    response = await client.post(
        "/api/v1/documents",
        files={"file": ("report.pdf", io.BytesIO(b"content"), "application/pdf")},
        data={"title": "   "},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_TITLE"


async def test_list_documents_empty(client: AsyncClient):
    response = await client.get("/api/v1/documents")
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0


async def test_list_documents_with_status_filter(client: AsyncClient):
    await client.post(
        "/api/v1/documents",
        files={"file": ("doc.pdf", io.BytesIO(b"content"), "application/pdf")},
    )
    response = await client.get("/api/v1/documents?status=uploaded")
    assert response.status_code == 200
    assert response.json()["total"] == 1

    response = await client.get("/api/v1/documents?status=completed")
    assert response.status_code == 200
    assert response.json()["total"] == 0


async def test_get_document_success(client: AsyncClient):
    upload = await client.post(
        "/api/v1/documents",
        files={"file": ("report.pdf", io.BytesIO(b"content"), "application/pdf")},
    )
    document_id = upload.json()["id"]

    response = await client.get(f"/api/v1/documents/{document_id}")
    assert response.status_code == 200
    assert response.json()["id"] == document_id


async def test_get_document_not_found(client: AsyncClient):
    response = await client.get(
        "/api/v1/documents/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"


async def test_get_document_invalid_uuid(client: AsyncClient):
    response = await client.get("/api/v1/documents/not-a-uuid")
    assert response.status_code == 422


async def test_delete_document_success(client: AsyncClient):
    upload = await client.post(
        "/api/v1/documents",
        files={"file": ("report.pdf", io.BytesIO(b"content"), "application/pdf")},
    )
    document_id = upload.json()["id"]

    response = await client.delete(f"/api/v1/documents/{document_id}")
    assert response.status_code == 204

    response = await client.get(f"/api/v1/documents/{document_id}")
    assert response.status_code == 404


async def test_delete_document_not_found(client: AsyncClient):
    response = await client.delete(
        "/api/v1/documents/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404
