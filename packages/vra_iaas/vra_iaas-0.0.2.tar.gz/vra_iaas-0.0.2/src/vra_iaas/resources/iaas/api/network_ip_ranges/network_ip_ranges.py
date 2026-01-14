# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal

import httpx

from ....._types import Body, Omit, Query, Headers, NoneType, NotGiven, SequenceNotStr, omit, not_given
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from .ip_addresses import (
    IPAddressesResource,
    AsyncIPAddressesResource,
    IPAddressesResourceWithRawResponse,
    AsyncIPAddressesResourceWithRawResponse,
    IPAddressesResourceWithStreamingResponse,
    AsyncIPAddressesResourceWithStreamingResponse,
)
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.iaas.api import (
    network_ip_range_delete_params,
    network_ip_range_update_params,
    network_ip_range_retrieve_params,
    network_ip_range_network_ip_ranges_params,
    network_ip_range_retrieve_network_ip_ranges_params,
)
from .unregistered_ip_addresses import (
    UnregisteredIPAddressesResource,
    AsyncUnregisteredIPAddressesResource,
    UnregisteredIPAddressesResourceWithRawResponse,
    AsyncUnregisteredIPAddressesResourceWithRawResponse,
    UnregisteredIPAddressesResourceWithStreamingResponse,
    AsyncUnregisteredIPAddressesResourceWithStreamingResponse,
)
from .....types.iaas.api.tag_param import TagParam
from .....types.iaas.api.network_ip_range_base import NetworkIPRangeBase
from .....types.iaas.api.network_ip_range_retrieve_response import NetworkIPRangeRetrieveResponse
from .....types.iaas.api.network_ip_range_retrieve_network_ip_ranges_response import (
    NetworkIPRangeRetrieveNetworkIPRangesResponse,
)

__all__ = ["NetworkIPRangesResource", "AsyncNetworkIPRangesResource"]


class NetworkIPRangesResource(SyncAPIResource):
    @cached_property
    def unregistered_ip_addresses(self) -> UnregisteredIPAddressesResource:
        return UnregisteredIPAddressesResource(self._client)

    @cached_property
    def ip_addresses(self) -> IPAddressesResource:
        return IPAddressesResource(self._client)

    @cached_property
    def with_raw_response(self) -> NetworkIPRangesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return NetworkIPRangesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> NetworkIPRangesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return NetworkIPRangesResourceWithStreamingResponse(self)

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
    ) -> NetworkIPRangeRetrieveResponse:
        """
        Get internal IPAM network IP range with a given id

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
            f"/iaas/api/network-ip-ranges/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, network_ip_range_retrieve_params.NetworkIPRangeRetrieveParams
                ),
            ),
            cast_to=NetworkIPRangeRetrieveResponse,
        )

    def update(
        self,
        id: str,
        *,
        end_ip_address: str,
        name: str,
        start_ip_address: str,
        api_version: str | Omit = omit,
        description: str | Omit = omit,
        fabric_network_ids: SequenceNotStr[str] | Omit = omit,
        ip_version: Literal["IPv4", "IPv6"] | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkIPRangeBase:
        """
        Update internal network IP range.

        Args:
          end_ip_address: End IP address of the range.

          name: A human-friendly name used as an identifier in APIs that support this option.

          start_ip_address: Start IP address of the range.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          description: A human-friendly description.

          fabric_network_ids: The Ids of the fabric networks.

          ip_version: IP address version: IPv4 or IPv6. Default: IPv4.

          tags: A set of tag keys and optional values that were set on this resource instance.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/network-ip-ranges/{id}",
            body=maybe_transform(
                {
                    "end_ip_address": end_ip_address,
                    "name": name,
                    "start_ip_address": start_ip_address,
                    "description": description,
                    "fabric_network_ids": fabric_network_ids,
                    "ip_version": ip_version,
                    "tags": tags,
                },
                network_ip_range_update_params.NetworkIPRangeUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, network_ip_range_update_params.NetworkIPRangeUpdateParams
                ),
            ),
            cast_to=NetworkIPRangeBase,
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
        Delete internal network IP range with a given id

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
            f"/iaas/api/network-ip-ranges/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, network_ip_range_delete_params.NetworkIPRangeDeleteParams
                ),
            ),
            cast_to=NoneType,
        )

    def network_ip_ranges(
        self,
        *,
        end_ip_address: str,
        name: str,
        start_ip_address: str,
        api_version: str | Omit = omit,
        description: str | Omit = omit,
        fabric_network_ids: SequenceNotStr[str] | Omit = omit,
        ip_version: Literal["IPv4", "IPv6"] | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkIPRangeBase:
        """
        Creates an internal network IP range.

        Args:
          end_ip_address: End IP address of the range.

          name: A human-friendly name used as an identifier in APIs that support this option.

          start_ip_address: Start IP address of the range.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          description: A human-friendly description.

          fabric_network_ids: The Ids of the fabric networks.

          ip_version: IP address version: IPv4 or IPv6. Default: IPv4.

          tags: A set of tag keys and optional values that were set on this resource instance.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/network-ip-ranges",
            body=maybe_transform(
                {
                    "end_ip_address": end_ip_address,
                    "name": name,
                    "start_ip_address": start_ip_address,
                    "description": description,
                    "fabric_network_ids": fabric_network_ids,
                    "ip_version": ip_version,
                    "tags": tags,
                },
                network_ip_range_network_ip_ranges_params.NetworkIPRangeNetworkIPRangesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    network_ip_range_network_ip_ranges_params.NetworkIPRangeNetworkIPRangesParams,
                ),
            ),
            cast_to=NetworkIPRangeBase,
        )

    def retrieve_network_ip_ranges(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkIPRangeRetrieveNetworkIPRangesResponse:
        """
        Get all internal IPAM network IP ranges

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/network-ip-ranges",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    network_ip_range_retrieve_network_ip_ranges_params.NetworkIPRangeRetrieveNetworkIPRangesParams,
                ),
            ),
            cast_to=NetworkIPRangeRetrieveNetworkIPRangesResponse,
        )


