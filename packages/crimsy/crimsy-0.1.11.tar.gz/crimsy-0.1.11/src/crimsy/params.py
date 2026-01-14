"""Parameter extraction and parsing utilities."""

import inspect
from enum import Enum
from typing import Any, Callable, overload

import msgspec
from starlette.requests import Request
from starlette.responses import Response

from crimsy.dependencies import _DependsClass, _SecurityClass


class ParamType(str, Enum):
    """Type of parameter."""

    QUERY = "query"
    BODY = "body"
    PATH = "path"
    HEADER = "header"
    FILE = "file"
    DEPENDENCY = "dependency"
    SECURITY = "security"
    REQUEST = "request"
    RESPONSE = "response"


class ParamInfo:
    """Information about a function parameter.

    Args:
        name: Parameter name
        annotation: Parameter type annotation
        default: Default value
        param_type: Type of parameter (query, body, path, dependency, request, response)
        dependency: _DependsClass instance if this is a dependency
    """

    def __init__(
        self,
        name: str,
        annotation: type[Any],
        default: Any,
        param_type: ParamType,
        dependency: _DependsClass | None = None,
    ) -> None:
        """Initialize parameter info.

        Args:
            name: Parameter name
            annotation: Parameter type annotation
            default: Default value
            param_type: Type of parameter (query, body, path, dependency, request, response)
            dependency: _DependsClass instance if this is a dependency
        """
        self.name = name
        self.annotation = annotation
        self.default = default
        self.param_type = param_type
        self.is_required = default is inspect.Parameter.empty
        self.dependency = dependency


class _ParamMarker:
    """Base class for parameter markers (Query, Body, Path)."""

    def __init__(self, default: Any = inspect.Parameter.empty) -> None:
        """Initialize parameter marker.

        Args:
            default: Default value for the parameter
        """
        self.default = default


class _QueryMarker(_ParamMarker):
    """Internal marker class for Query parameters."""

    def __repr__(self) -> str:
        """Return string representation."""
        if self.default is inspect.Parameter.empty:
            return "Query()"
        return f"Query(default={self.default!r})"


class _BodyMarker(_ParamMarker):
    """Internal marker class for Body parameters."""

    def __repr__(self) -> str:
        """Return string representation."""
        if self.default is inspect.Parameter.empty:
            return "Body()"
        return f"Body(default={self.default!r})"


class _PathMarker(_ParamMarker):
    """Internal marker class for Path parameters."""

    def __repr__(self) -> str:
        """Return string representation."""
        if self.default is inspect.Parameter.empty:
            return "Path()"
        return f"Path(default={self.default!r})"


class _HeaderMarker(_ParamMarker):
    """Internal marker class for Header parameters."""

    def __repr__(self) -> str:
        """Return string representation."""
        if self.default is inspect.Parameter.empty:
            return "Header()"
        return f"Header(default={self.default!r})"


class _FileMarker(_ParamMarker):
    """Internal marker class for File parameters."""

    def __repr__(self) -> str:
        """Return string representation."""
        if self.default is inspect.Parameter.empty:
            return "File()"
        return f"File(default={self.default!r})"


# Query overloads - to satisfy mypy requirement for multiple overloads
@overload
def Query() -> Any: ...


@overload
def Query(default: Any) -> Any: ...


def Query(default: Any = inspect.Parameter.empty) -> _QueryMarker:
    """Marker to indicate a parameter should come from query string.

    Example:
        @router.get("/")
        async def handler(name: str = Query(default="guest")) -> dict:
            return {"name": name}
    """
    return _QueryMarker(default)


# Body overloads - to satisfy mypy requirement for multiple overloads
@overload
def Body() -> Any: ...


@overload
def Body(default: Any) -> Any: ...


def Body(default: Any = inspect.Parameter.empty) -> _BodyMarker:
    """Marker to indicate a parameter should come from request body.

    Example:
        @router.post("/")
        async def handler(data: dict = Body()) -> dict:
            return data
    """
    return _BodyMarker(default)


# Path overloads - to satisfy mypy requirement for multiple overloads
@overload
def Path() -> Any: ...


@overload
def Path(default: Any) -> Any: ...


def Path(default: Any = inspect.Parameter.empty) -> _PathMarker:
    """Marker to indicate a parameter should come from URL path.

    Example:
        @router.get("/{user_id}")
        async def handler(user_id: int = Path()) -> dict:
            return {"user_id": user_id}
    """
    return _PathMarker(default)


