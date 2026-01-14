"""Example demonstrating app.state usage with a database engine.

This example shows how to store a database engine (or any other resource)
in app.state and access it from request handlers, similar to the use case
described in the issue.
"""

import uvicorn
from typing import AsyncIterator

from crimsy import Crimsy, Depends, Request, Router


class MockEngine:
    """Mock database engine for demonstration."""

    def __init__(self, connection_string: str) -> None:
        self.connection_string = connection_string

    def execute(self, query: str) -> list[dict[str, str]]:
        """Execute a query and return results."""
        return [{"id": "1", "name": "Test User"}]


class MockSession:
    """Mock database session for demonstration."""

    def __init__(self, engine: MockEngine) -> None:
        self.engine = engine

    def query(self, query: str) -> list[dict[str, str]]:
        """Query the database."""
        return self.engine.execute(query)


async def get_session(request: Request) -> AsyncIterator[MockSession]:
    """Dependency that provides a database session.

    This demonstrates the use case from the issue where we need to access
    the engine from request.app.state.
    """
    # Access the engine from app.state
    engine = request.app.state.engine

    # Create and yield a session
    session = MockSession(engine)
    try:
        yield session
    finally:
        # Cleanup logic would go here
        pass


# Create the application
app = Crimsy(title="App State Example", version="1.0.0")
router = Router(prefix="/api")


@router.get("/users")
async def list_users(
    session: MockSession = Depends(get_session),
) -> list[dict[str, str]]:
    """List users using the database session from app.state."""
    return session.query("SELECT * FROM users")


@router.get("/config")
async def get_config(request: Request) -> dict[str, str]:
    """Get configuration from app.state."""
    return {
        "engine": request.app.state.engine.connection_string,
        "app_name": getattr(request.app.state, "app_name", "Unknown"),
    }


app.add_router(router)

# Initialize app state - this would typically be done at application startup
# For example, in a Cloudflare Worker, this would be done in the fetch handler
app.state.engine = MockEngine("postgresql://localhost:5432/mydb")
app.state.app_name = "My Application"

if __name__ == "__main__":
    # Run the application
    uvicorn.run(app, host="127.0.0.1", port=8000)
