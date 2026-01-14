# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["NatRuleParam"]


class NatRuleParam(TypedDict, total=False):
    """NAT Rule"""

    index: Required[int]
    """Index in which the rule must be applied"""

    target_link: Required[Annotated[str, PropertyInfo(alias="targetLink")]]
    """
    A links to target load balancer or a machine's network interface where the
    request will be forwarded.
    """

    description: str
    """Description of the NAT rule."""

    destination_ports: Annotated[str, PropertyInfo(alias="destinationPorts")]
    """The edge gateway port. Default is `any`"""

    kind: str
    """Kind of NAT: NAT44/NAT64/NAT66.

    Only NAT44 is supported currently and it is the default value
    """

    protocol: str
    """The protocol of the incoming requests. Default is TCP."""

    source_ips: Annotated[str, PropertyInfo(alias="sourceIPs")]
    """The IP of the external source. Default is `any`"""

    source_ports: Annotated[str, PropertyInfo(alias="sourcePorts")]
    """Ports from where the request is originating. Default is `any`"""

    translated_ports: Annotated[str, PropertyInfo(alias="translatedPorts")]
    """The machine port where the request will be forwarded. Default is `any`"""

    type: str
    """Type of the NAT rule. Only DNAT is supported currently."""