# Header overloads - to satisfy mypy requirement for multiple overloads
@overload
def Header() -> Any: ...


@overload
def Header(default: Any) -> Any: ...


def Header(default: Any = inspect.Parameter.empty) -> _HeaderMarker:
    """Marker to indicate a parameter should come from HTTP headers.

    Example:
        @router.get("/")
        async def handler(api_key: str = Header()) -> dict:
            return {"authenticated": True}
    """
    return _HeaderMarker(default)


# File overloads - to satisfy mypy requirement for multiple overloads
@overload
def File() -> Any: ...


@overload
def File(default: Any) -> Any: ...


def File(default: Any = inspect.Parameter.empty) -> _FileMarker:
    """Marker to indicate a parameter should come from uploaded files.

    Example:
        from starlette.datastructures import UploadFile

        @router.post("/upload")
        async def handler(file: UploadFile = File()) -> dict:
            contents = await file.read()
            return {"filename": file.filename}
    """
    return _FileMarker(default)


def is_msgspec_struct(annotation: type[Any]) -> bool:
    """Check if a type is a msgspec Struct.

    Args:
        annotation: Type to check

    Returns:
        True if the type is a msgspec Struct
    """
    try:
        return isinstance(annotation, type) and issubclass(annotation, msgspec.Struct)
    except TypeError:
        return False


def is_upload_file(annotation: type[Any]) -> bool:
    """Check if a type is UploadFile.

    Args:
        annotation: Type to check

    Returns:
        True if the type is UploadFile or a list of UploadFiles
    """
    from starlette.datastructures import UploadFile

    # Check direct UploadFile type
    try:
        if isinstance(annotation, type) and issubclass(annotation, UploadFile):
            return True
    except TypeError:
        pass

    # Check if it's a generic type like list[UploadFile]
    origin = getattr(annotation, "__origin__", None)
    if origin is list:
        args = getattr(annotation, "__args__", ())
        if args:
            try:
                return isinstance(args[0], type) and issubclass(args[0], UploadFile)
            except TypeError:
                pass

    return False


def get_param_type(
    annotation: type[Any], default: Any, http_method: str = "GET"
) -> ParamType:
    """Determine the parameter type based on annotation and default value.

    Args:
        annotation: Type annotation
        default: Default value (may be a _ParamMarker instance)
        http_method: HTTP method for the route

    Returns:
        Parameter type (query, body, path, file)
    """
    # If default is a parameter marker, use that to determine type
    if isinstance(default, _QueryMarker):
        return ParamType.QUERY
    if isinstance(default, _BodyMarker):
        return ParamType.BODY
    if isinstance(default, _PathMarker):
        return ParamType.PATH
    if isinstance(default, _HeaderMarker):
        return ParamType.HEADER
    if isinstance(default, _FileMarker):
        return ParamType.FILE

    # UploadFile types default to file
    if is_upload_file(annotation):
        return ParamType.FILE

    # msgspec.Struct types default to body for POST/PUT/PATCH, query for GET
    if is_msgspec_struct(annotation):
        if http_method.upper() in ("POST", "PUT", "PATCH"):
            return ParamType.BODY
        return ParamType.QUERY

    # Simple types are query parameters by default
    return ParamType.QUERY


