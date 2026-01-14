"""Dependency injection system for Crimsy."""

from collections.abc import AsyncIterator, Awaitable
from typing import Any, Callable, TypeVar, overload

T = TypeVar("T")


class _DependsClass:
    """Internal class for dependency injection marker."""

    dependency: Callable[..., Any]
    use_cache: bool

    def __init__(self, dependency: Callable[..., Any], use_cache: bool = True) -> None:
        """Initialize dependency marker.

        Args:
            dependency: Callable that provides the dependency
            use_cache: Whether to cache the dependency result (default: True)
        """
        self.dependency = dependency
        self.use_cache = use_cache

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Depends({self.dependency.__name__})"


class _SecurityClass(_DependsClass):
    """Internal class for security dependency marker.

    Extends _DependsClass to add OpenAPI security scheme information.
    """

    scheme_name: str | None

    def __init__(
        self,
        dependency: Callable[..., Any],
        use_cache: bool = True,
        scheme_name: str | None = None,
    ) -> None:
        """Initialize security marker.

        Args:
            dependency: Callable that provides the security dependency
            use_cache: Whether to cache the dependency result (default: True)
            scheme_name: Name for the security scheme in OpenAPI (optional)
        """
        super().__init__(dependency, use_cache)
        self.scheme_name = scheme_name

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Security({self.dependency.__name__})"


# Overloads for async iterators (unwrap AsyncIterator[T] to T)
@overload
def Depends(
    dependency: Callable[..., AsyncIterator[T]], use_cache: bool = True
) -> T: ...


# Overloads for async functions returning T (unwrap Awaitable[T] to T)
@overload
def Depends(dependency: Callable[..., Awaitable[T]], use_cache: bool = True) -> T: ...


# Overloads for sync functions returning T
@overload
def Depends(dependency: Callable[..., T], use_cache: bool = True) -> T: ...


def Depends(dependency: Callable[..., Any], use_cache: bool = True) -> Any:
    """Marker for dependency injection.

    Similar to FastAPI's Depends, this function marks a parameter as a dependency
    that should be resolved and injected by the framework.

    The function signature is designed so that type checkers understand that
    Depends(func) returns the same type as func's return type (unwrapping
    Awaitable and AsyncIterator for async functions).

    Example:
        async def get_db() -> Database:
            return Database()

        @router.get("/")
        async def handler(db: Database = Depends(get_db)) -> dict:
            return {"status": "ok"}
    """
    return _DependsClass(dependency, use_cache)


# Overloads for Security with async iterators (unwrap AsyncIterator[T] to T)
@overload
def Security(
    dependency: Callable[..., AsyncIterator[T]],
    use_cache: bool = True,
    scheme_name: str | None = None,
) -> T: ...


# Overloads for Security with async functions returning T (unwrap Awaitable[T] to T)
@overload
def Security(
    dependency: Callable[..., Awaitable[T]],
    use_cache: bool = True,
    scheme_name: str | None = None,
) -> T: ...


# Overloads for Security with sync functions returning T
@overload
def Security(
    dependency: Callable[..., T],
    use_cache: bool = True,
    scheme_name: str | None = None,
) -> T: ...


def Security(
    dependency: Callable[..., Any],
    use_cache: bool = True,
    scheme_name: str | None = None,
) -> Any:
    """Marker for security dependency injection.

    Similar to Depends(), but specifically for security/authentication dependencies.
    This function marks a parameter as a security dependency that should be resolved
    and injected by the framework, and will be documented in OpenAPI/Swagger with
    authentication requirements.

    The function signature is designed so that type checkers understand that
    Security(func) returns the same type as func's return type (unwrapping
    Awaitable and AsyncIterator for async functions).

    Args:
        dependency: Callable that provides the security dependency
        use_cache: Whether to cache the dependency result (default: True)
        scheme_name: Name for the security scheme in OpenAPI (optional, defaults to function name)

    Example:
        async def get_current_user(token: str) -> User:
            # Verify token and return user
            return User(id=1, name="John")

        @router.get("/profile")
        async def get_profile(user: User = Security(get_current_user)) -> User:
            return user
    """
    return _SecurityClass(dependency, use_cache, scheme_name)
