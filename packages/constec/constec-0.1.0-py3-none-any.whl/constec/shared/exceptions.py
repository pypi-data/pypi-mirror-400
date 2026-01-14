"""
Shared exception classes for the Constec library ecosystem.
"""
from typing import Optional


class ConstecError(Exception):
    """Base exception for all Constec-related errors."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)
    
    def __str__(self):
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class ConstecAPIError(ConstecError):
    """Raised when API requests fail."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[dict] = None):
        self.status_code = status_code
        self.response_data = response_data or {}
        details = {"status_code": status_code, "response": response_data}
        super().__init__(message, details)


class ConstecConnectionError(ConstecError):
    """Raised when connection to a service fails."""
    pass


class ConstecValidationError(ConstecError):
    """Raised when data validation fails."""
    pass


class ConstecAuthenticationError(ConstecAPIError):
    """Raised when authentication fails."""
    pass


class ConstecNotFoundError(ConstecAPIError):
    """Raised when a requested resource is not found."""
    pass
