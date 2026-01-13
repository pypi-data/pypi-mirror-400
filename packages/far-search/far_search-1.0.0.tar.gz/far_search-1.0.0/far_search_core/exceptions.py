"""Exceptions for FAR Search Core SDK."""


class FARSearchError(Exception):
    """Base exception for FAR Search errors."""
    pass


class FARAPIError(FARSearchError):
    """Error from FAR RAG API."""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class FARRateLimitError(FARSearchError):
    """Rate limit exceeded."""
    
    def __init__(self, message: str = None):
        super().__init__(
            message or (
                "Rate limit exceeded. Upgrade at: "
                "https://rapidapi.com/yschang/api/far-rag-federal-acquisition-regulation-search"
            )
        )

