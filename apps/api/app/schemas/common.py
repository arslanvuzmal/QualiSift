"""
Common Pydantic schemas for API responses.
"""

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    """
    Standard wrapper for API responses.

    Provides a consistent response format across all endpoints.
    """

    success: bool
    data: Optional[T] = None
    meta: dict[str, Any] = {}
    error: Optional[str] = None
