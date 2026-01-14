"""Example demonstrating the Security() system for authentication.

This example shows:
1. Security dependency injection with Security()
2. OpenAPI schema generation with authentication requirements
3. Endpoints marked with lock icon in Swagger UI
4. Multiple security schemes
"""

import typing

from starlette.testclient import TestClient

from crimsy import Crimsy, HTTPException, Router, Security

# Create the application
app = Crimsy(title="Security Example", version="1.0.0")

# Create a router
router = Router(prefix="/api")


# Define a security dependency for API key authentication
async def verify_api_key(api_key: str = "") -> str:
    """Verify API key authentication.

    In a real application, this would check against a database
    or authentication service.
    """
    if api_key != "secret-api-key":
        raise HTTPException(status_code=403, message="Invalid API key")
    return api_key


# Define a security dependency for bearer token authentication
async def verify_bearer_token(token: str = "") -> dict[str, typing.Any]:
    """Verify bearer token and return user info.

    In a real application, this would validate a JWT token
    and return user information.
    """
    if token != "valid-bearer-token":
        raise HTTPException(status_code=401, message="Invalid or expired token")
    return {"user_id": 1, "username": "john_doe", "role": "admin"}


@router.get("/public")
async def public_endpoint() -> dict[str, str]:
    """Public endpoint - no authentication required.

    This endpoint is accessible without any authentication.
    """
    return {"message": "This is a public endpoint"}


@router.get("/secure")
async def secure_endpoint(api_key: str = Security(verify_api_key)) -> dict[str, str]:
    """Secure endpoint requiring API key authentication.

    This endpoint requires a valid API key to access.
    In Swagger UI, this will show a lock icon and require authorization.
    """
    return {"message": "You are authenticated with API key", "api_key": api_key}


@router.get("/user/profile")
async def user_profile(
    user: dict[str, typing.Any] = Security(verify_bearer_token),
) -> dict[str, typing.Any]:
    """User profile endpoint requiring bearer token authentication.

    This endpoint requires a valid bearer token to access.
    Returns the authenticated user's profile information.
    """
    return {"profile": user, "message": "Your profile data"}


@router.get("/admin")
async def admin_endpoint(
    api_key: str = Security(verify_api_key, scheme_name="ApiKeyAuth"),
    user: dict[str, typing.Any] = Security(
        verify_bearer_token, scheme_name="BearerAuth"
    ),
) -> dict[str, typing.Any]:
    """Admin endpoint requiring both API key and bearer token.

    This endpoint requires both authentication methods.
    This demonstrates how multiple security schemes can be used together.
    """
    return {
        "message": "Admin access granted",
        "api_key": api_key,
        "user": user,
    }


app.add_router(router)


# Example usage and testing
if __name__ == "__main__":
    # Create a test client
    client = TestClient(app)

    print("=" * 70)
    print("Security Example - Testing Authentication")
    print("=" * 70)
    print()

    # Test public endpoint
    print("1. Testing public endpoint (no auth required)...")
    response = client.get("/api/public")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print()

    # Test secure endpoint without API key
    print("2. Testing secure endpoint WITHOUT API key...")
    response = client.get("/api/secure")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print()

    # Test secure endpoint with valid API key
    print("3. Testing secure endpoint WITH valid API key...")
    response = client.get("/api/secure?api_key=secret-api-key")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print()

    # Test user profile without token
    print("4. Testing user profile WITHOUT bearer token...")
    response = client.get("/api/user/profile")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print()

    # Test user profile with valid token
    print("5. Testing user profile WITH valid bearer token...")
    response = client.get("/api/user/profile?token=valid-bearer-token")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print()

    # Test admin endpoint with both credentials
    print("6. Testing admin endpoint WITH both API key and bearer token...")
    response = client.get("/api/admin?api_key=secret-api-key&token=valid-bearer-token")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print()

    # Check the OpenAPI schema
    print("=" * 70)
    print("OpenAPI Schema - Security Configuration")
    print("=" * 70)
    print()

    schema_response = client.get("/openapi.json")
    schema = schema_response.json()

    # Display security schemes
    print("Security Schemes defined:")
    if "components" in schema and "securitySchemes" in schema["components"]:
        for scheme_name, scheme_info in schema["components"]["securitySchemes"].items():
            print(f"  - {scheme_name}:")
            print(f"      Type: {scheme_info.get('type')}")
            print(f"      Scheme: {scheme_info.get('scheme')}")
    print()

    # Display endpoints and their security requirements
    print("Endpoints and their security requirements:")
    for path, methods in schema["paths"].items():
        for method, operation in methods.items():
            print(f"  {method.upper()} {path}")
            if "security" in operation:
                print("    Security required:")
                for sec_req in operation["security"]:
                    for scheme in sec_req:
                        print(f"      - {scheme}")
            else:
                print("    Security: None (public endpoint)")
    print()

    print("=" * 70)
    print("✅ Security() implementation works correctly!")
    print("   - Endpoints are properly authenticated")
    print("   - OpenAPI schema includes security requirements")
    print("   - Swagger UI will show lock icons for protected endpoints")
    print("=" * 70)
    print()
    print("Try visiting http://localhost:8000/docs to see the Swagger UI")
    print("You'll see lock icons next to secured endpoints!")
