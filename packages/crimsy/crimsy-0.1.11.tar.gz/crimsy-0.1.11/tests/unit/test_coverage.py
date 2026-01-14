"""Tests to achieve 100% code coverage."""

import msgspec
from starlette.responses import Response
from starlette.testclient import TestClient

from crimsy import Body, Crimsy, Path, Router


class User(msgspec.Struct):
    """User model for testing."""

    name: str
    age: int = 25


class Item(msgspec.Struct):
    """Item model for testing."""

    title: str
    price: float


async def test_sync_handler() -> None:
    """Test synchronous (non-async) handler function."""
    app = Crimsy()
    router = Router(prefix="/sync")

    @router.get("/")
    def sync_handler(name: str) -> dict[str, str]:  # Not async
        return {"message": f"Hello, {name}!"}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/sync/?name=World")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


async def test_response_return() -> None:
    """Test handler that returns a Starlette Response directly."""
    app = Crimsy()
    router = Router(prefix="/custom")

    @router.get("/")
    async def custom_response() -> Response:
        return Response(content=b"Custom response", media_type="text/plain")

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/custom/")

    assert response.status_code == 200
    assert response.text == "Custom response"


async def test_none_response() -> None:
    """Test handler that returns None (204 No Content)."""
    app = Crimsy()
    router = Router(prefix="/empty")

    @router.delete("/{item_id}")
    async def delete_item(item_id: int = Path()) -> None:
        return None

    app.add_router(router)

    client = TestClient(app)
    response = client.delete("/empty/123")

    assert response.status_code == 204


async def test_generic_exception_handling() -> None:
    """Test that generic exceptions return 500 status code."""
    app = Crimsy()
    router = Router(prefix="/error")

    @router.get("/")
    async def raise_error() -> dict[str, str]:
        raise RuntimeError("Something went wrong")

    app.add_router(router)

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/error/")

    assert response.status_code == 500
    assert "error" in response.json()


async def test_head_and_options_routes() -> None:
    """Test HEAD and OPTIONS HTTP methods."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.head("/")
    async def head_handler() -> dict[str, str]:
        return {"method": "HEAD"}

    @router.options("/")
    async def options_handler() -> dict[str, str]:
        return {"method": "OPTIONS"}

    app.add_router(router)

    client = TestClient(app)

    head_response = client.head("/test/")
    assert head_response.status_code == 200

    options_response = client.options("/test/")
    assert options_response.status_code == 200
    assert options_response.json() == {"method": "OPTIONS"}


async def test_handler_without_docstring() -> None:
    """Test handler without docstring for OpenAPI generation."""
    app = Crimsy()
    router = Router(prefix="/nodoc")

    @router.get("/")
    async def no_doc_handler(name: str) -> dict[str, str]:
        # No docstring
        return {"name": name}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/nodoc/?name=test")
    assert response.status_code == 200


async def test_path_parameters() -> None:
    """Test path parameter extraction and OpenAPI generation."""
    app = Crimsy()
    router = Router(prefix="/items")

    @router.get("/{item_id}")
    async def get_item(item_id: int = Path()) -> dict[str, int]:
        """Get an item by ID."""
        return {"item_id": item_id}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/items/456")
    assert response.status_code == 200
    assert response.json() == {"item_id": 456}

    # Check OpenAPI includes path parameter
    openapi_response = client.get("/openapi.json")
    schema = openapi_response.json()
    assert "/items/{item_id}" in schema["paths"]


async def test_missing_path_parameter() -> None:
    """Test error when required path parameter is missing."""
    app = Crimsy()
    router = Router(prefix="/items")

    @router.get("/{item_id}")
    async def get_item(item_id: int = Path()) -> dict[str, int]:
        return {"item_id": item_id}

    app.add_router(router)

    # This would actually be handled by Starlette routing,
    # but we test the parameter extraction logic
    client = TestClient(app)
    response = client.get("/items/abc")  # Invalid int
    assert response.status_code == 400


async def test_invalid_json_in_query_param() -> None:
    """Test invalid JSON for msgspec.Struct in query parameter."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/")
    async def handler(user: User) -> User:
        return user

    app.add_router(router)

    client = TestClient(app)
    # Invalid JSON
    response = client.get("/test/?user=not_valid_json")
    assert response.status_code == 400
    assert "error" in response.json()


