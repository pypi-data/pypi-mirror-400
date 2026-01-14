"""Test that response content-type header is properly set."""

import msgspec
from starlette.testclient import TestClient

from crimsy import Crimsy, Router


class Token(msgspec.Struct):
    """Schema for authentication token."""

    access_token: str
    token_type: str = "bearer"


async def test_msgspec_response_has_content_type() -> None:
    """Test that endpoints returning msgspec.Struct have proper content-type header.

    This reproduces the issue where Swagger UI displays "Unrecognized response type"
    because the response doesn't have a content-type header.
    """
    app = Crimsy()
    router = Router(prefix="/auth")

    @router.post("/login")
    async def login() -> Token:
        """Login user and return JWT token."""
        return Token(access_token="test_token_123", token_type="bearer")

    app.add_router(router)

    client = TestClient(app)
    response = client.post("/auth/login")

    # Check that response is successful
    assert response.status_code == 200

    # Check that content-type header is set properly
    assert response.headers.get("content-type") == "application/json"

    # Check that body is correct
    data = response.json()
    assert data["access_token"] == "test_token_123"
    assert data["token_type"] == "bearer"


async def test_dict_response_has_content_type() -> None:
    """Test that endpoints returning dict have proper content-type header."""
    app = Crimsy()
    router = Router(prefix="/api")

    @router.get("/data")
    async def get_data() -> dict[str, str]:
        """Get some data."""
        return {"message": "Hello, World!"}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/api/data")

    # Check that response is successful
    assert response.status_code == 200

    # Check that content-type header is set properly
    assert response.headers.get("content-type") == "application/json"

    # Check that body is correct
    data = response.json()
    assert data["message"] == "Hello, World!"


async def test_list_response_has_content_type() -> None:
    """Test that endpoints returning list have proper content-type header."""
    app = Crimsy()
    router = Router(prefix="/api")

    @router.get("/items")
    async def get_items() -> list[dict[str, str]]:
        """Get items."""
        return [{"name": "Item 1"}, {"name": "Item 2"}]

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/api/items")

    # Check that response is successful
    assert response.status_code == 200

    # Check that content-type header is set properly
    assert response.headers.get("content-type") == "application/json"

    # Check that body is correct
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Item 1"
