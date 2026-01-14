# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["PlacementConstraint"]


class PlacementConstraint(BaseModel):
    """A constraint that is conveyed to the policy engine."""

    expression: str
    """
    An expression of the form "[!]tag-key[:[tag-value]]", used to indicate a
    constraint match on keys and values of tags.
    """

    mandatory: bool
    """Indicates whether this constraint should be strictly enforced or not."""
