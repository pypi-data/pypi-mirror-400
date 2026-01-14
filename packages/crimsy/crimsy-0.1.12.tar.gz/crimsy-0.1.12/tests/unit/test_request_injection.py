"""Test Request injection issue."""

from starlette.testclient import TestClient

from crimsy import Crimsy, Depends, Request, Router


async def test_request_in_dependency() -> None:
    """Test that Request is automatically injected into dependencies."""
    app = Crimsy()
    router = Router(prefix="/")

    # Dependency that uses Request
    async def get_value(request: Request) -> str:
        # Access some property from the request
        return f"path:{request.url.path}"

    @router.get("/test")
    async def handler(value: str = Depends(get_value)) -> dict[str, str]:
        return {"value": value}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/test")

    assert response.status_code == 200
    assert response.json() == {"value": "path:/test"}


async def test_request_in_endpoint() -> None:
    """Test that Request is automatically injected into endpoints."""
    app = Crimsy()
    router = Router(prefix="/")

    @router.get("/test")
    async def handler(request: Request) -> dict[str, str]:
        return {"path": request.url.path}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/test")

    assert response.status_code == 200
    assert response.json() == {"path": "/test"}


async def test_request_in_nested_dependency() -> None:
    """Test that Request is injected in nested dependencies."""
    app = Crimsy()
    router = Router(prefix="/")

    # First level dependency that uses Request
    async def get_base(request: Request) -> str:
        return request.url.path

    # Second level dependency that depends on first
    async def get_value(base: str = Depends(get_base)) -> str:
        return f"base:{base}"

    @router.get("/nested")
    async def handler(value: str = Depends(get_value)) -> dict[str, str]:
        return {"value": value}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/nested")

    assert response.status_code == 200
    assert response.json() == {"value": "base:/nested"}


async def test_request_with_other_params() -> None:
    """Test Request injection alongside other parameters."""
    app = Crimsy()
    router = Router(prefix="/")

    async def get_info(request: Request, name: str) -> str:
        return f"{name}@{request.url.path}"

    @router.get("/info")
    async def handler(info: str = Depends(get_info)) -> dict[str, str]:
        return {"info": info}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/info?name=Alice")

    assert response.status_code == 200
    assert response.json() == {"info": "Alice@/info"}


async def test_endpoint_with_request_and_other_params() -> None:
    """Test endpoint with Request and other parameters."""
    app = Crimsy()
    router = Router(prefix="/")

    @router.get("/test")
    async def handler(request: Request, name: str) -> dict[str, str]:
        return {"path": request.url.path, "name": name}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/test?name=Bob")

    assert response.status_code == 200
    assert response.json() == {"path": "/test", "name": "Bob"}


async def test_sync_dependency_with_request() -> None:
    """Test synchronous dependency with Request."""
    app = Crimsy()
    router = Router(prefix="/")

    def get_method(request: Request) -> str:
        return request.method

    @router.post("/test")
    async def handler(method: str = Depends(get_method)) -> dict[str, str]:
        return {"method": method}

    app.add_router(router)

    client = TestClient(app)
    response = client.post("/test")

    assert response.status_code == 200
    assert response.json() == {"method": "POST"}
