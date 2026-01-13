"""Email resource client using TypedDict shapes (no Pydantic)."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from .legacy_types import APIError, Email
from .types import (
    EmailsPostRequest,
    EmailsPostResponse,
    EmailsBatchPostRequest,
    EmailsBatchPostResponse,
    EmailsEmailIdCancelPostResponse,
    EmailsEmailIdPatchRequest,
    EmailsEmailIdPatchResponse,
)


class Emails:
    """Client for `/emails` endpoints."""

    def __init__(self, unsent: "unsent") -> None:
        self.unsent = unsent

    # Basic operations -------------------------------------------------
    def send(self, payload: EmailsPostRequest) -> Tuple[Optional[EmailsPostResponse], Optional[APIError]]:
        """Alias for :meth:`create`."""
        return self.create(payload)

    def create(self, payload: Union[EmailsPostRequest, Dict[str, Any]]) -> Tuple[Optional[EmailsPostResponse], Optional[APIError]]:
        if isinstance(payload, dict):
            # If dict is passed, try to validate against model or just pass it
            pass
        elif hasattr(payload, "model_dump"):
            payload = payload.model_dump(by_alias=True, exclude_none=True)

        # Normalize fields - payload is now a dict
        body: Dict[str, Any] = dict(payload) # type: ignore

        # Support accidental 'from_' usage
        if "from_" in body and "from" not in body:
            body["from"] = body.pop("from_")
        # Convert scheduledAt to ISO 8601 if datetime
        if isinstance(body.get("scheduledAt"), datetime):
            body["scheduledAt"] = body["scheduledAt"].isoformat()

        data, err = self.unsent.post("/emails", body)
        return (data, err)  # type: ignore[return-value]

    def batch(self, payload: Union[EmailsBatchPostRequest, Sequence[Dict[str, Any]]]) -> Tuple[Optional[EmailsBatchPostResponse], Optional[APIError]]:
        items: List[Dict[str, Any]] = []
        
        # Handle Pydantic RootModel
        input_payload = payload
        if hasattr(payload, "model_dump"):
             # It's expected to be a RootModel[List[Any]] but check just in case
             input_payload = payload.root # type: ignore

        for item in input_payload:
            d = item
            if hasattr(item, "model_dump"):
                d = item.model_dump(by_alias=True, exclude_none=True)
            else:
                d = dict(d) # type: ignore

            if "from_" in d and "from" not in d:
                d["from"] = d.pop("from_")
            if isinstance(d.get("scheduledAt"), datetime):
                d["scheduledAt"] = d["scheduledAt"].isoformat()
            items.append(d)
        
        data, err = self.unsent.post("/emails/batch", items)
        return (data, err)  # type: ignore[return-value]

    def get(self, email_id: str) -> Tuple[Optional[Email], Optional[APIError]]:
        data, err = self.unsent.get(f"/emails/{email_id}")
        return (data, err)  # type: ignore[return-value]

    def update(self, email_id: str, payload: Union[EmailsEmailIdPatchRequest, Dict[str, Any]]) -> Tuple[Optional[EmailsEmailIdPatchResponse], Optional[APIError]]:
        body: Dict[str, Any] 
        if hasattr(payload, "model_dump"):
            body = payload.model_dump(by_alias=True, exclude_none=True)
        else:
            body = dict(payload) # type: ignore
            
        if isinstance(body.get("scheduledAt"), datetime):
            body["scheduledAt"] = body["scheduledAt"].isoformat()

        data, err = self.unsent.patch(f"/emails/{email_id}", body)
        return (data, err)  # type: ignore[return-value]

    def cancel(self, email_id: str) -> Tuple[Optional[EmailsEmailIdCancelPostResponse], Optional[APIError]]:
        data, err = self.unsent.post(f"/emails/{email_id}/cancel", {})
        return (data, err)  # type: ignore[return-value]

    def list(
        self,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        domain_id: Optional[Union[str, List[str]]] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[APIError]]:
        """List emails with optional filters.
        
        Args:
            page: Page number for pagination
            limit: Number of results per page
            start_date: Filter emails from this date (ISO 8601)
            end_date: Filter emails until this date (ISO 8601)
            domain_id: Filter by domain ID (single string or list of strings)
        """
        query_params = []
        if page is not None:
            query_params.append(f"page={page}")
        if limit is not None:
            query_params.append(f"limit={limit}")
        if start_date is not None:
            query_params.append(f"startDate={start_date}")
        if end_date is not None:
            query_params.append(f"endDate={end_date}")
        if domain_id is not None:
            if isinstance(domain_id, list):
                for did in domain_id:
                    query_params.append(f"domainId={did}")
            else:
                query_params.append(f"domainId={domain_id}")

        query_string = "&".join(query_params) if query_params else ""
        path = f"/emails?{query_string}" if query_string else "/emails"
        data, err = self.unsent.get(path)
        return (data, err)  # type: ignore[return-value]

    def get_complaints(
        self,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[APIError]]:
        """Get email complaints with pagination.
        
        Args:
            page: Page number for pagination
            limit: Number of results per page
        """
        query_params = []
        if page is not None:
            query_params.append(f"page={page}")
        if limit is not None:
            query_params.append(f"limit={limit}")

        query_string = "&".join(query_params) if query_params else ""
        path = f"/emails/complaints?{query_string}" if query_string else "/emails/complaints"
        data, err = self.unsent.get(path)
        return (data, err)  # type: ignore[return-value]

    def get_bounces(
        self,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[APIError]]:
        """Get email bounces with pagination.
        
        Args:
            page: Page number for pagination
            limit: Number of results per page
        """
        query_params = []
        if page is not None:
            query_params.append(f"page={page}")
        if limit is not None:
            query_params.append(f"limit={limit}")

        query_string = "&".join(query_params) if query_params else ""
        path = f"/emails/bounces?{query_string}" if query_string else "/emails/bounces"
        data, err = self.unsent.get(path)
        return (data, err)  # type: ignore[return-value]

    def get_unsubscribes(
        self,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[APIError]]:
        """Get email unsubscribes with pagination.
        
        Args:
            page: Page number for pagination
            limit: Number of results per page
        """
        query_params = []
        if page is not None:
            query_params.append(f"page={page}")
        if limit is not None:
            query_params.append(f"limit={limit}")

        query_string = "&".join(query_params) if query_params else ""
        path = f"/emails/unsubscribes?{query_string}" if query_string else "/emails/unsubscribes"
        data, err = self.unsent.get(path)
        return (data, err)  # type: ignore[return-value]


from .unsent import unsent  # noqa: E402  pylint: disable=wrong-import-position
