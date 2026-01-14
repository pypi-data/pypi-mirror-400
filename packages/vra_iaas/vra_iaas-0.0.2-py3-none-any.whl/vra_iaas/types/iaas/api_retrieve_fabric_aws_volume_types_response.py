# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["APIRetrieveFabricAwsVolumeTypesResponse"]


class APIRetrieveFabricAwsVolumeTypesResponse(BaseModel):
    volume_types: Optional[List[str]] = FieldInfo(alias="volumeTypes", default=None)
