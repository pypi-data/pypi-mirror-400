"""Domain resource client using TypedDict shapes (no Pydantic)."""

from __future__ import annotations

from typing import Optional, Tuple, List

from .legacy_types import APIError
from .types import (
    DomainsGetResponse,
    DomainsPostRequest,
    DomainsPostResponse,
    DomainsIdDeleteResponse,
    DomainsIdVerifyPutResponse,
    DomainsIdGetResponse,
)


class Domains:
    """Client for `/domains` endpoints."""

    def __init__(self, unsent: "unsent") -> None:
        self.unsent = unsent

    def list(self) -> Tuple[Optional[DomainsGetResponse], Optional[APIError]]:
        data, err = self.unsent.get("/domains")
        return (data, err)  # type: ignore[return-value]

    def create(
        self, payload: Union[DomainsPostRequest, Dict[str, Any]]
    ) -> Tuple[Optional[DomainsPostResponse], Optional[APIError]]:
        body = payload
        if hasattr(payload, "model_dump"):
            body = payload.model_dump(by_alias=True, exclude_none=True) # type: ignore
        data, err = self.unsent.post("/domains", body)
        return (data, err)  # type: ignore[return-value]

    def verify(
        self, domain_id: str
    ) -> Tuple[Optional[DomainsIdVerifyPutResponse], Optional[APIError]]:
        data, err = self.unsent.put(f"/domains/{domain_id}/verify", {})
        return (data, err)  # type: ignore[return-value]

    def get(self, domain_id: str) -> Tuple[Optional[DomainsIdGetResponse], Optional[APIError]]:
        data, err = self.unsent.get(f"/domains/{domain_id}")
        return (data, err)  # type: ignore[return-value]

    def delete(
        self, domain_id: str
    ) -> Tuple[Optional[DomainsIdDeleteResponse], Optional[APIError]]:
        data, err = self.unsent.delete(f"/domains/{domain_id}")
        return (data, err)  # type: ignore[return-value]


from .unsent import unsent  # noqa: E402  pylint: disable=wrong-import-position
