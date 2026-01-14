# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .fabric_image import FabricImage

__all__ = ["FabricImageRetrieveFabricImagesResponse"]


class FabricImageRetrieveFabricImagesResponse(BaseModel):
    """State object representing a query result of fabric images."""

    content: Optional[List[FabricImage]] = None
    """List of content items"""

    number_of_elements: Optional[int] = FieldInfo(alias="numberOfElements", default=None)
    """Number of elements in the current page"""

    total_elements: Optional[int] = FieldInfo(alias="totalElements", default=None)
    """Total number of elements. In some cases the field may not be populated"""
