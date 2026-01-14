# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["ConfigurationPropertyUpdateConfigurationPropertiesParams"]


class ConfigurationPropertyUpdateConfigurationPropertiesParams(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    key: Required[
        Literal["SESSION_TIMEOUT_DURATION_MINUTES, RELEASE_IPADDRESS_PERIOD_MINUTES, NSXT_RETRY_DURATION_MINUTES"]
    ]
    """The key of the property."""

    value: Required[str]
    """The value of the property."""