async def test_missing_required_body_parameter() -> None:
    """Test missing required body parameter."""
    app = Crimsy()
    router = Router(prefix="/users")

    @router.post("/")
    async def create_user(user: User = Body()) -> User:
        return user

    app.add_router(router)

    client = TestClient(app)
    # Empty body
    response = client.post("/users/", json=None)
    assert response.status_code == 400


async def test_body_parameter_with_default() -> None:
    """Test body parameter with default value."""
    app = Crimsy()
    router = Router(prefix="/test")

    default_user = User(name="Default", age=0)

    @router.post("/")
    async def handler(user: User = Body(default=default_user)) -> User:
        return user

    app.add_router(router)

    client = TestClient(app)
    # Empty body should use default
    response = client.post("/test/", content=b"")
    assert response.status_code == 200
    assert response.json()["name"] == "Default"


async def test_invalid_body_json() -> None:
    """Test invalid JSON in request body."""
    app = Crimsy()
    router = Router(prefix="/users")

    @router.post("/")
    async def create_user(user: User = Body()) -> User:
        return user

    app.add_router(router)

    client = TestClient(app)
    # Invalid JSON
    response = client.post(
        "/users/",
        content=b"not valid json",
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 400


async def test_non_struct_body_parameter() -> None:
    """Test non-msgspec.Struct body parameter."""
    app = Crimsy()
    router = Router(prefix="/data")

    @router.post("/")
    async def process_data(data: dict[str, str] = Body()) -> dict[str, str]:
        return {"received": str(data)}

    app.add_router(router)

    client = TestClient(app)
    response = client.post("/data/", json={"key": "value"})
    assert response.status_code == 200


async def test_parameter_without_annotation() -> None:
    """Test parameter without type annotation."""
    from crimsy.params import analyze_function_params

    # Create a function with no type annotation
    def handler(value):  # type: ignore[no-untyped-def]
        return {"value": str(value)}

    # Analyze it - should default to str
    params = analyze_function_params(handler, "GET")
    assert len(params) == 1
    assert params[0].annotation is str  # Should default to str


async def test_invalid_int_query_param() -> None:
    """Test invalid integer value in query parameter."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/")
    async def handler(count: int) -> dict[str, int]:
        return {"count": count}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/test/?count=not_a_number")
    assert response.status_code == 400


async def test_invalid_float_query_param() -> None:
    """Test invalid float value in query parameter."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/")
    async def handler(price: float) -> dict[str, float]:
        return {"price": price}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/test/?price=not_a_float")
    assert response.status_code == 400


async def test_bool_query_param() -> None:
    """Test boolean query parameter conversion."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/")
    async def handler(active: bool) -> dict[str, bool]:
        return {"active": active}

    app.add_router(router)

    client = TestClient(app)

    # Test various true values
    for value in ["true", "True", "1", "yes"]:
        response = client.get(f"/test/?active={value}")
        assert response.status_code == 200
        assert response.json()["active"] is True

    # Test false value
    response = client.get("/test/?active=false")
    assert response.status_code == 200
    assert response.json()["active"] is False


async def test_complex_type_query_param() -> None:
    """Test complex type in query parameter (decoded as JSON)."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/")
    async def handler(data: list[str]) -> dict[str, list[str]]:
        return {"data": data}

    app.add_router(router)

    client = TestClient(app)
    import json

    data_json = json.dumps(["a", "b", "c"])
    response = client.get(f"/test/?data={data_json}")
    assert response.status_code == 200
    assert response.json()["data"] == ["a", "b", "c"]


