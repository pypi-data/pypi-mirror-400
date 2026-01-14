# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .custom_naming_project import CustomNamingProject

__all__ = ["NamingListResponse", "Content"]


class Content(BaseModel):
    """Custom names"""

    id: str
    """The id of this resource instance"""

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """Date when the entity was created. The date is in ISO 8601 and UTC."""

    created_by: Optional[str] = FieldInfo(alias="createdBy", default=None)
    """Email of the user or display name of the group that created the entity."""

    name: Optional[str] = None
    """A human-friendly name used as an identifier in APIs that support this option."""

    projects: Optional[List[CustomNamingProject]] = None
    """Set of projects associated with custom name"""

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""

    updated_by: Optional[str] = FieldInfo(alias="updatedBy", default=None)
    """Email of the user or display name of the group that updated the entity."""


class NamingListResponse(BaseModel):
    """State object representing a query result of custom names"""

    content: Optional[List[Content]] = None
    """List of content items"""

    number_of_elements: Optional[int] = FieldInfo(alias="numberOfElements", default=None)
    """Number of elements in the current page"""

    total_elements: Optional[int] = FieldInfo(alias="totalElements", default=None)
    """Total number of elements. In some cases the field may not be populated"""
