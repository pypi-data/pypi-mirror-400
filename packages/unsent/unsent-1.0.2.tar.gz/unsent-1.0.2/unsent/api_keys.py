"""Api Keys resource client."""
from __future__ import annotations

from typing import Optional, Tuple

from .legacy_types import APIError
from .types import (
    ApiKeysGetResponse,
    ApiKeysPostRequest,
    ApiKeysPostResponse,
    ApiKeysIdDeleteResponse,
)


class ApiKeys:
    """Client for `/api-keys` endpoints."""

    def __init__(self, unsent: "unsent") -> None:
        self.unsent = unsent

    def list(self) -> Tuple[Optional[ApiKeysGetResponse], Optional[APIError]]:
        data, err = self.unsent.get("/api-keys")
        return (data, err)  # type: ignore[return-value]

    def create(
        self, payload: Union[ApiKeysPostRequest, Dict[str, Any]]
    ) -> Tuple[Optional[ApiKeysPostResponse], Optional[APIError]]:
        body = payload
        if hasattr(payload, "model_dump"):
            body = payload.model_dump(by_alias=True, exclude_none=True) # type: ignore
        data, err = self.unsent.post("/api-keys", body)
        return (data, err)  # type: ignore[return-value]

    def revoke(
        self, api_key_id: str
    ) -> Tuple[Optional[ApiKeysIdDeleteResponse], Optional[APIError]]:
        data, err = self.unsent.delete(f"/api-keys/{api_key_id}")
        return (data, err)  # type: ignore[return-value]


from .unsent import unsent  # noqa: E402
