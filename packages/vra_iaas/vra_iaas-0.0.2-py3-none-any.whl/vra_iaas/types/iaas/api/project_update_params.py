# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .user_param import UserParam
from .placement_constraint_param import PlacementConstraintParam
from .projects.zone_assignment_specification_param import ZoneAssignmentSpecificationParam

__all__ = ["ProjectUpdateParams"]


class ProjectUpdateParams(TypedDict, total=False):
    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    validate_principals: Annotated[bool, PropertyInfo(alias="validatePrincipals")]
    """If true, a limit of 20 principals is enforced.

    Additionally each principal is validated in the Identity provider and important
    rules for group email formats are enforced.
    """

    administrators: Iterable[UserParam]
    """List of administrator users associated with the project.

    Only administrators can manage project's configuration.
    """

    constraints: Dict[str, Iterable[PlacementConstraintParam]]
    """
    List of storage, network and extensibility constraints to be applied when
    provisioning through this project.
    """

    custom_properties: Annotated[Dict[str, str], PropertyInfo(alias="customProperties")]
    """The project custom properties which are added to all requests in this project"""

    description: str
    """A human-friendly description."""

    machine_naming_template: Annotated[str, PropertyInfo(alias="machineNamingTemplate")]
    """The naming template to be used for machines provisioned in this project"""

    members: Iterable[UserParam]
    """List of member users associated with the project."""

    operation_timeout: Annotated[int, PropertyInfo(alias="operationTimeout")]
    """The timeout that should be used for Blueprint operations and Provisioning tasks.

    The timeout is in seconds
    """

    placement_policy: Annotated[str, PropertyInfo(alias="placementPolicy")]
    """Placement policy for the project.

    Determines how a zone will be selected for provisioning. DEFAULT, SPREAD or
    SPREAD_MEMORY.
    """

    shared_resources: Annotated[bool, PropertyInfo(alias="sharedResources")]
    """Specifies whether the resources in this projects are shared or not.

    If not set default will be used.
    """

    supervisors: Iterable[UserParam]
    """List of supervisor users associated with the project."""

    viewers: Iterable[UserParam]
    """List of viewer users associated with the project."""

    zone_assignment_configurations: Annotated[
        Iterable[ZoneAssignmentSpecificationParam], PropertyInfo(alias="zoneAssignmentConfigurations")
    ]
    """List of configurations for zone assignment to a project."""
