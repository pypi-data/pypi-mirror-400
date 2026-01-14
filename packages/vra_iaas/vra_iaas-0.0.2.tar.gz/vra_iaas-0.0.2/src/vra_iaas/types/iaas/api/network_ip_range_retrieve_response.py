# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .tag import Tag
from ...._models import BaseModel

__all__ = ["NetworkIPRangeRetrieveResponse", "_Links", "Link"]


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


class NetworkIPRangeRetrieveResponse(BaseModel):
    """
    State object representing an internal IP address range for a Fabric Network.<br>**HATEOAS** links:<br>**region** - Region - Region for the network.<br>**self** - NetworkIPRange - Self link to this IP address range
    """

    id: str
    """The id of this resource instance"""

    api_links: _Links = FieldInfo(alias="_links")
    """HATEOAS of the entity"""

    end_ip_address: str = FieldInfo(alias="endIPAddress")
    """End IP address of the range."""

    start_ip_address: str = FieldInfo(alias="startIPAddress")
    """Start IP address of the range."""

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """Date when the entity was created. The date is in ISO 8601 and UTC."""

    description: Optional[str] = None
    """A human-friendly description."""

    external_id: Optional[str] = FieldInfo(alias="externalId", default=None)
    """External entity Id on the provider side."""

    ip_version: Optional[Literal["IPv4", "IPv6"]] = FieldInfo(alias="ipVersion", default=None)
    """IP address version: IPv4 or IPv6. Default: IPv4."""

    name: Optional[str] = None
    """A human-friendly name used as an identifier in APIs that support this option."""

    number_of_allocated_ips: Optional[int] = FieldInfo(alias="numberOfAllocatedIPs", default=None)
    """Number of IP addresses in range that are allocated."""

    number_of_available_ips: Optional[int] = FieldInfo(alias="numberOfAvailableIPs", default=None)
    """Number of IP addresses in range that are available."""

    number_of_released_ips: Optional[int] = FieldInfo(alias="numberOfReleasedIPs", default=None)
    """Number of IP addresses in range that have been released but are not available."""

    number_of_system_allocated_ips: Optional[int] = FieldInfo(alias="numberOfSystemAllocatedIPs", default=None)
    """Number of IP addresses allocated by system."""

    number_of_user_allocated_ips: Optional[int] = FieldInfo(alias="numberOfUserAllocatedIPs", default=None)
    """Number of IP addresses allocated by user."""

    org_id: Optional[str] = FieldInfo(alias="orgId", default=None)
    """The id of the organization this entity belongs to."""

    owner: Optional[str] = None
    """Email of the user or display name of the group that owns the entity."""

    owner_type: Optional[str] = FieldInfo(alias="ownerType", default=None)
    """Type of a owner(user/ad_group) that owns the entity."""

    tags: Optional[List[Tag]] = None
    """A set of tag keys and optional values that were set on this resource instance."""

    total_number_of_ips: Optional[int] = FieldInfo(alias="totalNumberOfIPs", default=None)
    """Total number of IP addresses in range."""

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""
