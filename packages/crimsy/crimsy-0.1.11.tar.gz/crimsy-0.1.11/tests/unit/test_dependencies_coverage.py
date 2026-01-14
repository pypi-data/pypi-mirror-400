"""Tests for 100% coverage of dependencies module."""

from crimsy import Depends
from crimsy.dependencies import _DependsClass


async def test_depends_repr() -> None:
    """Test __repr__ method of _DependsClass."""

    async def get_value() -> int:
        return 42

    dep = _DependsClass(get_value)
    assert repr(dep) == "Depends(get_value)"


async def test_dependency_error_case() -> None:
    """Test error case when dependency is None in params."""
    from starlette.testclient import TestClient

    from crimsy import Crimsy, Router
    from crimsy.params import ParamInfo, ParamType, extract_params

    # Create a ParamInfo with dependency type but no dependency
    param = ParamInfo(
        name="test",
        annotation=int,
        default=None,
        param_type=ParamType.DEPENDENCY,
        dependency=None,
    )

    # Create a mock request
    app = Crimsy()
    router = Router(prefix="/")

    @router.get("/test")
    async def test_handler() -> dict[str, str]:
        return {"status": "ok"}

    app.add_router(router)
    client = TestClient(app)

    # Get a real request object
    with client:
        response = client.get("/test")
        # We can't directly test extract_params with a None dependency
        # because it would be caught during parameter analysis,
        # but we verify the error message would be correct
        assert response.status_code == 200

    # Test the error condition directly

    class MockRequest:
        method = "GET"

    try:
        # This should raise ValueError
        await extract_params(MockRequest(), [param], {})  # type: ignore[arg-type]
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Dependency not configured for parameter: test" in str(e)


async def test_async_iterator_dependency() -> None:
    """Test async iterator dependency to cover line 290."""
    import typing

    from starlette.testclient import TestClient

    from crimsy import Crimsy, Router

    async def get_async_value() -> typing.AsyncIterator[int]:
        """Async generator dependency."""
        yield 100

    app = Crimsy()
    router = Router(prefix="/")

    @router.get("/")
    async def handler(value: int = Depends(get_async_value)) -> dict[str, int]:
        return {"value": value}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"value": 100}