async def test_invalid_complex_type_query_param() -> None:
    """Test invalid JSON for complex type in query parameter."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/")
    async def handler(data: list[str]) -> dict[str, list[str]]:
        return {"data": data}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/test/?data=not_valid_json")
    assert response.status_code == 400


async def test_openapi_with_various_types() -> None:
    """Test OpenAPI schema generation with various parameter types."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/types")
    async def handler(
        text: str,
        number: int,
        decimal: float,
        flag: bool,
        items: list[str],
        data: dict[str, str],
    ) -> dict[str, str]:
        """Handler with various types."""
        return {"status": "ok"}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/openapi.json")
    schema = response.json()

    # Check that all parameter types are documented
    params = schema["paths"]["/test/types"]["get"]["parameters"]
    param_names = [p["name"] for p in params]
    assert "text" in param_names
    assert "number" in param_names
    assert "decimal" in param_names
    assert "flag" in param_names


async def test_openapi_with_generic_list() -> None:
    """Test OpenAPI schema generation with generic list type."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/")
    async def handler() -> list[Item]:
        """Return a list of items."""
        return [Item(title="Test", price=10.0)]

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/openapi.json")
    schema = response.json()

    # Check response schema
    assert "/test/" in schema["paths"]


async def test_openapi_with_plain_list() -> None:
    """Test OpenAPI schema generation with plain list type."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/")
    async def handler() -> list[int]:  #
        """Return a plain list."""
        return [1, 2, 3]

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/openapi.json")
    schema = response.json()

    # Check that it generates schema
    assert "/test/" in schema["paths"]


async def test_openapi_with_dict_type() -> None:
    """Test OpenAPI schema generation with dict type."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/")
    async def handler() -> dict[str, int]:
        """Return a dict."""
        return {"count": 5}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/openapi.json")
    schema = response.json()

    # Check that it generates schema
    assert "/test/" in schema["paths"]


async def test_param_marker_repr() -> None:
    """Test __repr__ method of parameter markers."""
    from crimsy.params import Query, Body, Path

    # Test without default
    q1 = Query()
    assert repr(q1) == "Query()"

    # Test with default
    q2 = Query(default="test")
    assert repr(q2) == "Query(default='test')"

    b1 = Body()
    assert repr(b1) == "Body()"

    b2 = Body(default={"key": "value"})
    assert repr(b2) == "Body(default={'key': 'value'})"

    p1 = Path()
    assert repr(p1) == "Path()"

    p2 = Path(default=0)
    assert repr(p2) == "Path(default=0)"


async def test_is_msgspec_struct_with_non_type() -> None:
    """Test is_msgspec_struct with non-type values."""
    from crimsy.params import is_msgspec_struct

    # Test with non-type value
    assert is_msgspec_struct("not a type") is False  # type: ignore[arg-type]
    assert is_msgspec_struct(123) is False  # type: ignore[arg-type]
    assert is_msgspec_struct(None) is False  # type: ignore[arg-type]

    # Test with actual struct
    assert is_msgspec_struct(User) is True


async def test_class_method_parameters_skipped() -> None:
    """Test that self and cls parameters are skipped in analysis."""
    from crimsy.params import analyze_function_params

    class Handler:
        def method(self, name: str) -> dict[str, str]:
            return {"name": name}

    # Analyze the method - 'self' should be skipped
    params = analyze_function_params(Handler.method, "GET")
    # Should only have 'name' parameter, not 'self'
    param_names = [p.name for p in params]
    assert "self" not in param_names
    assert "name" in param_names


async def test_openapi_endpoint_without_original_endpoint() -> None:
    """Test OpenAPI generation skips routes without _original_endpoint."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/")
    async def handler() -> dict[str, str]:
        return {"status": "ok"}

    # Manually remove the _original_endpoint attribute
    if router.routes:
        delattr(router.routes[0].endpoint, "_original_endpoint")

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/openapi.json")
    # Should not crash, just skip the route
    assert response.status_code == 200


async def test_openapi_with_any_type() -> None:
    """Test OpenAPI schema generation with Any type."""
    from typing import Any

    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/")
    async def handler() -> Any:
        """Return Any type."""
        return {"anything": "goes"}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/openapi.json")
    schema = response.json()
    # Should generate schema without error
    assert "/test/" in schema["paths"]


