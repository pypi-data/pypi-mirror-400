"""Tests for Security dependency injection system."""

import msgspec
from starlette.testclient import TestClient

from crimsy import Crimsy, Depends, HTTPException, Router, Security


async def test_simple_security() -> None:
    """Test basic security dependency injection."""
    app = Crimsy()
    router = Router(prefix="/")

    async def verify_token(token: str = "") -> str:
        if token != "valid-token":
            raise HTTPException(status_code=401, message="Invalid token")
        return token

    @router.get("/")
    async def handler(token: str = Security(verify_token)) -> dict[str, str]:
        return {"token": token}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/?token=valid-token")

    assert response.status_code == 200
    assert response.json() == {"token": "valid-token"}


async def test_security_with_invalid_token() -> None:
    """Test security dependency with invalid credentials."""
    app = Crimsy()
    router = Router(prefix="/")

    async def verify_token(token: str = "") -> str:
        if token != "valid-token":
            raise HTTPException(status_code=401, message="Unauthorized")
        return token

    @router.get("/secure")
    async def handler(token: str = Security(verify_token)) -> dict[str, str]:
        return {"data": "secure"}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/secure?token=invalid")

    assert response.status_code == 401
    assert response.json() == {"error": "Unauthorized"}


async def test_security_with_user_object() -> None:
    """Test security dependency returning a user object."""
    app = Crimsy()
    router = Router(prefix="/")

    class User(msgspec.Struct):
        id: int
        name: str

    async def get_current_user(user_id: int = 1) -> User:
        if user_id == 0:
            raise HTTPException(status_code=403, message="Forbidden")
        return User(id=user_id, name=f"User{user_id}")

    @router.get("/profile")
    async def get_profile(user: User = Security(get_current_user)) -> User:
        return user

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/profile?user_id=42")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 42
    assert data["name"] == "User42"


async def test_security_openapi_schema() -> None:
    """Test that Security with plain function does NOT add security to OpenAPI.

    This matches FastAPI's behavior where Security() with a plain function
    (not a security scheme object) behaves like Depends() - parameters appear
    in OpenAPI but no security requirements are added.
    """
    app = Crimsy()
    router = Router(prefix="/api")

    async def verify_token(token: str = "") -> str:
        return token

    @router.get("/secure")
    async def handler(name: str, user: str = Security(verify_token)) -> dict[str, str]:
        """Secure endpoint requiring authentication."""
        return {"name": name, "user": user}

    app.add_router(router)

    client = TestClient(app)

    # Get OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    # Check that the endpoint is documented
    assert "/api/secure" in schema["paths"]
    endpoint = schema["paths"]["/api/secure"]["get"]

    # Check that 'name' parameter appears and 'token' from security function also appears
    assert "parameters" in endpoint
    param_names = [p["name"] for p in endpoint["parameters"]]
    assert "name" in param_names
    # The 'token' parameter from verify_token function should appear as it's needed
    assert "token" in param_names
    # But 'user' (the handler's parameter name for the security dependency) should NOT appear
    assert "user" not in param_names

    # Security() with plain function does NOT add security requirements (matches FastAPI)
    assert "security" not in endpoint

    # No security schemes should be added for plain functions (matches FastAPI)
    if "components" in schema and "securitySchemes" in schema["components"]:
        assert "verify_token" not in schema["components"]["securitySchemes"]


async def test_security_with_custom_scheme_name() -> None:
    """Test that Security with plain function does NOT add security to OpenAPI.

    Even with a custom scheme_name, Security() with a plain function should
    not add security requirements to OpenAPI (matches FastAPI behavior).
    """
    app = Crimsy()
    router = Router(prefix="/")

    async def verify_api_key(api_key: str = "") -> str:
        if api_key != "secret":
            raise HTTPException(status_code=403, message="Invalid API key")
        return api_key

    @router.get("/data")
    async def handler(
        key: str = Security(verify_api_key, scheme_name="ApiKeyAuth"),
    ) -> dict[str, str]:
        """Endpoint with custom security scheme name."""
        return {"data": "secure"}

    app.add_router(router)

    client = TestClient(app)

    # Get OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    endpoint = schema["paths"]["/data"]["get"]

    # Security() with plain function does NOT add security requirements (matches FastAPI)
    assert "security" not in endpoint

    # No security schemes should be added for plain functions (matches FastAPI)
    if "components" in schema and "securitySchemes" in schema["components"]:
        assert "ApiKeyAuth" not in schema["components"]["securitySchemes"]


