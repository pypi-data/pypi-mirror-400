# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .tag import Tag
from ...._models import BaseModel

__all__ = ["VsphereStorageProfile", "_Links", "Link"]


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


class VsphereStorageProfile(BaseModel):
    """
    Defines a structure that holds storage profile details defined for vSphere for a specific region.**HATEOAS** links:<br>**datastore** - FabricVsphereDatastore - Datastore for this storage profile.<br>**storage-policy** - FabricVsphereStoragePolicy - vSphere storage policy for this storage profile.<br> **region** - Region - Region for the profile.<br>**self** - VsphereStorageProfile - Self link to this vSphere storage profile.
    """

    id: str
    """The id of this resource instance"""

    api_links: _Links = FieldInfo(alias="_links")
    """HATEOAS of the entity"""

    default_item: bool = FieldInfo(alias="defaultItem")
    """Indicates if a storage profile contains default storage properties."""

    cloud_account_id: Optional[str] = FieldInfo(alias="cloudAccountId", default=None)
    """Id of the cloud account this storage profile belongs to."""

    compute_host_id: Optional[str] = FieldInfo(alias="computeHostId", default=None)
    """The compute host Id to be associated with the storage profile."""

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """Date when the entity was created. The date is in ISO 8601 and UTC."""

    description: Optional[str] = None
    """A human-friendly description."""

    disk_mode: Optional[str] = FieldInfo(alias="diskMode", default=None)
    """Type of mode for the disk"""

    disk_type: Optional[str] = FieldInfo(alias="diskType", default=None)
    """
    Disk types are specified as Standard - Simple vSphere virtual disks which cannot
    be managed independently without an attached VM. First Class - Improved version
    of standard virtual disks, designed to be fully mananged independent storage
    objects. Empty value is considered as Standard
    """

    external_region_id: Optional[str] = FieldInfo(alias="externalRegionId", default=None)
    """The id of the region for which this profile is defined"""

    limit_iops: Optional[str] = FieldInfo(alias="limitIops", default=None)
    """The upper bound for the I/O operations per second allocated for each disk."""

    name: Optional[str] = None
    """A human-friendly name used as an identifier in APIs that support this option."""

    org_id: Optional[str] = FieldInfo(alias="orgId", default=None)
    """The id of the organization this entity belongs to."""

    owner: Optional[str] = None
    """Email of the user or display name of the group that owns the entity."""

    owner_type: Optional[str] = FieldInfo(alias="ownerType", default=None)
    """Type of a owner(user/ad_group) that owns the entity."""

    priority: Optional[int] = None
    """Defines the priority of the storage profile with the highest priority being 0.

    Defaults to the value of 1.
    """

    provisioning_type: Optional[str] = FieldInfo(alias="provisioningType", default=None)
    """Type of format for the disk."""

    shares: Optional[str] = None
    """A specific number of shares assigned to each virtual machine."""

    shares_level: Optional[str] = FieldInfo(alias="sharesLevel", default=None)
    """Shares level are specified as High, Normal, Low or Custom."""

    storage_filter_type: Optional[Literal["INCLUDE_ALL", "TAG_BASED", "MANUAL"]] = FieldInfo(
        alias="storageFilterType", default=None
    )
    """
    Defines filter type for adding storage objects (datastores) to the storage
    profile. Defaults to INCLUDE_ALL.
    """

    supports_encryption: Optional[bool] = FieldInfo(alias="supportsEncryption", default=None)
    """Indicates whether this storage profile should support encryption or not."""

    tags: Optional[List[Tag]] = None
    """A list of tags that represent the capabilities of this storage profile"""

    tags_to_match: Optional[List[Tag]] = FieldInfo(alias="tagsToMatch", default=None)
    """
    A set of tag keys and optional values to be set on datastores to be included in
    this storage profile based on the storageFilterType: TAG_BASED.
    """

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""
