# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["ProjectListParams"]


class ProjectListParams(TypedDict, total=False):
    count: Annotated[bool, PropertyInfo(alias="$count")]
    """
    Flag which when specified, regardless of the assigned value, shows the total
    number of records. If the collection has a filter it shows the number of records
    matching the filter.
    """

    filter: Annotated[str, PropertyInfo(alias="$filter")]
    """Filter the results by a specified predicate expression.

    A set of operators and functions are defined for use: Operators: eq, ne, gt, ge,
    lt, le, and, or, not. Functions: bool substringof(string p0, string p1) bool
    endswith(string p0, string p1) bool startswith(string p0, string p1) int
    length(string p0) int indexof(string p0, string p1) string replace(string p0,
    string find, string replace) string substring(string p0, int pos) string
    substring(string p0, int pos, int length) string tolower(string p0) string
    toupper(string p0) string trim(string p0) string concat(string p0, string p1)
    """

    order_by: Annotated[str, PropertyInfo(alias="$orderBy")]
    """Sorting criteria in the format: property (asc|desc).

    Default sort order is ascending. Multiple sort criteria are supported.
    """

    skip: Annotated[int, PropertyInfo(alias="$skip")]
    """Number of records you want to skip."""

    top: Annotated[int, PropertyInfo(alias="$top")]
    """Number of records you want to get."""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """
