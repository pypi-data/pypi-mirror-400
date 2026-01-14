"""Test GET request with msgspec.Struct in query parameters."""

import msgspec
from starlette.testclient import TestClient

from crimsy import Crimsy, Router


class User(msgspec.Struct):
    """User model."""

    name: str
    age: int = 25


async def test_get_with_struct_in_query_param() -> None:
    """Test GET route with msgspec.Struct passed as JSON in query parameter."""
    app = Crimsy()
    router = Router(prefix="/users")

    @router.get("/")
    async def handler(user: User, name: str) -> User:
        """Handler that takes both a User struct and a name string."""
        return User(name=f"{user.name} and {name}", age=user.age)

    app.add_router(router)

    client = TestClient(app)

    # Pass user as JSON string in query parameter
    import json

    user_json = json.dumps({"name": "Alice", "age": 30})
    response = client.get(
        f"/users/?user={user_json}&name=Bob",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alice and Bob"
    assert data["age"] == 30


async def test_get_with_struct_in_query_param_url_encoded() -> None:
    """Test GET route with URL-encoded JSON in query parameter."""
    app = Crimsy()
    router = Router(prefix="/api")

    @router.get("/greet")
    async def greet(user: User) -> dict[str, str]:
        """Greet a user."""
        return {"message": f"Hello, {user.name}!"}

    app.add_router(router)

    client = TestClient(app)

    # The TestClient should handle URL encoding
    import urllib.parse

    user_json = '{"name":"Charlie","age":35}'
    encoded_user = urllib.parse.quote(user_json)

    response = client.get(f"/api/greet?user={encoded_user}")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello, Charlie!"
