"""Webhook resource client.

Note: Webhooks functionality is currently under development in the API.
This module provides a placeholder implementation for when the feature becomes available.
"""
from __future__ import annotations

from typing import Optional, Tuple, Dict, Any, List

from .legacy_types import APIError


class Webhooks:
    """Client for `/webhooks` endpoints."""

    def __init__(self, unsent: "unsent") -> None:
        self.unsent = unsent

    def list(self) -> Tuple[Optional[List[Dict[str, Any]]], Optional[APIError]]:
        data, err = self.unsent.get("/webhooks")
        return (data, err)  # type: ignore[return-value]

    def create(
        self, payload: Dict[str, Any]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[APIError]]:
        data, err = self.unsent.post("/webhooks", payload)
        return (data, err)  # type: ignore[return-value]

    def get(self, webhook_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[APIError]]:
        data, err = self.unsent.get(f"/webhooks/{webhook_id}")
        return (data, err)  # type: ignore[return-value]

    def update(
        self, webhook_id: str, payload: Dict[str, Any]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[APIError]]:
        data, err = self.unsent.patch(f"/webhooks/{webhook_id}", payload)
        return (data, err)  # type: ignore[return-value]

    def delete(
        self, webhook_id: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[APIError]]:
        data, err = self.unsent.delete(f"/webhooks/{webhook_id}")
        return (data, err)  # type: ignore[return-value]


from .unsent import unsent  # noqa: E402
