# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["RegionListParams"]


class RegionListParams(TypedDict, total=False):
    skip: Annotated[int, PropertyInfo(alias="$skip")]
    """Number of records you want to skip."""

    top: Annotated[int, PropertyInfo(alias="$top")]
    """Number of records you want to get."""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """
