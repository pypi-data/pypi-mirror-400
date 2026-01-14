# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._types import SequenceNotStr
from ...._utils import PropertyInfo
from .tag_param import TagParam

__all__ = ["NetworkIPRangeNetworkIPRangesParams"]


class NetworkIPRangeNetworkIPRangesParams(TypedDict, total=False):
    end_ip_address: Required[Annotated[str, PropertyInfo(alias="endIPAddress")]]
    """End IP address of the range."""

    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    start_ip_address: Required[Annotated[str, PropertyInfo(alias="startIPAddress")]]
    """Start IP address of the range."""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    description: str
    """A human-friendly description."""

    fabric_network_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="fabricNetworkIds")]
    """The Ids of the fabric networks."""

    ip_version: Annotated[Literal["IPv4", "IPv6"], PropertyInfo(alias="ipVersion")]
    """IP address version: IPv4 or IPv6. Default: IPv4."""

    tags: Iterable[TagParam]
    """A set of tag keys and optional values that were set on this resource instance."""
