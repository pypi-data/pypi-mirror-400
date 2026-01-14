# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .tag_param import TagParam

__all__ = ["StorageProfilesGcpUpdateParams"]


class StorageProfilesGcpUpdateParams(TypedDict, total=False):
    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    persistent_disk_type: Required[Annotated[str, PropertyInfo(alias="persistentDiskType")]]
    """Indicates the type of disk."""

    region_id: Required[Annotated[str, PropertyInfo(alias="regionId")]]
    """A link to the region that is associated with the storage profile."""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    default_item: Annotated[bool, PropertyInfo(alias="defaultItem")]
    """Indicates if a storage profile is default or not."""

    description: str
    """A human-friendly description."""

    supports_encryption: Annotated[bool, PropertyInfo(alias="supportsEncryption")]
    """Indicates whether this storage profile supports encryption or not."""

    tags: Iterable[TagParam]
    """A list of tags that represent the capabilities of this storage profile"""