def analyze_function_params(
    func: Callable[..., Any], http_method: str = "GET", path: str = ""
) -> list[ParamInfo]:
    """Analyze function parameters to extract parameter information.

    Args:
        func: Function to analyze
        http_method: HTTP method for the route
        path: URL path for the route (used to detect path parameters)

    Returns:
        List of parameter information
    """
    import re

    # Extract path parameter names from the path (e.g., /users/{user_id})
    path_param_names = set(re.findall(r"\{(\w+)\}", path))

    sig = inspect.signature(func)
    params: list[ParamInfo] = []

    for param_name, param in sig.parameters.items():
        # Skip 'self' and 'cls'
        if param_name in ("self", "cls"):
            continue

        # Get annotation
        annotation = param.annotation
        if annotation is inspect.Parameter.empty:
            annotation = str

        # Get default value
        default = param.default

        # Check if this is a security dependency (check before _DependsClass since it's a subclass)
        if isinstance(default, _SecurityClass):
            # This is a security parameter
            security = default

            params.append(
                ParamInfo(
                    name=param_name,
                    annotation=annotation,
                    default=inspect.Parameter.empty,  # Security deps are required
                    param_type=ParamType.SECURITY,
                    dependency=security,
                )
            )
            continue

        # Check if this is a dependency
        if isinstance(default, _DependsClass):
            # This is a dependency parameter
            dependency = default

            params.append(
                ParamInfo(
                    name=param_name,
                    annotation=annotation,
                    default=inspect.Parameter.empty,  # Dependencies are required
                    param_type=ParamType.DEPENDENCY,
                    dependency=dependency,
                )
            )
            continue

        # Check if this is a Request parameter (should be auto-injected)
        if annotation is Request or (
            isinstance(annotation, type) and issubclass(annotation, Request)
        ):
            params.append(
                ParamInfo(
                    name=param_name,
                    annotation=annotation,
                    default=inspect.Parameter.empty,  # Request is always provided
                    param_type=ParamType.REQUEST,
                )
            )
            continue

        # Check if this is a Response parameter (should be auto-injected)
        if annotation is Response or (
            isinstance(annotation, type) and issubclass(annotation, Response)
        ):
            params.append(
                ParamInfo(
                    name=param_name,
                    annotation=annotation,
                    default=inspect.Parameter.empty,  # Response is always provided
                    param_type=ParamType.RESPONSE,
                )
            )
            continue

        # If default is a parameter marker, extract the actual default value
        actual_default = default
        if isinstance(default, _ParamMarker):
            actual_default = default.default

        # Check if this parameter is in the path
        if param_name in path_param_names:
            param_type = ParamType.PATH
        else:
            # Determine parameter type
            param_type = get_param_type(annotation, default, http_method)

        params.append(
            ParamInfo(
                name=param_name,
                annotation=annotation,
                default=actual_default,
                param_type=param_type,
            )
        )

    return params


