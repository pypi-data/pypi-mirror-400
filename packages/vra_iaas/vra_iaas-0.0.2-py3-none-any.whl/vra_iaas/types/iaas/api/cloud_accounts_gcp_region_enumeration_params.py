# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["CloudAccountsGcpRegionEnumerationParams"]


class CloudAccountsGcpRegionEnumerationParams(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    client_email: Annotated[str, PropertyInfo(alias="clientEmail")]
    """GCP Client email.

    Either provide clientEmail or provide a cloudAccountId of an existing account.
    """

    cloud_account_id: Annotated[str, PropertyInfo(alias="cloudAccountId")]
    """Existing cloud account id.

    Either provide id of existing account, or cloud account credentials: projectId,
    privateKeyId, privateKey and clientEmail.
    """

    private_key: Annotated[str, PropertyInfo(alias="privateKey")]
    """GCP Private key.

    Either provide privateKey or provide a cloudAccountId of an existing account.
    """

    private_key_id: Annotated[str, PropertyInfo(alias="privateKeyId")]
    """GCP Private key ID.

    Either provide privateKeyId or provide a cloudAccountId of an existing account.
    """

    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """GCP Project ID.

    Either provide projectId or provide a cloudAccountId of an existing account.
    """
