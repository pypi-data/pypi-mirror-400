# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional

from pydantic import Field as FieldInfo

from .tag import Tag
from ...._models import BaseModel

__all__ = ["FabricNetworkVsphere", "_Links", "Link"]


class Link(BaseModel):
    """HATEOAS of the entity"""

    href: Optional[str] = None

    hrefs: Optional[List[str]] = None


class _Links(BaseModel):
    """HATEOAS of the entity"""

    empty: Optional[bool] = None

    if TYPE_CHECKING:
        # Some versions of Pydantic <2.8.0 have a bug and don’t allow assigning a
        # value to this field, so for compatibility we avoid doing it at runtime.
        __pydantic_extra__: Dict[str, Link] = FieldInfo(init=False)  # pyright: ignore[reportIncompatibleVariableOverride]

        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> Link: ...
    else:
        __pydantic_extra__: Dict[str, Link]


class FabricNetworkVsphere(BaseModel):
    """
    State object representing a vSphere network on a external cloud provider.<br>**domain** - domain for the vSphere network.<br>**defaultGateway** - default IPv4 gateway for the vSphere network.<br>**defaultIPv6Gateway** - default IPv6 gateway for the vSphere network.<br>**dnsServerAddresses** - list of dns server address for the vSphere network.<br>**dnsSearchDomains** - ist of dns search domains for the vSphere network
    """

    id: str
    """The id of this resource instance"""

    api_links: _Links = FieldInfo(alias="_links")
    """HATEOAS of the entity"""

    cidr: Optional[str] = None
    """Network CIDR to be used."""

    cloud_account_ids: Optional[List[str]] = FieldInfo(alias="cloudAccountIds", default=None)
    """Set of ids of the cloud accounts this entity belongs to."""

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """Date when the entity was created. The date is in ISO 8601 and UTC."""

    custom_properties: Optional[Dict[str, str]] = FieldInfo(alias="customProperties", default=None)
    """Custom properties of the fabric network instance"""

    default_gateway: Optional[str] = FieldInfo(alias="defaultGateway", default=None)
    """IPv4 default gateway to be used."""

    default_ipv6_gateway: Optional[str] = FieldInfo(alias="defaultIpv6Gateway", default=None)
    """IPv6 default gateway to be used."""

    description: Optional[str] = None
    """A human-friendly description."""

    dns_search_domains: Optional[List[str]] = FieldInfo(alias="dnsSearchDomains", default=None)
    """A list of DNS search domains that were set on this resource instance."""

    dns_server_addresses: Optional[List[str]] = FieldInfo(alias="dnsServerAddresses", default=None)
    """A list of DNS server addresses that were set on this resource instance."""

    domain: Optional[str] = None
    """Domain value."""

    external_id: Optional[str] = FieldInfo(alias="externalId", default=None)
    """External entity Id on the provider side."""

    external_region_id: Optional[str] = FieldInfo(alias="externalRegionId", default=None)
    """The id of the region for which this network is defined."""

    ipv6_cidr: Optional[str] = FieldInfo(alias="ipv6Cidr", default=None)
    """Network IPv6 CIDR to be used."""

    is_default: Optional[bool] = FieldInfo(alias="isDefault", default=None)
    """Indicates whether this is the default subnet for the zone."""

    is_public: Optional[bool] = FieldInfo(alias="isPublic", default=None)
    """Indicates whether the sub-network supports public IP assignment."""

    name: Optional[str] = None
    """A human-friendly name used as an identifier in APIs that support this option."""

    network_domain_id: Optional[str] = FieldInfo(alias="networkDomainId", default=None)
    """The id of the network domain, that contains this fabric network."""

    org_id: Optional[str] = FieldInfo(alias="orgId", default=None)
    """The id of the organization this entity belongs to."""

    owner: Optional[str] = None
    """Email of the user or display name of the group that owns the entity."""

    owner_type: Optional[str] = FieldInfo(alias="ownerType", default=None)
    """Type of a owner(user/ad_group) that owns the entity."""

    tags: Optional[List[Tag]] = None
    """A set of tag keys and optional values that were set on this resource instance."""

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""
