# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .tag_param import TagParam

__all__ = ["StorageProfilesAzureStorageProfilesAzureParams"]


class StorageProfilesAzureStorageProfilesAzureParams(TypedDict, total=False):
    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    region_id: Required[Annotated[str, PropertyInfo(alias="regionId")]]
    """The If of the region that is associated with the storage profile."""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    data_disk_caching: Annotated[str, PropertyInfo(alias="dataDiskCaching")]
    """Indicates the caching mechanism for additional disk."""

    default_item: Annotated[bool, PropertyInfo(alias="defaultItem")]
    """Indicates if a storage policy contains default storage properties."""

    description: str
    """A human-friendly description."""

    disk_encryption_set_id: Annotated[str, PropertyInfo(alias="diskEncryptionSetId")]
    """Indicates the id of disk encryption set."""

    disk_type: Annotated[str, PropertyInfo(alias="diskType")]
    """Indicates the performance tier for the storage type.

    Premium disks are SSD backed and Standard disks are HDD backed.
    """

    os_disk_caching: Annotated[str, PropertyInfo(alias="osDiskCaching")]
    """Indicates the caching mechanism for OS disk.

    Default policy for OS disks is Read/Write.
    """

    storage_account_id: Annotated[str, PropertyInfo(alias="storageAccountId")]
    """Id of a storage account where in the disk is placed."""

    supports_encryption: Annotated[bool, PropertyInfo(alias="supportsEncryption")]
    """Indicates whether this storage policy should support encryption or not."""

    tags: Iterable[TagParam]
    """
    A set of tag keys and optional values for a storage policy which define set of
    specifications for creating a disk.
    """
