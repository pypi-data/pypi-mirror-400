# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["APILoginResponse"]


class APILoginResponse(BaseModel):
    """Entity that holds auth token details."""

    token: str
    """Base64 encoded auth token."""

    token_type: str = FieldInfo(alias="tokenType")
    """Type of the token."""
