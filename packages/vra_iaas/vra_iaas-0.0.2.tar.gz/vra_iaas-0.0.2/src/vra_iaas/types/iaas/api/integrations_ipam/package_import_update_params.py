# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ....._types import FileTypes
from ....._utils import PropertyInfo

__all__ = ["PackageImportUpdateParams"]


class PackageImportUpdateParams(TypedDict, total=False):
    tus_resumable: Required[Annotated[str, PropertyInfo(alias="Tus-Resumable")]]

    upload_offset: Required[Annotated[str, PropertyInfo(alias="Upload-Offset")]]

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    body: FileTypes
