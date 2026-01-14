# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo
from .tag_param import TagParam

__all__ = ["FabricNetworkUpdateParams"]


class FabricNetworkUpdateParams(TypedDict, total=False):
    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    tags: Iterable[TagParam]
    """A set of tag keys and optional values that were set on this resource instance."""
