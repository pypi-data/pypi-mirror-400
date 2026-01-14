# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.iaas.api import (
    cloud_accounts_azure_delete_params,
    cloud_accounts_azure_update_params,
    cloud_accounts_azure_retrieve_params,
    cloud_accounts_azure_region_enumeration_params,
    cloud_accounts_azure_cloud_accounts_azure_params,
    cloud_accounts_azure_private_image_enumeration_params,
    cloud_accounts_azure_retrieve_cloud_accounts_azure_params,
)
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.cloud_account_azure import CloudAccountAzure
from ....types.iaas.api.projects.request_tracker import RequestTracker
from ....types.iaas.api.region_specification_param import RegionSpecificationParam
from ....types.iaas.api.cloud_accounts_azure_retrieve_cloud_accounts_azure_response import (
    CloudAccountsAzureRetrieveCloudAccountsAzureResponse,
)

__all__ = ["CloudAccountsAzureResource", "AsyncCloudAccountsAzureResource"]


class CloudAccountsAzureResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CloudAccountsAzureResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return CloudAccountsAzureResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CloudAccountsAzureResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return CloudAccountsAzureResourceWithStreamingResponse(self)

    def retrieve(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CloudAccountAzure:
        """
        Get an Azure Cloud Account with a given id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/iaas/api/cloud-accounts-azure/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_azure_retrieve_params.CloudAccountsAzureRetrieveParams
                ),
            ),
            cast_to=CloudAccountAzure,
        )

    def update(
        self,
        id: str,
        *,
        api_version: str,
        client_application_id: str,
        client_application_secret_key: str,
        name: str,
        regions: Iterable[RegionSpecificationParam],
        subscription_id: str,
        tenant_id: str,
        create_default_zones: bool | Omit = omit,
        description: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Update Azure cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          client_application_id: Azure Client Application ID

          client_application_secret_key: Azure Client Application Secret Key

          name: A human-friendly name used as an identifier in APIs that support this option.

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          subscription_id: Azure Subscribtion ID

          tenant_id: Azure Tenant ID

          create_default_zones: Create default cloud zones for the enabled regions.

          description: A human-friendly description.

          tags: A set of tag keys and optional values to set on the Cloud Account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/cloud-accounts-azure/{id}",
            body=maybe_transform(
                {
                    "client_application_id": client_application_id,
                    "client_application_secret_key": client_application_secret_key,
                    "name": name,
                    "regions": regions,
                    "subscription_id": subscription_id,
                    "tenant_id": tenant_id,
                    "create_default_zones": create_default_zones,
                    "description": description,
                    "tags": tags,
                },
                cloud_accounts_azure_update_params.CloudAccountsAzureUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_azure_update_params.CloudAccountsAzureUpdateParams
                ),
            ),
            cast_to=RequestTracker,
        )

    def delete(
        self,
        id: str,
        *,
        api_version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Delete an Azure Cloud Account with a given id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            f"/iaas/api/cloud-accounts-azure/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_azure_delete_params.CloudAccountsAzureDeleteParams
                ),
            ),
            cast_to=RequestTracker,
        )

    def cloud_accounts_azure(
        self,
        *,
        api_version: str,
        client_application_id: str,
        client_application_secret_key: str,
        name: str,
        regions: Iterable[RegionSpecificationParam],
        subscription_id: str,
        tenant_id: str,
        validate_only: str | Omit = omit,
        create_default_zones: bool | Omit = omit,
        description: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Create a cloud account in the current organization

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          client_application_id: Azure Client Application ID

          client_application_secret_key: Azure Client Application Secret Key

          name: A human-friendly name used as an identifier in APIs that support this option.

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          subscription_id: Azure Subscribtion ID

          tenant_id: Azure Tenant ID

          validate_only: If provided, it only validates the credentials in the Cloud Account
              Specification, and cloud account will not be created.

          create_default_zones: Create default cloud zones for the enabled regions.

          description: A human-friendly description.

          tags: A set of tag keys and optional values to set on the Cloud Account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/cloud-accounts-azure",
            body=maybe_transform(
                {
                    "client_application_id": client_application_id,
                    "client_application_secret_key": client_application_secret_key,
                    "name": name,
                    "regions": regions,
                    "subscription_id": subscription_id,
                    "tenant_id": tenant_id,
                    "create_default_zones": create_default_zones,
                    "description": description,
                    "tags": tags,
                },
                cloud_accounts_azure_cloud_accounts_azure_params.CloudAccountsAzureCloudAccountsAzureParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_version": api_version,
                        "validate_only": validate_only,
                    },
                    cloud_accounts_azure_cloud_accounts_azure_params.CloudAccountsAzureCloudAccountsAzureParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def private_image_enumeration(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Enumerate all private images for enabled regions of the specified Azure account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/iaas/api/cloud-accounts-azure/{id}/private-image-enumeration",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_azure_private_image_enumeration_params.CloudAccountsAzurePrivateImageEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def region_enumeration(
        self,
        *,
        api_version: str,
        client_application_id: str | Omit = omit,
        client_application_secret_key: str | Omit = omit,
        cloud_account_id: str | Omit = omit,
        subscription_id: str | Omit = omit,
        tenant_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Get the available regions for specified Azure cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          client_application_id: Azure Client Application ID. Either provide clientApplicationId or provide a
              cloudAccountId of an existing account.

          client_application_secret_key: Azure Client Application Secret Key. Either provide clientApplicationSecretKey
              or provide a cloudAccountId of an existing account.

          cloud_account_id: Existing cloud account id. Either provide id of existing account, or cloud
              account credentials: clientApplicationId, clientApplicationSecretKey and
              tenantId.

          subscription_id: Azure Subscribtion ID. Either provide subscriptionId or provide a cloudAccountId
              of an existing account.

          tenant_id: Azure Tenant ID. Either provide tenantId or provide a cloudAccountId of an
              existing account.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/cloud-accounts-azure/region-enumeration",
            body=maybe_transform(
                {
                    "client_application_id": client_application_id,
                    "client_application_secret_key": client_application_secret_key,
                    "cloud_account_id": cloud_account_id,
                    "subscription_id": subscription_id,
                    "tenant_id": tenant_id,
                },
                cloud_accounts_azure_region_enumeration_params.CloudAccountsAzureRegionEnumerationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_azure_region_enumeration_params.CloudAccountsAzureRegionEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def retrieve_cloud_accounts_azure(
        self,
        *,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CloudAccountsAzureRetrieveCloudAccountsAzureResponse:
        """
        Get all Azure cloud accounts within the current organization

        Args:
          skip: Number of records you want to skip.

          top: Number of records you want to get.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/cloud-accounts-azure",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "skip": skip,
                        "top": top,
                        "api_version": api_version,
                    },
                    cloud_accounts_azure_retrieve_cloud_accounts_azure_params.CloudAccountsAzureRetrieveCloudAccountsAzureParams,
                ),
            ),
            cast_to=CloudAccountsAzureRetrieveCloudAccountsAzureResponse,
        )


class AsyncCloudAccountsAzureResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCloudAccountsAzureResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCloudAccountsAzureResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCloudAccountsAzureResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncCloudAccountsAzureResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CloudAccountAzure:
        """
        Get an Azure Cloud Account with a given id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/iaas/api/cloud-accounts-azure/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_azure_retrieve_params.CloudAccountsAzureRetrieveParams
                ),
            ),
            cast_to=CloudAccountAzure,
        )

    async def update(
        self,
        id: str,
        *,
        api_version: str,
        client_application_id: str,
        client_application_secret_key: str,
        name: str,
        regions: Iterable[RegionSpecificationParam],
        subscription_id: str,
        tenant_id: str,
        create_default_zones: bool | Omit = omit,
        description: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Update Azure cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          client_application_id: Azure Client Application ID

          client_application_secret_key: Azure Client Application Secret Key

          name: A human-friendly name used as an identifier in APIs that support this option.

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          subscription_id: Azure Subscribtion ID

          tenant_id: Azure Tenant ID

          create_default_zones: Create default cloud zones for the enabled regions.

          description: A human-friendly description.

          tags: A set of tag keys and optional values to set on the Cloud Account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/cloud-accounts-azure/{id}",
            body=await async_maybe_transform(
                {
                    "client_application_id": client_application_id,
                    "client_application_secret_key": client_application_secret_key,
                    "name": name,
                    "regions": regions,
                    "subscription_id": subscription_id,
                    "tenant_id": tenant_id,
                    "create_default_zones": create_default_zones,
                    "description": description,
                    "tags": tags,
                },
                cloud_accounts_azure_update_params.CloudAccountsAzureUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_azure_update_params.CloudAccountsAzureUpdateParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def delete(
        self,
        id: str,
        *,
        api_version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Delete an Azure Cloud Account with a given id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            f"/iaas/api/cloud-accounts-azure/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_azure_delete_params.CloudAccountsAzureDeleteParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def cloud_accounts_azure(
        self,
        *,
        api_version: str,
        client_application_id: str,
        client_application_secret_key: str,
        name: str,
        regions: Iterable[RegionSpecificationParam],
        subscription_id: str,
        tenant_id: str,
        validate_only: str | Omit = omit,
        create_default_zones: bool | Omit = omit,
        description: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Create a cloud account in the current organization

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          client_application_id: Azure Client Application ID

          client_application_secret_key: Azure Client Application Secret Key

          name: A human-friendly name used as an identifier in APIs that support this option.

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          subscription_id: Azure Subscribtion ID

          tenant_id: Azure Tenant ID

          validate_only: If provided, it only validates the credentials in the Cloud Account
              Specification, and cloud account will not be created.

          create_default_zones: Create default cloud zones for the enabled regions.

          description: A human-friendly description.

          tags: A set of tag keys and optional values to set on the Cloud Account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/cloud-accounts-azure",
            body=await async_maybe_transform(
                {
                    "client_application_id": client_application_id,
                    "client_application_secret_key": client_application_secret_key,
                    "name": name,
                    "regions": regions,
                    "subscription_id": subscription_id,
                    "tenant_id": tenant_id,
                    "create_default_zones": create_default_zones,
                    "description": description,
                    "tags": tags,
                },
                cloud_accounts_azure_cloud_accounts_azure_params.CloudAccountsAzureCloudAccountsAzureParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_version": api_version,
                        "validate_only": validate_only,
                    },
                    cloud_accounts_azure_cloud_accounts_azure_params.CloudAccountsAzureCloudAccountsAzureParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def private_image_enumeration(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Enumerate all private images for enabled regions of the specified Azure account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/iaas/api/cloud-accounts-azure/{id}/private-image-enumeration",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_azure_private_image_enumeration_params.CloudAccountsAzurePrivateImageEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def region_enumeration(
        self,
        *,
        api_version: str,
        client_application_id: str | Omit = omit,
        client_application_secret_key: str | Omit = omit,
        cloud_account_id: str | Omit = omit,
        subscription_id: str | Omit = omit,
        tenant_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Get the available regions for specified Azure cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          client_application_id: Azure Client Application ID. Either provide clientApplicationId or provide a
              cloudAccountId of an existing account.

          client_application_secret_key: Azure Client Application Secret Key. Either provide clientApplicationSecretKey
              or provide a cloudAccountId of an existing account.

          cloud_account_id: Existing cloud account id. Either provide id of existing account, or cloud
              account credentials: clientApplicationId, clientApplicationSecretKey and
              tenantId.

          subscription_id: Azure Subscribtion ID. Either provide subscriptionId or provide a cloudAccountId
              of an existing account.

          tenant_id: Azure Tenant ID. Either provide tenantId or provide a cloudAccountId of an
              existing account.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/cloud-accounts-azure/region-enumeration",
            body=await async_maybe_transform(
                {
                    "client_application_id": client_application_id,
                    "client_application_secret_key": client_application_secret_key,
                    "cloud_account_id": cloud_account_id,
                    "subscription_id": subscription_id,
                    "tenant_id": tenant_id,
                },
                cloud_accounts_azure_region_enumeration_params.CloudAccountsAzureRegionEnumerationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_azure_region_enumeration_params.CloudAccountsAzureRegionEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def retrieve_cloud_accounts_azure(
        self,
        *,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CloudAccountsAzureRetrieveCloudAccountsAzureResponse:
        """
        Get all Azure cloud accounts within the current organization

        Args:
          skip: Number of records you want to skip.

          top: Number of records you want to get.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/cloud-accounts-azure",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "skip": skip,
                        "top": top,
                        "api_version": api_version,
                    },
                    cloud_accounts_azure_retrieve_cloud_accounts_azure_params.CloudAccountsAzureRetrieveCloudAccountsAzureParams,
                ),
            ),
            cast_to=CloudAccountsAzureRetrieveCloudAccountsAzureResponse,
        )


