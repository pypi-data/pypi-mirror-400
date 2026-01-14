"""Exception classes for Crimsy."""


class HTTPException(Exception):
    """HTTP exception with status code and message.

    This exception can be raised anywhere in your application (endpoints, dependencies, etc.)
    and will be automatically handled to return an HTTP response with the specified
    status code and message.

    Example:
        @router.get("/users/{user_id}")
        async def get_user(user_id: int) -> User:
            if user_id not in database:
                raise HTTPException(status_code=404, message="User not found")
            return database[user_id]
    """

    def __init__(self, status_code: int, message: str = "") -> None:
        """Initialize HTTP exception.

        Args:
            status_code: HTTP status code to return
            message: Error message to include in response
        """
        self.status_code = status_code
        self.message = message
        super().__init__(message)

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"HTTPException(status_code={self.status_code}, message={self.message!r})"
        )
