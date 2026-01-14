"""Main Crimsy application class."""

from typing import Any, Callable

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount

from crimsy.exceptions import HTTPException
from crimsy.openapi import get_openapi_route, get_scalar_ui_route
from crimsy.router import Router


class Crimsy(Starlette):
    """Main Crimsy application class that wraps Starlette."""

    def __init__(
        self,
        *,
        debug: bool = False,
        middleware: list[Middleware] | None = None,
        title: str = "Crimsy API",
        version: str = "0.1.0",
        openapi_url: str = "/openapi.json",
        docs_url: str = "/docs",
    ) -> None:
        """Initialize the Crimsy application.

        Args:
            debug: Enable debug mode
            middleware: List of middleware to add
            title: API title for OpenAPI
            version: API version for OpenAPI
            openapi_url: URL path for OpenAPI JSON schema
            docs_url: URL path for Swagger UI documentation
        """
        self.title = title
        self.version = version
        self.openapi_url = openapi_url
        self.docs_url = docs_url
        self._routers: list[Router] = []

        routes = []

        # Add OpenAPI and docs routes
        if openapi_url:
            routes.append(get_openapi_route(self, openapi_url))
        if docs_url and openapi_url:
            routes.append(get_scalar_ui_route(self, docs_url, openapi_url))

        # Create default exception handlers
        exception_handlers = self._create_default_exception_handlers()

        super().__init__(
            debug=debug,
            routes=routes,
            middleware=middleware,
            exception_handlers=exception_handlers,
        )

    def add_router(self, router: Router) -> None:
        """Add a router to the application.

        Args:
            router: Router instance to add
        """
        self._routers.append(router)
        # Mount the router's routes
        mount = Mount(router.prefix, routes=router.routes)
        self.routes.append(mount)

    def _create_default_exception_handlers(
        self,
    ) -> dict[type[Exception] | int, Callable[..., Any]]:
        """Create default exception handlers for the application."""

        async def http_exception_handler(
            request: Request, exc: HTTPException
        ) -> JSONResponse:
            """Handle HTTPException by returning JSON response with status code and message."""
            return JSONResponse(
                content={"error": exc.message} if exc.message else {},
                status_code=exc.status_code,
            )

        async def generic_exception_handler(
            request: Request, exc: Exception
        ) -> JSONResponse:
            """Handle generic exceptions by returning 500 with error message."""
            return JSONResponse(
                content={"error": str(exc)},
                status_code=500,
            )

        return {
            HTTPException: http_exception_handler,
            Exception: generic_exception_handler,
        }

    def exception_handler(  # type: ignore[override]
        self, exc_class: type[Exception]
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to register an exception handler.

        Args:
            exc_class: Exception class to handle

        Returns:
            Decorator function

        Example:
            @app.exception_handler(CustomException)
            async def handler(request, exc):
                raise HTTPException(status_code=503, message="Service unavailable")
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            # Register with Starlette
            self.add_exception_handler(exc_class, func)
            return func

        return decorator

    def openapi_schema(self) -> dict[str, Any]:
        """Generate the OpenAPI schema for the application.

        Returns:
            OpenAPI schema dictionary
        """
        from crimsy.openapi import generate_openapi_schema

        return generate_openapi_schema(self)
