# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["RegionSpecification"]


class RegionSpecification(BaseModel):
    """Specification for a region in a cloud account."""

    external_region_id: str = FieldInfo(alias="externalRegionId")
    """Unique identifier of region on the provider side."""

    name: str
    """Name of region on the provider side.

    In vSphere, the name of the region is different from its id.
    """
