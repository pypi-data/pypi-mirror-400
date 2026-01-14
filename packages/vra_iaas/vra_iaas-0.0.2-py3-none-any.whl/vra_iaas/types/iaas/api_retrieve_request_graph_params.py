# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["APIRetrieveRequestGraphParams"]


class APIRetrieveRequestGraphParams(TypedDict, total=False):
    deployment_id: Required[Annotated[str, PropertyInfo(alias="deploymentId")]]
    """Deployment Id For Provisioning Request"""

    flow_id: Required[Annotated[str, PropertyInfo(alias="flowId")]]
    """Flow Id For Provisioning Request"""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """
