# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["ZoneAssignmentSpecificationParam"]


class ZoneAssignmentSpecificationParam(TypedDict, total=False):
    """A zone assignment configuration"""

    cpu_limit: Annotated[int, PropertyInfo(alias="cpuLimit")]
    """The maximum amount of cpus that can be used by this cloud zone.

    Default is 0 (unlimited cpu).
    """

    max_number_instances: Annotated[int, PropertyInfo(alias="maxNumberInstances")]
    """The maximum number of instances that can be provisioned in this cloud zone.

    Default is 0 (unlimited instances).
    """

    memory_limit_mb: Annotated[int, PropertyInfo(alias="memoryLimitMB")]
    """The maximum amount of memory that can be used by this cloud zone.

    Default is 0 (unlimited memory).
    """

    priority: int
    """The priority of this zone in the current project.

    Lower numbers mean higher priority. Default is 0 (highest)
    """

    storage_limit_gb: Annotated[int, PropertyInfo(alias="storageLimitGB")]
    """
    Defines an upper limit on storage that can be requested from a cloud zone which
    is part of this project. Default is 0 (unlimited storage). Please note that this
    feature is supported only for vSphere cloud zones. Not valid for other cloud
    zone types.
    """

    zone_id: Annotated[str, PropertyInfo(alias="zoneId")]
    """The Cloud Zone Id"""
