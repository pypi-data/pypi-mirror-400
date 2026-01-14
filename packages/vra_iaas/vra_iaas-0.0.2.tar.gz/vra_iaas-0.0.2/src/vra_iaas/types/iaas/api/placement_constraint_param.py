# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["PlacementConstraintParam"]


class PlacementConstraintParam(TypedDict, total=False):
    """A constraint that is conveyed to the policy engine."""

    expression: Required[str]
    """
    An expression of the form "[!]tag-key[:[tag-value]]", used to indicate a
    constraint match on keys and values of tags.
    """

    mandatory: Required[bool]
    """Indicates whether this constraint should be strictly enforced or not."""
