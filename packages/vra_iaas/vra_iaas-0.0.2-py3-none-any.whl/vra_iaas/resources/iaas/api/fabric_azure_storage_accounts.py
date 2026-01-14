# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

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
    fabric_azure_storage_account_retrieve_params,
    fabric_azure_storage_account_retrieve_fabric_azure_storage_accounts_params,
)
from ....types.iaas.api.fabric_azure_storage_account import FabricAzureStorageAccount
from ....types.iaas.api.fabric_azure_storage_account_retrieve_fabric_azure_storage_accounts_response import (
    FabricAzureStorageAccountRetrieveFabricAzureStorageAccountsResponse,
)

__all__ = ["FabricAzureStorageAccountsResource", "AsyncFabricAzureStorageAccountsResource"]


class FabricAzureStorageAccountsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FabricAzureStorageAccountsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return FabricAzureStorageAccountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FabricAzureStorageAccountsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return FabricAzureStorageAccountsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        id: str,
        *,
        select: str | Omit = omit,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FabricAzureStorageAccount:
        """
        Get fabric Azure storage account with a given id

        Args:
          select: Select a subset of properties to include in the response.

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
            f"/iaas/api/fabric-azure-storage-accounts/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "select": select,
                        "api_version": api_version,
                    },
                    fabric_azure_storage_account_retrieve_params.FabricAzureStorageAccountRetrieveParams,
                ),
            ),
            cast_to=FabricAzureStorageAccount,
        )

    def retrieve_fabric_azure_storage_accounts(
        self,
        *,
        count: bool | Omit = omit,
        filter: str | Omit = omit,
        select: str | Omit = omit,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FabricAzureStorageAccountRetrieveFabricAzureStorageAccountsResponse:
        """
        Get all fabric Azure storage accounts.

        Args:
          count: Flag which when specified, regardless of the assigned value, shows the total
              number of records. If the collection has a filter it shows the number of records
              matching the filter.

          filter: Filter the results by a specified predicate expression. Operators: eq, ne, and,
              or.

          select: Select a subset of properties to include in the response.

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
            "/iaas/api/fabric-azure-storage-accounts",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "count": count,
                        "filter": filter,
                        "select": select,
                        "skip": skip,
                        "top": top,
                        "api_version": api_version,
                    },
                    fabric_azure_storage_account_retrieve_fabric_azure_storage_accounts_params.FabricAzureStorageAccountRetrieveFabricAzureStorageAccountsParams,
                ),
            ),
            cast_to=FabricAzureStorageAccountRetrieveFabricAzureStorageAccountsResponse,
        )


class AsyncFabricAzureStorageAccountsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFabricAzureStorageAccountsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFabricAzureStorageAccountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFabricAzureStorageAccountsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncFabricAzureStorageAccountsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        id: str,
        *,
        select: str | Omit = omit,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FabricAzureStorageAccount:
        """
        Get fabric Azure storage account with a given id

        Args:
          select: Select a subset of properties to include in the response.

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
            f"/iaas/api/fabric-azure-storage-accounts/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "select": select,
                        "api_version": api_version,
                    },
                    fabric_azure_storage_account_retrieve_params.FabricAzureStorageAccountRetrieveParams,
                ),
            ),
            cast_to=FabricAzureStorageAccount,
        )

    async def retrieve_fabric_azure_storage_accounts(
        self,
        *,
        count: bool | Omit = omit,
        filter: str | Omit = omit,
        select: str | Omit = omit,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FabricAzureStorageAccountRetrieveFabricAzureStorageAccountsResponse:
        """
        Get all fabric Azure storage accounts.

        Args:
          count: Flag which when specified, regardless of the assigned value, shows the total
              number of records. If the collection has a filter it shows the number of records
              matching the filter.

          filter: Filter the results by a specified predicate expression. Operators: eq, ne, and,
              or.

          select: Select a subset of properties to include in the response.

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
            "/iaas/api/fabric-azure-storage-accounts",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "count": count,
                        "filter": filter,
                        "select": select,
                        "skip": skip,
                        "top": top,
                        "api_version": api_version,
                    },
                    fabric_azure_storage_account_retrieve_fabric_azure_storage_accounts_params.FabricAzureStorageAccountRetrieveFabricAzureStorageAccountsParams,
                ),
            ),
            cast_to=FabricAzureStorageAccountRetrieveFabricAzureStorageAccountsResponse,
        )


class FabricAzureStorageAccountsResourceWithRawResponse:
    def __init__(self, fabric_azure_storage_accounts: FabricAzureStorageAccountsResource) -> None:
        self._fabric_azure_storage_accounts = fabric_azure_storage_accounts

        self.retrieve = to_raw_response_wrapper(
            fabric_azure_storage_accounts.retrieve,
        )
        self.retrieve_fabric_azure_storage_accounts = to_raw_response_wrapper(
            fabric_azure_storage_accounts.retrieve_fabric_azure_storage_accounts,
        )


class AsyncFabricAzureStorageAccountsResourceWithRawResponse:
    def __init__(self, fabric_azure_storage_accounts: AsyncFabricAzureStorageAccountsResource) -> None:
        self._fabric_azure_storage_accounts = fabric_azure_storage_accounts

        self.retrieve = async_to_raw_response_wrapper(
            fabric_azure_storage_accounts.retrieve,
        )
        self.retrieve_fabric_azure_storage_accounts = async_to_raw_response_wrapper(
            fabric_azure_storage_accounts.retrieve_fabric_azure_storage_accounts,
        )


class FabricAzureStorageAccountsResourceWithStreamingResponse:
    def __init__(self, fabric_azure_storage_accounts: FabricAzureStorageAccountsResource) -> None:
        self._fabric_azure_storage_accounts = fabric_azure_storage_accounts

        self.retrieve = to_streamed_response_wrapper(
            fabric_azure_storage_accounts.retrieve,
        )
        self.retrieve_fabric_azure_storage_accounts = to_streamed_response_wrapper(
            fabric_azure_storage_accounts.retrieve_fabric_azure_storage_accounts,
        )


class AsyncFabricAzureStorageAccountsResourceWithStreamingResponse:
    def __init__(self, fabric_azure_storage_accounts: AsyncFabricAzureStorageAccountsResource) -> None:
        self._fabric_azure_storage_accounts = fabric_azure_storage_accounts

        self.retrieve = async_to_streamed_response_wrapper(
            fabric_azure_storage_accounts.retrieve,
        )
        self.retrieve_fabric_azure_storage_accounts = async_to_streamed_response_wrapper(
            fabric_azure_storage_accounts.retrieve_fabric_azure_storage_accounts,
        )
