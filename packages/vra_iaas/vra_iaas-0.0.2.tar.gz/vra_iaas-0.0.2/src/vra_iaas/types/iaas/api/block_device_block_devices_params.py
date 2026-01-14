# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .tag_param import TagParam
from .placement_constraint_param import PlacementConstraintParam

__all__ = ["BlockDeviceBlockDevicesParams"]


class BlockDeviceBlockDevicesParams(TypedDict, total=False):
    capacity_in_gb: Required[Annotated[int, PropertyInfo(alias="capacityInGB")]]
    """Capacity of the block device in GB."""

    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    project_id: Required[Annotated[str, PropertyInfo(alias="projectId")]]
    """The id of the project the current user belongs to."""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    constraints: Iterable[PlacementConstraintParam]
    """
    Constraints that are used to drive placement policies for the block device that
    is produced from this specification. Constraint expressions are matched against
    tags on existing placement targets.
    """

    custom_properties: Annotated[Dict[str, str], PropertyInfo(alias="customProperties")]
    """Additional custom properties that may be used to extend this resource."""

    deployment_id: Annotated[str, PropertyInfo(alias="deploymentId")]
    """The id of the deployment that is associated with this resource"""

    description: str
    """A human-friendly description."""

    disk_content_base64: Annotated[str, PropertyInfo(alias="diskContentBase64")]
    """Content of a disk, base64 encoded."""

    encrypted: bool
    """Indicates whether the block device should be encrypted or not."""

    persistent: bool
    """Indicates whether the block device survives a delete action."""

    source_reference: Annotated[str, PropertyInfo(alias="sourceReference")]
    """Reference to URI using which the block device has to be created."""

    tags: Iterable[TagParam]
    """
    A set of tag keys and optional values that should be set on any resource that is
    produced from this specification.
    """
