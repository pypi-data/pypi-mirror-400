"""Tests for Header parameter extraction."""

from starlette.testclient import TestClient

from crimsy import Crimsy, Header, Router, Security


async def test_simple_header_parameter() -> None:
    """Test basic header parameter extraction."""
    app = Crimsy()
    router = Router(prefix="/")

    @router.get("/")
    async def handler(api_key: str = Header()) -> dict[str, str]:
        return {"api_key": api_key}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/", headers={"api-key": "test-key"})

    assert response.status_code == 200
    assert response.json() == {"api_key": "test-key"}


async def test_header_parameter_with_default() -> None:
    """Test header parameter with default value."""
    app = Crimsy()
    router = Router(prefix="/")

    @router.get("/")
    async def handler(x_custom: str = Header(default="unknown")) -> dict[str, str]:
        return {"x_custom": x_custom}

    app.add_router(router)

    client = TestClient(app)

    # Test without header
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"x_custom": "unknown"}

    # Test with header
    response = client.get("/", headers={"x-custom": "my-value"})
    assert response.status_code == 200
    assert response.json() == {"x_custom": "my-value"}


async def test_missing_required_header() -> None:
    """Test that missing required header returns error."""
    app = Crimsy()
    router = Router(prefix="/")

    @router.get("/")
    async def handler(authorization: str = Header()) -> dict[str, str]:
        return {"auth": authorization}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 400
    assert "Missing required header" in response.json()["error"]


async def test_header_in_security_dependency() -> None:
    """Test header parameter in security dependency."""
    app = Crimsy()
    router = Router(prefix="/")

    async def verify_api_key(api_key: str = Header()) -> str:
        if api_key != "secret-key":
            from crimsy import HTTPException

            raise HTTPException(status_code=403, message="Invalid API key")
        return api_key

    @router.get("/secure")
    async def handler(key: str = Security(verify_api_key)) -> dict[str, str]:
        return {"message": "authenticated", "key": key}

    app.add_router(router)

    client = TestClient(app)

    # Test with valid key
    response = client.get("/secure", headers={"api-key": "secret-key"})
    assert response.status_code == 200
    assert response.json() == {"message": "authenticated", "key": "secret-key"}

    # Test with invalid key
    response = client.get("/secure", headers={"api-key": "wrong-key"})
    assert response.status_code == 403

    # Test without key
    response = client.get("/secure")
    assert response.status_code == 400


async def test_header_in_openapi_schema() -> None:
    """Test that Header parameters appear in OpenAPI schema."""
    app = Crimsy()
    router = Router(prefix="/api")

    @router.get("/data")
    async def handler(
        api_key: str = Header(), authorization: str = Header()
    ) -> dict[str, str]:
        """Get data with API key and authorization."""
        return {"data": "secure"}

    app.add_router(router)

    client = TestClient(app)

    # Get OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    # Check that the endpoint is documented
    assert "/api/data" in schema["paths"]
    endpoint = schema["paths"]["/api/data"]["get"]

    # Check that header parameters appear
    assert "parameters" in endpoint
    params = endpoint["parameters"]
    assert len(params) == 2

    # Verify header parameters
    param_names = {p["name"] for p in params}
    assert "api_key" in param_names
    assert "authorization" in param_names

    for param in params:
        assert param["in"] == "header"
        assert param["required"] is True


async def test_header_with_security_in_openapi() -> None:
    """Test that headers in Security dependencies appear in OpenAPI."""
    app = Crimsy()
    router = Router(prefix="/")

    async def verify_token(authorization: str = Header()) -> str:
        return authorization

    @router.get("/secure")
    async def handler(token: str = Security(verify_token)) -> dict[str, str]:
        """Secure endpoint."""
        return {"token": token}

    app.add_router(router)

    client = TestClient(app)

    # Get OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    # Check that the endpoint is documented
    endpoint = schema["paths"]["/secure"]["get"]

    # Check that 'authorization' header parameter appears
    assert "parameters" in endpoint
    param_names = [p["name"] for p in endpoint["parameters"]]
    assert "authorization" in param_names

    # Check that it's documented as a header
    auth_param = next(p for p in endpoint["parameters"] if p["name"] == "authorization")
    assert auth_param["in"] == "header"
    assert auth_param["required"] is True

    # Security() with plain function does NOT add security requirements (matches FastAPI)
    assert "security" not in endpoint


async def test_multiple_header_types() -> None:
    """Test multiple header parameters with different types."""
    app = Crimsy()
    router = Router(prefix="/")

    @router.get("/")
    async def handler(
        x_count: int = Header(default=0),
        x_enabled: bool = Header(default=False),
        x_name: str = Header(default="unknown"),
    ) -> dict[str, str | int | bool]:
        return {"count": x_count, "enabled": x_enabled, "name": x_name}

    app.add_router(router)

    client = TestClient(app)

    # Test with headers
    response = client.get(
        "/", headers={"x-count": "42", "x-enabled": "true", "x-name": "test"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 42
    assert data["enabled"] is True
    assert data["name"] == "test"

    # Test without headers (defaults)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["enabled"] is False
    assert data["name"] == "unknown"


async def test_header_repr() -> None:
    """Test Header __repr__ method."""
    from crimsy.params import _HeaderMarker

    header = _HeaderMarker()
    assert repr(header) == "Header()"

    header_with_default = _HeaderMarker(default="test")
    assert repr(header_with_default) == "Header(default='test')"
