"""Tests for file download functionality."""

import tempfile
from pathlib import Path
from typing import Any

from starlette.responses import FileResponse
from starlette.testclient import TestClient

from crimsy import Crimsy, Router


async def test_file_download_with_fileresponse() -> None:
    """Test downloading a file using FileResponse."""
    app = Crimsy()
    router = Router(prefix="/files")

    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("Test file content")
        temp_file = f.name

    try:

        @router.get("/download")
        async def download_file() -> FileResponse:
            """Download a test file."""
            return FileResponse(
                temp_file, media_type="text/plain", filename="downloaded.txt"
            )

        app.add_router(router)

        client = TestClient(app)
        response = client.get("/files/download")

        assert response.status_code == 200
        assert response.text == "Test file content"
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        # Check Content-Disposition header
        assert "attachment" in response.headers.get("content-disposition", "")
        assert "downloaded.txt" in response.headers.get("content-disposition", "")

    finally:
        # Clean up
        Path(temp_file).unlink()


async def test_file_download_with_path_parameter() -> None:
    """Test downloading different files based on path parameter."""
    app = Crimsy()
    router = Router(prefix="/files")

    # Create temporary files
    files = {}
    for name in ["file1.txt", "file2.txt"]:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write(f"Content of {name}")
            files[name] = f.name

    try:

        @router.get("/download/{filename}")
        async def download_specific_file(filename: str) -> FileResponse:
            """Download a specific file by name."""
            if filename not in files:
                from crimsy import HTTPException

                raise HTTPException(status_code=404, message="File not found")
            return FileResponse(files[filename], media_type="text/plain")

        app.add_router(router)

        client = TestClient(app)

        # Download file1
        response = client.get("/files/download/file1.txt")
        assert response.status_code == 200
        assert response.text == "Content of file1.txt"

        # Download file2
        response = client.get("/files/download/file2.txt")
        assert response.status_code == 200
        assert response.text == "Content of file2.txt"

        # Try non-existent file
        response = client.get("/files/download/missing.txt")
        assert response.status_code == 404

    finally:
        # Clean up
        for temp_file in files.values():
            Path(temp_file).unlink()


async def test_binary_file_download() -> None:
    """Test downloading a binary file."""
    app = Crimsy()
    router = Router(prefix="/files")

    # Create a temporary binary file
    binary_content = bytes([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
        f.write(binary_content)
        temp_file = f.name

    try:

        @router.get("/download-binary")
        async def download_binary() -> FileResponse:
            """Download a binary file."""
            return FileResponse(
                temp_file,
                media_type="application/octet-stream",
                filename="binary.bin",
            )

        app.add_router(router)

        client = TestClient(app)
        response = client.get("/files/download-binary")

        assert response.status_code == 200
        assert response.content == binary_content
        assert response.headers["content-type"] == "application/octet-stream"

    finally:
        # Clean up
        Path(temp_file).unlink()


async def test_conditional_file_download() -> None:
    """Test conditionally returning either JSON or FileResponse."""
    app = Crimsy()
    router = Router(prefix="/files")

    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("File content")
        temp_file = f.name

    try:

        @router.get("/resource")
        async def get_resource(download: bool = False) -> dict[str, Any] | FileResponse:
            """Get resource as JSON or file based on query parameter."""
            if download:
                return FileResponse(temp_file, media_type="text/plain")
            return {"message": "Resource info", "available": True}

        app.add_router(router)

        client = TestClient(app)

        # Get as JSON
        response = client.get("/files/resource")
        assert response.status_code == 200
        assert response.json() == {"message": "Resource info", "available": True}

        # Download as file
        response = client.get("/files/resource?download=true")
        assert response.status_code == 200
        assert response.text == "File content"

    finally:
        # Clean up
        Path(temp_file).unlink()
