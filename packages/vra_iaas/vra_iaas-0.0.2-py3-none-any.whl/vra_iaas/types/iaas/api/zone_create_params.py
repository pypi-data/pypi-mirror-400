# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._types import SequenceNotStr
from ...._utils import PropertyInfo
from .tag_param import TagParam

__all__ = ["ZoneCreateParams"]


class ZoneCreateParams(TypedDict, total=False):
    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    region_id: Required[Annotated[str, PropertyInfo(alias="regionId")]]
    """The id of the region for which this profile is created"""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    compute_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="computeIds")]
    """The ids of the compute resources that will be explicitly assigned to this zone"""

    custom_properties: Annotated[Dict[str, str], PropertyInfo(alias="customProperties")]
    """A list of key value pair of properties that will be used"""

    description: str
    """A human-friendly description."""

    folder: str
    """The folder relative path to the datacenter where resources are deployed to.

    (only applicable for vSphere cloud zones)
    """

    placement_policy: Annotated[str, PropertyInfo(alias="placementPolicy")]
    """Placement policy for the zone.

    One of DEFAULT, SPREAD, BINPACK or SPREAD_MEMORY.
    """

    tags: Iterable[TagParam]
    """
    A set of tag keys and optional values that are effectively applied to all
    compute resources in this zone, but only in the context of this zone.
    """

    tags_to_match: Annotated[Iterable[TagParam], PropertyInfo(alias="tagsToMatch")]
    """A set of tag keys and optional values that will be used"""