class CloudAccountsAzureResourceWithRawResponse:
    def __init__(self, cloud_accounts_azure: CloudAccountsAzureResource) -> None:
        self._cloud_accounts_azure = cloud_accounts_azure

        self.retrieve = to_raw_response_wrapper(
            cloud_accounts_azure.retrieve,
        )
        self.update = to_raw_response_wrapper(
            cloud_accounts_azure.update,
        )
        self.delete = to_raw_response_wrapper(
            cloud_accounts_azure.delete,
        )
        self.cloud_accounts_azure = to_raw_response_wrapper(
            cloud_accounts_azure.cloud_accounts_azure,
        )
        self.private_image_enumeration = to_raw_response_wrapper(
            cloud_accounts_azure.private_image_enumeration,
        )
        self.region_enumeration = to_raw_response_wrapper(
            cloud_accounts_azure.region_enumeration,
        )
        self.retrieve_cloud_accounts_azure = to_raw_response_wrapper(
            cloud_accounts_azure.retrieve_cloud_accounts_azure,
        )


class AsyncCloudAccountsAzureResourceWithRawResponse:
    def __init__(self, cloud_accounts_azure: AsyncCloudAccountsAzureResource) -> None:
        self._cloud_accounts_azure = cloud_accounts_azure

        self.retrieve = async_to_raw_response_wrapper(
            cloud_accounts_azure.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            cloud_accounts_azure.update,
        )
        self.delete = async_to_raw_response_wrapper(
            cloud_accounts_azure.delete,
        )
        self.cloud_accounts_azure = async_to_raw_response_wrapper(
            cloud_accounts_azure.cloud_accounts_azure,
        )
        self.private_image_enumeration = async_to_raw_response_wrapper(
            cloud_accounts_azure.private_image_enumeration,
        )
        self.region_enumeration = async_to_raw_response_wrapper(
            cloud_accounts_azure.region_enumeration,
        )
        self.retrieve_cloud_accounts_azure = async_to_raw_response_wrapper(
            cloud_accounts_azure.retrieve_cloud_accounts_azure,
        )


