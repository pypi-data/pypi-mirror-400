# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ....._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.iaas.api.network_ip_ranges import (
    ip_address_release_params,
    ip_address_allocate_params,
    ip_address_retrieve_params,
    ip_address_retrieve_ip_addresses_params,
)
from .....types.iaas.api.projects.request_tracker import RequestTracker
from .....types.iaas.api.network_ip_ranges.network_ip_address import NetworkIPAddress
from .....types.iaas.api.network_ip_ranges.ip_address_retrieve_ip_addresses_response import (
    IPAddressRetrieveIPAddressesResponse,
)

__all__ = ["IPAddressesResource", "AsyncIPAddressesResource"]


class IPAddressesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> IPAddressesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return IPAddressesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IPAddressesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return IPAddressesResourceWithStreamingResponse(self)

    def retrieve(
        self,
        ip_address_id: str,
        *,
        network_ip_range_id: str,
        api_version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkIPAddress:
        """
        Get an allocated or released address of an IPAM network IP range

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not network_ip_range_id:
            raise ValueError(
                f"Expected a non-empty value for `network_ip_range_id` but received {network_ip_range_id!r}"
            )
        if not ip_address_id:
            raise ValueError(f"Expected a non-empty value for `ip_address_id` but received {ip_address_id!r}")
        return self._get(
            f"/iaas/api/network-ip-ranges/{network_ip_range_id}/ip-addresses/{ip_address_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, ip_address_retrieve_params.IPAddressRetrieveParams),
            ),
            cast_to=NetworkIPAddress,
        )

    def allocate(
        self,
        id: str,
        *,
        api_version: str,
        description: str | Omit = omit,
        ip_addresses: SequenceNotStr[str] | Omit = omit,
        number_of_ips: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        allocate network IPs by user

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          description: Description

          ip_addresses: A set of ip addresses IPv4 or IPv6.

          number_of_ips: Number of ip addresses to allocate from the network ip range.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/iaas/api/network-ip-ranges/{id}/ip-addresses/allocate",
            body=maybe_transform(
                {
                    "description": description,
                    "ip_addresses": ip_addresses,
                    "number_of_ips": number_of_ips,
                },
                ip_address_allocate_params.IPAddressAllocateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, ip_address_allocate_params.IPAddressAllocateParams),
            ),
            cast_to=RequestTracker,
        )

    def release(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        ip_addresses: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        release network IPs by user

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          ip_addresses: A set of ip addresses IPv4 or IPv6.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/iaas/api/network-ip-ranges/{id}/ip-addresses/release",
            body=maybe_transform({"ip_addresses": ip_addresses}, ip_address_release_params.IPAddressReleaseParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, ip_address_release_params.IPAddressReleaseParams),
            ),
            cast_to=RequestTracker,
        )

    def retrieve_ip_addresses(
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
    ) -> IPAddressRetrieveIPAddressesResponse:
        """
        Get all allocated and released addresses of an IPAM network IP range

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
            f"/iaas/api/network-ip-ranges/{id}/ip-addresses",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    ip_address_retrieve_ip_addresses_params.IPAddressRetrieveIPAddressesParams,
                ),
            ),
            cast_to=IPAddressRetrieveIPAddressesResponse,
        )


class AsyncIPAddressesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncIPAddressesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncIPAddressesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIPAddressesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncIPAddressesResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        ip_address_id: str,
        *,
        network_ip_range_id: str,
        api_version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkIPAddress:
        """
        Get an allocated or released address of an IPAM network IP range

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not network_ip_range_id:
            raise ValueError(
                f"Expected a non-empty value for `network_ip_range_id` but received {network_ip_range_id!r}"
            )
        if not ip_address_id:
            raise ValueError(f"Expected a non-empty value for `ip_address_id` but received {ip_address_id!r}")
        return await self._get(
            f"/iaas/api/network-ip-ranges/{network_ip_range_id}/ip-addresses/{ip_address_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, ip_address_retrieve_params.IPAddressRetrieveParams
                ),
            ),
            cast_to=NetworkIPAddress,
        )

    async def allocate(
        self,
        id: str,
        *,
        api_version: str,
        description: str | Omit = omit,
        ip_addresses: SequenceNotStr[str] | Omit = omit,
        number_of_ips: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        allocate network IPs by user

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          description: Description

          ip_addresses: A set of ip addresses IPv4 or IPv6.

          number_of_ips: Number of ip addresses to allocate from the network ip range.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/iaas/api/network-ip-ranges/{id}/ip-addresses/allocate",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "ip_addresses": ip_addresses,
                    "number_of_ips": number_of_ips,
                },
                ip_address_allocate_params.IPAddressAllocateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, ip_address_allocate_params.IPAddressAllocateParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def release(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        ip_addresses: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        release network IPs by user

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          ip_addresses: A set of ip addresses IPv4 or IPv6.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/iaas/api/network-ip-ranges/{id}/ip-addresses/release",
            body=await async_maybe_transform(
                {"ip_addresses": ip_addresses}, ip_address_release_params.IPAddressReleaseParams
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, ip_address_release_params.IPAddressReleaseParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def retrieve_ip_addresses(
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
    ) -> IPAddressRetrieveIPAddressesResponse:
        """
        Get all allocated and released addresses of an IPAM network IP range

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
            f"/iaas/api/network-ip-ranges/{id}/ip-addresses",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    ip_address_retrieve_ip_addresses_params.IPAddressRetrieveIPAddressesParams,
                ),
            ),
            cast_to=IPAddressRetrieveIPAddressesResponse,
        )


class IPAddressesResourceWithRawResponse:
    def __init__(self, ip_addresses: IPAddressesResource) -> None:
        self._ip_addresses = ip_addresses

        self.retrieve = to_raw_response_wrapper(
            ip_addresses.retrieve,
        )
        self.allocate = to_raw_response_wrapper(
            ip_addresses.allocate,
        )
        self.release = to_raw_response_wrapper(
            ip_addresses.release,
        )
        self.retrieve_ip_addresses = to_raw_response_wrapper(
            ip_addresses.retrieve_ip_addresses,
        )


class AsyncIPAddressesResourceWithRawResponse:
    def __init__(self, ip_addresses: AsyncIPAddressesResource) -> None:
        self._ip_addresses = ip_addresses

        self.retrieve = async_to_raw_response_wrapper(
            ip_addresses.retrieve,
        )
        self.allocate = async_to_raw_response_wrapper(
            ip_addresses.allocate,
        )
        self.release = async_to_raw_response_wrapper(
            ip_addresses.release,
        )
        self.retrieve_ip_addresses = async_to_raw_response_wrapper(
            ip_addresses.retrieve_ip_addresses,
        )


class IPAddressesResourceWithStreamingResponse:
    def __init__(self, ip_addresses: IPAddressesResource) -> None:
        self._ip_addresses = ip_addresses

        self.retrieve = to_streamed_response_wrapper(
            ip_addresses.retrieve,
        )
        self.allocate = to_streamed_response_wrapper(
            ip_addresses.allocate,
        )
        self.release = to_streamed_response_wrapper(
            ip_addresses.release,
        )
        self.retrieve_ip_addresses = to_streamed_response_wrapper(
            ip_addresses.retrieve_ip_addresses,
        )


class AsyncIPAddressesResourceWithStreamingResponse:
    def __init__(self, ip_addresses: AsyncIPAddressesResource) -> None:
        self._ip_addresses = ip_addresses

        self.retrieve = async_to_streamed_response_wrapper(
            ip_addresses.retrieve,
        )
        self.allocate = async_to_streamed_response_wrapper(
            ip_addresses.allocate,
        )
        self.release = async_to_streamed_response_wrapper(
            ip_addresses.release,
        )
        self.retrieve_ip_addresses = async_to_streamed_response_wrapper(
            ip_addresses.retrieve_ip_addresses,
        )
