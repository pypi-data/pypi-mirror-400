# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._types import SequenceNotStr
from ...._utils import PropertyInfo

__all__ = ["TagTagsUsageParams"]


class TagTagsUsageParams(TypedDict, total=False):
    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    tag_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="tagIds")]
    """List of Tag IDs.

    All provided tags will be matched to all resources containing that tag.
    """
