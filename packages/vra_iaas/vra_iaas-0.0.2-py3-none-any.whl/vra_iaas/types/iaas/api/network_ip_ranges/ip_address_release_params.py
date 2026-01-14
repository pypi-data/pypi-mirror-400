# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ....._types import SequenceNotStr
from ....._utils import PropertyInfo

__all__ = ["IPAddressReleaseParams"]


class IPAddressReleaseParams(TypedDict, total=False):
    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    ip_addresses: Annotated[SequenceNotStr[str], PropertyInfo(alias="ipAddresses")]
    """A set of ip addresses IPv4 or IPv6."""
