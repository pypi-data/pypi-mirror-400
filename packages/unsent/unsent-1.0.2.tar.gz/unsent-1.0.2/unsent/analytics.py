"""Analytics resource client."""
from __future__ import annotations

from typing import Optional, Tuple

from .legacy_types import APIError
from .types import (
    AnalyticsGetResponse,
    AnalyticsTimeSeriesGetResponse,
    AnalyticsReputationGetResponse,
)


class Analytics:
    """Client for `/analytics` endpoints."""

    def __init__(self, unsent: "unsent") -> None:
        self.unsent = unsent

    def get_usage(self) -> Tuple[Optional[AnalyticsGetResponse], Optional[APIError]]:
        data, err = self.unsent.get("/analytics/usage")
        return (data, err)  # type: ignore[return-value]

    def get_daily_stats(
        self, start_date: str, end_date: str
    ) -> Tuple[Optional[AnalyticsTimeSeriesGetResponse], Optional[APIError]]:
        data, err = self.unsent.get(
            f"/analytics/daily-stats?startDate={start_date}&endDate={end_date}"
        )
        return (data, err)  # type: ignore[return-value]

    def get_domain_reputation(
        self, domain_id: str
    ) -> Tuple[Optional[AnalyticsReputationGetResponse], Optional[APIError]]:
        data, err = self.unsent.get(f"/analytics/domain-reputation?domainId={domain_id}")
        return (data, err)  # type: ignore[return-value]


from .unsent import unsent  # noqa: E402
