# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from ....._types import SequenceNotStr
from ....._utils import PropertyInfo
from .network_interface_specification_param import NetworkInterfaceSpecificationParam

__all__ = ["OperationChangeSecurityGroupsParams", "_Links", "Link"]


class OperationChangeSecurityGroupsParams(TypedDict, total=False):
    body_id: Required[Annotated[str, PropertyInfo(alias="id")]]
    """The id of this resource instance"""

    _links: Required[_Links]
    """HATEOAS of the entity"""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    created_at: Annotated[str, PropertyInfo(alias="createdAt")]
    """Date when the entity was created. The date is in ISO 8601 and UTC."""

    description: str
    """A human-friendly description."""

    name: str
    """A human-friendly name used as an identifier in APIs that support this option."""

    network_interface_specifications: Annotated[
        Iterable[NetworkInterfaceSpecificationParam], PropertyInfo(alias="networkInterfaceSpecifications")
    ]
    """A set of network interface controller specifications for this machine.

    If not specified, then no reconfiguration will be performed.
    """

    org_id: Annotated[str, PropertyInfo(alias="orgId")]
    """The id of the organization this entity belongs to."""

    owner: str
    """Email of the user or display name of the group that owns the entity."""

    owner_type: Annotated[str, PropertyInfo(alias="ownerType")]
    """Type of a owner(user/ad_group) that owns the entity."""

    updated_at: Annotated[str, PropertyInfo(alias="updatedAt")]
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""


class Link(TypedDict, total=False):
    """HATEOAS of the entity"""

    href: str

    hrefs: SequenceNotStr[str]


class _LinksTyped(TypedDict, total=False):
    """HATEOAS of the entity"""

    empty: bool


_Links: TypeAlias = Union[_LinksTyped, Dict[str, Link]]
