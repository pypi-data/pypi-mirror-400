"""OpenAPI schema generation and documentation endpoints."""

import inspect
from typing import Any

import msgspec
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route

from crimsy.params import (
    ParamInfo,
    ParamType,
    analyze_function_params,
    is_msgspec_struct,
)


def is_security_scheme(dependency: Any) -> bool:
    """Check if a dependency is a security scheme object vs a plain function.

    In FastAPI, Security() only adds security requirements to OpenAPI when
    it wraps a security scheme object (like HTTPBearer), not plain functions.

    This function distinguishes between:
    - Plain functions/methods: Return False (do not add security to OpenAPI)
    - Callable objects (security scheme instances): Return True (add security)
    - Non-callable objects: Return False (do not add security)

    Since Crimsy does not define its own security scheme base class, this
    function uses a heuristic: any callable that is not a plain function or
    method is assumed to be a security scheme object. This matches FastAPI's
    behavior where security scheme objects are instances of classes like
    HTTPBearer, APIKeyHeader, etc.

    Note: This heuristic means that callable objects (instances with __call__)
    will be treated as security schemes. This is intentional and matches the
    expected pattern where users create security scheme classes for use in
    OpenAPI documentation.

    Args:
        dependency: The dependency to check

    Returns:
        True if it's a security scheme object (callable but not a function/method),
        False otherwise (plain function, method, or non-callable)

    Examples:
        >>> def my_func(): pass
        >>> is_security_scheme(my_func)
        False
        >>> class SecurityScheme:
        ...     def __call__(self): pass
        >>> is_security_scheme(SecurityScheme())
        True
        >>> is_security_scheme("not_callable")
        False
    """
    # Must be callable first
    if not callable(dependency):
        return False

    # If it's a plain function or method, it's not a security scheme
    if inspect.isfunction(dependency) or inspect.ismethod(dependency):
        return False

    # If it's callable but not a function/method, it's a security scheme object
    # This matches FastAPI's pattern where security schemes are instances like HTTPBearer()
    return True


def collect_security_from_dependency(
    param: ParamInfo, http_method: str = "GET"
) -> tuple[list[dict[str, list[str]]], list[ParamInfo]]:
    """Recursively collect security requirements and parameters from a dependency.

    This function traverses the dependency tree, collecting:
    1. All security requirements from Security() dependencies at any level
    2. All query/path/body parameters needed by those security dependencies

    The recursion handles nested dependencies like:
        Depends(func1) -> Security(func2) -> Depends(func3) -> Security(func4)

    Args:
        param: ParamInfo for a dependency or security parameter
        http_method: HTTP method for analyzing nested dependencies

    Returns:
        Tuple of (security_requirements, parameters) where:
        - security_requirements is a list of security requirement dicts
        - parameters is a list of ParamInfo objects for OpenAPI parameters
    """
    security_requirements: list[dict[str, list[str]]] = []
    parameters: list[ParamInfo] = []

    if param.dependency is None:
        return security_requirements, parameters

    # Analyze the dependency function's parameters
    dep_params = analyze_function_params(
        param.dependency.dependency, http_method=http_method
    )

    for dep_param in dep_params:
        if dep_param.param_type == ParamType.SECURITY:
            # Found a security dependency - add its security requirement
            # Only add if it's a security scheme object, not a plain function
            if dep_param.dependency:
                dependency_callable = dep_param.dependency.dependency
                if is_security_scheme(dependency_callable):
                    scheme_name = (
                        dep_param.dependency.scheme_name
                        if hasattr(dep_param.dependency, "scheme_name")
                        and dep_param.dependency.scheme_name
                        else dependency_callable.__name__
                    )
                    security_requirements.append({scheme_name: []})

            # Recursively collect from nested security dependencies
            nested_sec, nested_params = collect_security_from_dependency(
                dep_param, http_method
            )
            security_requirements.extend(nested_sec)
            parameters.extend(nested_params)

        elif dep_param.param_type == ParamType.DEPENDENCY:
            # Recursively check regular dependencies for nested security
            nested_sec, nested_params = collect_security_from_dependency(
                dep_param, http_method
            )
            security_requirements.extend(nested_sec)
            parameters.extend(nested_params)

        elif dep_param.param_type in (
            ParamType.QUERY,
            ParamType.PATH,
            ParamType.BODY,
            ParamType.HEADER,
        ):
            # Add regular parameters from the dependency
            parameters.append(dep_param)

        # REQUEST and RESPONSE types are not documented in OpenAPI
        # because they are auto-injected by the framework

    return security_requirements, parameters


