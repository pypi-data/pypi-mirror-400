# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .tag_param import TagParam
from .storage_profile_associations_param import StorageProfileAssociationsParam

__all__ = ["StorageProfilesVsphereUpdateParams"]


class StorageProfilesVsphereUpdateParams(TypedDict, total=False):
    default_item: Required[Annotated[bool, PropertyInfo(alias="defaultItem")]]
    """Indicates if a storage profile acts as a default storage profile for a disk."""

    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    region_id: Required[Annotated[str, PropertyInfo(alias="regionId")]]
    """The Id of the region that is associated with the storage profile."""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    compute_host_id: Annotated[str, PropertyInfo(alias="computeHostId")]
    """The compute host Id to be associated with the storage profile."""

    datastore_id: Annotated[str, PropertyInfo(alias="datastoreId")]
    """Id of the vSphere Datastore for placing disk and VM.

    Deprecated, instead use 'storageProfileAssociations' parameter to associate
    datastores with the storage profile.
    """

    description: str
    """A human-friendly description."""

    disk_mode: Annotated[str, PropertyInfo(alias="diskMode")]
    """Type of mode for the disk"""

    disk_type: Annotated[str, PropertyInfo(alias="diskType")]
    """Disk types are specified as

    Standard - Simple vSphere virtual disks which cannot be managed independently
    without an attached VM. First Class - Improved version of standard virtual
    disks, designed to be fully mananged independent storage objects.

    Empty value is considered as Standard
    """

    limit_iops: Annotated[str, PropertyInfo(alias="limitIops")]
    """
    The upper bound for the I/O operations per second allocated for each virtual
    disk.
    """

    priority: int
    """Defines the priority of the storage profile with the highest priority being 0.

    Defaults to the value of 1.
    """

    provisioning_type: Annotated[str, PropertyInfo(alias="provisioningType")]
    """Type of provisioning policy for the disk."""

    shares: str
    """A specific number of shares assigned to each virtual machine."""

    shares_level: Annotated[str, PropertyInfo(alias="sharesLevel")]
    """
    Shares are specified as High, Normal, Low or Custom and these values specify
    share values with a 4:2:1 ratio, respectively.
    """

    storage_filter_type: Annotated[
        Literal["INCLUDE_ALL", "TAG_BASED", "MANUAL"], PropertyInfo(alias="storageFilterType")
    ]
    """
    Defines filter type for adding storage objects (data stores) to the storage
    profile. Defaults to INCLUDE_ALL.
    """

    storage_policy_id: Annotated[str, PropertyInfo(alias="storagePolicyId")]
    """Id of the vSphere Storage Policy to be applied."""

    storage_profile_associations: Annotated[
        Iterable[StorageProfileAssociationsParam], PropertyInfo(alias="storageProfileAssociations")
    ]
    """Defines a specification of Storage Profile datastore associations."""

    supports_encryption: Annotated[bool, PropertyInfo(alias="supportsEncryption")]
    """Indicates whether this storage profile supports encryption or not."""

    tags: Iterable[TagParam]
    """A list of tags that represent the capabilities of this storage profile."""

    tags_to_match: Annotated[Iterable[TagParam], PropertyInfo(alias="tagsToMatch")]
    """
    A set of tag keys and optional values to be set on data stores to be included in
    this storage profile based on the storageFilterType: TAG_BASED.
    """
