# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ....._models import BaseModel

__all__ = ["Rule"]


class Rule(BaseModel):
    """A rule used in a security group."""

    access: Literal["Allow", "Deny", "Drop"]
    """Type of access (Allow, Deny or Drop) for the security rule.

    Allow is default. Traffic that does not match any rules will be denied.
    """

    direction: Literal["Inbound", "Outbound"]
    """Direction of the security rule (inbound or outboud)."""

    ip_range_cidr: str = FieldInfo(alias="ipRangeCidr")
    """IP address(es) in CIDR format which the security rule applies to."""

    ports: str
    """Ports the security rule applies to."""

    name: Optional[str] = None
    """Name of security rule."""

    protocol: Optional[str] = None
    """Protocol the security rule applies to."""

    service: Optional[str] = None
    """Service defined by the provider (such as: SSH, HTTPS).

    Either service or protocol have to be specified.
    """
