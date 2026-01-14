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
from .....types.iaas.api.network_ip_ranges import unregistered_ip_address_release_params
from .....types.iaas.api.projects.request_tracker import RequestTracker

__all__ = ["UnregisteredIPAddressesResource", "AsyncUnregisteredIPAddressesResource"]


class UnregisteredIPAddressesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> UnregisteredIPAddressesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return UnregisteredIPAddressesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UnregisteredIPAddressesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return UnregisteredIPAddressesResourceWithStreamingResponse(self)

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
        release unregistered network IPs

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
            f"/iaas/api/network-ip-ranges/{id}/unregistered-ip-addresses/release",
            body=maybe_transform(
                {"ip_addresses": ip_addresses},
                unregistered_ip_address_release_params.UnregisteredIPAddressReleaseParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    unregistered_ip_address_release_params.UnregisteredIPAddressReleaseParams,
                ),
            ),
            cast_to=RequestTracker,
        )


class AsyncUnregisteredIPAddressesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncUnregisteredIPAddressesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncUnregisteredIPAddressesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUnregisteredIPAddressesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncUnregisteredIPAddressesResourceWithStreamingResponse(self)

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
        release unregistered network IPs

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
            f"/iaas/api/network-ip-ranges/{id}/unregistered-ip-addresses/release",
            body=await async_maybe_transform(
                {"ip_addresses": ip_addresses},
                unregistered_ip_address_release_params.UnregisteredIPAddressReleaseParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    unregistered_ip_address_release_params.UnregisteredIPAddressReleaseParams,
                ),
            ),
            cast_to=RequestTracker,
        )


class UnregisteredIPAddressesResourceWithRawResponse:
    def __init__(self, unregistered_ip_addresses: UnregisteredIPAddressesResource) -> None:
        self._unregistered_ip_addresses = unregistered_ip_addresses

        self.release = to_raw_response_wrapper(
            unregistered_ip_addresses.release,
        )


class AsyncUnregisteredIPAddressesResourceWithRawResponse:
    def __init__(self, unregistered_ip_addresses: AsyncUnregisteredIPAddressesResource) -> None:
        self._unregistered_ip_addresses = unregistered_ip_addresses

        self.release = async_to_raw_response_wrapper(
            unregistered_ip_addresses.release,
        )


class UnregisteredIPAddressesResourceWithStreamingResponse:
    def __init__(self, unregistered_ip_addresses: UnregisteredIPAddressesResource) -> None:
        self._unregistered_ip_addresses = unregistered_ip_addresses

        self.release = to_streamed_response_wrapper(
            unregistered_ip_addresses.release,
        )


class AsyncUnregisteredIPAddressesResourceWithStreamingResponse:
    def __init__(self, unregistered_ip_addresses: AsyncUnregisteredIPAddressesResource) -> None:
        self._unregistered_ip_addresses = unregistered_ip_addresses

        self.release = async_to_streamed_response_wrapper(
            unregistered_ip_addresses.release,
        )
