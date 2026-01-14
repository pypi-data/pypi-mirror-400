# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ....._types import SequenceNotStr
from ....._utils import PropertyInfo

__all__ = ["IPAddressAllocateParams"]


class IPAddressAllocateParams(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    description: str
    """Description"""

    ip_addresses: Annotated[SequenceNotStr[str], PropertyInfo(alias="ipAddresses")]
    """A set of ip addresses IPv4 or IPv6."""

    number_of_ips: Annotated[int, PropertyInfo(alias="numberOfIps")]
    """Number of ip addresses to allocate from the network ip range."""