async def test_openapi_with_unknown_type() -> None:
    """Test OpenAPI schema generation with unknown type (fallback to string)."""
    app = Crimsy()
    router = Router(prefix="/test")

    class CustomClass:
        pass

    @router.get("/")
    async def handler() -> CustomClass:
        """Return custom class."""
        return CustomClass()

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/openapi.json")
    schema = response.json()
    # Should generate schema with default 'string' type
    assert "/test/" in schema["paths"]


async def test_openapi_with_list_without_args() -> None:
    """Test OpenAPI schema generation with generic list without type args."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/")
    async def handler(items: list[str]) -> dict[str, str]:
        """Handler with plain list parameter."""
        return {"status": "ok"}

    app.add_router(router)

    client = TestClient(app)
    response = client.get("/openapi.json")
    schema = response.json()
    # Should handle list without args
    assert "/test/" in schema["paths"]


async def test_get_request_with_missing_struct_in_query() -> None:
    """Test GET request with msgspec.Struct but missing query parameter."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/")
    async def handler(user: User) -> User:
        return user

    app.add_router(router)

    client = TestClient(app)
    # No user parameter provided - should try to read from body and fail
    response = client.get("/test/")
    assert response.status_code == 400


async def test_path_parameter_with_default() -> None:
    """Test path parameter with default value (edge case)."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/{item_id}")
    async def handler(
        item_id: int = Path(default=0),
    ) -> dict[str, int]:
        return {"item_id": item_id}

    app.add_router(router)

    client = TestClient(app)
    # Normal case with path param
    response = client.get("/test/123")
    assert response.status_code == 200
    assert response.json()["item_id"] == 123


async def test_is_msgspec_struct_typeerror() -> None:
    """Test is_msgspec_struct handles TypeError."""
    from crimsy.params import is_msgspec_struct
    from typing import Union

    # Test with type that causes TypeError in issubclass
    result = is_msgspec_struct(Union[str, int])  # type: ignore[arg-type]
    assert result is False


async def test_get_request_with_invalid_struct_json_in_query() -> None:
    """Test GET request with msgspec.Struct and invalid JSON in query."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/")
    async def handler(user: User) -> User:
        return user

    app.add_router(router)

    client = TestClient(app)
    # Invalid JSON in user query parameter for GET request
    response = client.get("/test/?user={bad json}")
    assert response.status_code == 400
    assert "error" in response.json()


async def test_missing_required_path_parameter_edge_case() -> None:
    """Test extraction logic for missing path parameter."""
    from crimsy.params import ParamInfo, ParamType, extract_params
    from starlette.datastructures import QueryParams
    import inspect

    # Create a mock request
    class MockRequest:
        method = "GET"
        query_params = QueryParams({})

        async def body(self) -> bytes:
            return b""

    # Create param info for required path parameter
    param = ParamInfo(
        name="missing_id",
        annotation=int,
        default=inspect.Parameter.empty,
        param_type=ParamType.PATH,
    )

    request = MockRequest()
    path_params: dict[str, str] = {}  # Empty path params

    # Should raise ValueError for missing required path parameter
    try:
        await extract_params(request, [param], path_params)  # type: ignore[arg-type]
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Missing required path parameter" in str(e)


async def test_path_parameter_with_default_missing() -> None:
    """Test path parameter with default when path param is missing."""
    from crimsy.params import ParamInfo, ParamType, extract_params
    from starlette.datastructures import QueryParams

    # Create a mock request
    class MockRequest:
        method = "GET"
        query_params = QueryParams({})

        async def body(self) -> bytes:
            return b""

    # Create param info for path parameter with default
    param = ParamInfo(
        name="item_id",
        annotation=int,
        default=99,  # Has default
        param_type=ParamType.PATH,
    )

    request = MockRequest()
    path_params: dict[str, str] = {}  # Empty path params

    # Should use default value
    result = await extract_params(request, [param], path_params)  # type: ignore[arg-type]
    assert result["item_id"] == 99


