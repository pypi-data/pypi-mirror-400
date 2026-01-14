# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Annotated, TypedDict

from ...._types import SequenceNotStr
from ...._utils import PropertyInfo
from .tag_param import TagParam

__all__ = ["FabricNetworksVsphereUpdateParams"]


class FabricNetworksVsphereUpdateParams(TypedDict, total=False):
    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    cidr: str
    """Network CIDR to be used."""

    default_gateway: Annotated[str, PropertyInfo(alias="defaultGateway")]
    """IPv4 default gateway to be used."""

    default_ipv6_gateway: Annotated[str, PropertyInfo(alias="defaultIpv6Gateway")]
    """IPv6 default gateway to be used."""

    dns_search_domains: Annotated[SequenceNotStr[str], PropertyInfo(alias="dnsSearchDomains")]
    """A list of DNS search domains that were set on this resource instance."""

    dns_server_addresses: Annotated[SequenceNotStr[str], PropertyInfo(alias="dnsServerAddresses")]
    """A list of DNS server addresses that were set on this resource instance."""

    domain: str
    """Domain value."""

    ipv6_cidr: Annotated[str, PropertyInfo(alias="ipv6Cidr")]
    """Network IPv6 CIDR to be used."""

    is_default: Annotated[bool, PropertyInfo(alias="isDefault")]
    """Indicates whether this is the default subnet for the zone."""

    is_public: Annotated[bool, PropertyInfo(alias="isPublic")]
    """Indicates whether the sub-network supports public IP assignment."""

    tags: Iterable[TagParam]
    """A set of tag keys and optional values that were set on this resource instance."""
