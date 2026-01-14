"""Tests for app.state functionality."""

import pytest
from starlette.testclient import TestClient

from crimsy import Crimsy, Request, Router


async def test_app_state_basic() -> None:
    """Test that app.state can be set and accessed."""
    app = Crimsy()

    # Set a value on app.state
    app.state.engine = "test_engine_value"
    app.state.config = {"key": "value"}

    # Verify values can be read back
    assert app.state.engine == "test_engine_value"
    assert app.state.config == {"key": "value"}


async def test_app_state_in_request() -> None:
    """Test that app.state can be accessed via request.app.state in endpoints."""
    app = Crimsy()
    router = Router(prefix="/test")

    # Set state before creating routes
    app.state.engine = "database_engine"
    app.state.api_key = "secret_key_123"

    @router.get("/config")
    async def get_config(request: Request) -> dict[str, str]:
        """Endpoint that accesses app state via request."""
        return {
            "engine": request.app.state.engine,
            "api_key": request.app.state.api_key,
        }

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/test/config")

    assert response.status_code == 200
    data = response.json()
    assert data["engine"] == "database_engine"
    assert data["api_key"] == "secret_key_123"


async def test_app_state_modify_after_routes() -> None:
    """Test that app.state can be modified after routes are added."""
    app = Crimsy()
    router = Router(prefix="/api")

    @router.get("/value")
    async def get_value(request: Request) -> dict[str, int | None]:
        """Return the current state value."""
        return {"value": getattr(request.app.state, "counter", None)}

    app.add_router(router)
    client = TestClient(app)

    # Initial state - attribute doesn't exist yet
    response = client.get("/api/value")
    assert response.status_code == 200
    assert response.json() == {"value": None}

    # Modify state after routes are added
    app.state.counter = 42

    # Verify new value is accessible
    response = client.get("/api/value")
    assert response.status_code == 200
    assert response.json() == {"value": 42}


async def test_app_state_complex_object() -> None:
    """Test storing complex objects in app.state."""

    class MockEngine:
        """Mock database engine for testing."""

        def __init__(self, connection_string: str) -> None:
            self.connection_string = connection_string

        def query(self, sql: str) -> list[dict[str, str]]:
            """Mock query method."""
            return [{"result": "data"}]

    app = Crimsy()
    router = Router(prefix="/db")

    # Store complex object in state
    engine = MockEngine("postgresql://localhost/test")
    app.state.engine = engine

    @router.get("/query")
    async def execute_query(request: Request) -> dict[str, str | list[dict[str, str]]]:
        """Execute a query using the engine from state."""
        engine = request.app.state.engine
        results = engine.query("SELECT * FROM users")
        return {
            "connection": engine.connection_string,
            "results": results,
        }

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/db/query")

    assert response.status_code == 200
    data = response.json()
    assert data["connection"] == "postgresql://localhost/test"
    assert data["results"] == [{"result": "data"}]


async def test_app_state_multiple_attributes() -> None:
    """Test setting multiple attributes on app.state."""
    app = Crimsy()

    # Set multiple attributes
    app.state.db_engine = "engine1"
    app.state.cache = "redis_cache"
    app.state.config = {"debug": True}
    app.state.version = "1.0.0"

    # Verify all attributes
    assert app.state.db_engine == "engine1"
    assert app.state.cache == "redis_cache"
    assert app.state.config == {"debug": True}
    assert app.state.version == "1.0.0"


async def test_app_state_missing_attribute() -> None:
    """Test that accessing non-existent state attribute raises AttributeError."""
    app = Crimsy()

    # Try to access non-existent attribute
    with pytest.raises(AttributeError, match="non_existent"):
        _ = app.state.non_existent
