"""Example demonstrating file upload and download functionality in Crimsy."""

from crimsy import Crimsy, File, FileResponse, Router
from starlette.datastructures import UploadFile


app = Crimsy(title="File Upload/Download Example")
router = Router(prefix="/files")


@router.post("/upload")
async def upload_single_file(file: UploadFile = File()) -> dict[str, str | int]:
    """Upload a single file and return its metadata."""
    content = await file.read()
    return {
        "filename": file.filename or "unknown",
        "content_type": file.content_type or "unknown",
        "size": len(content),
    }


@router.post("/upload-multiple")
async def upload_multiple_files(
    files: list[UploadFile] = File(),
) -> dict[str, list[dict[str, object]]]:
    """Upload multiple files and return their metadata."""
    results: list[dict[str, object]] = []
    for file in files:
        content = await file.read()
        results.append(
            {
                "filename": file.filename or "unknown",
                "size": len(content),
            }
        )
    return {"files": results}


@router.post("/upload-with-description")
async def upload_with_metadata(
    file: UploadFile = File(), description: str = ""
) -> dict[str, str | int]:
    """Upload a file along with additional form data."""
    content = await file.read()
    return {
        "filename": file.filename or "unknown",
        "size": len(content),
        "description": description,
    }


@router.get("/download")
async def download_file() -> FileResponse:
    """Download a file.

    In a real application, you would specify an actual file path.
    This is just a demonstration of the API.
    """
    # Replace with actual file path in production
    return FileResponse("example.txt", media_type="text/plain", filename="download.txt")


app.add_router(router)

if __name__ == "__main__":
    import uvicorn

    print("Starting file upload/download example server...")
    print("Visit http://localhost:8000/docs to test the API")
    uvicorn.run(app, host="0.0.0.0", port=8000)
