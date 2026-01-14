# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
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
    data_collector_delete_params,
    data_collector_retrieve_params,
    data_collector_data_collectors_params,
    data_collector_retrieve_data_collectors_params,
)
from ....types.iaas.api.data_collector import DataCollector
from ....types.iaas.api.data_collector_data_collectors_response import DataCollectorDataCollectorsResponse
from ....types.iaas.api.data_collector_retrieve_data_collectors_response import (
    DataCollectorRetrieveDataCollectorsResponse,
)

__all__ = ["DataCollectorsResource", "AsyncDataCollectorsResource"]


class DataCollectorsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DataCollectorsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return DataCollectorsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DataCollectorsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return DataCollectorsResourceWithStreamingResponse(self)

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
    ) -> DataCollector:
        """
        Get Data Collector with a given id.

        Note: Data collector endpoints are not available in VMware Aria Automation
        (on-prem) release.

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
            f"/iaas/api/data-collectors/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, data_collector_retrieve_params.DataCollectorRetrieveParams
                ),
            ),
            cast_to=DataCollector,
        )

    def delete(
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
    ) -> None:
        """
        Delete Data Collector with a given id.

        Note: Data collector endpoints are not available in VMware Aria Automation
        (on-prem) release.

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
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/iaas/api/data-collectors/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, data_collector_delete_params.DataCollectorDeleteParams
                ),
            ),
            cast_to=NoneType,
        )

    def data_collectors(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DataCollectorDataCollectorsResponse:
        """
        Create a new Data Collector.

        Note: Data collector endpoints are not available in VMware Aria Automation
        (on-prem) release.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/data-collectors",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    data_collector_data_collectors_params.DataCollectorDataCollectorsParams,
                ),
            ),
            cast_to=DataCollectorDataCollectorsResponse,
        )

    def retrieve_data_collectors(
        self,
        *,
        api_version: str | Omit = omit,
        disabled: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DataCollectorRetrieveDataCollectorsResponse:
        """
        Get all Data Collectors.

        Note: Data collector endpoints are not available in VMware Aria Automation
        (on-prem) release.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          disabled: If query param is provided with value equals to true, only disabled data
              collectors will be retrieved.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/data-collectors",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_version": api_version,
                        "disabled": disabled,
                    },
                    data_collector_retrieve_data_collectors_params.DataCollectorRetrieveDataCollectorsParams,
                ),
            ),
            cast_to=DataCollectorRetrieveDataCollectorsResponse,
        )


class AsyncDataCollectorsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDataCollectorsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDataCollectorsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDataCollectorsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncDataCollectorsResourceWithStreamingResponse(self)

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
    ) -> DataCollector:
        """
        Get Data Collector with a given id.

        Note: Data collector endpoints are not available in VMware Aria Automation
        (on-prem) release.

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
            f"/iaas/api/data-collectors/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, data_collector_retrieve_params.DataCollectorRetrieveParams
                ),
            ),
            cast_to=DataCollector,
        )

    async def delete(
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
    ) -> None:
        """
        Delete Data Collector with a given id.

        Note: Data collector endpoints are not available in VMware Aria Automation
        (on-prem) release.

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
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/iaas/api/data-collectors/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, data_collector_delete_params.DataCollectorDeleteParams
                ),
            ),
            cast_to=NoneType,
        )

    async def data_collectors(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DataCollectorDataCollectorsResponse:
        """
        Create a new Data Collector.

        Note: Data collector endpoints are not available in VMware Aria Automation
        (on-prem) release.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/data-collectors",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    data_collector_data_collectors_params.DataCollectorDataCollectorsParams,
                ),
            ),
            cast_to=DataCollectorDataCollectorsResponse,
        )

    async def retrieve_data_collectors(
        self,
        *,
        api_version: str | Omit = omit,
        disabled: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DataCollectorRetrieveDataCollectorsResponse:
        """
        Get all Data Collectors.

        Note: Data collector endpoints are not available in VMware Aria Automation
        (on-prem) release.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          disabled: If query param is provided with value equals to true, only disabled data
              collectors will be retrieved.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/data-collectors",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_version": api_version,
                        "disabled": disabled,
                    },
                    data_collector_retrieve_data_collectors_params.DataCollectorRetrieveDataCollectorsParams,
                ),
            ),
            cast_to=DataCollectorRetrieveDataCollectorsResponse,
        )


class DataCollectorsResourceWithRawResponse:
    def __init__(self, data_collectors: DataCollectorsResource) -> None:
        self._data_collectors = data_collectors

        self.retrieve = to_raw_response_wrapper(
            data_collectors.retrieve,
        )
        self.delete = to_raw_response_wrapper(
            data_collectors.delete,
        )
        self.data_collectors = to_raw_response_wrapper(
            data_collectors.data_collectors,
        )
        self.retrieve_data_collectors = to_raw_response_wrapper(
            data_collectors.retrieve_data_collectors,
        )


class AsyncDataCollectorsResourceWithRawResponse:
    def __init__(self, data_collectors: AsyncDataCollectorsResource) -> None:
        self._data_collectors = data_collectors

        self.retrieve = async_to_raw_response_wrapper(
            data_collectors.retrieve,
        )
        self.delete = async_to_raw_response_wrapper(
            data_collectors.delete,
        )
        self.data_collectors = async_to_raw_response_wrapper(
            data_collectors.data_collectors,
        )
        self.retrieve_data_collectors = async_to_raw_response_wrapper(
            data_collectors.retrieve_data_collectors,
        )


class DataCollectorsResourceWithStreamingResponse:
    def __init__(self, data_collectors: DataCollectorsResource) -> None:
        self._data_collectors = data_collectors

        self.retrieve = to_streamed_response_wrapper(
            data_collectors.retrieve,
        )
        self.delete = to_streamed_response_wrapper(
            data_collectors.delete,
        )
        self.data_collectors = to_streamed_response_wrapper(
            data_collectors.data_collectors,
        )
        self.retrieve_data_collectors = to_streamed_response_wrapper(
            data_collectors.retrieve_data_collectors,
        )


class AsyncDataCollectorsResourceWithStreamingResponse:
    def __init__(self, data_collectors: AsyncDataCollectorsResource) -> None:
        self._data_collectors = data_collectors

        self.retrieve = async_to_streamed_response_wrapper(
            data_collectors.retrieve,
        )
        self.delete = async_to_streamed_response_wrapper(
            data_collectors.delete,
        )
        self.data_collectors = async_to_streamed_response_wrapper(
            data_collectors.data_collectors,
        )
        self.retrieve_data_collectors = async_to_streamed_response_wrapper(
            data_collectors.retrieve_data_collectors,
        )