def add_nested_params_to_openapi(
    nested_params: list[ParamInfo],
    parameters: list[dict[str, Any]],
    request_body: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Add nested parameters to OpenAPI parameters and request body.

    Args:
        nested_params: List of nested ParamInfo objects
        parameters: List to append query/path parameters to
        request_body: Current request body (may be None)

    Returns:
        Updated request_body (may be None or a dict)
    """
    for nested_param in nested_params:
        if nested_param.param_type == ParamType.QUERY:
            param_schema = get_parameter_schema(nested_param)
            parameters.append(
                {
                    "name": nested_param.name,
                    "in": "query",
                    "required": nested_param.is_required,
                    "schema": param_schema,
                }
            )
        elif nested_param.param_type == ParamType.HEADER:
            param_schema = get_parameter_schema(nested_param)
            parameters.append(
                {
                    "name": nested_param.name,
                    "in": "header",
                    "required": nested_param.is_required,
                    "schema": param_schema,
                }
            )
        elif nested_param.param_type == ParamType.PATH:
            param_schema = get_parameter_schema(nested_param)
            parameters.append(
                {
                    "name": nested_param.name,
                    "in": "path",
                    "required": True,
                    "schema": param_schema,
                }
            )
        elif nested_param.param_type == ParamType.BODY:
            schema = get_parameter_schema(nested_param)
            request_body = {
                "required": nested_param.is_required,
                "content": {
                    "application/json": {
                        "schema": schema,
                    }
                },
            }
    return request_body


def get_openapi_route(app: Any, path: str) -> Route:
    """Create the OpenAPI JSON endpoint.

    Args:
        app: Crimsy application instance
        path: URL path for the endpoint

    Returns:
        Starlette Route for OpenAPI JSON
    """

    async def openapi_handler(request: Request) -> JSONResponse:
        schema = app.openapi_schema()
        return JSONResponse(schema)

    return Route(path, openapi_handler, methods=["GET"])


def get_scalar_ui_route(app: Any, docs_path: str, openapi_path: str) -> Route:
    """Create the Scalar API documentation endpoint.

    Args:
        app: Crimsy application instance
        docs_path: URL path for Scalar UI
        openapi_path: URL path for OpenAPI JSON

    Returns:
        Starlette Route for Scalar UI
    """

    async def scalar_ui_handler(request: Request) -> HTMLResponse:
        html = f"""
        <!doctype html>
        <html>
        <head>
            <title>{app.title} - API Documentation</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
        </head>
        <body>
            <script id="api-reference" data-url="{openapi_path}"></script>
            <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
        </body>
        </html>
        """
        return HTMLResponse(content=html)

    return Route(docs_path, scalar_ui_handler, methods=["GET"])


def generate_openapi_schema(app: Any) -> dict[str, Any]:
    """Generate OpenAPI 3.0 schema for the application.

    Args:
        app: Crimsy application instance

    Returns:
        OpenAPI schema dictionary
    """
    paths: dict[str, Any] = {}
    security_schemes: dict[str, Any] = {}

    # Iterate through all routers
    for router in app._routers:
        for route in router.routes:
            # Get the path with router prefix
            # Handle the case where route.path is "/" (from empty string paths)
            if route.path == "/":
                # Empty path should result in prefix/
                full_path = router.prefix.rstrip("/") + "/"
            else:
                full_path = router.prefix.rstrip("/") + route.path
            # Ensure we have at least "/"
            if not full_path:
                full_path = "/"

            # Get the original endpoint and parameters
            endpoint = getattr(route.endpoint, "_original_endpoint", None)
            params = getattr(route.endpoint, "_params", [])
            # Get the original methods list (before Starlette adds HEAD for GET)
            original_methods = getattr(route.endpoint, "_original_methods", None)

            if endpoint is None:
                continue

            # Use original methods if available, otherwise fallback to route.methods
            methods_to_document = (
                original_methods if original_methods else route.methods or []
            )

            # Get endpoint metadata
            operation = generate_operation(
                endpoint, params, methods_to_document, app, router.tags
            )

            # Collect security schemes from this endpoint
            primary_method = methods_to_document[0] if methods_to_document else "GET"
            for param in params:
                if param.param_type == ParamType.SECURITY and param.dependency:
                    dependency_callable = param.dependency.dependency
                    # Only add security scheme if it's a security scheme object
                    if is_security_scheme(dependency_callable):
                        scheme_name = (
                            param.dependency.scheme_name
                            if hasattr(param.dependency, "scheme_name")
                            and param.dependency.scheme_name
                            else dependency_callable.__name__
                        )
                        if scheme_name not in security_schemes:
                            # Add a generic HTTP bearer security scheme
                            # In a real implementation, this could be more sophisticated
                            security_schemes[scheme_name] = {
                                "type": "http",
                                "scheme": "bearer",
                            }

                        # Also collect nested security schemes
                        nested_sec, _ = collect_security_from_dependency(
                            param, primary_method
                        )
                        for sec_req in nested_sec:
                            for nested_scheme_name in sec_req:
                                if nested_scheme_name not in security_schemes:
                                    security_schemes[nested_scheme_name] = {
                                        "type": "http",
                                        "scheme": "bearer",
                                    }

                elif param.param_type == ParamType.DEPENDENCY and param.dependency:
                    # Check for nested security in regular dependencies
                    nested_sec, _ = collect_security_from_dependency(
                        param, primary_method
                    )
                    for sec_req in nested_sec:
                        for nested_scheme_name in sec_req:
                            if nested_scheme_name not in security_schemes:
                                security_schemes[nested_scheme_name] = {
                                    "type": "http",
                                    "scheme": "bearer",
                                }

            # Add to paths
            if full_path not in paths:
                paths[full_path] = {}

            for method in methods_to_document:
                paths[full_path][method.lower()] = operation

    schema = {
        "openapi": "3.0.0",
        "info": {
            "title": app.title,
            "version": app.version,
        },
        "paths": paths,
    }

    # Only add components if we have security schemes
    if security_schemes:
        schema["components"] = {"securitySchemes": security_schemes}

    return schema


def generate_operation(
    endpoint: Any,
    params: list[ParamInfo],
    methods: list[str],
    app: Any,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Generate OpenAPI operation object for an endpoint.

    Args:
        endpoint: Endpoint function
        params: List of parameter information
        methods: HTTP methods
        app: Crimsy application instance
        tags: Optional tags for grouping endpoints

    Returns:
        OpenAPI operation dictionary
    """
    operation: dict[str, Any] = {
        "responses": {
            "200": {
                "description": "Successful response",
            }
        },
    }

    # Add tags if provided
    if tags:
        operation["tags"] = tags

    # Add summary and description from docstring
    if endpoint.__doc__:
        operation["summary"] = endpoint.__doc__.strip().split("\n")[0]
        operation["description"] = endpoint.__doc__.strip()

    # Add parameters
    parameters: list[dict[str, Any]] = []
    request_body = None
    security_requirements: list[dict[str, list[str]]] = []

    # Determine the primary HTTP method for analyzing nested dependencies
    primary_method = methods[0] if methods else "GET"

    # Check if we have file parameters for multipart/form-data
    has_file_params = any(param.param_type == ParamType.FILE for param in params)

    for param in params:
        if param.param_type == ParamType.DEPENDENCY:
            # Check if dependency has nested security dependencies
            nested_sec, nested_params = collect_security_from_dependency(
                param, primary_method
            )
            security_requirements.extend(nested_sec)
            # Add parameters from nested dependencies
            request_body = add_nested_params_to_openapi(
                nested_params, parameters, request_body
            )
        elif param.param_type == ParamType.SECURITY:
            # Security dependencies show up as security requirements
            # Only add if it's a security scheme object, not a plain function
            if param.dependency:
                dependency_callable = param.dependency.dependency
                if is_security_scheme(dependency_callable):
                    scheme_name = (
                        param.dependency.scheme_name
                        if hasattr(param.dependency, "scheme_name")
                        and param.dependency.scheme_name
                        else dependency_callable.__name__
                    )
                    security_requirements.append({scheme_name: []})

            # Collect parameters from the security dependency itself
            nested_sec, nested_params = collect_security_from_dependency(
                param, primary_method
            )
            security_requirements.extend(nested_sec)
            # Add parameters from the security dependency
            request_body = add_nested_params_to_openapi(
                nested_params, parameters, request_body
            )
        elif param.param_type == ParamType.REQUEST:
            # Request parameters don't show up in OpenAPI parameters (auto-injected)
            pass
        elif param.param_type == ParamType.FILE:
            # File parameters are part of multipart/form-data request body
            if not request_body or "multipart/form-data" not in request_body.get(
                "content", {}
            ):
                request_body = {
                    "required": True,
                    "content": {
                        "multipart/form-data": {
                            "schema": {"type": "object", "properties": {}}
                        }
                    },
                }

            # Get the schema for file type
            file_schema = get_file_schema(param)
            request_body["content"]["multipart/form-data"]["schema"]["properties"][
                param.name
            ] = file_schema

            # Add to required if the parameter is required
            if param.is_required:
                if (
                    "required"
                    not in request_body["content"]["multipart/form-data"]["schema"]
                ):
                    request_body["content"]["multipart/form-data"]["schema"][
                        "required"
                    ] = []
                request_body["content"]["multipart/form-data"]["schema"][
                    "required"
                ].append(param.name)

        elif param.param_type == ParamType.QUERY:
            param_schema = get_parameter_schema(param)
            parameters.append(
                {
                    "name": param.name,
                    "in": "query",
                    "required": param.is_required,
                    "schema": param_schema,
                }
            )
        elif param.param_type == ParamType.HEADER:
            param_schema = get_parameter_schema(param)
            parameters.append(
                {
                    "name": param.name,
                    "in": "header",
                    "required": param.is_required,
                    "schema": param_schema,
                }
            )
        elif param.param_type == ParamType.BODY:
            # Body parameters (only if we don't have file params - can't mix JSON and multipart)
            if not has_file_params:
                schema = get_parameter_schema(param)
                request_body = {
                    "required": param.is_required,
                    "content": {
                        "application/json": {
                            "schema": schema,
                        }
                    },
                }
        elif param.param_type == ParamType.PATH:
            param_schema = get_parameter_schema(param)
            parameters.append(
                {
                    "name": param.name,
                    "in": "path",
                    "required": True,
                    "schema": param_schema,
                }
            )

    if parameters:
        operation["parameters"] = parameters

    if request_body:
        operation["requestBody"] = request_body

    # Add security requirements if any
    if security_requirements:
        operation["security"] = security_requirements

    # Add response schema
    sig = inspect.signature(endpoint)
    if sig.return_annotation is not inspect.Signature.empty:
        return_schema = get_type_schema(sig.return_annotation)
        operation["responses"]["200"]["content"] = {
            "application/json": {
                "schema": return_schema,
            }
        }

    return operation


def get_parameter_schema(param: ParamInfo) -> dict[str, Any]:
    """Get OpenAPI schema for a parameter.

    Args:
        param: Parameter information

    Returns:
        OpenAPI schema dictionary
    """
    return get_type_schema(param.annotation)


def get_file_schema(param: ParamInfo) -> dict[str, Any]:
    """Get OpenAPI schema for a file parameter.

    Args:
        param: Parameter information

    Returns:
        OpenAPI schema dictionary for file upload
    """
    # Check if it's a list of files
    origin = getattr(param.annotation, "__origin__", None)
    if origin is list:
        return {
            "type": "array",
            "items": {"type": "string", "format": "binary"},
        }

    # Single file
    return {"type": "string", "format": "binary"}


def get_type_schema(annotation: type[Any]) -> dict[str, Any]:
    """Get OpenAPI schema for a type annotation.

    Args:
        annotation: Type annotation

    Returns:
        OpenAPI schema dictionary
    """
    # Handle msgspec.Struct
    if is_msgspec_struct(annotation):
        return get_msgspec_struct_schema(annotation)

    # Handle basic types
    if annotation is str:
        return {"type": "string"}
    if annotation is int:
        return {"type": "integer"}
    if annotation is float:
        return {"type": "number"}
    if annotation is bool:
        return {"type": "boolean"}
    if annotation in (dict, Any):
        return {"type": "object"}
    if annotation is list:
        return {"type": "array", "items": {}}

    # Handle generic types
    origin = getattr(annotation, "__origin__", None)
    if origin is list:
        args = getattr(annotation, "__args__", ())
        if args:
            return {"type": "array", "items": get_type_schema(args[0])}
        return {"type": "array", "items": {}}

    if origin is dict:
        return {"type": "object"}

    # Default
    return {"type": "string"}


def get_msgspec_struct_schema(struct_type: type[msgspec.Struct]) -> dict[str, Any]:
    """Get OpenAPI schema for a msgspec.Struct type.

    Args:
        struct_type: msgspec.Struct type

    Returns:
        OpenAPI schema dictionary
    """
    properties: dict[str, Any] = {}
    required = []

    # Get struct fields
    for field in msgspec.structs.fields(struct_type):
        field_schema = get_type_schema(field.type)
        properties[field.name] = field_schema

        # Check if field is required (no default value)
        if (
            field.default is msgspec.NODEFAULT
            and field.default_factory is msgspec.NODEFAULT
        ):
            required.append(field.name)

    schema: dict[str, Any] = {
        "type": "object",
        "properties": properties,
    }

    if required:
        schema["required"] = required

    return schema
