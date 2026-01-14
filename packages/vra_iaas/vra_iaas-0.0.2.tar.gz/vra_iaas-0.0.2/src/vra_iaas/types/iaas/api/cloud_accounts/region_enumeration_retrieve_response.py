# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ....._models import BaseModel
from ..region_specification import RegionSpecification

__all__ = ["RegionEnumerationRetrieveResponse"]


class RegionEnumerationRetrieveResponse(BaseModel):
    """
    State object representing cloud account region.<br><br>**externalRegions** - array[RegionSpecification] - Set of regions that can be enabled for this cloud account.<br>**externalRegionIds** - array[String] - Set of ids of regions that can be enabled for this cloud account.<br>
    """

    external_regions: Optional[List[RegionSpecification]] = FieldInfo(alias="externalRegions", default=None)
    """A set of regions that can be enabled for this cloud account."""