class AsyncNetworkIPRangesResource(AsyncAPIResource):
    @cached_property
    def unregistered_ip_addresses(self) -> AsyncUnregisteredIPAddressesResource:
        return AsyncUnregisteredIPAddressesResource(self._client)

    @cached_property
    def ip_addresses(self) -> AsyncIPAddressesResource:
        return AsyncIPAddressesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncNetworkIPRangesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncNetworkIPRangesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncNetworkIPRangesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncNetworkIPRangesResourceWithStreamingResponse(self)

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
    ) -> NetworkIPRangeRetrieveResponse:
        """
        Get internal IPAM network IP range with a given id

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
            f"/iaas/api/network-ip-ranges/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, network_ip_range_retrieve_params.NetworkIPRangeRetrieveParams
                ),
            ),
            cast_to=NetworkIPRangeRetrieveResponse,
        )

    async def update(
        self,
        id: str,
        *,
        end_ip_address: str,
        name: str,
        start_ip_address: str,
        api_version: str | Omit = omit,
        description: str | Omit = omit,
        fabric_network_ids: SequenceNotStr[str] | Omit = omit,
        ip_version: Literal["IPv4", "IPv6"] | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkIPRangeBase:
        """
        Update internal network IP range.

        Args:
          end_ip_address: End IP address of the range.

          name: A human-friendly name used as an identifier in APIs that support this option.

          start_ip_address: Start IP address of the range.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          description: A human-friendly description.

          fabric_network_ids: The Ids of the fabric networks.

          ip_version: IP address version: IPv4 or IPv6. Default: IPv4.

          tags: A set of tag keys and optional values that were set on this resource instance.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/network-ip-ranges/{id}",
            body=await async_maybe_transform(
                {
                    "end_ip_address": end_ip_address,
                    "name": name,
                    "start_ip_address": start_ip_address,
                    "description": description,
                    "fabric_network_ids": fabric_network_ids,
                    "ip_version": ip_version,
                    "tags": tags,
                },
                network_ip_range_update_params.NetworkIPRangeUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, network_ip_range_update_params.NetworkIPRangeUpdateParams
                ),
            ),
            cast_to=NetworkIPRangeBase,
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
        Delete internal network IP range with a given id

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
            f"/iaas/api/network-ip-ranges/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, network_ip_range_delete_params.NetworkIPRangeDeleteParams
                ),
            ),
            cast_to=NoneType,
        )

    async def network_ip_ranges(
        self,
        *,
        end_ip_address: str,
        name: str,
        start_ip_address: str,
        api_version: str | Omit = omit,
        description: str | Omit = omit,
        fabric_network_ids: SequenceNotStr[str] | Omit = omit,
        ip_version: Literal["IPv4", "IPv6"] | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkIPRangeBase:
        """
        Creates an internal network IP range.

        Args:
          end_ip_address: End IP address of the range.

          name: A human-friendly name used as an identifier in APIs that support this option.

          start_ip_address: Start IP address of the range.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          description: A human-friendly description.

          fabric_network_ids: The Ids of the fabric networks.

          ip_version: IP address version: IPv4 or IPv6. Default: IPv4.

          tags: A set of tag keys and optional values that were set on this resource instance.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/network-ip-ranges",
            body=await async_maybe_transform(
                {
                    "end_ip_address": end_ip_address,
                    "name": name,
                    "start_ip_address": start_ip_address,
                    "description": description,
                    "fabric_network_ids": fabric_network_ids,
                    "ip_version": ip_version,
                    "tags": tags,
                },
                network_ip_range_network_ip_ranges_params.NetworkIPRangeNetworkIPRangesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    network_ip_range_network_ip_ranges_params.NetworkIPRangeNetworkIPRangesParams,
                ),
            ),
            cast_to=NetworkIPRangeBase,
        )

    async def retrieve_network_ip_ranges(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkIPRangeRetrieveNetworkIPRangesResponse:
        """
        Get all internal IPAM network IP ranges

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/network-ip-ranges",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    network_ip_range_retrieve_network_ip_ranges_params.NetworkIPRangeRetrieveNetworkIPRangesParams,
                ),
            ),
            cast_to=NetworkIPRangeRetrieveNetworkIPRangesResponse,
        )


