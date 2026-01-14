# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["TagDeleteParams"]


class TagDeleteParams(TypedDict, total=False):
    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    ignore_usage: Annotated[bool, PropertyInfo(alias="ignoreUsage")]
    """Controls whether this is a delete operation while ignoring tag usage.

    If true, best effort is made for deleting this tag. All the tag assignments are
    removed. Only after successfully un-assigning the tag from resources, the tag is
    deleted from VMware Aria Automation. Note, that a discovered tag, if deleted,
    gets re-enumerated in the system after next data collection cycle and also gets
    self-assigned to the discovered resources.
    """
