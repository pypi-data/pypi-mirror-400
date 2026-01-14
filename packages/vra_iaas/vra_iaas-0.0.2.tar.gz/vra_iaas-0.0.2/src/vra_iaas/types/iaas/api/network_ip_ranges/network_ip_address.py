# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ....._models import BaseModel

__all__ = ["NetworkIPAddress", "_Links", "Link"]


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


class NetworkIPAddress(BaseModel):
    """
    State object representing an IP address.<br>**HATEOAS** links:<br>**self** - NetworkIPAddress - Self link to this IP address<br>**network-ip-range** - Network IP Range - Network IP Range that the ip address belongs to.<br>**connected-resource** - Connected Resource - Resource that the ip address is connected to.
    """

    id: str
    """The id of this resource instance"""

    api_links: _Links = FieldInfo(alias="_links")
    """HATEOAS of the entity"""

    ip_address: str = FieldInfo(alias="ipAddress")
    """IP address."""

    ip_address_decimal_value: int = FieldInfo(alias="ipAddressDecimalValue")
    """Decimal value of the ip address."""

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """Date when the entity was created. The date is in ISO 8601 and UTC."""

    description: Optional[str] = None
    """A human-friendly description."""

    external_id: Optional[str] = FieldInfo(alias="externalId", default=None)
    """External entity Id on the provider side."""

    ip_address_status: Optional[Literal["ALLOCATED", "RELEASED", "AVAILABLE", "UNREGISTERED"]] = FieldInfo(
        alias="ipAddressStatus", default=None
    )
    """IP address status"""

    ip_allocation_type: Optional[Literal["SYSTEM", "USER", "NONE"]] = FieldInfo(alias="ipAllocationType", default=None)
    """IP Allocation type"""

    ip_version: Optional[Literal["IPv4", "IPv6"]] = FieldInfo(alias="ipVersion", default=None)
    """IP address version: IPv4 or IPv6. Default: IPv4."""

    name: Optional[str] = None
    """A human-friendly name used as an identifier in APIs that support this option."""

    org_id: Optional[str] = FieldInfo(alias="orgId", default=None)
    """The id of the organization this entity belongs to."""

    owner: Optional[str] = None
    """Email of the user or display name of the group that owns the entity."""

    owner_type: Optional[str] = FieldInfo(alias="ownerType", default=None)
    """Type of a owner(user/ad_group) that owns the entity."""

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""
