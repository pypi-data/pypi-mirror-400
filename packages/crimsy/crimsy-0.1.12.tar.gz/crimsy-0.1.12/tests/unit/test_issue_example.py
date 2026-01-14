"""Test the exact example from the issue."""

import msgspec
from starlette.testclient import TestClient

from crimsy import Crimsy, Router


class User(msgspec.Struct):
    """User model."""

    name: str


async def test_issue_example() -> None:
    """Test the exact example from the issue using GET with query params."""
    app = Crimsy()

    router = Router(prefix="/users")

    @router.get("/")
    async def handler(user: User, name: str) -> User:
        # users code implementation goes here
        return User(name=f"{user.name} and {name}")

    app.add_router(router)

    # Test the application with GET request
    # Per the issue: "the application will expect a valid encoded User and name
    # to be in the query parameters"
    client = TestClient(app)

    import json

    user_json = json.dumps({"name": "Alice"})
    response = client.get(f"/users/?user={user_json}&name=Bob")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alice and Bob"


async def test_openapi_generation_for_issue_example() -> None:
    """Test that OpenAPI schema is generated correctly."""
    app = Crimsy()

    router = Router(prefix="/users")

    @router.post("/")
    async def handler(user: User, name: str) -> User:
        return User(name=f"{user.name} and {name}")

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()

    # Verify basic structure
    assert schema["openapi"] == "3.0.0"
    assert "paths" in schema
    assert "/users/" in schema["paths"]

    # Verify the endpoint is documented
    post_endpoint = schema["paths"]["/users/"]["post"]
    assert "requestBody" in post_endpoint
    assert "parameters" in post_endpoint

    # Check that name parameter is in query
    params = post_endpoint["parameters"]
    assert any(p["name"] == "name" and p["in"] == "query" for p in params)

    # Check that user is in request body
    assert "application/json" in post_endpoint["requestBody"]["content"]


async def test_get_endpoint_does_not_show_head_in_openapi() -> None:
    """Test that GET endpoints do not show HEAD method in OpenAPI docs.

    This tests the fix for the issue where HEAD methods were appearing
    in Swagger docs even though they were only auto-added by Starlette.
    """
    app = Crimsy()

    router = Router(prefix="/api")

    @router.get("/items")
    async def get_items() -> dict[str, str]:
        """Get all items."""
        return {"message": "items"}

    app.add_router(router)

    client = TestClient(app)

    # Test that HEAD request still works (Starlette auto-adds it)
    head_response = client.head("/api/items")
    assert head_response.status_code == 200

    # Test that GET request works
    get_response = client.get("/api/items")
    assert get_response.status_code == 200
    assert get_response.json() == {"message": "items"}

    # Check OpenAPI schema does NOT include HEAD method
    schema_response = client.get("/openapi.json")
    assert schema_response.status_code == 200
    schema = schema_response.json()

    # Verify the endpoint exists
    assert "/api/items" in schema["paths"]

    # Verify only GET is documented, not HEAD
    assert "get" in schema["paths"]["/api/items"]
    assert "head" not in schema["paths"]["/api/items"]

    # Verify there's only one method documented
    assert len(schema["paths"]["/api/items"]) == 1


async def test_explicit_head_endpoint_shows_in_openapi() -> None:
    """Test that explicitly defined HEAD endpoints do show in OpenAPI docs."""
    app = Crimsy()

    router = Router(prefix="/api")

    @router.head("/status")
    async def check_status() -> None:
        """Check status with HEAD request."""
        return None

    app.add_router(router)

    client = TestClient(app)

    # Test that HEAD request works
    head_response = client.head("/api/status")
    assert head_response.status_code == 204  # No content

    # Check OpenAPI schema DOES include HEAD method
    schema_response = client.get("/openapi.json")
    assert schema_response.status_code == 200
    schema = schema_response.json()

    # Verify the endpoint exists and HEAD is documented
    assert "/api/status" in schema["paths"]
    assert "head" in schema["paths"]["/api/status"]


async def test_head_requests_work_with_query_parameters() -> None:
    """Test that HEAD requests work correctly for GET endpoints with query parameters.

    This verifies that HEAD requests properly handle parameters the same way as GET requests.
    """
    app = Crimsy()

    router = Router(prefix="/api")

    @router.get("/search")
    async def search(query: str, limit: int = 10) -> dict[str, str | int]:
        """Search with query parameters."""
        return {"query": query, "limit": limit}

    app.add_router(router)

    client = TestClient(app)

    # Test GET request with parameters
    get_response = client.get("/api/search?query=test&limit=5")
    assert get_response.status_code == 200
    assert get_response.json() == {"query": "test", "limit": 5}

    # Test HEAD request with same parameters (should work)
    head_response = client.head("/api/search?query=test&limit=5")
    assert head_response.status_code == 200
    assert len(head_response.content) == 0  # HEAD should have no body

    # Test HEAD request with only required parameter
    head_response = client.head("/api/search?query=test")
    assert head_response.status_code == 200

    # Test HEAD request missing required parameter (should fail like GET)
    head_response = client.head("/api/search")
    assert head_response.status_code == 400  # Missing required parameter

    # Test GET request missing required parameter (should also fail)
    get_response = client.get("/api/search")
    assert get_response.status_code == 400  # Missing required parameter
