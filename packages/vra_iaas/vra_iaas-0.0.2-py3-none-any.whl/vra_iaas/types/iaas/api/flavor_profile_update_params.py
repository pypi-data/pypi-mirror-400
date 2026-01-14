# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["FlavorProfileUpdateParams", "FlavorMapping"]


class FlavorProfileUpdateParams(TypedDict, total=False):
    flavor_mapping: Required[Annotated[Dict[str, FlavorMapping], PropertyInfo(alias="flavorMapping")]]
    """
    Map between global fabric flavor keys <String> and fabric flavor descriptions
    <FabricFlavorDescription>
    """

    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    include_cores: Annotated[bool, PropertyInfo(alias="includeCores")]
    """If set to true will include cores in response."""

    description: str
    """A human-friendly description."""


class FlavorMapping(TypedDict, total=False):
    """Represents fabric flavor instance type description.

    Used when creating flavor profiles.
    """

    id: str
    """The id of the instance type in the corresponding cloud."""

    core_count: Annotated[int, PropertyInfo(alias="coreCount")]
    """Number of Cores per Socket.

    Mandatory for private clouds such as vSphere. Not populated when inapplicable.
    """

    cpu_count: Annotated[int, PropertyInfo(alias="cpuCount")]
    """Number of CPU cores.

    Mandatory for private clouds such as vSphere. Not populated when inapplicable.
    """

    memory_in_mb: Annotated[int, PropertyInfo(alias="memoryInMB")]
    """Total amount of memory (in megabytes).

    Mandatory for private clouds such as vSphere. Not populated when inapplicable.
    """

    name: str
    """The value of the instance type in the corresponding cloud.

    Valid and mandatory for public clouds
    """
