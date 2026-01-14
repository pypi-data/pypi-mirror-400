# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["CloudAccountsAwRegionEnumerationParams"]


class CloudAccountsAwRegionEnumerationParams(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    access_key_id: Annotated[str, PropertyInfo(alias="accessKeyId")]
    """Aws Access key ID.

    Either provide accessKeyId or provide a cloudAccountId of an existing account.
    """

    cloud_account_id: Annotated[str, PropertyInfo(alias="cloudAccountId")]
    """Existing cloud account id.

    Either provide existing cloud account id, or accessKeyId/secretAccessKey
    credentials pair.
    """

    secret_access_key: Annotated[str, PropertyInfo(alias="secretAccessKey")]
    """Aws Secret Access Key.

    Either provide secretAccessKey or provide a cloudAccountId of an existing
    account.
    """
