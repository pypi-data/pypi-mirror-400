"""
Shared utilities for the Constec library ecosystem.
"""
from constec.shared.exceptions import (
    ConstecError,
    ConstecAPIError,
    ConstecConnectionError,
    ConstecValidationError,
    ConstecAuthenticationError,
    ConstecNotFoundError,
)

__all__ = [
    "ConstecError",
    "ConstecAPIError",
    "ConstecConnectionError",
    "ConstecValidationError",
    "ConstecAuthenticationError",
    "ConstecNotFoundError",
]
