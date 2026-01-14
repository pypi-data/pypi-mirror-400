# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo
from .tag_param import TagParam

__all__ = ["FabricComputeUpdateParams"]


class FabricComputeUpdateParams(TypedDict, total=False):
    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    maximum_allowed_cpu_allocation_percent: Annotated[int, PropertyInfo(alias="maximumAllowedCpuAllocationPercent")]
    """
    What percent of the total available vcPu on the compute will be used for VM
    provisioning.This value can be more than 100. e.g. If the compute has 100 vCPUs
    and this value is set to80, then VMware Aria Automation will act as if this
    compute has only 80 vCPUs. If it is 120, then VMware Aria Automation will act as
    if this compute has 120 vCPUs thus allowing 20 vCPUs overallocation. Applies
    only for private cloud computes.
    """

    maximum_allowed_memory_allocation_percent: Annotated[
        int, PropertyInfo(alias="maximumAllowedMemoryAllocationPercent")
    ]
    """
    What percent of the total available memory on the compute will be used for VM
    provisioning.This value can be more than 100. e.g. If the compute has 100gb of
    memory and this value is set to80, then VMware Aria Automation will act as if
    this compute has only 80gb. If it is 120, then VMware Aria Automation will act
    as if this compute has 120gb thus allowing 20gb overallocation. Applies only for
    private cloud computes.
    """

    tags: Iterable[TagParam]
    """A set of tag keys and optional values that were set on this resource instance."""