async def test_openapi_generic_list_without_args_edge_case() -> None:
    """Test OpenAPI schema for list type without __args__."""
    from crimsy.openapi import get_type_schema

    # Create a type that has __origin__ as list but no __args__
    class FakeListType:
        __origin__ = list

    result = get_type_schema(FakeListType())  # type: ignore[arg-type]
    # Should return array with empty items
    assert result["type"] == "array"
    assert "items" in result


async def test_is_msgspec_struct_with_generic_causing_typeerror() -> None:
    """Test is_msgspec_struct with type that causes TypeError in issubclass."""
    from crimsy.params import is_msgspec_struct
    from typing import Generic, TypeVar

    T = TypeVar("T")

    class GenericClass(Generic[T]):
        pass

    # This should trigger the TypeError exception handler
    result = is_msgspec_struct(GenericClass[str])
    assert result is False


async def test_get_request_body_struct_with_empty_query() -> None:
    """Test GET request with struct parameter when query param is empty/missing."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/process")
    async def handler(user: User) -> User:
        """Process user data."""
        return user

    app.add_router(router)

    client = TestClient(app)
    # GET request without user in query - should try body and fail
    response = client.get("/test/process")
    assert response.status_code == 400
    assert "error" in response.json()


async def test_get_request_body_struct_query_empty_string() -> None:
    """Test GET request with struct parameter as empty string in query."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/process")
    async def handler(user: User) -> User:
        """Process user data."""
        return user

    app.add_router(router)

    client = TestClient(app)
    # GET request with empty user query param - should skip to body
    response = client.get("/test/process?user=")
    assert response.status_code == 400


async def test_head_request_body_struct() -> None:
    """Test HEAD request with msgspec.Struct parameter."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.head("/check")
    async def handler(user: User) -> User:
        """Check user."""
        return user

    app.add_router(router)

    client = TestClient(app)
    # HEAD request should also try query params for struct
    import json

    user_json = json.dumps({"name": "Alice", "age": 30})
    response = client.head(f"/test/check?user={user_json}")
    assert response.status_code == 200


async def test_options_request_body_struct() -> None:
    """Test OPTIONS request with msgspec.Struct parameter."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.options("/info")
    async def handler(user: User) -> User:
        """Get info."""
        return user

    app.add_router(router)

    client = TestClient(app)
    # OPTIONS request should also try query params for struct
    import json

    user_json = json.dumps({"name": "Bob", "age": 25})
    response = client.options(f"/test/info?user={user_json}")
    assert response.status_code == 200


async def test_openapi_plain_list_type() -> None:
    """Test OpenAPI schema generation with plain list type (not list[T])."""
    from crimsy.openapi import get_type_schema

    # Test with plain list type
    result = get_type_schema(list)
    assert result["type"] == "array"
    assert "items" in result


async def test_is_msgspec_struct_with_union_type() -> None:
    """Test is_msgspec_struct with Union type that causes TypeError."""
    from crimsy.params import is_msgspec_struct
    from typing import Union

    # Union types cause TypeError in issubclass check
    result = is_msgspec_struct(Union[str, int])  # type: ignore[arg-type]
    assert result is False


async def test_get_request_struct_without_query_value() -> None:
    """Test GET request with msgspec.Struct when query param value is missing."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/process")
    async def handler(user: User) -> User:
        """Process user."""
        return user

    app.add_router(router)

    client = TestClient(app)
    # GET request without user query param - should fail looking for body
    response = client.get("/test/process")
    assert response.status_code == 400
    assert "error" in response.json()


async def test_head_request_struct_without_query_value() -> None:
    """Test HEAD request with msgspec.Struct when query param value is missing."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.head("/check")
    async def handler(user: User) -> User:
        """Check user."""
        return user

    app.add_router(router)

    client = TestClient(app)
    # HEAD request without user query param - should fail
    response = client.head("/test/check")
    assert response.status_code == 400


