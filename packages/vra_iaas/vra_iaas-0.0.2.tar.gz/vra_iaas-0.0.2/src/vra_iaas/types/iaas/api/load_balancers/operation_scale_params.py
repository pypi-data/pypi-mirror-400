# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, Annotated, TypedDict

from ....._types import SequenceNotStr
from ....._utils import PropertyInfo
from ..tag_param import TagParam
from .route_configuration_param import RouteConfigurationParam
from ..machines.network_interface_specification_param import NetworkInterfaceSpecificationParam

__all__ = ["OperationScaleParams"]


class OperationScaleParams(TypedDict, total=False):
    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    nics: Required[Iterable[NetworkInterfaceSpecificationParam]]
    """A set of network interface specifications for this load balancer."""

    project_id: Required[Annotated[str, PropertyInfo(alias="projectId")]]
    """The id of the project the current user belongs to."""

    routes: Required[Iterable[RouteConfigurationParam]]
    """The load balancer route configuration regarding ports and protocols."""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    custom_properties: Annotated[Dict[str, str], PropertyInfo(alias="customProperties")]
    """Additional custom properties that may be used to extend this resource."""

    deployment_id: Annotated[str, PropertyInfo(alias="deploymentId")]
    """The id of the deployment that is associated with this resource"""

    description: str
    """A human-friendly description."""

    internet_facing: Annotated[bool, PropertyInfo(alias="internetFacing")]
    """
    An Internet-facing load balancer has a publicly resolvable DNS name, so it can
    route requests from clients over the Internet to the instances that are
    registered with the load balancer.
    """

    logging_level: Annotated[str, PropertyInfo(alias="loggingLevel")]
    """Defines logging level for collecting load balancer traffic logs."""

    tags: Iterable[TagParam]
    """
    A set of tag keys and optional values that should be set on any resource that is
    produced from this specification.
    """

    target_links: Annotated[SequenceNotStr[str], PropertyInfo(alias="targetLinks")]
    """A list of links to target load balancer pool members.

    Links can be to either a machine or a machine's network interface.
    """

    type: str
    """
    Define the type/variant of load balancer numbers e.g.for NSX the number virtual
    servers and pool members load balancer can host
    """
