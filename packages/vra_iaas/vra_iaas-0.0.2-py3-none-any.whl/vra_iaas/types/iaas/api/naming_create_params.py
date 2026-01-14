# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["NamingCreateParams", "Project", "Template", "TemplateCounter"]


class NamingCreateParams(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    id: str

    description: str

    name: str

    projects: Iterable[Project]

    templates: Iterable[Template]


class Project(TypedDict, total=False):
    id: str

    active: bool

    default_org: Annotated[bool, PropertyInfo(alias="defaultOrg")]

    org_id: Annotated[str, PropertyInfo(alias="orgId")]

    project_id: Annotated[str, PropertyInfo(alias="projectId")]

    project_name: Annotated[str, PropertyInfo(alias="projectName")]


class TemplateCounter(TypedDict, total=False):
    id: str

    active: bool

    cn_resource_type: Annotated[
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
        ],
        PropertyInfo(alias="cnResourceType"),
    ]

    current_counter: Annotated[int, PropertyInfo(alias="currentCounter")]

    project_id: Annotated[str, PropertyInfo(alias="projectId")]


class Template(TypedDict, total=False):
    id: str

    counters: Iterable[TemplateCounter]

    increment_step: Annotated[int, PropertyInfo(alias="incrementStep")]

    name: str

    pattern: str

    resource_default: Annotated[bool, PropertyInfo(alias="resourceDefault")]

    resource_type: Annotated[
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
        ],
        PropertyInfo(alias="resourceType"),
    ]

    resource_type_name: Annotated[str, PropertyInfo(alias="resourceTypeName")]

    start_counter: Annotated[int, PropertyInfo(alias="startCounter")]

    static_pattern: Annotated[str, PropertyInfo(alias="staticPattern")]

    unique_name: Annotated[bool, PropertyInfo(alias="uniqueName")]
