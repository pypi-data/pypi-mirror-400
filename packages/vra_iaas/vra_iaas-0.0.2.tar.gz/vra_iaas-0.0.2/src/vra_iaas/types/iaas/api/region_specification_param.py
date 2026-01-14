# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["RegionSpecificationParam"]


class RegionSpecificationParam(TypedDict, total=False):
    """Specification for a region in a cloud account."""

    external_region_id: Required[Annotated[str, PropertyInfo(alias="externalRegionId")]]
    """Unique identifier of region on the provider side."""

    name: Required[str]
    """Name of region on the provider side.

    In vSphere, the name of the region is different from its id.
    """
