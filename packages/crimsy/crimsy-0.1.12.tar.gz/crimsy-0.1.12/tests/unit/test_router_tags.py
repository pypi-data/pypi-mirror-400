"""Test router tags for OpenAPI grouping."""

from starlette.testclient import TestClient

from crimsy import Crimsy, Router


async def test_router_tags_in_openapi() -> None:
    """Test that router tags appear in OpenAPI schema."""
    app = Crimsy()

    # Create routers with tags
    users_router = Router(prefix="/users", tags=["Users"])
    items_router = Router(prefix="/items", tags=["Items", "Inventory"])

    @users_router.get("/")
    async def list_users() -> list[dict[str, str]]:
        """List all users."""
        return [{"name": "Alice"}]

    @items_router.get("/")
    async def list_items() -> list[dict[str, str]]:
        """List all items."""
        return [{"name": "Widget"}]

    app.add_router(users_router)
    app.add_router(items_router)

    client = TestClient(app)

    # Get OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    # Check that endpoints have tags
    assert "/users/" in schema["paths"]
    users_endpoint = schema["paths"]["/users/"]["get"]
    assert "tags" in users_endpoint
    assert users_endpoint["tags"] == ["Users"]

    assert "/items/" in schema["paths"]
    items_endpoint = schema["paths"]["/items/"]["get"]
    assert "tags" in items_endpoint
    assert items_endpoint["tags"] == ["Items", "Inventory"]


async def test_router_without_tags() -> None:
    """Test that routers without explicit tags get automatic tags from prefix."""
    app = Crimsy()
    router = Router(prefix="/api")

    @router.get("/test")
    async def test_endpoint() -> dict[str, str]:
        """Test endpoint."""
        return {"status": "ok"}

    app.add_router(router)

    client = TestClient(app)

    # Get OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    # Check that endpoint exists and has automatic tag from prefix
    assert "/api/test" in schema["paths"]
    endpoint = schema["paths"]["/api/test"]["get"]
    assert "tags" in endpoint
    assert endpoint["tags"] == ["api"]


async def test_empty_path_with_router() -> None:
    """Test that empty path routes work correctly."""
    app = Crimsy()
    router = Router(prefix="/users", tags=["Users"])

    @router.get("")
    async def list_users() -> list[dict[str, str]]:
        """List all users."""
        return [{"name": "Alice"}, {"name": "Bob"}]

    app.add_router(router)

    client = TestClient(app)

    # Test that both /users and /users/ work
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json() == [{"name": "Alice"}, {"name": "Bob"}]

    response2 = client.get("/users/")
    assert response2.status_code == 200
    assert response2.json() == [{"name": "Alice"}, {"name": "Bob"}]

    # Check OpenAPI schema
    openapi_response = client.get("/openapi.json")
    assert openapi_response.status_code == 200
    schema = openapi_response.json()

    # The path should be /users/ in OpenAPI (normalized)
    assert "/users/" in schema["paths"]
    endpoint = schema["paths"]["/users/"]["get"]
    assert "tags" in endpoint
    assert endpoint["tags"] == ["Users"]


async def test_router_with_empty_prefix() -> None:
    """Test that routers with empty prefix don't get automatic tags."""
    app = Crimsy()
    router = Router(prefix="")

    @router.get("/test")
    async def test_endpoint() -> dict[str, str]:
        """Test endpoint."""
        return {"status": "ok"}

    app.add_router(router)

    client = TestClient(app)

    # Get OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    # Check that endpoint exists but has no tags (empty prefix)
    assert "/test" in schema["paths"]
    endpoint = schema["paths"]["/test"]["get"]
    assert "tags" not in endpoint or endpoint.get("tags") == []


async def test_router_with_nested_prefix() -> None:
    """Test that nested prefixes use only the first segment as tag."""
    app = Crimsy()
    router = Router(prefix="/api/v1/users")

    @router.get("/")
    async def list_users() -> list[dict[str, str]]:
        """List users."""
        return [{"name": "Alice"}]

    app.add_router(router)

    client = TestClient(app)

    # Get OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    # Check that endpoint has tag from first segment
    assert "/api/v1/users/" in schema["paths"]
    endpoint = schema["paths"]["/api/v1/users/"]["get"]
    assert "tags" in endpoint
    assert endpoint["tags"] == ["api"]


async def test_explicit_empty_tags_list() -> None:
    """Test that explicitly setting tags=[] prevents automatic tag generation."""
    app = Crimsy()
    router = Router(prefix="/api", tags=[])

    @router.get("/test")
    async def test_endpoint() -> dict[str, str]:
        """Test endpoint."""
        return {"status": "ok"}

    app.add_router(router)

    client = TestClient(app)

    # Get OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    # Check that endpoint has no tags (explicitly set to empty)
    assert "/api/test" in schema["paths"]
    endpoint = schema["paths"]["/api/test"]["get"]
    assert "tags" not in endpoint or endpoint.get("tags") == []
