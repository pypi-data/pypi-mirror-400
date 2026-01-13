"""Contact resource client using TypedDict shapes (no Pydantic)."""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from .legacy_types import APIError
from .types import (
    ContactBooksContactBookIdContactsPostRequest,
    ContactBooksContactBookIdContactsPostResponse,
    ContactBooksContactBookIdContactsContactIdGetResponse,
    ContactBooksContactBookIdContactsContactIdPatchRequest,
    ContactBooksContactBookIdContactsContactIdPatchResponse,
    ContactBooksContactBookIdContactsContactIdPutRequest,
    ContactBooksContactBookIdContactsContactIdPutResponse,
    ContactBooksContactBookIdContactsContactIdDeleteResponse,
)


class Contacts:
    """Client for `/contactBooks` endpoints."""

    def __init__(self, unsent: "unsent") -> None:
        self.unsent = unsent

    def list(
        self,
        book_id: str,
        *,
        emails: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        ids: Optional[str] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[APIError]]:
        """List contacts in a contact book.
        
        Args:
            book_id: ID of the contact book
            emails: Filter by comma-separated email addresses
            page: Page number for pagination
            limit: Number of results per page
            ids: Filter by comma-separated contact IDs
        """
        query_params = []
        if emails is not None:
            query_params.append(f"emails={emails}")
        if page is not None:
            query_params.append(f"page={page}")
        if limit is not None:
            query_params.append(f"limit={limit}")
        if ids is not None:
            query_params.append(f"ids={ids}")

        query_string = "&".join(query_params) if query_params else ""
        path = f"/contactBooks/{book_id}/contacts?{query_string}" if query_string else f"/contactBooks/{book_id}/contacts"
        data, err = self.unsent.get(path)
        return (data, err)  # type: ignore[return-value]

    def create(
        self, book_id: str, payload: Union[ContactBooksContactBookIdContactsPostRequest, Dict[str, Any]]
    ) -> Tuple[Optional[ContactBooksContactBookIdContactsPostResponse], Optional[APIError]]:
        body = payload
        if hasattr(payload, "model_dump"):
            body = payload.model_dump(by_alias=True, exclude_none=True) # type: ignore
        data, err = self.unsent.post(
            f"/contactBooks/{book_id}/contacts",
            body,
        )
        return (data, err)  # type: ignore[return-value]

    def get(
        self, book_id: str, contact_id: str
    ) -> Tuple[Optional[ContactBooksContactBookIdContactsContactIdGetResponse], Optional[APIError]]:
        data, err = self.unsent.get(
            f"/contactBooks/{book_id}/contacts/{contact_id}"
        )
        return (data, err)  # type: ignore[return-value]

    def update(
        self, book_id: str, contact_id: str, payload: Union[ContactBooksContactBookIdContactsContactIdPatchRequest, Dict[str, Any]]
    ) -> Tuple[Optional[ContactBooksContactBookIdContactsContactIdPatchResponse], Optional[APIError]]:
        body = payload
        if hasattr(payload, "model_dump"):
            body = payload.model_dump(by_alias=True, exclude_none=True) # type: ignore
        data, err = self.unsent.patch(
            f"/contactBooks/{book_id}/contacts/{contact_id}",
            body,
        )
        return (data, err)  # type: ignore[return-value]

    def upsert(
        self, book_id: str, contact_id: str, payload: Union[ContactBooksContactBookIdContactsContactIdPutRequest, Dict[str, Any]]
    ) -> Tuple[Optional[ContactBooksContactBookIdContactsContactIdPutResponse], Optional[APIError]]:
        body = payload
        if hasattr(payload, "model_dump"):
            body = payload.model_dump(by_alias=True, exclude_none=True) # type: ignore
        data, err = self.unsent.put(
            f"/contactBooks/{book_id}/contacts/{contact_id}",
            body,
        )
        return (data, err)  # type: ignore[return-value]

    def delete(
        self, book_id: str, contact_id: str
    ) -> Tuple[Optional[ContactBooksContactBookIdContactsContactIdDeleteResponse], Optional[APIError]]:
        data, err = self.unsent.delete(
            f"/contactBooks/{book_id}/contacts/{contact_id}"
        )
        return (data, err)  # type: ignore[return-value]


from .unsent import unsent  # noqa: E402  pylint: disable=wrong-import-position
