# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .tag import Tag
from ...._models import BaseModel

__all__ = ["NetworkProfile", "_Links", "Link"]


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


class NetworkProfile(BaseModel):
    """
    Represents a network Profile.<br>**HATEOAS** links:<br>**fabric-networks** - array[FabricNetwork] - Fabric networks defined in this profile.<br>**security-groups** - array[SecurityGroup] - List of security groups for this profile.<br>**network-domains** - array[NetworkDomain] - List of network domains for this profile.<br>**isolated-external-fabric-networks** - array[FabricNetwork] - Isolated external fabric networks in this profile.<br>**self** - NetowrkProfile - Self link to this network profile
    """

    id: str
    """The id of this resource instance"""

    api_links: _Links = FieldInfo(alias="_links")
    """HATEOAS of the entity"""

    cloud_account_id: Optional[str] = FieldInfo(alias="cloudAccountId", default=None)
    """Id of the cloud account this profile belongs to."""

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """Date when the entity was created. The date is in ISO 8601 and UTC."""

    custom_properties: Optional[Dict[str, str]] = FieldInfo(alias="customProperties", default=None)
    """
    Additional properties that may be used to extend the Network Profile object that
    is produced from this specification. For isolationType security group,
    datastoreId identifies the Compute Resource Edge datastore. computeCluster and
    resourcePoolId identify the Compute Resource Edge cluster. For isolationType
    subnet, distributedLogicalRouterStateLink identifies the on-demand network
    distributed local router (NSX-V only). For isolationType subnet,
    tier0LogicalRouterStateLink identifies the on-demand network tier-0 logical
    router (NSX-T only). onDemandNetworkIPAssignmentType identifies the on-demand
    network IP range assignment type static, dynamic, or mixed.
    """

    description: Optional[str] = None
    """A human-friendly description."""

    external_region_id: Optional[str] = FieldInfo(alias="externalRegionId", default=None)
    """The id of the region for which this profile is defined"""

    isolated_network_cidr_prefix: Optional[int] = FieldInfo(alias="isolatedNetworkCIDRPrefix", default=None)
    """
    The CIDR prefix length to be used for the isolated networks that are created
    with the network profile.
    """

    isolation_network_domain_cidr: Optional[str] = FieldInfo(alias="isolationNetworkDomainCIDR", default=None)
    """CIDR of the isolation network domain."""

    isolation_type: Optional[Literal["NONE", "SUBNET", "SECURITY_GROUP"]] = FieldInfo(
        alias="isolationType", default=None
    )
    """Specifies the isolation type e.g. none, subnet or security group"""

    name: Optional[str] = None
    """A human-friendly name used as an identifier in APIs that support this option."""

    org_id: Optional[str] = FieldInfo(alias="orgId", default=None)
    """The id of the organization this entity belongs to."""

    owner: Optional[str] = None
    """Email of the user or display name of the group that owns the entity."""

    owner_type: Optional[str] = FieldInfo(alias="ownerType", default=None)
    """Type of a owner(user/ad_group) that owns the entity."""

    tags: Optional[List[Tag]] = None
    """A set of tag keys and optional values that were set on this Network Profile."""

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""
