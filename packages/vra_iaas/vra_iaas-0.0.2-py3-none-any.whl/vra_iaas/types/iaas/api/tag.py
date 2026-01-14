# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["Tag"]


class Tag(BaseModel):
    """A set of tag keys and optional values that were set on this resource."""

    key: str
    """Tag's key."""

    value: str
    """Tag's value."""

    id: Optional[str] = None
    """Tag's id."""
