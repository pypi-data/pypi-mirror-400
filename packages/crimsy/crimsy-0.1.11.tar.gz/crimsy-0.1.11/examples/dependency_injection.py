"""Example demonstrating the dependency injection system with HTTPException.

This example shows:
1. Dependency injection with Depends()
2. HTTPException for error handling with status codes and messages
3. Custom exception handlers
4. OpenAPI schema generation
"""

import typing

from starlette.testclient import TestClient

from crimsy import Crimsy, Depends, HTTPException, Router


# Define custom exceptions
class ServiceUnavailableException(Exception):
    """Raised when the service is unavailable."""

    pass


# Create the application
app = Crimsy(title="Dependency Injection Example", version="1.0.0")


# Register exception handler
@app.exception_handler(ServiceUnavailableException)
async def service_unavailable_handler(request: typing.Any, exc: typing.Any) -> None:
    """Handle service unavailable exceptions by returning 503."""
    raise HTTPException(status_code=503, message="Service unavailable")


# Create a router
router = Router(prefix="/")


# Define a dependency that can raise HTTPException
async def get_repo(repo_id: int = 1) -> int:
    """Get repository - can raise HTTPException.

    This dependency can raise HTTPException with various status codes
    based on the repo_id provided.
    """
    if repo_id == 404:
        raise HTTPException(status_code=404, message="Repository not found")
    if repo_id == 403:
        raise HTTPException(status_code=403, message="Access forbidden")
    # In a real application, this would connect to a database or service
    return repo_id


@router.get("/")
async def foo(repo: int = Depends(get_repo)) -> int:
    """Endpoint that uses the repo dependency.

    This endpoint demonstrates:
    - Dependency injection with Depends()
    - HTTPException handling in dependencies
    - Automatic error responses with status codes
    """
    return repo


app.add_router(router)


# Example usage and testing
if __name__ == "__main__":
    # Create a test client
    client = TestClient(app)

    # Test the endpoint - successful case
    print("Testing endpoint with repo_id=1...")
    response = client.get("/?repo_id=1")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

    # Test 404 error
    print("Testing endpoint with repo_id=404...")
    response = client.get("/?repo_id=404")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

    # Test 403 error
    print("Testing endpoint with repo_id=403...")
    response = client.get("/?repo_id=403")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

    # Check the OpenAPI schema
    print("Checking OpenAPI schema...")
    schema_response = client.get("/openapi.json")
    schema = schema_response.json()

    # Display the endpoint documentation
    endpoint_info = schema["paths"]["/"]["get"]
    print("Endpoint: GET /")
    print("Responses:")
    for status_code, response_info in sorted(endpoint_info["responses"].items()):
        description = response_info.get("description", "")
        print(f"  {status_code}: {description}")
    print()

    print("✅ HTTPException handling works correctly!")
    print("   HTTPException automatically handles error responses with status codes")
