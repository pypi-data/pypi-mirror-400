# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .tag import Tag
from ...._models import BaseModel
from .salt_configuration import SaltConfiguration
from .machine_boot_config import MachineBootConfig

__all__ = ["Machine", "_Links", "Link"]


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


class Machine(BaseModel):
    """
    Represents a cloud agnostic machine.<br>**HATEOAS** links:<br>**operations** - array[String] - Supported operations for the machine.<br>**network-interfaces** - array[NetworkInterface] - Network interfaces for the machine.<br>**disks** - array[MachineDisk] - disks for the machine.<br>**deployment** - Deployment - Deployment that this machine is part of.<br>**cloud-accounts** - array[CloudAccount] - Cloud accounts where this machine is provisioned.<br>**self** - Machine - Self link to this machine
    """

    id: str
    """The id of this resource instance"""

    api_links: _Links = FieldInfo(alias="_links")
    """HATEOAS of the entity"""

    external_region_id: str = FieldInfo(alias="externalRegionId")
    """The external regionId of the resource."""

    power_state: Literal["ON", "OFF", "GUEST_OFF", "UNKNOWN", "SUSPEND"] = FieldInfo(alias="powerState")
    """Power state of machine."""

    address: Optional[str] = None
    """Primary address allocated or in use by this machine.

    The actual type of the address depends on the adapter type. Typically it is
    either the public or the external IP address.
    """

    boot_config: Optional[MachineBootConfig] = FieldInfo(alias="bootConfig", default=None)
    """
    Machine boot config that will be passed to the instance that can be used to
    perform common automated configuration tasks and even run scripts after the
    instance starts.
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

    hostname: Optional[str] = None
    """Hostname associated with this machine instance."""

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

    salt_configuration: Optional[SaltConfiguration] = FieldInfo(alias="saltConfiguration", default=None)
    """
    Represents salt configuration settings that has to be applied on the machine. To
    successfully apply the configurations, remoteAccess property is mandatory.The
    supported remoteAccess authentication types are usernamePassword and
    generatedPublicPrivateKey
    """

    tags: Optional[List[Tag]] = None
    """A set of tag keys and optional values that were set on this resource."""

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""
