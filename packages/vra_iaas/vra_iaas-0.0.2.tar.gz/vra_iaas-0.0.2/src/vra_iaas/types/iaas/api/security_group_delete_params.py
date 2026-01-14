# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["SecurityGroupDeleteParams"]


class SecurityGroupDeleteParams(TypedDict, total=False):
    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    force_delete: Annotated[bool, PropertyInfo(alias="forceDelete")]
    """Controls whether this is a force delete operation.

    If true, best effort is made for deleting this security group. Use with caution
    as force deleting may cause inconsistencies between the cloud provider and
    VMware Aria Automation.
    """
