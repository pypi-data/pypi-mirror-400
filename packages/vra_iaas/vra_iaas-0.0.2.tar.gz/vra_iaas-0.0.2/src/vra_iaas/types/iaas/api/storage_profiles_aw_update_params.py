# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .tag_param import TagParam

__all__ = ["StorageProfilesAwUpdateParams"]


class StorageProfilesAwUpdateParams(TypedDict, total=False):
    device_type: Required[Annotated[str, PropertyInfo(alias="deviceType")]]
    """Indicates the type of storage."""

    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

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

    iops: str
    """Indicates maximum I/O operations per second."""

    supports_encryption: Annotated[bool, PropertyInfo(alias="supportsEncryption")]
    """Indicates whether this storage profile supports encryption or not."""

    tags: Iterable[TagParam]
    """A list of tags that represent the capabilities of this storage profile"""

    volume_type: Annotated[str, PropertyInfo(alias="volumeType")]
    """Indicates the type of volume associated with type of storage."""
