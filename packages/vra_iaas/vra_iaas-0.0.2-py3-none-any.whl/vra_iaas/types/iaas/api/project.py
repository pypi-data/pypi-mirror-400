# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional

from pydantic import Field as FieldInfo

from .user import User
from ...._models import BaseModel
from .placement_constraint import PlacementConstraint
from .projects.zone_assignment import ZoneAssignment

__all__ = ["Project", "_Links", "Link"]


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


class Project(BaseModel):
    """
    Projects link users and cloud zones, thus controlling who can use what cloud resources.<br>**HATEOAS** links:<br>**self** - Project - Self link to this project
    """

    id: str
    """The id of this resource instance"""

    api_links: _Links = FieldInfo(alias="_links")
    """HATEOAS of the entity"""

    administrators: Optional[List[User]] = None
    """List of administrator users associated with the project.

    Only administrators can manage project's configuration.
    """

    constraints: Optional[Dict[str, List[PlacementConstraint]]] = None
    """
    List of storage, network and extensibility constraints to be applied when
    provisioning through this project.
    """

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """Date when the entity was created. The date is in ISO 8601 and UTC."""

    custom_properties: Optional[Dict[str, str]] = FieldInfo(alias="customProperties", default=None)
    """The project custom properties which are added to all requests in this project"""

    description: Optional[str] = None
    """A human-friendly description."""

    machine_naming_template: Optional[str] = FieldInfo(alias="machineNamingTemplate", default=None)
    """The naming template to be used for machines provisioned in this project"""

    members: Optional[List[User]] = None
    """List of member users associated with the project."""

    name: Optional[str] = None
    """A human-friendly name used as an identifier in APIs that support this option."""

    operation_timeout: Optional[int] = FieldInfo(alias="operationTimeout", default=None)
    """The timeout that should be used for Blueprint operations and Provisioning tasks.

    The timeout is in seconds
    """

    org_id: Optional[str] = FieldInfo(alias="orgId", default=None)
    """The id of the organization this entity belongs to."""

    owner: Optional[str] = None
    """Email of the user or display name of the group that owns the entity."""

    owner_type: Optional[str] = FieldInfo(alias="ownerType", default=None)
    """Type of a owner(user/ad_group) that owns the entity."""

    placement_policy: Optional[str] = FieldInfo(alias="placementPolicy", default=None)
    """Placement policy for the project.

    Determines how a zone will be selected for provisioning. DEFAULT or SPREAD.
    """

    shared_resources: Optional[bool] = FieldInfo(alias="sharedResources", default=None)
    """Specifies whether the resources in this projects are shared or not."""

    supervisors: Optional[List[User]] = None
    """List of supervisor users associated with the project."""

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""

    viewers: Optional[List[User]] = None
    """List of viewer users associated with the project."""

    zones: Optional[List[ZoneAssignment]] = None
    """List of Cloud Zones assigned to this project.

    You can limit deployment to a single region or allow multi-region placement by
    adding more than one cloud zone to a project. A cloud zone lists available
    resources. Use tags on resources to control workload placement.
    """
