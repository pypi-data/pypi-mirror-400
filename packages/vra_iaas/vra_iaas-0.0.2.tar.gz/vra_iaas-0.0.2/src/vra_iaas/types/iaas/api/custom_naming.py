# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .custom_naming_project import CustomNamingProject

__all__ = ["CustomNaming", "_Links", "Link", "Template", "TemplateCounter"]


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


class TemplateCounter(BaseModel):
    """A representation of a Counter."""

    cn_resource_type: Literal[
        "COMPUTE",
        "NETWORK",
        "COMPUTE_STORAGE",
        "LOAD_BALANCER",
        "RESOURCE_GROUP",
        "GATEWAY",
        "NAT",
        "SECURITY_GROUP",
        "GENERIC",
    ] = FieldInfo(alias="cnResourceType")
    """The resource type of custom name"""

    current_counter: int = FieldInfo(alias="currentCounter")
    """The current counter of custom name"""

    project_id: str = FieldInfo(alias="projectId")
    """The project id to which the counter is mapped"""

    id: Optional[str] = None

    active: Optional[bool] = None


class Template(BaseModel):
    """A representation of a Template."""

    id: Optional[str] = None
    """Unique id of custom naming template"""

    counters: Optional[List[TemplateCounter]] = None

    increment_step: Optional[int] = FieldInfo(alias="incrementStep", default=None)
    """Set the increment to the counter value to be taken for each name."""

    pattern: Optional[str] = None
    """The specified template used to generate the resource names"""

    resource_default: Optional[bool] = FieldInfo(alias="resourceDefault", default=None)
    """Flag to represent default pattern or static pattern"""

    resource_type: Optional[
        Literal[
            "COMPUTE",
            "NETWORK",
            "COMPUTE_STORAGE",
            "LOAD_BALANCER",
            "RESOURCE_GROUP",
            "GATEWAY",
            "NAT",
            "SECURITY_GROUP",
            "GENERIC",
        ]
    ] = FieldInfo(alias="resourceType", default=None)
    """Resource type"""

    resource_type_name: Optional[str] = FieldInfo(alias="resourceTypeName", default=None)
    """Resource type"""

    start_counter: Optional[int] = FieldInfo(alias="startCounter", default=None)
    """The value from which naming pattern counter will start."""

    static_pattern: Optional[str] = FieldInfo(alias="staticPattern", default=None)
    """Static pattern text"""

    unique_name: Optional[bool] = FieldInfo(alias="uniqueName", default=None)
    """Flag to check if name should be unique"""


class CustomNaming(BaseModel):
    """
    Custom names**HATEOAS** links:<br>**self** - Custom naming - Self link to this CustomNamingEntity
    """

    id: str
    """The id of this resource instance"""

    api_links: _Links = FieldInfo(alias="_links")
    """HATEOAS of the entity"""

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """Date when the entity was created. The date is in ISO 8601 and UTC."""

    description: Optional[str] = None
    """A human-friendly description."""

    name: Optional[str] = None
    """A human-friendly name used as an identifier in APIs that support this option."""

    org_id: Optional[str] = FieldInfo(alias="orgId", default=None)
    """The id of the organization this entity belongs to."""

    owner: Optional[str] = None
    """Email of the user or display name of the group that owns the entity."""

    owner_type: Optional[str] = FieldInfo(alias="ownerType", default=None)
    """Type of a owner(user/ad_group) that owns the entity."""

    projects: Optional[List[CustomNamingProject]] = None
    """Set of projects associated with custom name"""

    templates: Optional[List[Template]] = None
    """Set of templates associated with custom name"""

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""
