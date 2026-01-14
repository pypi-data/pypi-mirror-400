"""Test OpenAPI generation with dependencies and Request parameters."""

from starlette.testclient import TestClient

from crimsy import Crimsy, Depends, Router


async def test_openapi_with_dependency() -> None:
    """Test that dependencies don't appear in OpenAPI parameters."""
    app = Crimsy()
    router = Router(prefix="/api")

    async def get_value() -> int:
        return 42

    @router.get("/test")
    async def handler(
        name: str, value: int = Depends(get_value)
    ) -> dict[str, int | str]:
        """Endpoint with dependency and regular parameter."""
        return {"name": name, "value": value}

    app.add_router(router)

    client = TestClient(app)

    # Get OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    # Check that the endpoint is documented
    assert "/api/test" in schema["paths"]
    endpoint = schema["paths"]["/api/test"]["get"]

    # Check that only 'name' parameter appears, not 'value' (dependency)
    assert "parameters" in endpoint
    param_names = [p["name"] for p in endpoint["parameters"]]
    assert "name" in param_names
    assert "value" not in param_names  # Dependencies should not appear
    assert len(param_names) == 1
