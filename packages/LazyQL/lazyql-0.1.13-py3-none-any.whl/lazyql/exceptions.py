class LazyQLException(Exception):
    """Base exception for all LazyQL errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class DocumentNotFoundException(LazyQLException):
    """Raised when a requested document is not found."""

    def __init__(self, message: str = "Document not found"):
        super().__init__(message)


class InvalidDocumentIdException(LazyQLException):
    """Raised when a document ID has an invalid format."""

    def __init__(self, message: str = "Invalid document ID format"):
        super().__init__(message)
