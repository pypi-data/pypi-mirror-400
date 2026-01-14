# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ....._models import BaseModel

__all__ = ["StorageProfileAssociationUpdateStorageProfileAssociationsResponse", "AssociationsLink"]


class AssociationsLink(BaseModel):
    """Represents an HTTP url"""

    href: str
    """The target URL."""

    rel: str
    """Relationship to the target."""


class StorageProfileAssociationUpdateStorageProfileAssociationsResponse(BaseModel):
    """Represents storage profile associations for a storage profile id."""

    associations_link: AssociationsLink = FieldInfo(alias="associationsLink")
    """Represents an HTTP url"""
