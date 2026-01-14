# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._types import SequenceNotStr
from ...._utils import PropertyInfo

__all__ = ["ExternalNetworkIPRangeUpdateParams"]


class ExternalNetworkIPRangeUpdateParams(TypedDict, total=False):
    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    fabric_network_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="fabricNetworkIds")]
    """A list of fabric network Ids that this IP range should be associated with."""
