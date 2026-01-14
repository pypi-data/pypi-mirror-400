# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["APIRetrieveEventLogsResponse", "Content"]


class Content(BaseModel):
    """An object used to show event state logs"""

    id: str
    """The id of this resource instance"""

    description: Optional[str] = None
    """User-friendly description of the event"""

    event_log_type: Optional[str] = FieldInfo(alias="eventLogType", default=None)
    """Severity type."""

    org_id: Optional[str] = FieldInfo(alias="orgId", default=None)
    """The id of the organization this entity belongs to."""

    owner: Optional[str] = None
    """Email of the user or display name of the group that owns the entity."""

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""


class APIRetrieveEventLogsResponse(BaseModel):
    """State object representing a query result of event logs."""

    content: Optional[List[Content]] = None
    """List of content items"""

    number_of_elements: Optional[int] = FieldInfo(alias="numberOfElements", default=None)
    """Number of elements in the current page"""

    total_elements: Optional[int] = FieldInfo(alias="totalElements", default=None)
    """Total number of elements. In some cases the field may not be populated"""
