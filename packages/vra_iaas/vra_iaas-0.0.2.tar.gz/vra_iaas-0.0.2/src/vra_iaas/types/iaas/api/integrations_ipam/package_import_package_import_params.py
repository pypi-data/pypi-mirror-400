# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from typing_extensions import Literal, Required, Annotated, TypedDict

from ....._types import Base64FileInput
from ....._utils import PropertyInfo

__all__ = ["PackageImportPackageImportParams"]


class PackageImportPackageImportParams(TypedDict, total=False):
    tus_resumable: Required[Annotated[str, PropertyInfo(alias="Tus-Resumable")]]

    upload_length: Required[Annotated[str, PropertyInfo(alias="Upload-Length")]]

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    bundle_id: Annotated[str, PropertyInfo(alias="bundleId")]

    compressed_bundle: Annotated[Union[str, Base64FileInput], PropertyInfo(alias="compressedBundle", format="base64")]

    option: Literal["FAIL", "OVERWRITE"]

    properties: Dict[str, str]
