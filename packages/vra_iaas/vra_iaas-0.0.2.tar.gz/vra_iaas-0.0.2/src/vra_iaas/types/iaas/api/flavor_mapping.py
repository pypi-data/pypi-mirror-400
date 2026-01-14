# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["FlavorMapping", "_Links", "Link", "Mapping"]


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


class Mapping(BaseModel):
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


class FlavorMapping(BaseModel):
    """
    Describes a flavor mapping between a global fabric flavor key and fabric flavor.<br>**HATEOAS** links:<br>**region** - Region - Region for the mapping.
    """

    api_links: _Links = FieldInfo(alias="_links")
    """HATEOAS of the entity"""

    mapping: Dict[str, Mapping]
    """Flavors defined for the particular region. Keyed by global flavor key."""

    external_region_id: Optional[str] = FieldInfo(alias="externalRegionId", default=None)
    """The id of the region for which this mapping is defined."""
