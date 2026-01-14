# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["User"]


class User(BaseModel):
    """A representation of a user."""

    email: str
    """The email of the user or name of the group."""

    type: Optional[str] = None
    """Type of the principal. Currently supported 'user' (default) and 'group'."""
