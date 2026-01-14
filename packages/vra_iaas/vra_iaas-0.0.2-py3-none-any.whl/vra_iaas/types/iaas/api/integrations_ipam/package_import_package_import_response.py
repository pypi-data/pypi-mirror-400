# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ....._models import BaseModel

__all__ = ["PackageImportPackageImportResponse"]


class PackageImportPackageImportResponse(BaseModel):
    logo_icon: Optional[str] = FieldInfo(alias="logoIcon", default=None)

    provider_id: Optional[str] = FieldInfo(alias="providerId", default=None)

    provider_name: Optional[str] = FieldInfo(alias="providerName", default=None)

    provider_version: Optional[str] = FieldInfo(alias="providerVersion", default=None)
