"""Test the exact example from the issue."""

import msgspec
from starlette.testclient import TestClient

from crimsy import Crimsy, Depends, Request, Router


class Session:
    """Mock session class."""

    def __init__(self, engine: str) -> None:
        """Initialize session."""
        self.engine = engine


class UserRepository:
    """Mock user repository."""

    def __init__(self, session: Session) -> None:
        """Initialize repository."""
        self.session = session


class UserService:
    """Mock user service."""

    def __init__(self, user_repository: UserRepository) -> None:
        """Initialize service."""
        self.user_repository = user_repository


class UserCreate(msgspec.Struct):
    """User creation data."""

    username: str


class UserResponse(msgspec.Struct):
    """User response data."""

    id: int
    username: str


async def test_issue_example_with_session() -> None:
    """Test the exact example from the issue."""
    app = Crimsy()
    app.state.engine = "test-engine"

    router = Router(prefix="/")

    async def get_session(request: Request) -> Session:
        engine = request.app.state.engine
        return Session(engine)

    async def get_user_repository(
        session: Session = Depends(get_session),
    ) -> UserRepository:
        return UserRepository(session)

    async def get_user_service(
        user_repository: UserRepository = Depends(get_user_repository),
    ) -> UserService:
        return UserService(user_repository)

    @router.post("/register")
    async def register(
        user_data: UserCreate, user_service: UserService = Depends(get_user_service)
    ) -> UserResponse:
        """Register a new user."""
        # Mock implementation
        return UserResponse(
            id=1,
            username=user_data.username,
        )

    app.add_router(router)

    client = TestClient(app)

    # Test the endpoint
    response = client.post("/register", json={"username": "testuser"})

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "testuser"


async def test_request_not_in_openapi() -> None:
    """Test that Request parameters don't appear in OpenAPI schema."""
    app = Crimsy()
    router = Router(prefix="/api")

    @router.get("/test")
    async def handler(request: Request, name: str) -> dict[str, str]:
        """Endpoint with Request and other parameters."""
        return {"path": request.url.path, "name": name}

    app.add_router(router)

    client = TestClient(app)

    # Get OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    # Check that the endpoint is documented
    assert "/api/test" in schema["paths"]
    endpoint = schema["paths"]["/api/test"]["get"]

    # Check that only 'name' parameter appears, not 'request'
    assert "parameters" in endpoint
    param_names = [p["name"] for p in endpoint["parameters"]]
    assert "name" in param_names
    assert "request" not in param_names
    assert len(param_names) == 1
