# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..tag import Tag
from ....._models import BaseModel

__all__ = ["ResourceMetadataRetrieveResourceMetadataResponse"]


class ResourceMetadataRetrieveResourceMetadataResponse(BaseModel):
    """Represents the resource metadata associated with a project"""

    tags: Optional[List[Tag]] = None
    """
    A list of keys and optional values to be applied to compute resources
    provisioned in a project
    """
