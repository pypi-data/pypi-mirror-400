"""Tests for the Crimsy application."""

import msgspec
from starlette.testclient import TestClient

from crimsy import Crimsy, Router


class User(msgspec.Struct):
    """User model for testing."""

    name: str
    age: int = 0


async def test_basic_get_route() -> None:
    """Test basic GET route with query parameters."""
    app = Crimsy()
    router = Router(prefix="/users")

    @router.get("/")
    async def handler(name: str) -> dict[str, str]:
        return {"message": f"Hello, {name}!"}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/users/?name=Alice")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Alice!"}


async def test_get_with_msgspec_struct() -> None:
    """Test GET route with msgspec.Struct in body."""
    app = Crimsy()
    router = Router(prefix="/users")

    @router.post("/")
    async def handler(user: User) -> User:
        return user

    app.add_router(router)

    client = TestClient(app)
    response = client.post(
        "/users/",
        json={"name": "Bob", "age": 30},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Bob"
    assert data["age"] == 30


async def test_multiple_query_params() -> None:
    """Test route with multiple query parameters."""
    app = Crimsy()
    router = Router(prefix="/api")

    @router.get("/search")
    async def search(query: str, limit: int = 10) -> dict[str, int | str]:
        return {"query": query, "limit": limit}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/api/search?query=test&limit=20")

    assert response.status_code == 200
    assert response.json() == {"query": "test", "limit": 20}


async def test_post_route() -> None:
    """Test POST route."""
    app = Crimsy()
    router = Router(prefix="/items")

    @router.post("/create")
    async def create_item(name: str, price: float) -> dict[str, str | float]:
        return {"name": name, "price": price, "status": "created"}

    app.add_router(router)

    client = TestClient(app)
    response = client.post("/items/create?name=Widget&price=9.99")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Widget"
    assert data["price"] == 9.99


async def test_put_route() -> None:
    """Test PUT route."""
    app = Crimsy()
    router = Router(prefix="/items")

    @router.put("/update")
    async def update_item(item_id: int) -> dict[str, int | str]:
        return {"item_id": item_id, "status": "updated"}

    app.add_router(router)

    client = TestClient(app)
    response = client.put("/items/update?item_id=123")

    assert response.status_code == 200
    assert response.json() == {"item_id": 123, "status": "updated"}


async def test_delete_route() -> None:
    """Test DELETE route."""
    app = Crimsy()
    router = Router(prefix="/items")

    @router.delete("/remove")
    async def delete_item(item_id: int) -> dict[str, int | str]:
        return {"item_id": item_id, "status": "deleted"}

    app.add_router(router)

    client = TestClient(app)
    response = client.delete("/items/remove?item_id=456")

    assert response.status_code == 200
    assert response.json() == {"item_id": 456, "status": "deleted"}


async def test_openapi_endpoint() -> None:
    """Test that OpenAPI JSON endpoint is available."""
    app = Crimsy()
    router = Router(prefix="/users")

    @router.get("/")
    async def list_users() -> list[dict[str, str]]:
        return [{"name": "Alice"}, {"name": "Bob"}]

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert schema["openapi"] == "3.0.0"
    assert schema["info"]["title"] == "Crimsy API"
    assert "/users/" in schema["paths"]


async def test_swagger_ui_endpoint() -> None:
    """Test that Scalar UI endpoint is available."""
    app = Crimsy()

    client = TestClient(app)
    response = client.get("/docs")

    assert response.status_code == 200
    # Check for Scalar-specific identifier
    assert "@scalar/api-reference" in response.text


async def test_msgspec_struct_response() -> None:
    """Test returning msgspec.Struct from endpoint."""
    app = Crimsy()
    router = Router(prefix="/users")

    @router.get("/user")
    async def get_user(name: str) -> User:
        return User(name=name, age=25)

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/users/user?name=Charlie")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Charlie"
    assert data["age"] == 25


async def test_missing_required_param() -> None:
    """Test that missing required parameters return error."""
    app = Crimsy()
    router = Router(prefix="/api")

    @router.get("/test")
    async def test_endpoint(required_param: str) -> dict[str, str]:
        return {"param": required_param}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/api/test")

    assert response.status_code == 400
    assert "error" in response.json()


async def test_complex_struct() -> None:
    """Test complex msgspec.Struct with nested data."""

    class Address(msgspec.Struct):
        street: str
        city: str

    class Person(msgspec.Struct):
        name: str
        address: Address

    app = Crimsy()
    router = Router(prefix="/people")

    @router.post("/")
    async def create_person(person: Person) -> Person:
        return person

    app.add_router(router)

    client = TestClient(app)
    response = client.post(
        "/people/",
        json={
            "name": "David",
            "address": {"street": "123 Main St", "city": "Springfield"},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "David"
    assert data["address"]["street"] == "123 Main St"
    assert data["address"]["city"] == "Springfield"


async def test_different_http_methods() -> None:
    """Test that all HTTP methods work correctly."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/")
    async def get_handler() -> dict[str, str]:
        return {"method": "GET"}

    @router.post("/")
    async def post_handler() -> dict[str, str]:
        return {"method": "POST"}

    @router.put("/")
    async def put_handler() -> dict[str, str]:
        return {"method": "PUT"}

    @router.delete("/")
    async def delete_handler() -> dict[str, str]:
        return {"method": "DELETE"}

    @router.patch("/")
    async def patch_handler() -> dict[str, str]:
        return {"method": "PATCH"}

    app.add_router(router)

    client = TestClient(app)

    assert client.get("/test/").json() == {"method": "GET"}
    assert client.post("/test/").json() == {"method": "POST"}
    assert client.put("/test/").json() == {"method": "PUT"}
    assert client.delete("/test/").json() == {"method": "DELETE"}
    assert client.patch("/test/").json() == {"method": "PATCH"}
