"""Suppression resource client."""
from __future__ import annotations

from typing import List, Optional, Tuple

from .legacy_types import APIError
from .types import (
    SuppressionsGetResponse,
    SuppressionsPostRequest,
    SuppressionsPostResponse,
    SuppressionsEmailEmailDeleteResponse,
)


class Suppressions:
    """Client for `/suppressions` endpoints."""

    def __init__(self, unsent: "unsent") -> None:
        self.unsent = unsent

    def list(
        self,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        search: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Tuple[Optional[SuppressionsGetResponse], Optional[APIError]]:
        """List suppressions with optional filters.
        
        Args:
            page: Page number for pagination
            limit: Number of results per page
            search: Search query string
            reason: Filter by reason - one of: HARD_BOUNCE, COMPLAINT, MANUAL, UNSUBSCRIBE
        """
        query_params = []
        if page is not None:
            query_params.append(f"page={page}")
        if limit is not None:
            query_params.append(f"limit={limit}")
        if search is not None:
            query_params.append(f"search={search}")
        if reason is not None:
            query_params.append(f"reason={reason}")

        query_string = "&".join(query_params) if query_params else ""
        path = f"/suppressions?{query_string}" if query_string else "/suppressions"
        data, err = self.unsent.get(path)
        return (data, err)  # type: ignore[return-value]

    def add(
        self, payload: Union[SuppressionsPostRequest, Dict[str, Any]]
    ) -> Tuple[Optional[SuppressionsPostResponse], Optional[APIError]]:
        body = payload
        if hasattr(payload, "model_dump"):
            body = payload.model_dump(by_alias=True, exclude_none=True) # type: ignore
        data, err = self.unsent.post("/suppressions", body)
        return (data, err)  # type: ignore[return-value]

    def delete(
        self, email: str
    ) -> Tuple[Optional[SuppressionsEmailEmailDeleteResponse], Optional[APIError]]:
        """Delete a suppression by email address.
        
        Args:
            email: Email address to remove from suppression list
        """
        data, err = self.unsent.delete(f"/suppressions/email/{email}")
        return (data, err)  # type: ignore[return-value]


from .unsent import unsent  # noqa: E402
