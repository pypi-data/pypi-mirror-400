# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["DataCollectorRetrieveDataCollectorsParams"]


class DataCollectorRetrieveDataCollectorsParams(TypedDict, total=False):
    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    disabled: bool
    """
    If query param is provided with value equals to true, only disabled data
    collectors will be retrieved.
    """
