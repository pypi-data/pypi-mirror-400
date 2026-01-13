"""ContactBook resource client."""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from .legacy_types import APIError
from .types import (
    ContactBooksPostRequest,
    ContactBooksPostResponse,
    ContactBooksGetResponse,
    ContactBooksIdGetResponse,
    ContactBooksIdPatchRequest,
    ContactBooksIdPatchResponse,
    ContactBooksIdDeleteResponse,
)


class ContactBooks:
    """Client for `/contactBooks` endpoints."""

    def __init__(self, unsent: "unsent") -> None:
        self.unsent = unsent

    def list(self) -> Tuple[Optional[ContactBooksGetResponse], Optional[APIError]]:
        data, err = self.unsent.get("/contactBooks")
        return (data, err)  # type: ignore[return-value]

    def create(
        self, payload: Union[ContactBooksPostRequest, Dict[str, Any]]
    ) -> Tuple[Optional[ContactBooksPostResponse], Optional[APIError]]:
        body = payload
        if hasattr(payload, "model_dump"):
            body = payload.model_dump(by_alias=True, exclude_none=True) # type: ignore
        data, err = self.unsent.post("/contactBooks", body)
        return (data, err)  # type: ignore[return-value]

    def get(self, book_id: str) -> Tuple[Optional[ContactBooksIdGetResponse], Optional[APIError]]:
        data, err = self.unsent.get(f"/contactBooks/{book_id}")
        return (data, err)  # type: ignore[return-value]

    def update(
        self, book_id: str, payload: Union[ContactBooksIdPatchRequest, Dict[str, Any]]
    ) -> Tuple[Optional[ContactBooksIdPatchResponse], Optional[APIError]]:
        body = payload
        if hasattr(payload, "model_dump"):
            body = payload.model_dump(by_alias=True, exclude_none=True) # type: ignore
        data, err = self.unsent.patch(f"/contactBooks/{book_id}", body)
        return (data, err)  # type: ignore[return-value]

    def delete(
        self, book_id: str
    ) -> Tuple[Optional[ContactBooksIdDeleteResponse], Optional[APIError]]:
        data, err = self.unsent.delete(f"/contactBooks/{book_id}")
        return (data, err)  # type: ignore[return-value]


from .unsent import unsent  # noqa: E402  pylint: disable=wrong-import-position
