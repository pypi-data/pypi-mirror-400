# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["DeploymentCreateParams"]


class DeploymentCreateParams(TypedDict, total=False):
    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    project_id: Required[Annotated[str, PropertyInfo(alias="projectId")]]
    """The id of the project the current user belongs to."""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    description: str
    """A human-friendly description."""
