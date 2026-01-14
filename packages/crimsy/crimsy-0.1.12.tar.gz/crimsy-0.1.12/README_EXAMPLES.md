# Crimsy Framework Examples

This document provides examples of how to use the Crimsy web framework.

## Quick Start

```python
import msgspec
from crimsy import Crimsy, Router


class User(msgspec.Struct):
    name: str
    age: int = 0


app = Crimsy()
router = Router(prefix="/users")


@router.get("/")
async def handler(user: User, name: str) -> User:
    # Your code implementation goes here
    return User(name=f"{user.name} and {name}")


app.add_router(router)
```

## Running the Examples

### Simple Example

```bash
# Run the simple example
uv run python example.py

# Test the endpoints
curl http://localhost:8000/users/
curl http://localhost:8000/users/search?name=Alice
curl -X POST http://localhost:8000/users/ -H "Content-Type: application/json" -d '{"name":"Alice","age":30}'
```

### Comprehensive Example

```bash
# Run the comprehensive example
uv run python example_comprehensive.py

# View the OpenAPI specification
curl http://localhost:8000/openapi.json

# Access Swagger UI documentation
open http://localhost:8000/docs
```

## Features Demonstrated

### 1. HTTP Method Support

All standard HTTP methods are supported:

```python
@router.get("/")      # GET requests
@router.post("/")     # POST requests
@router.put("/")      # PUT requests
@router.delete("/")   # DELETE requests
@router.patch("/")    # PATCH requests
@router.head("/")     # HEAD requests
@router.options("/")  # OPTIONS requests
```

### 2. Query Parameters

Extract query parameters with automatic type conversion:

```python
@router.get("/search")
async def search(name: str, limit: int = 10) -> dict:
    return {"name": name, "limit": limit}

# Usage: GET /search?name=Alice&limit=20
```

### 3. Request Body with msgspec.Struct

Define request bodies using msgspec.Struct for automatic validation and deserialization:

```python
class CreateUserRequest(msgspec.Struct):
    name: str
    age: int
    email: str


@router.post("/")
async def create_user(user: CreateUserRequest) -> dict:
    return {"status": "created", "user": user}

# Usage: POST / -d '{"name":"Alice","age":30,"email":"alice@example.com"}'
```

### 4. Path Parameters

Extract parameters from URL paths:

```python
@router.get("/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"user_id": user_id}

# Usage: GET /123
```

### 5. msgspec.Struct in Query Parameters (GET requests)

For GET requests, you can pass msgspec.Struct types as JSON-encoded query parameters:

```python
@router.get("/greet")
async def greet(user: User, greeting: str = "Hello") -> dict:
    return {"message": f"{greeting}, {user.name}!"}

# Usage: GET /greet?user={"name":"Alice","age":30}&greeting=Hi
# URL-encoded: GET /greet?user=%7B%22name%22%3A%22Alice%22%2C%22age%22%3A30%7D&greeting=Hi
```

### 6. Response Encoding

Responses are automatically encoded using msgspec:

```python
@router.get("/user")
async def get_user() -> User:
    return User(name="Alice", age=30)

# Returns: {"name":"Alice","age":30}
```

### 7. OpenAPI Documentation

Automatic OpenAPI 3.0 schema generation:

- **OpenAPI JSON**: Available at `/openapi.json` (configurable)
- **Swagger UI**: Available at `/docs` (configurable)

```python
app = Crimsy(
    title="My API",
    version="1.0.0",
    openapi_url="/openapi.json",  # Customize or disable with None
    docs_url="/docs",              # Customize or disable with None
)
```

## Type Support

Crimsy automatically handles encoding/decoding for:

- **Simple types**: `str`, `int`, `float`, `bool`
- **Collections**: `list`, `dict`
- **msgspec.Struct**: Custom data structures
- **Optional types**: `str | None`, `int | None`, etc.

## Error Handling

Crimsy automatically returns appropriate error responses:

- **400 Bad Request**: Missing required parameters or invalid data
- **500 Internal Server Error**: Unhandled exceptions

```python
# Missing required parameter
GET /search  # -> 400: Missing required query parameter: name

# Invalid data type
GET /search?limit=abc  # -> 400: Invalid value for parameter: limit
```

## Running with uvicorn

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Or from the command line:

```bash
uvicorn my_app:app --reload
```
