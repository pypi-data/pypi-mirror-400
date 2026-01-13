"""Campaign resource client using TypedDict shapes (no Pydantic)."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from .legacy_types import APIError
from .types import (
    CampaignsPostRequest,
    CampaignsPostResponse,
    CampaignsGetResponse,
    CampaignsCampaignIdGetResponse,
    CampaignsCampaignIdSchedulePostRequest,
    CampaignsCampaignIdSchedulePostResponse,
    CampaignsCampaignIdPausePostResponse,
    CampaignsCampaignIdResumePostResponse,
)


class Campaigns:
    """Client for `/campaigns` endpoints."""

    def __init__(self, unsent: "unsent") -> None:
        self.unsent = unsent

    def list(self) -> Tuple[Optional[CampaignsGetResponse], Optional[APIError]]:
        data, err = self.unsent.get("/campaigns")
        return (data, err)  # type: ignore[return-value]

    def create(
        self, payload: Union[CampaignsPostRequest, Dict[str, Any]]
    ) -> Tuple[Optional[CampaignsPostResponse], Optional[APIError]]:
        body = payload
        if hasattr(payload, "model_dump"):
            body = payload.model_dump(by_alias=True, exclude_none=True) # type: ignore
        
        data, err = self.unsent.post(
            "/campaigns",
            body,
        )
        return (data, err)  # type: ignore[return-value]

    def get(self, campaign_id: str) -> Tuple[Optional[CampaignsCampaignIdGetResponse], Optional[APIError]]:
        data, err = self.unsent.get(f"/campaigns/{campaign_id}")
        return (data, err)  # type: ignore[return-value]

    def schedule(
        self, campaign_id: str, payload: Union[CampaignsCampaignIdSchedulePostRequest, Dict[str, Any]]
    ) -> Tuple[Optional[CampaignsCampaignIdSchedulePostResponse], Optional[APIError]]:
        body = payload
        if hasattr(payload, "model_dump"):
            body = payload.model_dump(by_alias=True, exclude_none=True) # type: ignore

        data, err = self.unsent.post(
            f"/campaigns/{campaign_id}/schedule",
            body,
        )
        return (data, err)  # type: ignore[return-value]

    def pause(
        self, campaign_id: str
    ) -> Tuple[Optional[CampaignsCampaignIdPausePostResponse], Optional[APIError]]:
        data, err = self.unsent.post(
            f"/campaigns/{campaign_id}/pause",
            {},
        )
        return (data, err)  # type: ignore[return-value]

    def resume(
        self, campaign_id: str
    ) -> Tuple[Optional[CampaignsCampaignIdResumePostResponse], Optional[APIError]]:
        data, err = self.unsent.post(
            f"/campaigns/{campaign_id}/resume",
            {},
        )
        return (data, err)  # type: ignore[return-value]


from .unsent import unsent  # noqa: E402  pylint: disable=wrong-import-position
