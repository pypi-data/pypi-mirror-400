# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo
from ..storage_profile_associations_param import StorageProfileAssociationsParam

__all__ = ["StorageProfileAssociationUpdateStorageProfileAssociationsParams"]


class StorageProfileAssociationUpdateStorageProfileAssociationsParams(TypedDict, total=False):
    region_id: Required[Annotated[str, PropertyInfo(alias="regionId")]]
    """The Id of the region that is associated with the storage profile."""

    storage_profile_associations: Required[
        Annotated[Iterable[StorageProfileAssociationsParam], PropertyInfo(alias="storageProfileAssociations")]
    ]
    """Defines a specification of Storage Profile datastore associations."""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """
