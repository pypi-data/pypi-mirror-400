# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional

from pydantic import Field as FieldInfo

from .tag import Tag
from ...._models import BaseModel

__all__ = ["GcpStorageProfile", "_Links", "Link"]


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


class GcpStorageProfile(BaseModel):
    """
    Defines a structure that holds list of storage policies defined for GCP for a specific region.**HATEOAS** links:<br>**region** - Region - Region for the profile.<br>**self** - GcpStorageProfile - Self link to this gcp Storage Profile
    """

    id: str
    """The id of this resource instance"""

    api_links: _Links = FieldInfo(alias="_links")
    """HATEOAS of the entity"""

    default_item: bool = FieldInfo(alias="defaultItem")
    """Indicates whether this storage profile is default or not."""

    cloud_account_id: Optional[str] = FieldInfo(alias="cloudAccountId", default=None)
    """Id of the cloud account this storage profile belongs to."""

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """Date when the entity was created. The date is in ISO 8601 and UTC."""

    description: Optional[str] = None
    """A human-friendly description."""

    external_region_id: Optional[str] = FieldInfo(alias="externalRegionId", default=None)
    """The id of the region for which this profile is defined"""

    name: Optional[str] = None
    """A human-friendly name used as an identifier in APIs that support this option."""

    org_id: Optional[str] = FieldInfo(alias="orgId", default=None)
    """The id of the organization this entity belongs to."""

    owner: Optional[str] = None
    """Email of the user or display name of the group that owns the entity."""

    owner_type: Optional[str] = FieldInfo(alias="ownerType", default=None)
    """Type of a owner(user/ad_group) that owns the entity."""

    persistent_disk_type: Optional[str] = FieldInfo(alias="persistentDiskType", default=None)
    """Indicates the type of storage device."""

    supports_encryption: Optional[bool] = FieldInfo(alias="supportsEncryption", default=None)
    """Indicates whether this storage profile supports encryption or not."""

    tags: Optional[List[Tag]] = None
    """A list of tags that represent the capabilities of this storage profile"""

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""
