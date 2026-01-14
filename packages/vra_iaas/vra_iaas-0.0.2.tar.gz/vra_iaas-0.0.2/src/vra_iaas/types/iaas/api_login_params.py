# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["APILoginParams"]


class APILoginParams(TypedDict, total=False):
    refresh_token: Required[Annotated[str, PropertyInfo(alias="refreshToken")]]
    """Refresh token obtained from the UI"""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """
