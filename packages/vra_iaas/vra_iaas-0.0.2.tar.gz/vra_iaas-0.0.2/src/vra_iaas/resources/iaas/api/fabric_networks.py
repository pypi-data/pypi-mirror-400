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
    fabric_network_update_params,
    fabric_network_retrieve_params,
    fabric_network_retrieve_fabric_networks_params,
    fabric_network_retrieve_network_ip_ranges_params,
)
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.fabric_network import FabricNetwork
from ....types.iaas.api.fabric_network_result import FabricNetworkResult

__all__ = ["FabricNetworksResource", "AsyncFabricNetworksResource"]


class FabricNetworksResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FabricNetworksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return FabricNetworksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FabricNetworksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return FabricNetworksResourceWithStreamingResponse(self)

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
    ) -> FabricNetwork:
        """
        Get fabric network with a given id

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
            f"/iaas/api/fabric-networks/{id}",
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
                    fabric_network_retrieve_params.FabricNetworkRetrieveParams,
                ),
            ),
            cast_to=FabricNetwork,
        )

    def update(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FabricNetwork:
        """Update fabric network.

        Only tag updates are supported.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          tags: A set of tag keys and optional values that were set on this resource instance.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/fabric-networks/{id}",
            body=maybe_transform({"tags": tags}, fabric_network_update_params.FabricNetworkUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, fabric_network_update_params.FabricNetworkUpdateParams
                ),
            ),
            cast_to=FabricNetwork,
        )

    def retrieve_fabric_networks(
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
    ) -> FabricNetworkResult:
        """
        Get all fabric networks.

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
            "/iaas/api/fabric-networks",
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
                    fabric_network_retrieve_fabric_networks_params.FabricNetworkRetrieveFabricNetworksParams,
                ),
            ),
            cast_to=FabricNetworkResult,
        )

    def retrieve_network_ip_ranges(
        self,
        id: str,
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
    ) -> FabricNetwork:
        """
        Get associated fabric network IP ranges for a fabric network with a given id

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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/iaas/api/fabric-networks/{id}/network-ip-ranges",
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
                    fabric_network_retrieve_network_ip_ranges_params.FabricNetworkRetrieveNetworkIPRangesParams,
                ),
            ),
            cast_to=FabricNetwork,
        )


class AsyncFabricNetworksResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFabricNetworksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFabricNetworksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFabricNetworksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncFabricNetworksResourceWithStreamingResponse(self)

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
    ) -> FabricNetwork:
        """
        Get fabric network with a given id

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
            f"/iaas/api/fabric-networks/{id}",
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
                    fabric_network_retrieve_params.FabricNetworkRetrieveParams,
                ),
            ),
            cast_to=FabricNetwork,
        )

    async def update(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FabricNetwork:
        """Update fabric network.

        Only tag updates are supported.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          tags: A set of tag keys and optional values that were set on this resource instance.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/fabric-networks/{id}",
            body=await async_maybe_transform({"tags": tags}, fabric_network_update_params.FabricNetworkUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, fabric_network_update_params.FabricNetworkUpdateParams
                ),
            ),
            cast_to=FabricNetwork,
        )

    async def retrieve_fabric_networks(
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
    ) -> FabricNetworkResult:
        """
        Get all fabric networks.

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
            "/iaas/api/fabric-networks",
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
                    fabric_network_retrieve_fabric_networks_params.FabricNetworkRetrieveFabricNetworksParams,
                ),
            ),
            cast_to=FabricNetworkResult,
        )

    async def retrieve_network_ip_ranges(
        self,
        id: str,
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
    ) -> FabricNetwork:
        """
        Get associated fabric network IP ranges for a fabric network with a given id

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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/iaas/api/fabric-networks/{id}/network-ip-ranges",
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
                    fabric_network_retrieve_network_ip_ranges_params.FabricNetworkRetrieveNetworkIPRangesParams,
                ),
            ),
            cast_to=FabricNetwork,
        )


class FabricNetworksResourceWithRawResponse:
    def __init__(self, fabric_networks: FabricNetworksResource) -> None:
        self._fabric_networks = fabric_networks

        self.retrieve = to_raw_response_wrapper(
            fabric_networks.retrieve,
        )
        self.update = to_raw_response_wrapper(
            fabric_networks.update,
        )
        self.retrieve_fabric_networks = to_raw_response_wrapper(
            fabric_networks.retrieve_fabric_networks,
        )
        self.retrieve_network_ip_ranges = to_raw_response_wrapper(
            fabric_networks.retrieve_network_ip_ranges,
        )


class AsyncFabricNetworksResourceWithRawResponse:
    def __init__(self, fabric_networks: AsyncFabricNetworksResource) -> None:
        self._fabric_networks = fabric_networks

        self.retrieve = async_to_raw_response_wrapper(
            fabric_networks.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            fabric_networks.update,
        )
        self.retrieve_fabric_networks = async_to_raw_response_wrapper(
            fabric_networks.retrieve_fabric_networks,
        )
        self.retrieve_network_ip_ranges = async_to_raw_response_wrapper(
            fabric_networks.retrieve_network_ip_ranges,
        )


class FabricNetworksResourceWithStreamingResponse:
    def __init__(self, fabric_networks: FabricNetworksResource) -> None:
        self._fabric_networks = fabric_networks

        self.retrieve = to_streamed_response_wrapper(
            fabric_networks.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            fabric_networks.update,
        )
        self.retrieve_fabric_networks = to_streamed_response_wrapper(
            fabric_networks.retrieve_fabric_networks,
        )
        self.retrieve_network_ip_ranges = to_streamed_response_wrapper(
            fabric_networks.retrieve_network_ip_ranges,
        )


class AsyncFabricNetworksResourceWithStreamingResponse:
    def __init__(self, fabric_networks: AsyncFabricNetworksResource) -> None:
        self._fabric_networks = fabric_networks

        self.retrieve = async_to_streamed_response_wrapper(
            fabric_networks.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            fabric_networks.update,
        )
        self.retrieve_fabric_networks = async_to_streamed_response_wrapper(
            fabric_networks.retrieve_fabric_networks,
        )
        self.retrieve_network_ip_ranges = async_to_streamed_response_wrapper(
            fabric_networks.retrieve_network_ip_ranges,
        )
