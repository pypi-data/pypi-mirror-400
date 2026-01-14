# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .tag_param import TagParam
from .region_specification_param import RegionSpecificationParam

__all__ = ["CloudAccountsAwUpdateParams"]


class CloudAccountsAwUpdateParams(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    name: Required[str]
    """A human-friendly name used as an identifier in APIs that support this option."""

    access_key_id: Annotated[str, PropertyInfo(alias="accessKeyId")]
    """Aws Access key ID"""

    create_default_zones: Annotated[bool, PropertyInfo(alias="createDefaultZones")]
    """Create default cloud zones for the enabled regions."""

    description: str
    """A human-friendly description."""

    iam_role_arn: Annotated[str, PropertyInfo(alias="iamRoleArn")]
    """Aws ARN role to be assumed by Aria Auto account"""

    regions: Iterable[RegionSpecificationParam]
    """
    A set of regions to enable provisioning on.Refer to
    /iaas/api/cloud-accounts/region-enumeration.
    """

    secret_access_key: Annotated[str, PropertyInfo(alias="secretAccessKey")]
    """Aws Secret Access Key"""

    tags: Iterable[TagParam]
    """A set of tag keys and optional values to set on the Cloud Account"""

    trusted_account: Annotated[bool, PropertyInfo(alias="trustedAccount")]
    """Create the account as trusted."""
