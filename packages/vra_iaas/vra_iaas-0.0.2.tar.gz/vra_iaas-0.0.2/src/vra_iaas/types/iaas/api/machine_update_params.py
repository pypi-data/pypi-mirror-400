# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo
from .tag_param import TagParam
from .machine_boot_config_param import MachineBootConfigParam

__all__ = ["MachineUpdateParams"]


class MachineUpdateParams(TypedDict, total=False):
    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    boot_config: Annotated[MachineBootConfigParam, PropertyInfo(alias="bootConfig")]
    """
    Machine boot config that will be passed to the instance that can be used to
    perform common automated configuration tasks and even run scripts after the
    instance starts.
    """

    custom_properties: Annotated[Dict[str, str], PropertyInfo(alias="customProperties")]
    """Additional custom properties that may be used to extend the machine.

    Internal custom properties (for example, prefixed with: "\\__\\__") are discarded.
    """

    description: str
    """
    Describes machine within the scope of your organization and is not propagated to
    the cloud
    """

    tags: Iterable[TagParam]
    """
    A set of tag keys and optional values that should be set on any resource that is
    produced from this specification.
    """
