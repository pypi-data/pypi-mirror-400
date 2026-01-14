# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional

from pydantic import Field as FieldInfo

from .tag import Tag
from ...._models import BaseModel
from .load_balancers.route_configuration import RouteConfiguration

__all__ = ["LoadBalancer", "_Links", "Link"]


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


class LoadBalancer(BaseModel):
    """
    Represents a load balancer.<br>**HATEOAS** links:<br>**load-balancer-targets** - array[Machine] - List of load balancer target machines.<br>**cloud-account** - CloudAccount - Cloud account where this LB is deployed.<br>**self** - LoadBalancer - Self link to this load balancer
    """

    id: str
    """The id of this resource instance"""

    api_links: _Links = FieldInfo(alias="_links")
    """HATEOAS of the entity"""

    external_region_id: str = FieldInfo(alias="externalRegionId")
    """The external regionId of the resource."""

    routes: List[RouteConfiguration]
    """The load balancer route configuration regarding ports and protocols."""

    address: Optional[str] = None
    """Primary address allocated or in use by this load balancer.

    The address could be an in the form of a publicly resolvable DNS name or an IP
    address.
    """

    cloud_account_ids: Optional[List[str]] = FieldInfo(alias="cloudAccountIds", default=None)
    """Set of ids of the cloud accounts this resource belongs to."""

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """Date when the entity was created. The date is in ISO 8601 and UTC."""

    custom_properties: Optional[Dict[str, str]] = FieldInfo(alias="customProperties", default=None)
    """Additional properties that may be used to extend the base resource."""

    deployment_id: Optional[str] = FieldInfo(alias="deploymentId", default=None)
    """Deployment id that is associated with this resource."""

    description: Optional[str] = None
    """A human-friendly description."""

    external_id: Optional[str] = FieldInfo(alias="externalId", default=None)
    """External entity Id on the provider side."""

    external_zone_id: Optional[str] = FieldInfo(alias="externalZoneId", default=None)
    """The external zoneId of the resource."""

    logging_level: Optional[str] = FieldInfo(alias="loggingLevel", default=None)
    """Defines logging level for collecting load balancer traffic logs."""

    name: Optional[str] = None
    """A human-friendly name used as an identifier in APIs that support this option."""

    org_id: Optional[str] = FieldInfo(alias="orgId", default=None)
    """The id of the organization this entity belongs to."""

    owner: Optional[str] = None
    """Email of the user or display name of the group that owns the entity."""

    owner_type: Optional[str] = FieldInfo(alias="ownerType", default=None)
    """Type of a owner(user/ad_group) that owns the entity."""

    project_id: Optional[str] = FieldInfo(alias="projectId", default=None)
    """The id of the project this resource belongs to."""

    provisioning_status: Optional[str] = FieldInfo(alias="provisioningStatus", default=None)
    """The provisioning status of the resource.

    One of three provisioning statuses. `PROVISIONING`: The resource is being
    provisioned. `READY`: The resource is already provisioned. `SUSPEND`: The
    resource is being destroyed.
    """

    tags: Optional[List[Tag]] = None
    """A set of tag keys and optional values that were set on this resource."""

    type: Optional[str] = None
    """
    Define the type/variant of load balancer numbers e.g.for NSX the number virtual
    servers and pool members load balancer can host
    """

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""
