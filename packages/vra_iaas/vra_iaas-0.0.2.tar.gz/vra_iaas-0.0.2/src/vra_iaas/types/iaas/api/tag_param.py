# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["TagParam"]


class TagParam(TypedDict, total=False):
    """A set of tag keys and optional values that were set on this resource."""

    key: Required[str]
    """Tag's key."""

    value: Required[str]
    """Tag's value."""