class NetworkIPRangesResourceWithRawResponse:
    def __init__(self, network_ip_ranges: NetworkIPRangesResource) -> None:
        self._network_ip_ranges = network_ip_ranges

        self.retrieve = to_raw_response_wrapper(
            network_ip_ranges.retrieve,
        )
        self.update = to_raw_response_wrapper(
            network_ip_ranges.update,
        )
        self.delete = to_raw_response_wrapper(
            network_ip_ranges.delete,
        )
        self.network_ip_ranges = to_raw_response_wrapper(
            network_ip_ranges.network_ip_ranges,
        )
        self.retrieve_network_ip_ranges = to_raw_response_wrapper(
            network_ip_ranges.retrieve_network_ip_ranges,
        )

    @cached_property
    def unregistered_ip_addresses(self) -> UnregisteredIPAddressesResourceWithRawResponse:
        return UnregisteredIPAddressesResourceWithRawResponse(self._network_ip_ranges.unregistered_ip_addresses)

    @cached_property
    def ip_addresses(self) -> IPAddressesResourceWithRawResponse:
        return IPAddressesResourceWithRawResponse(self._network_ip_ranges.ip_addresses)


class AsyncNetworkIPRangesResourceWithRawResponse:
    def __init__(self, network_ip_ranges: AsyncNetworkIPRangesResource) -> None:
        self._network_ip_ranges = network_ip_ranges

        self.retrieve = async_to_raw_response_wrapper(
            network_ip_ranges.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            network_ip_ranges.update,
        )
        self.delete = async_to_raw_response_wrapper(
            network_ip_ranges.delete,
        )
        self.network_ip_ranges = async_to_raw_response_wrapper(
            network_ip_ranges.network_ip_ranges,
        )
        self.retrieve_network_ip_ranges = async_to_raw_response_wrapper(
            network_ip_ranges.retrieve_network_ip_ranges,
        )

    @cached_property
    def unregistered_ip_addresses(self) -> AsyncUnregisteredIPAddressesResourceWithRawResponse:
        return AsyncUnregisteredIPAddressesResourceWithRawResponse(self._network_ip_ranges.unregistered_ip_addresses)

    @cached_property
    def ip_addresses(self) -> AsyncIPAddressesResourceWithRawResponse:
        return AsyncIPAddressesResourceWithRawResponse(self._network_ip_ranges.ip_addresses)


class NetworkIPRangesResourceWithStreamingResponse:
    def __init__(self, network_ip_ranges: NetworkIPRangesResource) -> None:
        self._network_ip_ranges = network_ip_ranges

        self.retrieve = to_streamed_response_wrapper(
            network_ip_ranges.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            network_ip_ranges.update,
        )
        self.delete = to_streamed_response_wrapper(
            network_ip_ranges.delete,
        )
        self.network_ip_ranges = to_streamed_response_wrapper(
            network_ip_ranges.network_ip_ranges,
        )
        self.retrieve_network_ip_ranges = to_streamed_response_wrapper(
            network_ip_ranges.retrieve_network_ip_ranges,
        )

    @cached_property
    def unregistered_ip_addresses(self) -> UnregisteredIPAddressesResourceWithStreamingResponse:
        return UnregisteredIPAddressesResourceWithStreamingResponse(self._network_ip_ranges.unregistered_ip_addresses)

    @cached_property
    def ip_addresses(self) -> IPAddressesResourceWithStreamingResponse:
        return IPAddressesResourceWithStreamingResponse(self._network_ip_ranges.ip_addresses)


class AsyncNetworkIPRangesResourceWithStreamingResponse:
    def __init__(self, network_ip_ranges: AsyncNetworkIPRangesResource) -> None:
        self._network_ip_ranges = network_ip_ranges

        self.retrieve = async_to_streamed_response_wrapper(
            network_ip_ranges.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            network_ip_ranges.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            network_ip_ranges.delete,
        )
        self.network_ip_ranges = async_to_streamed_response_wrapper(
            network_ip_ranges.network_ip_ranges,
        )
        self.retrieve_network_ip_ranges = async_to_streamed_response_wrapper(
            network_ip_ranges.retrieve_network_ip_ranges,
        )

    @cached_property
    def unregistered_ip_addresses(self) -> AsyncUnregisteredIPAddressesResourceWithStreamingResponse:
        return AsyncUnregisteredIPAddressesResourceWithStreamingResponse(
            self._network_ip_ranges.unregistered_ip_addresses
        )

    @cached_property
    def ip_addresses(self) -> AsyncIPAddressesResourceWithStreamingResponse:
        return AsyncIPAddressesResourceWithStreamingResponse(self._network_ip_ranges.ip_addresses)
