# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional

from pydantic import Field as FieldInfo

from .tag import Tag
from ...._models import BaseModel

__all__ = ["FabricCompute", "_Links", "Link"]


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


class FabricCompute(BaseModel):
    """
    Represents a compute which is an entity on the cloud provider side that can be used to provision resources in. It could be an availability zone in a public cloud, cluster, host or resource pool in vSphere
    """

    id: str
    """The id of this resource instance"""

    external_region_id: str = FieldInfo(alias="externalRegionId")
    """The external regionId of the compute"""

    api_links: Optional[_Links] = FieldInfo(alias="_links", default=None)
    """HATEOAS of the entity"""

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """Date when the entity was created. The date is in ISO 8601 and UTC."""

    custom_properties: Optional[Dict[str, str]] = FieldInfo(alias="customProperties", default=None)
    """Custom properties of the compute instance"""

    description: Optional[str] = None
    """A human-friendly description."""

    external_id: Optional[str] = FieldInfo(alias="externalId", default=None)
    """External entity Id on the provider side."""

    external_zone_id: Optional[str] = FieldInfo(alias="externalZoneId", default=None)
    """The external zoneId of the compute."""

    lifecycle_state: Optional[str] = FieldInfo(alias="lifecycleState", default=None)
    """Lifecycle status of the compute instance"""

    maximum_allowed_cpu_allocation_percent: Optional[int] = FieldInfo(
        alias="maximumAllowedCpuAllocationPercent", default=None
    )
    """
    What percent of the total available vCPU on the compute will be used for VM
    provisioning. This value can be more than 100. e.g. If the compute has 100 vCPUs
    and this value is set to 80, then VMware Aria Automation will act as if this
    compute has only 80 vCPUs. If it is 120, then VMware Aria Automation will act as
    if this compute has 120 vCPUs thus allowing 20 vCPU overallocation. Applies only
    for private cloud computes.
    """

    maximum_allowed_memory_allocation_percent: Optional[int] = FieldInfo(
        alias="maximumAllowedMemoryAllocationPercent", default=None
    )
    """
    What percent of the total available memory on the compute will be used for VM
    provisioning. This value can be more than 100. e.g. If the compute has 100gb of
    memory and this value is set to 80, then VMware Aria Automation will act as if
    this compute has only 80gb. If it is 120, then VMware Aria Automation will act
    as if this compute has 120gb thus allowing 20gb overallocation. Applies only for
    private cloud computes.
    """

    name: Optional[str] = None
    """A human-friendly name used as an identifier in APIs that support this option."""

    org_id: Optional[str] = FieldInfo(alias="orgId", default=None)
    """The id of the organization this entity belongs to."""

    owner: Optional[str] = None
    """Email of the user or display name of the group that owns the entity."""

    owner_type: Optional[str] = FieldInfo(alias="ownerType", default=None)
    """Type of a owner(user/ad_group) that owns the entity."""

    power_state: Optional[str] = FieldInfo(alias="powerState", default=None)
    """Power state of compute instance"""

    tags: Optional[List[Tag]] = None
    """A set of tag keys and optional values that were set on this resource instance."""

    type: Optional[str] = None
    """Type of the compute instance"""

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""
