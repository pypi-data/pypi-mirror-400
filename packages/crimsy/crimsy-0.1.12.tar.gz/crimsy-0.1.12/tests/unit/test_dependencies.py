"""Tests for dependency injection system."""

import typing

import msgspec
from starlette.testclient import TestClient

from crimsy import Crimsy, Depends, HTTPException, Router


async def test_simple_dependency() -> None:
    """Test basic dependency injection."""
    app = Crimsy()
    router = Router(prefix="/")

    async def get_value() -> int:
        return 42

    @router.get("/")
    async def handler(value: int = Depends(get_value)) -> dict[str, int]:
        return {"value": value}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"value": 42}


async def test_dependency_with_params() -> None:
    """Test dependency that has its own parameters."""
    app = Crimsy()
    router = Router(prefix="/api")

    async def get_multiplier(factor: int = 2) -> int:
        return factor

    @router.get("/multiply")
    async def handler(
        value: int,
        multiplier: int = Depends(get_multiplier),
    ) -> dict[str, int]:
        return {"result": value * multiplier}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/api/multiply?value=5&factor=3")

    assert response.status_code == 200
    assert response.json() == {"result": 15}


async def test_http_exception_in_endpoint() -> None:
    """Test HTTPException raised in an endpoint."""
    app = Crimsy()
    router = Router(prefix="/")

    @router.get("/users/{user_id}")
    async def get_user(user_id: int) -> dict[str, int]:
        if user_id == 999:
            raise HTTPException(status_code=404, message="User not found")
        return {"user_id": user_id}

    app.add_router(router)

    client = TestClient(app)

    # Test successful case
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json() == {"user_id": 1}

    # Test HTTPException case
    response = client.get("/users/999")
    assert response.status_code == 404
    assert response.json() == {"error": "User not found"}


async def test_http_exception_in_dependency() -> None:
    """Test HTTPException raised in a dependency."""
    app = Crimsy()
    router = Router(prefix="/")

    async def get_repo(repo_id: int) -> int:
        if repo_id == 404:
            raise HTTPException(status_code=404, message="Repository not found")
        return repo_id

    @router.get("/repos")
    async def handler(repo: int = Depends(get_repo)) -> int:
        return repo

    app.add_router(router)

    client = TestClient(app)

    # Test successful case
    response = client.get("/repos?repo_id=1")
    assert response.status_code == 200
    assert response.json() == 1

    # Test HTTPException case
    response = client.get("/repos?repo_id=404")
    assert response.status_code == 404
    assert response.json() == {"error": "Repository not found"}


async def test_http_exception_without_message() -> None:
    """Test HTTPException without a message."""
    app = Crimsy()
    router = Router(prefix="/")

    @router.get("/unauthorized")
    async def handler() -> dict[str, str]:
        raise HTTPException(status_code=401)

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/unauthorized")

    assert response.status_code == 401
    # Empty message should return empty object
    assert response.json() == {}


async def test_custom_exception_handler() -> None:
    """Test custom exception handler."""
    app = Crimsy()

    class CustomException(Exception):
        """Custom exception."""

        pass

    @app.exception_handler(CustomException)
    async def custom_handler(request: typing.Any, exc: typing.Any) -> None:
        raise HTTPException(status_code=503, message="Service unavailable")

    router = Router(prefix="/")

    @router.get("/")
    async def handler() -> dict[str, str]:
        raise CustomException("Something went wrong")

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 503
    assert response.json() == {"error": "Service unavailable"}


async def test_nested_dependencies() -> None:
    """Test nested dependency injection."""
    app = Crimsy()
    router = Router(prefix="/")

    async def get_base() -> int:
        return 10

    async def get_multiplier(base: int = Depends(get_base)) -> int:
        return base * 2

    @router.get("/")
    async def handler(result: int = Depends(get_multiplier)) -> dict[str, int]:
        return {"result": result}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"result": 20}


async def test_multiple_dependencies() -> None:
    """Test multiple dependencies in a single endpoint."""
    app = Crimsy()
    router = Router(prefix="/")

    async def get_value1() -> int:
        return 10

    async def get_value2() -> int:
        return 20

    @router.get("/")
    async def handler(
        v1: int = Depends(get_value1),
        v2: int = Depends(get_value2),
    ) -> dict[str, int]:
        return {"sum": v1 + v2}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"sum": 30}


async def test_dependency_with_struct() -> None:
    """Test dependency returning a msgspec.Struct."""
    app = Crimsy()
    router = Router(prefix="/")

    class User(msgspec.Struct):
        name: str
        age: int

    async def get_user() -> User:
        return User(name="Alice", age=30)

    @router.get("/")
    async def handler(user: User = Depends(get_user)) -> User:
        return user

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alice"
    assert data["age"] == 30


async def test_sync_dependency() -> None:
    """Test synchronous dependency function."""
    app = Crimsy()
    router = Router(prefix="/")

    def get_value() -> int:
        return 100

    @router.get("/")
    async def handler(value: int = Depends(get_value)) -> dict[str, int]:
        return {"value": value}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"value": 100}


async def test_http_exception_repr() -> None:
    """Test HTTPException __repr__ method."""
    exc = HTTPException(status_code=404, message="Not found")
    assert repr(exc) == "HTTPException(status_code=404, message='Not found')"

    exc_no_msg = HTTPException(status_code=500)
    assert repr(exc_no_msg) == "HTTPException(status_code=500, message='')"
