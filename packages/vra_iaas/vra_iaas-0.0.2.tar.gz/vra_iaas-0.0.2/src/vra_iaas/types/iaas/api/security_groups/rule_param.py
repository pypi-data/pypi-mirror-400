# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["RuleParam"]


class RuleParam(TypedDict, total=False):
    """A rule used in a security group."""

    access: Required[Literal["Allow", "Deny", "Drop"]]
    """Type of access (Allow, Deny or Drop) for the security rule.

    Allow is default. Traffic that does not match any rules will be denied.
    """

    direction: Required[Literal["Inbound", "Outbound"]]
    """Direction of the security rule (inbound or outboud)."""

    ip_range_cidr: Required[Annotated[str, PropertyInfo(alias="ipRangeCidr")]]
    """IP address(es) in CIDR format which the security rule applies to."""

    ports: Required[str]
    """Ports the security rule applies to."""

    name: str
    """Name of security rule."""

    protocol: str
    """Protocol the security rule applies to."""

    service: str
    """Service defined by the provider (such as: SSH, HTTPS).

    Either service or protocol have to be specified.
    """
