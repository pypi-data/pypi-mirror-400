# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional

from pydantic import Field as FieldInfo

from ..tag import Tag
from ....._models import BaseModel

__all__ = ["DiskSnapshot", "_Links", "Link"]


class Link(BaseModel):
    """HATEOAS of the entity"""

    href: Optional[str] = None

    hrefs: Optional[List[str]] = None


class _Links(BaseModel):
    """HATEOAS of the entity"""

    empty: Optional[bool] = None

    if TYPE_CHECKING:
        # Some versions of Pydantic <2.8.0 have a bug and don’t allow assigning a
        # value to this field, so for compatibility we avoid doing it at runtime.
        __pydantic_extra__: Dict[str, Link] = FieldInfo(init=False)  # pyright: ignore[reportIncompatibleVariableOverride]

        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> Link: ...
    else:
        __pydantic_extra__: Dict[str, Link]


class DiskSnapshot(BaseModel):
    """Represents a disk snapshot"""

    id: str
    """The id of this resource instance"""

    api_links: _Links = FieldInfo(alias="_links")
    """HATEOAS of the entity"""

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """Date when the entity was created. The date is in ISO 8601 and UTC."""

    desc: Optional[str] = None
    """A human-friendly description."""

    name: Optional[str] = None
    """A human-friendly name used as an identifier in APIs that support this option."""

    org_id: Optional[str] = FieldInfo(alias="orgId", default=None)
    """The id of the organization this entity belongs to."""

    owner: Optional[str] = None
    """Email of the user or display name of the group that owns the entity."""

    owner_type: Optional[str] = FieldInfo(alias="ownerType", default=None)
    """Type of a owner(user/ad_group) that owns the entity."""

    snapshot_properties: Optional[Dict[str, str]] = FieldInfo(alias="snapshotProperties", default=None)
    """Snapshot specific properties"""

    tags: Optional[List[Tag]] = None
    """
    A set of tag keys and optional values that have to be set on the snapshot in the
    cloud. Currently supported for Azure Snapshots
    """

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""
