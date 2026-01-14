"""Router class for grouping endpoints."""

import inspect
from typing import Any, Callable

import msgspec
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from crimsy.params import analyze_function_params, extract_params


class Router:
    """Router for grouping API endpoints."""

    def __init__(self, prefix: str = "", tags: list[str] | None = None) -> None:
        """Initialize a router.

        Args:
            prefix: URL prefix for all routes in this router
            tags: Tags for grouping endpoints in OpenAPI documentation.
                  If not provided and prefix is set, a tag will be derived from the prefix.
        """
        self._prefix = prefix
        # If no tags provided but prefix is set, derive tag from prefix
        if tags is None and prefix:
            # Remove leading/trailing slashes and use as tag
            tag_name = prefix.strip("/")
            # Handle nested paths by taking the first segment
            if "/" in tag_name:
                tag_name = tag_name.split("/")[0]
            self._tags = [tag_name] if tag_name else []
        else:
            self._tags = tags or []
        self.routes: list[Route] = []

    @property
    def prefix(self) -> str:
        """Get the router prefix."""
        return self._prefix

    @property
    def tags(self) -> list[str]:
        """Get the router tags."""
        return self._tags

    def add_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        methods: list[str],
    ) -> None:
        """Add a route to the router.

        Args:
            path: URL path for the route
            endpoint: Handler function
            methods: HTTP methods for the route
        """
        # Convert empty path to "/" to satisfy Starlette's requirement
        if not path:
            path = "/"

        # Analyze function parameters based on primary HTTP method
        primary_method = methods[0] if methods else "GET"
        params = analyze_function_params(endpoint, primary_method, path)

        # Create wrapper that handles parameter extraction and response encoding
        async def route_handler(request: Request) -> Response:
            try:
                # Create a response object for injection
                response = Response()

                # Extract path parameters
                path_params = request.path_params

                # Extract all parameters from request
                kwargs = await extract_params(request, params, path_params, response)

                # Call the endpoint
                if inspect.iscoroutinefunction(endpoint):
                    result = await endpoint(**kwargs)
                else:
                    result = endpoint(**kwargs)

                # Encode response
                if isinstance(result, Response):
                    return result

                # Use msgspec to encode the result
                if result is None:
                    response.status_code = 204
                    return response

                json_bytes = msgspec.json.encode(result)
                response.body = json_bytes
                response.media_type = "application/json"
                # Set headers to match the encoded body
                response.headers["content-type"] = "application/json"
                response.headers["content-length"] = str(len(json_bytes))
                return response

            except ValueError as e:
                # ValueError becomes 400 Bad Request
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=400,
                )
            # Let all other exceptions propagate to Starlette's exception handlers

        route = Route(path, route_handler, methods=methods)
        # Store metadata for OpenAPI generation
        route.endpoint._original_endpoint = endpoint  # type: ignore[attr-defined]
        route.endpoint._params = params  # type: ignore[attr-defined]
        route.endpoint._original_methods = methods  # type: ignore[attr-defined]
        self.routes.append(route)

    def get(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to add a GET route.

        Args:
            path: URL path for the route

        Returns:
            Decorator function
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.add_route(path, func, ["GET"])
            return func

        return decorator

    def post(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to add a POST route.

        Args:
            path: URL path for the route

        Returns:
            Decorator function
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.add_route(path, func, ["POST"])
            return func

        return decorator

    def put(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to add a PUT route.

        Args:
            path: URL path for the route

        Returns:
            Decorator function
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.add_route(path, func, ["PUT"])
            return func

        return decorator

    def delete(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to add a DELETE route.

        Args:
            path: URL path for the route

        Returns:
            Decorator function
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.add_route(path, func, ["DELETE"])
            return func

        return decorator

    def patch(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to add a PATCH route.

        Args:
            path: URL path for the route

        Returns:
            Decorator function
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.add_route(path, func, ["PATCH"])
            return func

        return decorator

    def head(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to add a HEAD route.

        Args:
            path: URL path for the route

        Returns:
            Decorator function
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.add_route(path, func, ["HEAD"])
            return func

        return decorator

    def options(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to add an OPTIONS route.

        Args:
            path: URL path for the route

        Returns:
            Decorator function
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.add_route(path, func, ["OPTIONS"])
            return func

        return decorator
