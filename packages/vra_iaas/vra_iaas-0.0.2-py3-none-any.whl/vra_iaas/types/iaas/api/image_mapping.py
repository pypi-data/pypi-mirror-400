# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .placement_constraint import PlacementConstraint

__all__ = [
    "ImageMapping",
    "_Links",
    "Link",
    "Mapping",
    "Mapping_Links",
    "MappingLink",
    "MappingDiskConfig",
    "MappingNetworkConfig",
]


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


class MappingLink(BaseModel):
    """HATEOAS of the entity"""

    href: Optional[str] = None

    hrefs: Optional[List[str]] = None


class Mapping_Links(BaseModel):
    """HATEOAS of the entity"""

    empty: Optional[bool] = None

    if TYPE_CHECKING:
        # Some versions of Pydantic <2.8.0 have a bug and don’t allow assigning a
        # value to this field, so for compatibility we avoid doing it at runtime.
        __pydantic_extra__: Dict[str, MappingLink] = FieldInfo(init=False)  # pyright: ignore[reportIncompatibleVariableOverride]

        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> MappingLink: ...
    else:
        __pydantic_extra__: Dict[str, MappingLink]


class MappingDiskConfig(BaseModel):
    """Represents the properties of a data disk in an image."""

    id: Optional[str] = None
    """Identifier of the disk."""

    capacity_m_bytes: Optional[int] = FieldInfo(alias="capacityMBytes", default=None)
    """Size of the disk in Mega Bytes."""

    encrypted: Optional[bool] = None
    """Encryption status of the disk."""

    persistent: Optional[bool] = None
    """Persistence capability of the disk across reboots."""


class MappingNetworkConfig(BaseModel):
    """Represents the properties of a network in an image."""

    id: Optional[str] = None
    """Network identifier"""

    name: Optional[str] = None
    """Network name"""

    resource_sub_type: Optional[str] = FieldInfo(alias="resourceSubType", default=None)
    """This is used to save network configuration resource sub type.

    For OVA/OVF use case its saved for ResourceType=10
    """


class Mapping(BaseModel):
    """
    Represents a fabric image from the corresponding cloud end-point with additional cloud configuration script that will be executed on provisioning
    """

    id: str
    """The id of this resource instance"""

    api_links: Mapping_Links = FieldInfo(alias="_links")
    """HATEOAS of the entity"""

    cloud_account_ids: Optional[List[str]] = FieldInfo(alias="cloudAccountIds", default=None)
    """Set of ids of the cloud accounts this entity belongs to."""

    cloud_account_name: Optional[str] = FieldInfo(alias="cloudAccountName", default=None)
    """Name of the cloud account this entity belongs to."""

    cloud_config: Optional[str] = FieldInfo(alias="cloudConfig", default=None)
    """Cloud config for this image.

    This cloud config will be merged during provisioning with other cloud
    configurations such as the bootConfig provided in MachineSpecification.
    """

    constraints: Optional[List[PlacementConstraint]] = None
    """
    Constraints that are used to drive placement policies for the image that is
    produced from this mapping.Constraint expressions are matched against tags on
    existing placement targets.
    """

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """Date when the entity was created. The date is in ISO 8601 and UTC."""

    custom_properties: Optional[Dict[str, str]] = FieldInfo(alias="customProperties", default=None)
    """Additional properties that may be used to extend the base type."""

    description: Optional[str] = None
    """A human-friendly description."""

    disk_configs: Optional[List[MappingDiskConfig]] = FieldInfo(alias="diskConfigs", default=None)
    """List of disk config for the image"""

    external_id: Optional[str] = FieldInfo(alias="externalId", default=None)
    """External entity Id on the provider side."""

    external_region_id: Optional[str] = FieldInfo(alias="externalRegionId", default=None)
    """The regionId of the image"""

    external_region_name: Optional[str] = FieldInfo(alias="externalRegionName", default=None)
    """The region name of the image"""

    is_private: Optional[bool] = FieldInfo(alias="isPrivate", default=None)
    """Indicates whether this fabric image is private.

    For vSphere, private images are considered to be templates and snapshots and
    public are Content Library Items
    """

    name: Optional[str] = None
    """A human-friendly name used as an identifier in APIs that support this option."""

    network_configs: Optional[List[MappingNetworkConfig]] = FieldInfo(alias="networkConfigs", default=None)
    """List of network config for the image"""

    org_id: Optional[str] = FieldInfo(alias="orgId", default=None)
    """The id of the organization this entity belongs to."""

    os_family: Optional[str] = FieldInfo(alias="osFamily", default=None)
    """Operating System family of the image."""

    owner: Optional[str] = None
    """Email of the user or display name of the group that owns the entity."""

    owner_type: Optional[str] = FieldInfo(alias="ownerType", default=None)
    """Type of a owner(user/ad_group) that owns the entity."""

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""


class ImageMapping(BaseModel):
    """
    Describes an image mapping between image key and fabric image.<br>**HATEOAS** links:<br>**region** - Region - Region for the mapping.
    """

    api_links: _Links = FieldInfo(alias="_links")
    """HATEOAS of the entity"""

    mapping: Dict[str, Mapping]
    """Image mapping defined for the particular region."""

    external_region_id: Optional[str] = FieldInfo(alias="externalRegionId", default=None)
    """The id of the region for which this mapping is defined."""