async def extract_params(
    request: Request,
    params: list[ParamInfo],
    path_params: dict[str, str],
    response: Response | None = None,
) -> dict[str, Any]:
    """Extract parameters from request.

    Args:
        request: Starlette request object
        params: List of parameter information
        path_params: Path parameters from URL
        response: Starlette response object (optional, for response injection)

    Returns:
        Dictionary of parameter values

    Raises:
        ValueError: If required parameters are missing or invalid
    """
    from starlette.datastructures import UploadFile

    result: dict[str, Any] = {}
    http_method = request.method.upper()

    # Check if we need to parse form data for file uploads
    has_file_params = any(param.param_type == ParamType.FILE for param in params)
    form_data = None
    if has_file_params:
        form_data = await request.form()

    for param in params:
        if (
            param.param_type == ParamType.DEPENDENCY
            or param.param_type == ParamType.SECURITY
        ):
            # Resolve dependency (includes security dependencies)
            if param.dependency is None:
                raise ValueError(
                    f"Dependency not configured for parameter: {param.name}"
                )

            # Call the dependency function
            dependency_func = param.dependency.dependency

            # Recursively analyze and extract dependency parameters
            dep_params = analyze_function_params(dependency_func, http_method)
            dep_kwargs = await extract_params(
                request, dep_params, path_params, response
            )

            # Call the dependency
            if inspect.iscoroutinefunction(dependency_func):
                dep_result = await dependency_func(**dep_kwargs)
            else:
                dep_result = dependency_func(**dep_kwargs)

            # Handle async generators (AsyncIterator)
            if inspect.isasyncgen(dep_result):
                # For async generators, we need to get the first yielded value
                dep_result = await dep_result.__anext__()

            result[param.name] = dep_result

        elif param.param_type == ParamType.REQUEST:
            # Inject the request object directly
            result[param.name] = request

        elif param.param_type == ParamType.RESPONSE:
            # Inject the response object directly
            if response is None:
                raise ValueError("Response object not available for injection")
            result[param.name] = response

        elif param.param_type == ParamType.FILE:
            # Extract from form data for file uploads
            if form_data is None:
                raise ValueError(
                    f"File parameter {param.name} requires multipart/form-data"
                )

            file_value = form_data.get(param.name)

            # Handle list of files (e.g., list[UploadFile])
            origin = getattr(param.annotation, "__origin__", None)
            if origin is list:
                # Get all files with this name
                all_files = form_data.getlist(param.name)
                if not all_files:
                    if param.is_required:
                        raise ValueError(
                            f"Missing required file parameter: {param.name}"
                        )
                    if param.default is not inspect.Parameter.empty:
                        result[param.name] = param.default
                    continue

                # Verify all items are UploadFiles
                for f in all_files:
                    if not isinstance(f, UploadFile):
                        raise ValueError(
                            f"Expected file upload for parameter: {param.name}"
                        )

                result[param.name] = all_files
            else:
                # Single file
                if file_value is None:
                    if param.is_required:
                        raise ValueError(
                            f"Missing required file parameter: {param.name}"
                        )
                    if param.default is not inspect.Parameter.empty:
                        result[param.name] = param.default
                    continue

                if not isinstance(file_value, UploadFile):
                    raise ValueError(
                        f"Expected file upload for parameter: {param.name}"
                    )

                result[param.name] = file_value

        elif param.param_type == ParamType.QUERY:
            # Extract from query parameters, or from form data if we're parsing files
            value: str | None = None
            if form_data is not None:
                # If we have form data, try to get from there first (for mixed file/form submissions)
                form_value = form_data.get(param.name)
                if form_value is not None and isinstance(form_value, str):
                    value = form_value
                else:
                    # Fall back to query params
                    value = request.query_params.get(param.name)
            else:
                value = request.query_params.get(param.name)

            if value is None:
                if param.is_required:
                    raise ValueError(f"Missing required query parameter: {param.name}")
                if param.default is not inspect.Parameter.empty:
                    result[param.name] = param.default
                continue

            # Convert to the appropriate type
            result[param.name] = convert_value(value, param.annotation)

        elif param.param_type == ParamType.HEADER:
            # Extract from request headers
            # Convert Python parameter name (snake_case) to HTTP header name (kebab-case)
            header_name = param.name.replace("_", "-")
            value_h: str | None = request.headers.get(header_name)
            if value_h is None:
                if param.is_required:
                    raise ValueError(f"Missing required header: {header_name}")
                if param.default is not inspect.Parameter.empty:
                    result[param.name] = param.default
                continue

            # Convert to the appropriate type
            result[param.name] = convert_value(value_h, param.annotation)

        elif param.param_type == ParamType.BODY:
            # For GET/HEAD/OPTIONS requests, try query params first for msgspec.Struct
            # This is a non-standard but intentional feature to support complex types
            # in GET requests by passing JSON-encoded data in query parameters
            if http_method in ("GET", "HEAD", "OPTIONS") and is_msgspec_struct(
                param.annotation
            ):
                # Try to get from query parameters as JSON string
                value_q: str | None = request.query_params.get(param.name)
                if value_q:
                    try:
                        result[param.name] = msgspec.json.decode(
                            value_q.encode(), type=param.annotation
                        )
                        continue
                    except msgspec.DecodeError as e:
                        raise ValueError(
                            f"Invalid JSON for parameter {param.name}: {e}"
                        ) from e

            # Extract from request body
            body = await request.body()
            if not body:
                if param.is_required:
                    raise ValueError(f"Missing required body parameter: {param.name}")
                if param.default is not inspect.Parameter.empty:
                    result[param.name] = param.default
                continue

            # Decode using msgspec
            try:
                if is_msgspec_struct(param.annotation):
                    result[param.name] = msgspec.json.decode(
                        body, type=param.annotation
                    )
                else:
                    # Try to decode as JSON
                    decoded = msgspec.json.decode(body)
                    result[param.name] = decoded
            except msgspec.DecodeError as e:
                raise ValueError(
                    f"Invalid JSON in request body for parameter {param.name}: {e}"
                ) from e

        elif param.param_type == ParamType.PATH:
            # Extract from path parameters
            value_p: str | None = path_params.get(param.name)
            if value_p is None:
                if param.is_required:
                    raise ValueError(f"Missing required path parameter: {param.name}")
                if param.default is not inspect.Parameter.empty:
                    result[param.name] = param.default
                continue

            result[param.name] = convert_value(value_p, param.annotation)

    return result


def convert_value(value: str, target_type: type[Any]) -> Any:
    """Convert a string value to the target type.

    Args:
        value: String value to convert
        target_type: Target type

    Returns:
        Converted value

    Raises:
        ValueError: If conversion fails
    """
    # Handle basic types
    if target_type in (str, inspect.Parameter.empty):
        return value
    if target_type is int:
        try:
            return int(value)
        except ValueError as e:
            raise ValueError(f"Invalid integer value: {value}") from e
    if target_type is float:
        try:
            return float(value)
        except ValueError as e:
            raise ValueError(f"Invalid float value: {value}") from e
    if target_type is bool:
        return value.lower() in ("true", "1", "yes")

    # Try to decode as JSON for complex types
    try:
        return msgspec.json.decode(value.encode(), type=target_type)
    except msgspec.DecodeError as e:
        raise ValueError(f"Invalid JSON value for type {target_type}: {value}") from e
