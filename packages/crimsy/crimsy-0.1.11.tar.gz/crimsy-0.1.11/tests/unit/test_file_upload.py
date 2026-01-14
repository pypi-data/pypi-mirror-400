"""Tests for file upload functionality."""

from typing import Any

from starlette.datastructures import UploadFile
from starlette.testclient import TestClient

from crimsy import Crimsy, File, Router


async def test_single_file_upload() -> None:
    """Test uploading a single file."""
    app = Crimsy()
    router = Router(prefix="/files")

    @router.post("/upload")
    async def upload_file(file: UploadFile = File()) -> dict[str, Any]:
        """Upload a single file."""
        content = await file.read()
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content),
        }

    app.add_router(router)

    client = TestClient(app)
    files = {"file": ("test.txt", b"Hello, World!", "text/plain")}
    response = client.post("/files/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["content_type"] == "text/plain"
    assert data["size"] == 13


async def test_multiple_file_upload() -> None:
    """Test uploading multiple files."""
    app = Crimsy()
    router = Router(prefix="/files")

    @router.post("/upload-multiple")
    async def upload_multiple(files: list[UploadFile] = File()) -> dict[str, Any]:
        """Upload multiple files."""
        results = []
        for file in files:
            content = await file.read()
            results.append(
                {
                    "filename": file.filename,
                    "size": len(content),
                }
            )
        return {"files": results}

    app.add_router(router)

    client = TestClient(app)
    files = [
        ("files", ("file1.txt", b"Content 1", "text/plain")),
        ("files", ("file2.txt", b"Content 2", "text/plain")),
    ]
    response = client.post("/files/upload-multiple", files=files)

    assert response.status_code == 200
    data = response.json()
    assert len(data["files"]) == 2
    assert data["files"][0]["filename"] == "file1.txt"
    assert data["files"][0]["size"] == 9
    assert data["files"][1]["filename"] == "file2.txt"
    assert data["files"][1]["size"] == 9


async def test_file_upload_with_other_fields() -> None:
    """Test uploading a file with other form fields."""
    app = Crimsy()
    router = Router(prefix="/files")

    @router.post("/upload-with-data")
    async def upload_with_data(
        file: UploadFile = File(), description: str = ""
    ) -> dict[str, Any]:
        """Upload a file with additional data."""
        content = await file.read()
        return {
            "filename": file.filename,
            "size": len(content),
            "description": description,
        }

    app.add_router(router)

    client = TestClient(app)
    files = {"file": ("test.txt", b"Test content", "text/plain")}
    data = {"description": "Test file"}
    response = client.post("/files/upload-with-data", files=files, data=data)

    assert response.status_code == 200
    result = response.json()
    assert result["filename"] == "test.txt"
    assert result["size"] == 12
    assert result["description"] == "Test file"


async def test_optional_file_upload() -> None:
    """Test optional file upload."""
    app = Crimsy()
    router = Router(prefix="/files")

    @router.post("/upload-optional")
    async def upload_optional(
        file: UploadFile | None = File(default=None),
    ) -> dict[str, Any]:
        """Upload an optional file."""
        if file is None:
            return {"uploaded": False}
        content = await file.read()
        return {"uploaded": True, "filename": file.filename, "size": len(content)}

    app.add_router(router)

    client = TestClient(app)

    # Without file
    response = client.post("/files/upload-optional")
    assert response.status_code == 200
    assert response.json() == {"uploaded": False}

    # With file
    files = {"file": ("test.txt", b"Content", "text/plain")}
    response = client.post("/files/upload-optional", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["uploaded"] is True
    assert data["filename"] == "test.txt"
    assert data["size"] == 7


async def test_missing_required_file() -> None:
    """Test missing required file parameter."""
    app = Crimsy()
    router = Router(prefix="/files")

    @router.post("/upload")
    async def upload_file(file: UploadFile = File()) -> dict[str, Any]:
        """Upload a required file."""
        return {"filename": file.filename}

    app.add_router(router)

    client = TestClient(app)
    response = client.post("/files/upload")

    assert response.status_code == 400
    assert "error" in response.json()


async def test_file_upload_auto_detection() -> None:
    """Test that UploadFile type is automatically detected as file parameter."""
    app = Crimsy()
    router = Router(prefix="/files")

    @router.post("/upload-auto")
    async def upload_auto(file: UploadFile) -> dict[str, Any]:
        """Upload file with auto-detection (no File() marker)."""
        content = await file.read()
        return {"filename": file.filename, "size": len(content)}

    app.add_router(router)

    client = TestClient(app)
    files = {"file": ("auto.txt", b"Auto detected", "text/plain")}
    response = client.post("/files/upload-auto", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "auto.txt"
    assert data["size"] == 13


async def test_multiple_files_auto_detection() -> None:
    """Test that list[UploadFile] is automatically detected."""
    app = Crimsy()
    router = Router(prefix="/files")

    @router.post("/upload-list")
    async def upload_list(files: list[UploadFile]) -> dict[str, Any]:
        """Upload multiple files with auto-detection."""
        count = len(files)
        total_size = 0
        for file in files:
            content = await file.read()
            total_size += len(content)
        return {"count": count, "total_size": total_size}

    app.add_router(router)

    client = TestClient(app)
    files = [
        ("files", ("file1.txt", b"A" * 10, "text/plain")),
        ("files", ("file2.txt", b"B" * 20, "text/plain")),
    ]
    response = client.post("/files/upload-list", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert data["total_size"] == 30
