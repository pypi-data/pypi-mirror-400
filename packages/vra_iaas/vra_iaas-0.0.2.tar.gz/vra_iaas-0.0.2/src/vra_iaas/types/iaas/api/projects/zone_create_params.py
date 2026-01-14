# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Annotated, TypedDict

from ....._utils import PropertyInfo
from .zone_assignment_specification_param import ZoneAssignmentSpecificationParam

__all__ = ["ZoneCreateParams"]


class ZoneCreateParams(TypedDict, total=False):
    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    zone_assignment_specifications: Annotated[
        Iterable[ZoneAssignmentSpecificationParam], PropertyInfo(alias="zoneAssignmentSpecifications")
    ]
    """List of configurations for zone assignment to a project"""
