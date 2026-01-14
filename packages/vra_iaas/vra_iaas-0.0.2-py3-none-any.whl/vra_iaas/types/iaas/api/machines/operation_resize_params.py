# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["OperationResizeParams"]


class OperationResizeParams(TypedDict, total=False):
    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    core_count: Annotated[str, PropertyInfo(alias="coreCount")]
    """The desired number of cores per socket to resize the Machine"""

    cpu_count: Annotated[str, PropertyInfo(alias="cpuCount")]
    """The desired number of CPUs to resize the"""

    flavor_name: Annotated[str, PropertyInfo(alias="flavorName")]
    """The desired flavor to resize the Machine."""

    memory_in_mb: Annotated[str, PropertyInfo(alias="memoryInMB")]
    """The desired memory in MBs to resize the Machine"""

    reboot_machine: Annotated[bool, PropertyInfo(alias="rebootMachine")]
    """
    Only applicable for vSphere VMs with the CPU Hot Add or Memory Hot Plug options
    enabled. If set to false, VM is resized without reboot.
    """
