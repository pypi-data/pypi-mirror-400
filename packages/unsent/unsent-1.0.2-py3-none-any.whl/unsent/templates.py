"""Template resource client."""
from __future__ import annotations

from typing import Optional, Tuple

from .legacy_types import APIError
from .types import (
    TemplatesGetResponse,
    TemplatesPostRequest,
    TemplatesPostResponse,
    TemplatesIdDeleteResponse,
    TemplatesIdGetResponse,
    TemplatesIdPatchRequest,
    TemplatesIdPatchResponse,
)


class Templates:
    """Client for `/templates` endpoints."""

    def __init__(self, unsent: "unsent") -> None:
        self.unsent = unsent

    def list(self) -> Tuple[Optional[TemplatesGetResponse], Optional[APIError]]:
        data, err = self.unsent.get("/templates")
        return (data, err)  # type: ignore[return-value]

    def get(self, template_id: str) -> Tuple[Optional[TemplatesIdGetResponse], Optional[APIError]]:
        data, err = self.unsent.get(f"/templates/{template_id}")
        return (data, err)  # type: ignore[return-value]

    def create(
        self, payload: Union[TemplatesPostRequest, Dict[str, Any]]
    ) -> Tuple[Optional[TemplatesPostResponse], Optional[APIError]]:
        body = payload
        if hasattr(payload, "model_dump"):
            body = payload.model_dump(by_alias=True, exclude_none=True) # type: ignore
        data, err = self.unsent.post("/templates", body)
        return (data, err)  # type: ignore[return-value]

    def update(
        self, template_id: str, payload: Union[TemplatesIdPatchRequest, Dict[str, Any]]
    ) -> Tuple[Optional[TemplatesIdPatchResponse], Optional[APIError]]:
        body = payload
        if hasattr(payload, "model_dump"):
            body = payload.model_dump(by_alias=True, exclude_none=True) # type: ignore
        data, err = self.unsent.patch(f"/templates/{template_id}", body)
        return (data, err)  # type: ignore[return-value]

    def delete(
        self, template_id: str
    ) -> Tuple[Optional[TemplatesIdDeleteResponse], Optional[APIError]]:
        data, err = self.unsent.delete(f"/templates/{template_id}")
        return (data, err)  # type: ignore[return-value]


from .unsent import unsent  # noqa: E402
