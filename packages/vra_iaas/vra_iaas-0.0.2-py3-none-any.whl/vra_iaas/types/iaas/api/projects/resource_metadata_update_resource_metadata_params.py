# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Annotated, TypedDict

from ....._utils import PropertyInfo
from ..tag_param import TagParam

__all__ = ["ResourceMetadataUpdateResourceMetadataParams"]


class ResourceMetadataUpdateResourceMetadataParams(TypedDict, total=False):
    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    tags: Iterable[TagParam]
    """
    A list of keys and optional values to be applied to compute resources
    provisioned in a project
    """
