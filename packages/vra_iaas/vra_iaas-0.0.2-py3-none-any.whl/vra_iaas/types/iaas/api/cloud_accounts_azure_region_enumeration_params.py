# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["CloudAccountsAzureRegionEnumerationParams"]


class CloudAccountsAzureRegionEnumerationParams(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The version of the API in yyyy-MM-dd format (UTC).

    For versioning information refer to /iaas/api/about
    """

    client_application_id: Annotated[str, PropertyInfo(alias="clientApplicationId")]
    """Azure Client Application ID.

    Either provide clientApplicationId or provide a cloudAccountId of an existing
    account.
    """

    client_application_secret_key: Annotated[str, PropertyInfo(alias="clientApplicationSecretKey")]
    """Azure Client Application Secret Key.

    Either provide clientApplicationSecretKey or provide a cloudAccountId of an
    existing account.
    """

    cloud_account_id: Annotated[str, PropertyInfo(alias="cloudAccountId")]
    """Existing cloud account id.

    Either provide id of existing account, or cloud account credentials:
    clientApplicationId, clientApplicationSecretKey and tenantId.
    """

    subscription_id: Annotated[str, PropertyInfo(alias="subscriptionId")]
    """Azure Subscribtion ID.

    Either provide subscriptionId or provide a cloudAccountId of an existing
    account.
    """

    tenant_id: Annotated[str, PropertyInfo(alias="tenantId")]
    """Azure Tenant ID.

    Either provide tenantId or provide a cloudAccountId of an existing account.
    """
