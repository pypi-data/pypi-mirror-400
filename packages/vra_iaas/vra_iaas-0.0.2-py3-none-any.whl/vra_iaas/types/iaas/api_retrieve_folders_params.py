# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["APIRetrieveFoldersParams"]


class APIRetrieveFoldersParams(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    count: Annotated[bool, PropertyInfo(alias="$count")]
    """
    Flag which when specified, regardless of the assigned value, shows the total
    number of records. If the collection has a filter it shows the number of records
    matching the filter.
    """

    filter: Annotated[str, PropertyInfo(alias="$filter")]
    """Filter the results by a specified predicate expression.

    Operators: eq, ne, and, or.
    """

    select: Annotated[str, PropertyInfo(alias="$select")]
    """Select a subset of properties to include in the response."""

    skip: Annotated[int, PropertyInfo(alias="$skip")]
    """Number of records you want to skip."""

    top: Annotated[int, PropertyInfo(alias="$top")]
    """Number of records you want to get."""

    cloud_account_id: Annotated[str, PropertyInfo(alias="cloudAccountId")]
    """The ID of a vcenter cloud account."""

    external_region_id: Annotated[str, PropertyInfo(alias="externalRegionId")]
    """
    The external unique identifier of the region associated with the vcenter cloud
    account.
    """
