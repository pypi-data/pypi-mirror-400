"""Legacy types for the Unsent Python SDK.

This file contains manually defined types that are not auto-generated.
"""

from __future__ import annotations

from typing import Any, TypedDict


class APIError(TypedDict, total=False):
    """Error response structure from the API."""
    code: str
    message: str


# Re-export commonly used types for compatibility
Email = Any  # Generic email type for flexibility
