# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["BlockDeviceUpdateParams"]


class BlockDeviceUpdateParams(TypedDict, total=False):
    capacity_in_gb: Required[Annotated[int, PropertyInfo(alias="capacityInGB")]]
    """Resize Capacity in GB"""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    use_sdrs: Annotated[bool, PropertyInfo(alias="useSdrs")]
    """Only applicable for vSphere block-devices deployed on SDRS cluster.

    If set to true, SDRS Recommendation will be used for resize operation.
    """
