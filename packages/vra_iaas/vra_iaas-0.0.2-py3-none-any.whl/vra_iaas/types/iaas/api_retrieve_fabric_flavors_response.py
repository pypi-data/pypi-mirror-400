# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["APIRetrieveFabricFlavorsResponse", "Content"]


class Content(BaseModel):
    """Represents a fabric flavor from the corresponding cloud end-point"""

    id: Optional[str] = None
    """The internal identification used by the corresponding cloud end-point"""

    boot_disk_size_in_mb: Optional[int] = FieldInfo(alias="bootDiskSizeInMB", default=None)
    """Size of the boot disk (in megabytes). Not populated when inapplicable."""

    core_count: Optional[int] = FieldInfo(alias="coreCount", default=None)
    """Number of Core per Socket. Not populated when inapplicable."""

    cpu_count: Optional[int] = FieldInfo(alias="cpuCount", default=None)
    """Number of CPU cores. Not populated when inapplicable."""

    data_disk_max_count: Optional[int] = FieldInfo(alias="dataDiskMaxCount", default=None)
    """Number of data disks. Not populated when inapplicable."""

    data_disk_size_in_mb: Optional[int] = FieldInfo(alias="dataDiskSizeInMB", default=None)
    """Size of the data disks (in megabytes). Not populated when inapplicable."""

    memory_in_mb: Optional[int] = FieldInfo(alias="memoryInMB", default=None)
    """Total amount of memory (in megabytes). Not populated when inapplicable."""

    name: Optional[str] = None
    """The value of the instance type in the corresponding cloud."""

    network_type: Optional[str] = FieldInfo(alias="networkType", default=None)
    """The type of network supported by this instance type.

    Not populated when inapplicable.
    """

    storage_type: Optional[str] = FieldInfo(alias="storageType", default=None)
    """The type of storage supported by this instance type.

    Not populated when inapplicable.
    """


class APIRetrieveFabricFlavorsResponse(BaseModel):
    """State object representing a query result of fabric flavors."""

    content: Optional[List[Content]] = None
    """List of content items"""

    number_of_elements: Optional[int] = FieldInfo(alias="numberOfElements", default=None)
    """Number of elements in the current page"""

    total_elements: Optional[int] = FieldInfo(alias="totalElements", default=None)
    """Total number of elements. In some cases the field may not be populated"""
