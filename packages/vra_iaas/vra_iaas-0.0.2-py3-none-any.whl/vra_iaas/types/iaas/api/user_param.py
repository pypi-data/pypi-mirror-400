# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["UserParam"]


class UserParam(TypedDict, total=False):
    """A representation of a user."""

    email: Required[str]
    """The email of the user or name of the group."""

    type: str
    """Type of the principal. Currently supported 'user' (default) and 'group'."""
