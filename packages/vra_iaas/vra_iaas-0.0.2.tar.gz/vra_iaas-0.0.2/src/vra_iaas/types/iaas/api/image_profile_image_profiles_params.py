# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .placement_constraint_param import PlacementConstraintParam

__all__ = ["ImageProfileImageProfilesParams", "ImageMapping"]


class ImageProfileImageProfilesParams(TypedDict, total=False):
    image_mapping: Required[Annotated[Dict[str, ImageMapping], PropertyInfo(alias="imageMapping")]]
    """Image mapping defined for the corresponding region."""

    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    region_id: Required[Annotated[str, PropertyInfo(alias="regionId")]]
    """The id of the region for which this profile is created"""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    description: str
    """A human-friendly description."""


class ImageMapping(TypedDict, total=False):
    """Represents fabric image description. Used when creating image profiles."""

    id: str
    """The id of the fabric image.

    This ID could be taken from id field of response of GET /iaas/api/fabric-images
    """

    cloud_config: Annotated[str, PropertyInfo(alias="cloudConfig")]
    """Cloud config for this image.

    This cloud config will be merged during provisioning with other cloud
    configurations such as the bootConfig provided in MachineSpecification.
    """

    constraints: Iterable[PlacementConstraintParam]
    """
    Constraints that are used to drive placement policies for the image that is
    produced from this mapping.Constraint expressions are matched against tags on
    existing placement targets.
    """

    external_id: Annotated[str, PropertyInfo(alias="externalId")]
    """External entity Id. Valid if id and name are not provided."""

    name: str
    """Fabric image name.

    Valid if id not provided. This name could be taken from name field of response
    of GET /iaas/api/fabric-images
    """
