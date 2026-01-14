# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._types import SequenceNotStr
from ...._utils import PropertyInfo
from .tag_param import TagParam

__all__ = ["NetworkProfileUpdateParams"]


class NetworkProfileUpdateParams(TypedDict, total=False):
    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    region_id: Required[Annotated[str, PropertyInfo(alias="regionId")]]
    """The Id of the region for which this profile is created"""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    custom_properties: Annotated[Dict[str, str], PropertyInfo(alias="customProperties")]
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

    description: str
    """A human-friendly description."""

    external_ip_block_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="externalIpBlockIds")]
    """
    List of external IP blocks coming from an external IPAM provider that can be
    used to create subnetworks inside them
    """

    fabric_network_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="fabricNetworkIds")]
    """A list of fabric network Ids which are assigned to the network profile."""

    isolated_network_cidr_prefix: Annotated[int, PropertyInfo(alias="isolatedNetworkCIDRPrefix")]
    """
    The CIDR prefix length to be used for the isolated networks that are created
    with the network profile.
    """

    isolation_external_fabric_network_id: Annotated[str, PropertyInfo(alias="isolationExternalFabricNetworkId")]
    """The Id of the fabric network used for outbound access."""

    isolation_network_domain_cidr: Annotated[str, PropertyInfo(alias="isolationNetworkDomainCIDR")]
    """CIDR of the isolation network domain."""

    isolation_network_domain_id: Annotated[str, PropertyInfo(alias="isolationNetworkDomainId")]
    """The Id of the network domain used for creating isolated networks."""

    isolation_type: Annotated[Literal["NONE", "SUBNET", "SECURITY_GROUP"], PropertyInfo(alias="isolationType")]
    """Specifies the isolation type e.g. none, subnet or security group"""

    load_balancer_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="loadBalancerIds")]
    """A list of load balancers which are assigned to the network profile."""

    security_group_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="securityGroupIds")]
    """A list of security group Ids which are assigned to the network profile."""

    tags: Iterable[TagParam]
    """
    A set of tag keys and optional values that should be set on any resource that is
    produced from this specification.
    """
