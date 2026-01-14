# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["NetworkInterfaceUpdateParams"]


class NetworkInterfaceUpdateParams(TypedDict, total=False):
    id: Required[str]

    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    address: str
    """Set IPv4 address for the machine network interface.

    The change will not propagate to cloud endpoint for provisioned machines.
    """

    custom_properties: Annotated[Dict[str, str], PropertyInfo(alias="customProperties")]
    """Additional custom properties that may be used to extend the machine.

    Internal custom properties (for example, prefixed with: "\\__\\__") can not be
    updated.
    """

    description: str
    """
    Describes the network interface of the machine within the scope of your
    organization and is not propagated to the cloud
    """

    name: str
    """Network interface name used during machine network interface provisioning.

    This property only takes effect if it is set before machine provisioning starts.
    The change will not propagate to cloud endpoint for provisioned machines.
    """
