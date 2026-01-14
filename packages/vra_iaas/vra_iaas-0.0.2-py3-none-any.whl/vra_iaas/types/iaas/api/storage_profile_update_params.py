# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .tag_param import TagParam
from .storage_profile_associations_param import StorageProfileAssociationsParam

__all__ = ["StorageProfileUpdateParams"]


class StorageProfileUpdateParams(TypedDict, total=False):
    default_item: Required[Annotated[bool, PropertyInfo(alias="defaultItem")]]
    """Indicates if a storage profile is a default profile."""

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

    description: str
    """A human-friendly description."""

    disk_properties: Annotated[Dict[str, str], PropertyInfo(alias="diskProperties")]
    """Map of storage properties that are to be applied on disk while provisioning."""

    disk_target_properties: Annotated[Dict[str, str], PropertyInfo(alias="diskTargetProperties")]
    """Map of storage placements to know where the disk is provisioned.

    'datastoreId' is deprecated, instead use 'storageProfileAssociations' parameter
    to associate datastores with the storage profile.
    """

    priority: int
    """Defines the priority of the storage profile with the highest priority being 0.

    Defaults to the value of 1.
    """

    storage_filter_type: Annotated[
        Literal["INCLUDE_ALL", "TAG_BASED", "MANUAL"], PropertyInfo(alias="storageFilterType")
    ]
    """
    Defines filter type for adding storage objects (datastores) to the storage
    profile. Defaults to INCLUDE_ALL. For INCLUDE_ALL and TAG_BASED all the valid
    Data stores will be associated with the priority 1.
    """

    storage_profile_associations: Annotated[
        Iterable[StorageProfileAssociationsParam], PropertyInfo(alias="storageProfileAssociations")
    ]
    """Defines a specification of Storage Profile datastore associations."""

    supports_encryption: Annotated[bool, PropertyInfo(alias="supportsEncryption")]
    """Indicates whether this storage profile supports encryption or not."""

    tags: Iterable[TagParam]
    """A list of tags that represent the capabilities of this storage profile"""

    tags_to_match: Annotated[Iterable[TagParam], PropertyInfo(alias="tagsToMatch")]
    """
    A set of tag keys and optional values to be set on datastores to be included in
    this storage profile based on the storageFilterType: TAG_BASED.
    """
