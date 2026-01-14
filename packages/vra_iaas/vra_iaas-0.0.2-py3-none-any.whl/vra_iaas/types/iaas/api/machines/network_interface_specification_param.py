# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Annotated, TypedDict

from ....._types import SequenceNotStr
from ....._utils import PropertyInfo

__all__ = ["NetworkInterfaceSpecificationParam"]


class NetworkInterfaceSpecificationParam(TypedDict, total=False):
    """Specification for attaching nic to machine"""

    addresses: SequenceNotStr[str]
    """A list of IP addresses allocated or in use by this network interface."""

    custom_properties: Annotated[Dict[str, str], PropertyInfo(alias="customProperties")]
    """Additional properties that may be used to extend the base type."""

    description: str
    """A human-friendly description."""

    device_index: Annotated[int, PropertyInfo(alias="deviceIndex")]
    """The device index of this network interface."""

    fabric_network_id: Annotated[str, PropertyInfo(alias="fabricNetworkId")]
    """Id of the fabric network for the network interface.

    Either networkId or fabricNetworkId can be specified, not both.
    """

    mac_address: Annotated[str, PropertyInfo(alias="macAddress")]
    """MAC address of the network interface."""

    name: str
    """A human-friendly name used as an identifier in APIs that support this option."""

    network_id: Annotated[str, PropertyInfo(alias="networkId")]
    """Id of the network for the network interface.

    Either networkId or fabricNetworkId can be specified, not both.
    """

    security_group_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="securityGroupIds")]
    """A list of security group ids which this network interface will be assigned to."""
