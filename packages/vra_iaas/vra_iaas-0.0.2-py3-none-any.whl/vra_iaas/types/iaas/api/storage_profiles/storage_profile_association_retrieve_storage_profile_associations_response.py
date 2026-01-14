# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional

from pydantic import Field as FieldInfo

from ..tag import Tag
from ....._models import BaseModel

__all__ = [
    "StorageProfileAssociationRetrieveStorageProfileAssociationsResponse",
    "Content",
    "Content_Links",
    "ContentLink",
]


class ContentLink(BaseModel):
    """HATEOAS of the entity"""

    href: Optional[str] = None

    hrefs: Optional[List[str]] = None


class Content_Links(BaseModel):
    """HATEOAS of the entity"""

    empty: Optional[bool] = None

    if TYPE_CHECKING:
        # Some versions of Pydantic <2.8.0 have a bug and don’t allow assigning a
        # value to this field, so for compatibility we avoid doing it at runtime.
        __pydantic_extra__: Dict[str, ContentLink] = FieldInfo(init=False)  # pyright: ignore[reportIncompatibleVariableOverride]

        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> ContentLink: ...
    else:
        __pydantic_extra__: Dict[str, ContentLink]


class Content(BaseModel):
    """
    Represents a structure that holds details of storage profile association state linked to one single datastore or multiple datastores.
    """

    id: str
    """The id of this resource instance"""

    api_links: Content_Links = FieldInfo(alias="_links")
    """HATEOAS of the entity"""

    data_store_id: str = FieldInfo(alias="dataStoreId")
    """Datastore ID associated with this storage profile."""

    data_store_name: str = FieldInfo(alias="dataStoreName")
    """Datestore ID associated with this storage profile."""

    priority: int
    """Defines the priority of the storage profile with the highest priority being 0.

    Defaults to the value of 1.
    """

    storage_profile_id: str = FieldInfo(alias="storageProfileId")
    """Defines the Id of the storage Profile."""

    created_at: Optional[str] = FieldInfo(alias="createdAt", default=None)
    """Date when the entity was created. The date is in ISO 8601 and UTC."""

    description: Optional[str] = None
    """A human-friendly description."""

    endpoint_links: Optional[List[str]] = FieldInfo(alias="endpointLinks", default=None)
    """Link reference to the cloud account endpoint of this host."""

    name: Optional[str] = None
    """A human-friendly name used as an identifier in APIs that support this option."""

    org_id: Optional[str] = FieldInfo(alias="orgId", default=None)
    """The id of the organization this entity belongs to."""

    owner: Optional[str] = None
    """Email of the user or display name of the group that owns the entity."""

    owner_type: Optional[str] = FieldInfo(alias="ownerType", default=None)
    """Type of a owner(user/ad_group) that owns the entity."""

    region_id: Optional[str] = FieldInfo(alias="regionId", default=None)
    """The ID of the region that is associated with this storage profile."""

    tags: Optional[List[Tag]] = None
    """
    A set of tag keys and optional values that were set on the Storage Profile
    Association Datastores.
    """

    updated_at: Optional[str] = FieldInfo(alias="updatedAt", default=None)
    """Date when the entity was last updated. The date is ISO 8601 and UTC."""


class StorageProfileAssociationRetrieveStorageProfileAssociationsResponse(BaseModel):
    """State object representing a query result of storage profiles association state."""

    content: Optional[List[Content]] = None
    """List of content items"""

    number_of_elements: Optional[int] = FieldInfo(alias="numberOfElements", default=None)
    """Number of elements in the current page"""

    total_elements: Optional[int] = FieldInfo(alias="totalElements", default=None)
    """Total number of elements. In some cases the field may not be populated"""
