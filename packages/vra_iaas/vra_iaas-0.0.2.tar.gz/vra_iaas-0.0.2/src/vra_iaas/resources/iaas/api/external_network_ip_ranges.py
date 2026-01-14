# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
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
    external_network_ip_range_update_params,
    external_network_ip_range_retrieve_params,
    external_network_ip_range_retrieve_external_network_ip_ranges_params,
)
from ....types.iaas.api.external_network_ip_range import ExternalNetworkIPRange
from ....types.iaas.api.external_network_ip_range_retrieve_external_network_ip_ranges_response import (
    ExternalNetworkIPRangeRetrieveExternalNetworkIPRangesResponse,
)

__all__ = ["ExternalNetworkIPRangesResource", "AsyncExternalNetworkIPRangesResource"]


class ExternalNetworkIPRangesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ExternalNetworkIPRangesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return ExternalNetworkIPRangesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ExternalNetworkIPRangesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return ExternalNetworkIPRangesResourceWithStreamingResponse(self)

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
    ) -> ExternalNetworkIPRange:
        """
        Get external IPAM network IP range with a given id

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
            f"/iaas/api/external-network-ip-ranges/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    external_network_ip_range_retrieve_params.ExternalNetworkIPRangeRetrieveParams,
                ),
            ),
            cast_to=ExternalNetworkIPRange,
        )

    def update(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        fabric_network_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ExternalNetworkIPRange:
        """
        Assign the external IPAM network IP range to a different network and/or change
        the tags of the external IPAM network IP range.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          fabric_network_ids: A list of fabric network Ids that this IP range should be associated with.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/external-network-ip-ranges/{id}",
            body=maybe_transform(
                {"fabric_network_ids": fabric_network_ids},
                external_network_ip_range_update_params.ExternalNetworkIPRangeUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    external_network_ip_range_update_params.ExternalNetworkIPRangeUpdateParams,
                ),
            ),
            cast_to=ExternalNetworkIPRange,
        )

    def retrieve_external_network_ip_ranges(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ExternalNetworkIPRangeRetrieveExternalNetworkIPRangesResponse:
        """
        Get all external IPAM network IP ranges

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/external-network-ip-ranges",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    external_network_ip_range_retrieve_external_network_ip_ranges_params.ExternalNetworkIPRangeRetrieveExternalNetworkIPRangesParams,
                ),
            ),
            cast_to=ExternalNetworkIPRangeRetrieveExternalNetworkIPRangesResponse,
        )


class AsyncExternalNetworkIPRangesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncExternalNetworkIPRangesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncExternalNetworkIPRangesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncExternalNetworkIPRangesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncExternalNetworkIPRangesResourceWithStreamingResponse(self)

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
    ) -> ExternalNetworkIPRange:
        """
        Get external IPAM network IP range with a given id

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
            f"/iaas/api/external-network-ip-ranges/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    external_network_ip_range_retrieve_params.ExternalNetworkIPRangeRetrieveParams,
                ),
            ),
            cast_to=ExternalNetworkIPRange,
        )

    async def update(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        fabric_network_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ExternalNetworkIPRange:
        """
        Assign the external IPAM network IP range to a different network and/or change
        the tags of the external IPAM network IP range.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          fabric_network_ids: A list of fabric network Ids that this IP range should be associated with.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/external-network-ip-ranges/{id}",
            body=await async_maybe_transform(
                {"fabric_network_ids": fabric_network_ids},
                external_network_ip_range_update_params.ExternalNetworkIPRangeUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    external_network_ip_range_update_params.ExternalNetworkIPRangeUpdateParams,
                ),
            ),
            cast_to=ExternalNetworkIPRange,
        )

    async def retrieve_external_network_ip_ranges(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ExternalNetworkIPRangeRetrieveExternalNetworkIPRangesResponse:
        """
        Get all external IPAM network IP ranges

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/external-network-ip-ranges",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    external_network_ip_range_retrieve_external_network_ip_ranges_params.ExternalNetworkIPRangeRetrieveExternalNetworkIPRangesParams,
                ),
            ),
            cast_to=ExternalNetworkIPRangeRetrieveExternalNetworkIPRangesResponse,
        )


class ExternalNetworkIPRangesResourceWithRawResponse:
    def __init__(self, external_network_ip_ranges: ExternalNetworkIPRangesResource) -> None:
        self._external_network_ip_ranges = external_network_ip_ranges

        self.retrieve = to_raw_response_wrapper(
            external_network_ip_ranges.retrieve,
        )
        self.update = to_raw_response_wrapper(
            external_network_ip_ranges.update,
        )
        self.retrieve_external_network_ip_ranges = to_raw_response_wrapper(
            external_network_ip_ranges.retrieve_external_network_ip_ranges,
        )


class AsyncExternalNetworkIPRangesResourceWithRawResponse:
    def __init__(self, external_network_ip_ranges: AsyncExternalNetworkIPRangesResource) -> None:
        self._external_network_ip_ranges = external_network_ip_ranges

        self.retrieve = async_to_raw_response_wrapper(
            external_network_ip_ranges.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            external_network_ip_ranges.update,
        )
        self.retrieve_external_network_ip_ranges = async_to_raw_response_wrapper(
            external_network_ip_ranges.retrieve_external_network_ip_ranges,
        )


class ExternalNetworkIPRangesResourceWithStreamingResponse:
    def __init__(self, external_network_ip_ranges: ExternalNetworkIPRangesResource) -> None:
        self._external_network_ip_ranges = external_network_ip_ranges

        self.retrieve = to_streamed_response_wrapper(
            external_network_ip_ranges.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            external_network_ip_ranges.update,
        )
        self.retrieve_external_network_ip_ranges = to_streamed_response_wrapper(
            external_network_ip_ranges.retrieve_external_network_ip_ranges,
        )


class AsyncExternalNetworkIPRangesResourceWithStreamingResponse:
    def __init__(self, external_network_ip_ranges: AsyncExternalNetworkIPRangesResource) -> None:
        self._external_network_ip_ranges = external_network_ip_ranges

        self.retrieve = async_to_streamed_response_wrapper(
            external_network_ip_ranges.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            external_network_ip_ranges.update,
        )
        self.retrieve_external_network_ip_ranges = async_to_streamed_response_wrapper(
            external_network_ip_ranges.retrieve_external_network_ip_ranges,
        )
