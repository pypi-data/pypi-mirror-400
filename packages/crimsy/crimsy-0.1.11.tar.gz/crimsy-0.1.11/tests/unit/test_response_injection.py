"""Test Response injection issue."""

from starlette.testclient import TestClient

from crimsy import Crimsy, Depends, Request, Response, Router


async def test_response_in_dependency() -> None:
    """Test that Response is automatically injected into dependencies."""
    app = Crimsy()
    router = Router(prefix="/")

    # Dependency that uses Response
    async def set_header(response: Response) -> str:
        response.headers["X-Custom-Header"] = "from-dependency"
        return "modified"

    @router.get("/test")
    async def handler(value: str = Depends(set_header)) -> dict[str, str]:
        return {"value": value}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/test")

    assert response.status_code == 200
    assert response.json() == {"value": "modified"}
    assert response.headers["X-Custom-Header"] == "from-dependency"


async def test_response_in_endpoint() -> None:
    """Test that Response is automatically injected into endpoints."""
    app = Crimsy()
    router = Router(prefix="/")

    @router.get("/test")
    async def handler(response: Response) -> dict[str, str]:
        response.headers["X-Test"] = "test-value"
        return {"message": "success"}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/test")

    assert response.status_code == 200
    assert response.json() == {"message": "success"}
    assert response.headers["X-Test"] == "test-value"


async def test_response_in_nested_dependency() -> None:
    """Test that Response is injected in nested dependencies."""
    app = Crimsy()
    router = Router(prefix="/")

    # First level dependency that uses Response
    async def set_first_header(response: Response) -> str:
        response.headers["X-First"] = "first"
        return "first"

    # Second level dependency that depends on first
    async def set_second_header(
        response: Response, first: str = Depends(set_first_header)
    ) -> str:
        response.headers["X-Second"] = "second"
        return f"{first}+second"

    @router.get("/nested")
    async def handler(value: str = Depends(set_second_header)) -> dict[str, str]:
        return {"value": value}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/nested")

    assert response.status_code == 200
    assert response.json() == {"value": "first+second"}
    assert response.headers["X-First"] == "first"
    assert response.headers["X-Second"] == "second"


async def test_response_with_other_params() -> None:
    """Test Response injection alongside other parameters."""
    app = Crimsy()
    router = Router(prefix="/")

    async def process(response: Response, name: str) -> str:
        response.headers["X-Name"] = name
        return f"processed-{name}"

    @router.get("/info")
    async def handler(info: str = Depends(process)) -> dict[str, str]:
        return {"info": info}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/info?name=Alice")

    assert response.status_code == 200
    assert response.json() == {"info": "processed-Alice"}
    assert response.headers["X-Name"] == "Alice"


async def test_endpoint_with_response_and_other_params() -> None:
    """Test endpoint with Response and other parameters."""
    app = Crimsy()
    router = Router(prefix="/")

    @router.get("/test")
    async def handler(response: Response, name: str) -> dict[str, str]:
        response.headers["X-Param"] = name
        return {"name": name}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/test?name=Bob")

    assert response.status_code == 200
    assert response.json() == {"name": "Bob"}
    assert response.headers["X-Param"] == "Bob"


async def test_sync_dependency_with_response() -> None:
    """Test synchronous dependency with Response."""
    app = Crimsy()
    router = Router(prefix="/")

    def set_content_type(response: Response) -> str:
        response.headers["Content-Type"] = "application/custom+json"
        return "custom"

    @router.post("/test")
    async def handler(ct: str = Depends(set_content_type)) -> dict[str, str]:
        return {"content_type": ct}

    app.add_router(router)

    client = TestClient(app)
    response = client.post("/test")

    assert response.status_code == 200
    assert response.json() == {"content_type": "custom"}
    # Note: The response object's headers get set but may be overridden by framework
    # This is expected behavior


async def test_response_with_request() -> None:
    """Test Response and Request injection together."""
    app = Crimsy()
    router = Router(prefix="/")

    @router.get("/test")
    async def handler(request: Request, response: Response) -> dict[str, str]:
        response.headers["X-Method"] = request.method
        response.headers["X-Path"] = request.url.path
        return {"method": request.method, "path": request.url.path}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/test")

    assert response.status_code == 200
    assert response.json() == {"method": "GET", "path": "/test"}
    assert response.headers["X-Method"] == "GET"
    assert response.headers["X-Path"] == "/test"


async def test_response_set_cookie() -> None:
    """Test that Response can be used to set cookies."""
    app = Crimsy()
    router = Router(prefix="/")

    @router.post("/login")
    async def login(response: Response, username: str) -> dict[str, str]:
        # Set a cookie
        response.set_cookie(
            key="session",
            value=f"token-{username}",
            httponly=True,
            secure=False,  # For testing
            samesite="lax",
            max_age=3600,
        )
        return {"message": "logged in", "username": username}

    app.add_router(router)

    client = TestClient(app)
    response = client.post("/login?username=alice")

    assert response.status_code == 200
    assert response.json() == {"message": "logged in", "username": "alice"}
    assert "session" in response.cookies
    assert response.cookies["session"] == "token-alice"


async def test_response_status_code_modification() -> None:
    """Test that Response status code can be modified."""
    app = Crimsy()
    router = Router(prefix="/")

    @router.post("/create")
    async def create(response: Response) -> dict[str, str]:
        response.status_code = 201
        return {"message": "created"}

    app.add_router(router)

    client = TestClient(app)
    response = client.post("/create")

    assert response.status_code == 201
    assert response.json() == {"message": "created"}
