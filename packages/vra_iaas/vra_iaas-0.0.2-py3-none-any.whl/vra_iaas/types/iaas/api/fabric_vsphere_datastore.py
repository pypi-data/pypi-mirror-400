# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional

from pydantic import Field as FieldInfo

from .tag import Tag
from ...._models import BaseModel

__all__ = ["FabricVsphereDatastore", "_Links", "Link"]


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


class FabricVsphereDatastore(BaseModel):
    """
    Represents a structure that holds details of vSphere datastore.<br>**HATEOAS** links:<br>**self** - FabricVsphereDatastore - Self link to this data store
    """

    id: str
    """The id of this resource instance"""

    api_links: _Links = FieldInfo(alias="_links")
    """HATEOAS of the entity"""

    allocated_non_disk_storage_space_bytes: Optional[int] = FieldInfo(
        alias="allocatedNonDiskStorageSpaceBytes", default=None
    )
    """
    What byte amount is the space occupied by items that are NOT disks on the data
    store.This property is NOT calculated or updated by VMware Aria Automation. It
    is a static config propertypopulated by the customer if it is needed (e.g. in
    the case of a big content library).
    """

    cloud_account_ids: Optional[List[str]] = FieldInfo(alias="cloudAccountIds", default=None)
    """Set of ids of the cloud accounts this entity belongs to."""

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """Date when the entity was created. The date is in ISO 8601 and UTC."""

    description: Optional[str] = None
    """A human-friendly description."""

    external_id: Optional[str] = FieldInfo(alias="externalId", default=None)
    """External entity Id on the provider side."""

    external_region_id: Optional[str] = FieldInfo(alias="externalRegionId", default=None)
    """Id of datacenter in which the datastore is present."""

    free_size_gb: Optional[str] = FieldInfo(alias="freeSizeGB", default=None)
    """Indicates free size available in datastore."""

    maximum_allowed_storage_allocation_percent: Optional[int] = FieldInfo(
        alias="maximumAllowedStorageAllocationPercent", default=None
    )
    """
    What percent of the total available storage on the datastore will be used for
    disk provisioning.This value can be more than 100. e.g. If the datastore has
    100gb of storage and this value is set to 80, then VMware Aria Automation will
    act as if this datastore has only 80gb. If it is 120, then VMware Aria
    Automation will act as if this datastore has 120g thus allowing 20gb
    overallocation.
    """

    name: Optional[str] = None
    """A human-friendly name used as an identifier in APIs that support this option."""

    org_id: Optional[str] = FieldInfo(alias="orgId", default=None)
    """The id of the organization this entity belongs to."""

    owner: Optional[str] = None
    """Email of the user or display name of the group that owns the entity."""

    owner_type: Optional[str] = FieldInfo(alias="ownerType", default=None)
    """Type of a owner(user/ad_group) that owns the entity."""

    tags: Optional[List[Tag]] = None
    """
    A set of tag keys and optional values that were set on this datastore /
    datastore cluster.
    """

    type: Optional[str] = None
    """Type of datastore."""

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""