async def test_options_request_struct_without_query_value() -> None:
    """Test OPTIONS request with msgspec.Struct when query param value is missing."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.options("/info")
    async def handler(user: User) -> User:
        """Get info."""
        return user

    app.add_router(router)

    client = TestClient(app)
    # OPTIONS request without user query param - should fail
    response = client.options("/test/info")
    assert response.status_code == 400


async def test_get_struct_query_param_explicit_coverage() -> None:
    """Explicit test to cover GET request with struct in query param - lines 249-257."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/handler")
    async def handler(data: User) -> User:
        """Handler with struct parameter."""
        return data

    app.add_router(router)

    client = TestClient(app)

    # Test with valid JSON in query param
    import json

    user_data = json.dumps({"name": "TestUser", "age": 42})
    response = client.get(f"/test/handler?data={user_data}")

    assert response.status_code == 200
    result = response.json()
    assert result["name"] == "TestUser"
    assert result["age"] == 42


async def test_get_struct_query_param_invalid_json_coverage() -> None:
    """Test GET request with invalid JSON for struct in query param - exception path."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/handler")
    async def handler(data: User) -> User:
        """Handler with struct parameter."""
        return data

    app.add_router(router)

    client = TestClient(app)

    # Test with invalid JSON in query param - should trigger DecodeError exception
    response = client.get("/test/handler?data={invalid json}")

    assert response.status_code == 400
    assert "error" in response.json()


async def test_get_with_body_marker_on_struct() -> None:
    """Test GET request with msgspec.Struct explicitly marked as Body().

    This covers the special case in lines 245-259 where a struct is marked
    as Body but the request is GET/HEAD/OPTIONS, so we try query params first.
    """
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/search")
    async def search(
        user: User = Body(),
    ) -> dict[str, str]:
        """Search with user data from body (or query for GET)."""
        return {"found": user.name}

    app.add_router(router)

    client = TestClient(app)

    # For GET with Body() marker, it should try query param first
    import json

    user_json = json.dumps({"name": "QueryUser", "age": 30})
    response = client.get(f"/test/search?user={user_json}")

    assert response.status_code == 200
    assert response.json()["found"] == "QueryUser"


async def test_get_with_body_marker_invalid_json() -> None:
    """Test GET request with Body() marker and invalid JSON in query param."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.get("/search")
    async def search(
        user: User = Body(),
    ) -> dict[str, str]:
        """Search with user data."""
        return {"found": user.name}

    app.add_router(router)

    client = TestClient(app)

    # Invalid JSON should trigger DecodeError in lines 256-259
    response = client.get("/test/search?user={not valid json}")

    assert response.status_code == 400
    assert "error" in response.json()


async def test_head_with_body_marker_on_struct() -> None:
    """Test HEAD request with Body() marker on struct."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.head("/check")
    async def check(
        user: User = Body(),
    ) -> dict[str, str]:
        """Check user."""
        return {"status": "ok"}

    app.add_router(router)

    client = TestClient(app)

    import json

    user_json = json.dumps({"name": "HeadUser", "age": 25})
    response = client.head(f"/test/check?user={user_json}")

    assert response.status_code == 200


async def test_options_with_body_marker_on_struct() -> None:
    """Test OPTIONS request with Body() marker on struct."""
    app = Crimsy()
    router = Router(prefix="/test")

    @router.options("/info")
    async def info(
        user: User = Body(),
    ) -> dict[str, str]:
        """Get info."""
        return {"info": "data"}

    app.add_router(router)

    client = TestClient(app)

    import json

    user_json = json.dumps({"name": "OptionsUser", "age": 20})
    response = client.options(f"/test/info?user={user_json}")

    assert response.status_code == 200


async def test_is_msgspec_struct_typeerror_with_mock() -> None:
    """Test is_msgspec_struct TypeError exception handler using mock."""
    from unittest.mock import patch
    from crimsy.params import is_msgspec_struct

    # Create a type-like object
    class FakeType(type):
        pass

    fake_cls = FakeType("FakeCls", (), {})

    # Mock issubclass to raise TypeError
    with patch("crimsy.params.issubclass", side_effect=TypeError("mock error")):
        result = is_msgspec_struct(fake_cls)
        assert result is False
