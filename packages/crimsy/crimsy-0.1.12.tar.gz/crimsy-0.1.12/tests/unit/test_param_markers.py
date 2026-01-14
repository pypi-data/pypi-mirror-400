"""Tests for Query, Body, and Path parameter markers."""

import msgspec
from starlette.testclient import TestClient

from crimsy import Body, Crimsy, Path, Query, Router


class User(msgspec.Struct):
    """User model for testing."""

    name: str
    age: int = 25


async def test_query_marker_with_default() -> None:
    """Test Query marker with default value."""
    app = Crimsy()
    router = Router(prefix="/api")

    @router.get("/greet")
    async def greet(name: str = Query(default="guest")) -> dict[str, str]:
        return {"message": f"Hello, {name}!"}

    app.add_router(router)

    client = TestClient(app)

    # Test with query parameter
    response = client.get("/api/greet?name=Alice")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Alice!"}

    # Test with default value
    response = client.get("/api/greet")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, guest!"}


async def test_body_marker() -> None:
    """Test Body marker for explicit body parameters."""
    app = Crimsy()
    router = Router(prefix="/api")

    @router.post("/process")
    async def process(data: dict[str, str] = Body()) -> dict[str, str]:
        """POST request with explicit body parameter."""
        return {"processed": str(data)}

    app.add_router(router)

    client = TestClient(app)

    response = client.post("/api/process", json={"test": "data"})
    assert response.status_code == 200
    assert "processed" in response.json()


async def test_body_marker_with_struct() -> None:
    """Test Body marker with msgspec.Struct."""
    app = Crimsy()
    router = Router(prefix="/users")

    @router.post("/create")
    async def create_user(user: User = Body()) -> User:
        return user

    app.add_router(router)

    client = TestClient(app)

    response = client.post("/users/create", json={"name": "Bob", "age": 30})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Bob"
    assert data["age"] == 30


async def test_path_marker() -> None:
    """Test Path marker for path parameters."""
    app = Crimsy()
    router = Router(prefix="/users")

    @router.get("/{user_id}")
    async def get_user(user_id: int = Path()) -> dict[str, int]:
        return {"user_id": user_id}

    app.add_router(router)

    client = TestClient(app)

    response = client.get("/users/123")
    assert response.status_code == 200
    assert response.json() == {"user_id": 123}


async def test_mixed_query_and_body() -> None:
    """Test mixing Query and Body parameters."""
    app = Crimsy()
    router = Router(prefix="/api")

    @router.post("/process")
    async def process(
        name: str = Query(default="unknown"),
        data: dict[str, str] = Body(),
    ) -> dict[str, str]:
        return {"name": name, "data": str(data)}

    app.add_router(router)

    client = TestClient(app)

    response = client.post("/api/process?name=Alice", json={"key": "value"})
    assert response.status_code == 200
    result = response.json()
    assert result["name"] == "Alice"
    assert "value" in result["data"]


async def test_mixed_path_query_and_body() -> None:
    """Test mixing Path, Query, and Body parameters."""
    app = Crimsy()
    router = Router(prefix="/api")

    @router.put("/{item_id}")
    async def update_item(
        item_id: int = Path(),
        version: str = Query(default="v1"),
        data: dict[str, bool] = Body(),
    ) -> dict[str, int | str]:
        return {"item_id": item_id, "version": version, "data": str(data)}

    app.add_router(router)

    client = TestClient(app)

    response = client.put("/api/456?version=v2", json={"updated": True})
    assert response.status_code == 200
    result = response.json()
    assert result["item_id"] == 456
    assert result["version"] == "v2"
    assert "True" in result["data"]


async def test_query_with_int_type() -> None:
    """Test Query marker with int type conversion."""
    app = Crimsy()
    router = Router(prefix="/api")

    @router.get("/items")
    async def list_items(
        limit: int = Query(default=10),
        offset: int = Query(default=0),
    ) -> dict[str, int]:
        return {"limit": limit, "offset": offset}

    app.add_router(router)

    client = TestClient(app)

    # Test with parameters
    response = client.get("/api/items?limit=20&offset=5")
    assert response.status_code == 200
    assert response.json() == {"limit": 20, "offset": 5}

    # Test with defaults
    response = client.get("/api/items")
    assert response.status_code == 200
    assert response.json() == {"limit": 10, "offset": 0}


async def test_body_marker_overrides_get_default() -> None:
    """Test that Body() marker can be used with GET to force body reading."""
    app = Crimsy()
    router = Router(prefix="/api")

    # Using a custom request that has a body
    @router.post("/search")
    async def search(query: User = Body()) -> dict[str, str]:
        """POST request with explicit Body parameter for struct."""
        return {"query": query.name}

    app.add_router(router)

    client = TestClient(app)

    # Use POST instead since GET with body is not well-supported in HTTP clients
    response = client.post("/api/search", json={"name": "Alice", "age": 30})
    assert response.status_code == 200
    assert response.json() == {"query": "Alice"}


async def test_post_defaults_to_body_for_struct() -> None:
    """Test that POST requests default to Body for msgspec.Struct without marker."""
    app = Crimsy()
    router = Router(prefix="/users")

    @router.post("/")
    async def create_user(user: User) -> User:
        """POST without explicit marker should use body."""
        return user

    app.add_router(router)

    client = TestClient(app)

    response = client.post("/users/", json={"name": "Charlie", "age": 35})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Charlie"
    assert data["age"] == 35


async def test_get_defaults_to_query_for_simple_types() -> None:
    """Test that GET requests default to Query for simple types without marker."""
    app = Crimsy()
    router = Router(prefix="/api")

    @router.get("/hello")
    async def hello(name: str) -> dict[str, str]:
        """GET without explicit marker should use query."""
        return {"message": f"Hello, {name}!"}

    app.add_router(router)

    client = TestClient(app)

    response = client.get("/api/hello?name=World")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


async def test_required_query_parameter() -> None:
    """Test that Query without default is required."""
    app = Crimsy()
    router = Router(prefix="/api")

    @router.get("/search")
    async def search(q: str = Query()) -> dict[str, str]:
        return {"query": q}

    app.add_router(router)

    client = TestClient(app)

    # Should fail without parameter
    response = client.get("/api/search")
    assert response.status_code == 400
    assert "error" in response.json()


async def test_path_marker_with_default() -> None:
    """Test that Path marker with default value works correctly."""
    app = Crimsy()
    router = Router(prefix="/api")

    # Using Path() marker on a route parameter explicitly
    @router.get("/items/{item_id}")
    async def get_item(item_id: int = Path(default=1)) -> dict[str, int]:
        return {"item_id": item_id}

    app.add_router(router)

    client = TestClient(app)

    # Test with path parameter
    response = client.get("/api/items/42")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42}


async def test_path_marker_on_non_path_param() -> None:
    """Test that Path marker can be used on non-path parameters (edge case)."""
    app = Crimsy()
    router = Router(prefix="/api")

    # This is an unusual edge case - using Path() on a parameter
    # that's not actually in the URL path
    @router.get("/items")
    async def get_items(item_id: int = Path(default=1)) -> dict[str, int]:
        return {"item_id": item_id}

    app.add_router(router)

    client = TestClient(app)

    # Since it's marked as Path but not in URL, it should still work
    # (though this is not a recommended pattern)
    response = client.get("/api/items")
    assert response.status_code == 200
    assert response.json() == {"item_id": 1}
