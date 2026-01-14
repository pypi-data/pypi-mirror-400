# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo
from .tag_param import TagParam

__all__ = ["FabricVsphereDatastoreUpdateParams"]


class FabricVsphereDatastoreUpdateParams(TypedDict, total=False):
    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    allocated_non_disk_storage_space_bytes: Annotated[int, PropertyInfo(alias="allocatedNonDiskStorageSpaceBytes")]
    """
    What byte amount is the space occupied by items that are NOT disks on the data
    store.This property is NOT calculated or updated by VMware Aria Automation. It
    is a static config propertypopulated by the customer if it is needed (e.g. in
    the case of a big content library).
    """

    maximum_allowed_storage_allocation_percent: Annotated[
        int, PropertyInfo(alias="maximumAllowedStorageAllocationPercent")
    ]
    """
    What percent of the total available storage on the datastore will be used for
    disk provisioning.This value can be more than 100. e.g. If the datastore has
    100gb of storage and this value is set to 80, then VMware Aria Automation will
    act as if this datastore has only 80gb. If it is 120, then VMware Aria
    Automation will act as if this datastore has 120g thus allowing 20gb
    overallocation.
    """

    tags: Iterable[TagParam]
    """A set of tag keys and optional values that were set on this resource instance."""
