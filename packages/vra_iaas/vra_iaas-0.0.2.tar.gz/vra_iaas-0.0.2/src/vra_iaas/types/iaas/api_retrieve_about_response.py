# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["APIRetrieveAboutResponse", "SupportedAPI", "SupportedAPIDeprecationPolicy"]


class SupportedAPIDeprecationPolicy(BaseModel):
    """
    The deprecation policy may contain information whether the api is in deprecated state and when it expires.
    """

    deprecated_at: Optional[str] = FieldInfo(alias="deprecatedAt", default=None)
    """The date the api was deprecated in yyyy-MM-dd format (UTC).

    Could be empty if the api is not deprecated.
    """

    description: Optional[str] = None
    """
    A free text description that contains information about why this api is
    deprecated and how to migrate to a newer version.
    """

    expires_at: Optional[str] = FieldInfo(alias="expiresAt", default=None)
    """The date the api support will be dropped in yyyy-MM-dd format (UTC).

    The api may still be available for use after that date but this is not
    guaranteed.
    """


class SupportedAPI(BaseModel):
    """A collection of all currently supported api versions."""

    api_version: str = FieldInfo(alias="apiVersion")
    """The version of the API in yyyy-MM-dd format (UTC)."""

    documentation_link: str = FieldInfo(alias="documentationLink")
    """The link to the documentation of this api version"""

    deprecation_policy: Optional[SupportedAPIDeprecationPolicy] = FieldInfo(alias="deprecationPolicy", default=None)
    """
    The deprecation policy may contain information whether the api is in deprecated
    state and when it expires.
    """


class APIRetrieveAboutResponse(BaseModel):
    """
    State object representing an about page that includes api versioning information
    """

    latest_api_version: str = FieldInfo(alias="latestApiVersion")
    """The latest version of the API in yyyy-MM-dd format (UTC)."""

    supported_apis: List[SupportedAPI] = FieldInfo(alias="supportedApis")
    """A collection of all currently supported api versions."""
