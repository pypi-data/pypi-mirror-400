"""Tests for OpenAPI schema generation with file uploads."""

from typing import Any

from starlette.datastructures import UploadFile
from starlette.testclient import TestClient

from crimsy import Crimsy, File, Router


async def test_openapi_file_upload_single() -> None:
    """Test OpenAPI schema for single file upload."""
    app = Crimsy()
    router = Router(prefix="/files")

    @router.post("/upload")
    async def upload_file(file: UploadFile = File()) -> dict[str, Any]:
        """Upload a single file."""
        return {"filename": "test"}

    app.add_router(router)

    schema = app.openapi_schema()

    # Check that the endpoint exists
    assert "/files/upload" in schema["paths"]
    post_op = schema["paths"]["/files/upload"]["post"]

    # Check request body is multipart/form-data
    assert "requestBody" in post_op
    assert "multipart/form-data" in post_op["requestBody"]["content"]

    # Check file parameter schema
    form_schema = post_op["requestBody"]["content"]["multipart/form-data"]["schema"]
    assert "properties" in form_schema
    assert "file" in form_schema["properties"]
    assert form_schema["properties"]["file"]["type"] == "string"
    assert form_schema["properties"]["file"]["format"] == "binary"

    # Check that file is required
    assert "required" in form_schema
    assert "file" in form_schema["required"]


async def test_openapi_file_upload_multiple() -> None:
    """Test OpenAPI schema for multiple file upload."""
    app = Crimsy()
    router = Router(prefix="/files")

    @router.post("/upload-multiple")
    async def upload_multiple(files: list[UploadFile] = File()) -> dict[str, Any]:
        """Upload multiple files."""
        return {"count": 0}

    app.add_router(router)

    schema = app.openapi_schema()

    post_op = schema["paths"]["/files/upload-multiple"]["post"]
    form_schema = post_op["requestBody"]["content"]["multipart/form-data"]["schema"]

    # Check that files is an array of binary strings
    assert "files" in form_schema["properties"]
    files_schema = form_schema["properties"]["files"]
    assert files_schema["type"] == "array"
    assert files_schema["items"]["type"] == "string"
    assert files_schema["items"]["format"] == "binary"


async def test_openapi_file_upload_auto_detection() -> None:
    """Test OpenAPI schema when UploadFile is auto-detected."""
    app = Crimsy()
    router = Router(prefix="/files")

    @router.post("/upload")
    async def upload_file(file: UploadFile) -> dict[str, Any]:
        """Upload a file (auto-detected)."""
        return {"filename": "test"}

    app.add_router(router)

    schema = app.openapi_schema()
    post_op = schema["paths"]["/files/upload"]["post"]

    # Should still generate multipart/form-data
    assert "multipart/form-data" in post_op["requestBody"]["content"]
    form_schema = post_op["requestBody"]["content"]["multipart/form-data"]["schema"]
    assert "file" in form_schema["properties"]
    assert form_schema["properties"]["file"]["format"] == "binary"


async def test_openapi_optional_file_upload() -> None:
    """Test OpenAPI schema for optional file upload."""
    app = Crimsy()
    router = Router(prefix="/files")

    @router.post("/upload-optional")
    async def upload_optional(
        file: UploadFile | None = File(default=None),
    ) -> dict[str, Any]:
        """Upload an optional file."""
        return {"uploaded": False}

    app.add_router(router)

    schema = app.openapi_schema()
    post_op = schema["paths"]["/files/upload-optional"]["post"]

    # File should be in schema but not required
    form_schema = post_op["requestBody"]["content"]["multipart/form-data"]["schema"]
    assert "file" in form_schema["properties"]

    # Should not be in required list (or required list shouldn't include it)
    required = form_schema.get("required", [])
    assert "file" not in required


async def test_openapi_file_response() -> None:
    """Test OpenAPI schema for file download endpoints."""
    from starlette.responses import FileResponse

    app = Crimsy()
    router = Router(prefix="/files")

    @router.get("/download")
    async def download_file() -> FileResponse:
        """Download a file."""
        return FileResponse("test.txt")

    app.add_router(router)

    schema = app.openapi_schema()

    # Check that the endpoint exists and has a response
    assert "/files/download" in schema["paths"]
    get_op = schema["paths"]["/files/download"]["get"]
    assert "responses" in get_op
    assert "200" in get_op["responses"]


async def test_openapi_swagger_ui_with_files() -> None:
    """Test that Swagger UI is accessible with file upload endpoints."""
    app = Crimsy()
    router = Router(prefix="/files")

    @router.post("/upload")
    async def upload_file(file: UploadFile = File()) -> dict[str, Any]:
        """Upload a file."""
        return {"filename": "test"}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/docs")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    # Check OpenAPI endpoint
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "/files/upload" in schema["paths"]
