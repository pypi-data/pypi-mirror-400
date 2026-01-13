"""Settings resource client."""
from __future__ import annotations

from typing import Optional, Tuple

from .legacy_types import APIError
from .types import SettingsGetResponse


class Settings:
    """Client for `/settings` endpoints."""

    def __init__(self, unsent: "unsent") -> None:
        self.unsent = unsent

    def get(self) -> Tuple[Optional[SettingsGetResponse], Optional[APIError]]:
        data, err = self.unsent.get("/settings")
        return (data, err)  # type: ignore[return-value]


from .unsent import unsent  # noqa: E402