async def test_multiple_security_dependencies() -> None:
    """Test multiple Security() dependencies with plain functions.

    Security() with plain functions does NOT add security requirements to OpenAPI
    (matches FastAPI behavior). Parameters from the security functions are still
    visible in the OpenAPI schema.
    """
    app = Crimsy()
    router = Router(prefix="/")

    async def verify_token(token: str = "") -> str:
        return token

    async def verify_scope(scope: str = "") -> str:
        return scope

    @router.get("/admin")
    async def handler(
        token: str = Security(verify_token),
        scope: str = Security(verify_scope),
    ) -> dict[str, str]:
        return {"token": token, "scope": scope}

    app.add_router(router)

    client = TestClient(app)

    # Get OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    endpoint = schema["paths"]["/admin"]["get"]

    # Security() with plain functions does NOT add security requirements (matches FastAPI)
    assert "security" not in endpoint

    # But parameters from the security functions should be visible
    assert "parameters" in endpoint
    param_names = [p["name"] for p in endpoint["parameters"]]
    assert "token" in param_names
    assert "scope" in param_names

    # No security schemes should be added for plain functions (matches FastAPI)
    if "components" in schema and "securitySchemes" in schema["components"]:
        assert "verify_token" not in schema["components"]["securitySchemes"]
        assert "verify_scope" not in schema["components"]["securitySchemes"]


async def test_security_with_nested_dependencies() -> None:
    """Test security dependency with nested dependencies."""
    app = Crimsy()
    router = Router(prefix="/")

    async def get_db_connection() -> str:
        return "db_connection"

    async def get_current_user(db: str = Security(get_db_connection)) -> dict[str, str]:
        return {"user": "admin", "db": db}

    @router.get("/users")
    async def handler(
        user: dict[str, str] = Security(get_current_user),
    ) -> dict[str, str]:
        return user

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/users")

    assert response.status_code == 200
    data = response.json()
    assert data["user"] == "admin"
    assert data["db"] == "db_connection"


async def test_security_repr() -> None:
    """Test Security __repr__ method."""
    from crimsy.dependencies import _SecurityClass

    async def verify_token() -> str:
        return "token"

    security = _SecurityClass(verify_token)
    assert repr(security) == "Security(verify_token)"


async def test_sync_security_dependency() -> None:
    """Test synchronous security dependency function."""
    app = Crimsy()
    router = Router(prefix="/")

    def verify_api_key(api_key: str = "default") -> str:
        return api_key

    @router.get("/")
    async def handler(key: str = Security(verify_api_key)) -> dict[str, str]:
        return {"key": key}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/?api_key=test-key")

    assert response.status_code == 200
    assert response.json() == {"key": "test-key"}


async def test_security_parameters_in_openapi() -> None:
    """Test that security dependency parameters appear in OpenAPI schema.

    This tests that parameters of security dependencies (like 'name' in
    some_security(name: str)) show up in the OpenAPI docs, even though
    Security() with plain functions does not add security requirements
    (matching FastAPI behavior).
    """
    app = Crimsy()
    router = Router("/users")

    async def some_security(name: str) -> int:
        return 1

    @router.get("/")
    async def index(sec: int = Security(some_security)) -> dict[str, int]:
        return {"sec": sec}

    app.add_router(router)

    client = TestClient(app)

    # Get OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    # Check that the endpoint is documented
    assert "/users/" in schema["paths"]
    endpoint = schema["paths"]["/users/"]["get"]

    # Check that 'name' parameter from security function appears
    assert "parameters" in endpoint
    param_names = [p["name"] for p in endpoint["parameters"]]
    assert "name" in param_names

    # Security() with plain function does NOT add security requirements (matches FastAPI)
    assert "security" not in endpoint

    # No security schemes should be added for plain functions (matches FastAPI)
    if "components" in schema and "securitySchemes" in schema["components"]:
        assert "some_security" not in schema["components"]["securitySchemes"]


async def test_nested_security_via_depends() -> None:
    """Test that nested security dependencies via Depends() are detected.

    This tests that using Depends(security_proxy) where security_proxy itself
    uses Security() with a plain function does not add security requirements
    to OpenAPI (matching FastAPI behavior).
    """
    app = Crimsy()
    router = Router("/users")

    async def some_security(name: str) -> int:
        return 1

    async def security_proxy(val: int = Security(some_security)) -> int:
        return val

    @router.get("/help")
    async def help(sec: int = Depends(security_proxy)) -> dict[str, int]:
        return {"sec": sec}

    app.add_router(router)

    client = TestClient(app)

    # Get OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    # Check that the endpoint is documented
    assert "/users/help" in schema["paths"]
    endpoint = schema["paths"]["/users/help"]["get"]

    # Security() with plain function does NOT add security requirements (matches FastAPI)
    assert "security" not in endpoint

    # Check that 'name' parameter from nested security function appears
    assert "parameters" in endpoint
    param_names = [p["name"] for p in endpoint["parameters"]]
    assert "name" in param_names

    # No security schemes should be added for plain functions (matches FastAPI)
    if "components" in schema and "securitySchemes" in schema["components"]:
        assert "some_security" not in schema["components"]["securitySchemes"]
