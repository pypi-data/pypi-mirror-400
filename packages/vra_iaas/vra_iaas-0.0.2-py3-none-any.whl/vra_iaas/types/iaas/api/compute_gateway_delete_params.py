# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["ComputeGatewayDeleteParams"]


class ComputeGatewayDeleteParams(TypedDict, total=False):
    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """Controls whether this is a force delete operation.

    If true, best effort is made for deleting this compute gateway. Use with caution
    as force deleting may cause inconsistencies between the cloud provider and
    VMware Aria Automation.
    """

    force_delete: Annotated[bool, PropertyInfo(alias="forceDelete")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """
