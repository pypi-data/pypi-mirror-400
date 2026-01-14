# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["CloudAccountHealthCheckParams"]


class CloudAccountHealthCheckParams(TypedDict, total=False):
    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    periodic_health_check_id: Annotated[str, PropertyInfo(alias="periodicHealthCheckId")]
    """
    If query param is provided then the endpoint health check is not started
    manually from the UI, but after a scheduled process.
    """