class CloudAccountsAzureResourceWithStreamingResponse:
    def __init__(self, cloud_accounts_azure: CloudAccountsAzureResource) -> None:
        self._cloud_accounts_azure = cloud_accounts_azure

        self.retrieve = to_streamed_response_wrapper(
            cloud_accounts_azure.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            cloud_accounts_azure.update,
        )
        self.delete = to_streamed_response_wrapper(
            cloud_accounts_azure.delete,
        )
        self.cloud_accounts_azure = to_streamed_response_wrapper(
            cloud_accounts_azure.cloud_accounts_azure,
        )
        self.private_image_enumeration = to_streamed_response_wrapper(
            cloud_accounts_azure.private_image_enumeration,
        )
        self.region_enumeration = to_streamed_response_wrapper(
            cloud_accounts_azure.region_enumeration,
        )
        self.retrieve_cloud_accounts_azure = to_streamed_response_wrapper(
            cloud_accounts_azure.retrieve_cloud_accounts_azure,
        )


class AsyncCloudAccountsAzureResourceWithStreamingResponse:
    def __init__(self, cloud_accounts_azure: AsyncCloudAccountsAzureResource) -> None:
        self._cloud_accounts_azure = cloud_accounts_azure

        self.retrieve = async_to_streamed_response_wrapper(
            cloud_accounts_azure.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            cloud_accounts_azure.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            cloud_accounts_azure.delete,
        )
        self.cloud_accounts_azure = async_to_streamed_response_wrapper(
            cloud_accounts_azure.cloud_accounts_azure,
        )
        self.private_image_enumeration = async_to_streamed_response_wrapper(
            cloud_accounts_azure.private_image_enumeration,
        )
        self.region_enumeration = async_to_streamed_response_wrapper(
            cloud_accounts_azure.region_enumeration,
        )
        self.retrieve_cloud_accounts_azure = async_to_streamed_response_wrapper(
            cloud_accounts_azure.retrieve_cloud_accounts_azure,
        )
