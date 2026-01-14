# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["APIRetrieveFabricAzureDiskEncryptionSetsResponse", "DiskEncryptionSet"]


class DiskEncryptionSet(BaseModel):
    id: Optional[str] = None

    key: Optional[str] = None

    name: Optional[str] = None

    region_id: Optional[str] = FieldInfo(alias="regionId", default=None)

    vault: Optional[str] = None


class APIRetrieveFabricAzureDiskEncryptionSetsResponse(BaseModel):
    disk_encryption_sets: Optional[List[DiskEncryptionSet]] = FieldInfo(alias="diskEncryptionSets", default=None)
