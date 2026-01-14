# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["StorageProfileAssociationsParam", "Association"]


class Association(TypedDict, total=False):
    """Storage Profile Data Store Associations."""

    data_store_id: Required[Annotated[str, PropertyInfo(alias="dataStoreId")]]
    """Id of the Datastore to be associated with the storage profile."""

    priority: Required[int]
    """Priority for the datastore to be associated with the highest priority being 0.

    Defaults to the value of 1.
    """


class StorageProfileAssociationsParam(TypedDict, total=False):
    """Represents a specification of Storage Profile datastore associations."""

    associations: Required[Iterable[Association]]
    """List of storage profile data store associations."""

    request_type: Required[Annotated[Literal["CREATE", "UPDATE", "DELETE"], PropertyInfo(alias="requestType")]]
    """Defines request type for data stores associations to the storage profile."""
