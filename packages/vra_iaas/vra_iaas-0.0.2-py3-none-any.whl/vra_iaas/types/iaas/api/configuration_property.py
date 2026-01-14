# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["ConfigurationProperty"]


class ConfigurationProperty(BaseModel):
    """A representation of a configuration property."""

    key: Literal["SESSION_TIMEOUT_DURATION_MINUTES, RELEASE_IPADDRESS_PERIOD_MINUTES, NSXT_RETRY_DURATION_MINUTES"]
    """The key of the property."""

    value: str
    """The value of the property."""
