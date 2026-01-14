# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Annotated, TypedDict

from ....._utils import PropertyInfo
from ..tag_param import TagParam

__all__ = ["OperationSnapshotsParams"]


class OperationSnapshotsParams(TypedDict, total=False):
    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    description: str
    """A human-friendly description."""

    name: str
    """A human-friendly name used as an identifier in APIs that support this option."""

    snapshot_properties: Annotated[Dict[str, str], PropertyInfo(alias="snapshotProperties")]
    """Cloud specific snapshot properties supplied in as name value pairs"""

    tags: Iterable[TagParam]
    """
    A set of tag keys and optional values that have to be set on the snapshot in the
    cloud. Currently supported for Azure Snapshots
    """
