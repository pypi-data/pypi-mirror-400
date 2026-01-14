# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional

from pydantic import Field as FieldInfo

from .tag import Tag
from ...._models import BaseModel

__all__ = ["Zone", "_Links", "Link"]


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


class Zone(BaseModel):
    """Description of a compute placement zone.

    This can be used to specify a subset of compute resources within a region where machines can be placed. <br>**HATEOAS** links:<br>**region** - Region - Region for the zone.<br>**computes** - Computes - Computes for the zone. <br>**cloud-account** - CloudAccount - The cloud account that the zone belongs to.<br>**self** - Zone - Self link to this zone
    """

    id: str
    """The id of this resource instance"""

    api_links: _Links = FieldInfo(alias="_links")
    """HATEOAS of the entity"""

    cloud_account_id: Optional[str] = FieldInfo(alias="cloudAccountId", default=None)
    """Cloud account this zone belongs to."""

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """Date when the entity was created. The date is in ISO 8601 and UTC."""

    custom_properties: Optional[Dict[str, str]] = FieldInfo(alias="customProperties", default=None)
    """A list of key value pair of properties that will be used"""

    description: Optional[str] = None
    """A human-friendly description."""

    external_region_id: Optional[str] = FieldInfo(alias="externalRegionId", default=None)
    """The id of the region for which this zone is defined"""

    folder: Optional[str] = None
    """The folder relative path to the datacenter where resources are deployed to.

    If a non-existent folder name is passed, a new folder will be created in the
    respective datacenter when a machine is provisioned via the cloud zone. (only
    applicable for vSphere cloud zones)
    """

    name: Optional[str] = None
    """A human-friendly name used as an identifier in APIs that support this option."""

    org_id: Optional[str] = FieldInfo(alias="orgId", default=None)
    """The id of the organization this entity belongs to."""

    owner: Optional[str] = None
    """Email of the user or display name of the group that owns the entity."""

    owner_type: Optional[str] = FieldInfo(alias="ownerType", default=None)
    """Type of a owner(user/ad_group) that owns the entity."""

    placement_policy: Optional[str] = FieldInfo(alias="placementPolicy", default=None)
    """The placement policy for the zone."""

    tags: Optional[List[Tag]] = None
    """A set of tag keys and optional values that were set on this placement."""

    tags_to_match: Optional[List[Tag]] = FieldInfo(alias="tagsToMatch", default=None)
    """A set of tag keys and optional values for compute resource filtering."""

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""
