class NotFoundError(FileNotFoundError):
    pass


class ConflictError(Exception):
    """Raised when a 409 Conflict error is encountered (e.g., item already exists)"""

    pass
