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
from ....types.iaas.api import external_ip_block_retrieve_params, external_ip_block_retrieve_external_ip_blocks_params
from ....types.iaas.api.fabric_network import FabricNetwork
from ....types.iaas.api.fabric_network_result import FabricNetworkResult

__all__ = ["ExternalIPBlocksResource", "AsyncExternalIPBlocksResource"]


class ExternalIPBlocksResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ExternalIPBlocksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return ExternalIPBlocksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ExternalIPBlocksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return ExternalIPBlocksResourceWithStreamingResponse(self)

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
    ) -> FabricNetwork:
        """
        An external IP block is network coming from external IPAM provider that can be
        used to create subnetworks inside it

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
            f"/iaas/api/external-ip-blocks/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, external_ip_block_retrieve_params.ExternalIPBlockRetrieveParams
                ),
            ),
            cast_to=FabricNetwork,
        )

    def retrieve_external_ip_blocks(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FabricNetworkResult:
        """
        An external IP block is network coming from external IPAM provider that can be
        used to create subnetworks inside it

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/external-ip-blocks",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    external_ip_block_retrieve_external_ip_blocks_params.ExternalIPBlockRetrieveExternalIPBlocksParams,
                ),
            ),
            cast_to=FabricNetworkResult,
        )


class AsyncExternalIPBlocksResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncExternalIPBlocksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncExternalIPBlocksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncExternalIPBlocksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncExternalIPBlocksResourceWithStreamingResponse(self)

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
    ) -> FabricNetwork:
        """
        An external IP block is network coming from external IPAM provider that can be
        used to create subnetworks inside it

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
            f"/iaas/api/external-ip-blocks/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, external_ip_block_retrieve_params.ExternalIPBlockRetrieveParams
                ),
            ),
            cast_to=FabricNetwork,
        )

    async def retrieve_external_ip_blocks(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FabricNetworkResult:
        """
        An external IP block is network coming from external IPAM provider that can be
        used to create subnetworks inside it

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/external-ip-blocks",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    external_ip_block_retrieve_external_ip_blocks_params.ExternalIPBlockRetrieveExternalIPBlocksParams,
                ),
            ),
            cast_to=FabricNetworkResult,
        )


class ExternalIPBlocksResourceWithRawResponse:
    def __init__(self, external_ip_blocks: ExternalIPBlocksResource) -> None:
        self._external_ip_blocks = external_ip_blocks

        self.retrieve = to_raw_response_wrapper(
            external_ip_blocks.retrieve,
        )
        self.retrieve_external_ip_blocks = to_raw_response_wrapper(
            external_ip_blocks.retrieve_external_ip_blocks,
        )


class AsyncExternalIPBlocksResourceWithRawResponse:
    def __init__(self, external_ip_blocks: AsyncExternalIPBlocksResource) -> None:
        self._external_ip_blocks = external_ip_blocks

        self.retrieve = async_to_raw_response_wrapper(
            external_ip_blocks.retrieve,
        )
        self.retrieve_external_ip_blocks = async_to_raw_response_wrapper(
            external_ip_blocks.retrieve_external_ip_blocks,
        )


class ExternalIPBlocksResourceWithStreamingResponse:
    def __init__(self, external_ip_blocks: ExternalIPBlocksResource) -> None:
        self._external_ip_blocks = external_ip_blocks

        self.retrieve = to_streamed_response_wrapper(
            external_ip_blocks.retrieve,
        )
        self.retrieve_external_ip_blocks = to_streamed_response_wrapper(
            external_ip_blocks.retrieve_external_ip_blocks,
        )


class AsyncExternalIPBlocksResourceWithStreamingResponse:
    def __init__(self, external_ip_blocks: AsyncExternalIPBlocksResource) -> None:
        self._external_ip_blocks = external_ip_blocks

        self.retrieve = async_to_streamed_response_wrapper(
            external_ip_blocks.retrieve,
        )
        self.retrieve_external_ip_blocks = async_to_streamed_response_wrapper(
            external_ip_blocks.retrieve_external_ip_blocks,
        )
