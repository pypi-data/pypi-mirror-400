# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["APIRetrieveFabricAzureDiskEncryptionSetsParams"]


class APIRetrieveFabricAzureDiskEncryptionSetsParams(TypedDict, total=False):
    region_id: Required[Annotated[str, PropertyInfo(alias="regionId")]]
    """Region id"""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """
