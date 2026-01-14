# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["DeploymentDeleteParams"]


class DeploymentDeleteParams(TypedDict, total=False):
    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    force_delete: Annotated[bool, PropertyInfo(alias="forceDelete")]
    """
    If true, best effort is made for deleting this deployment and all related
    resources. In some situations, this may leave provisioned infrastructure
    resources behind. Please ensure you remove them manually. If false, a standard
    delete action will be executed.
    """
