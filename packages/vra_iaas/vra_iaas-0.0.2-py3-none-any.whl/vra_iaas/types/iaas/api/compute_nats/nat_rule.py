# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ....._models import BaseModel

__all__ = ["NatRule"]


class NatRule(BaseModel):
    """NAT Rule"""

    index: int
    """Index in which the rule must be applied"""

    target_link: str = FieldInfo(alias="targetLink")
    """
    A links to target load balancer or a machine's network interface where the
    request will be forwarded.
    """

    description: Optional[str] = None
    """Description of the NAT rule."""

    destination_address: Optional[str] = FieldInfo(alias="destinationAddress", default=None)
    """The external IP address of the outbound or routed network"""

    destination_ports: Optional[str] = FieldInfo(alias="destinationPorts", default=None)
    """The edge gateway port. Default is `any`"""

    kind: Optional[str] = None
    """Kind of NAT: NAT44/NAT64/NAT66.

    Only NAT44 is supported currently and it is the default value
    """

    protocol: Optional[str] = None
    """The protocol of the incoming requests. Default is TCP."""

    rule_id: Optional[str] = FieldInfo(alias="ruleId", default=None)
    """Unique ID of the NAT Rule"""

    source_ips: Optional[str] = FieldInfo(alias="sourceIPs", default=None)
    """The IP of the external source. Default is `any`"""

    source_ports: Optional[str] = FieldInfo(alias="sourcePorts", default=None)
    """Ports from where the request is originating. Default is `any`"""

    translated_ports: Optional[str] = FieldInfo(alias="translatedPorts", default=None)
    """The machine port where the request will be forwarded. Default is `any`"""

    type: Optional[str] = None
    """Type of the NAT rule. Only DNAT is supported currently."""
