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
from ....types.iaas.api import network_domain_retrieve_params, network_domain_retrieve_network_domains_params
from ....types.iaas.api.network_domain import NetworkDomain
from ....types.iaas.api.network_domain_retrieve_network_domains_response import (
    NetworkDomainRetrieveNetworkDomainsResponse,
)

__all__ = ["NetworkDomainsResource", "AsyncNetworkDomainsResource"]


class NetworkDomainsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> NetworkDomainsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return NetworkDomainsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> NetworkDomainsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return NetworkDomainsResourceWithStreamingResponse(self)

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
    ) -> NetworkDomain:
        """
        Get network domain with a given id

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
            f"/iaas/api/network-domains/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, network_domain_retrieve_params.NetworkDomainRetrieveParams
                ),
            ),
            cast_to=NetworkDomain,
        )

    def retrieve_network_domains(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkDomainRetrieveNetworkDomainsResponse:
        """
        Get all network domains.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/network-domains",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    network_domain_retrieve_network_domains_params.NetworkDomainRetrieveNetworkDomainsParams,
                ),
            ),
            cast_to=NetworkDomainRetrieveNetworkDomainsResponse,
        )


class AsyncNetworkDomainsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncNetworkDomainsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncNetworkDomainsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncNetworkDomainsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncNetworkDomainsResourceWithStreamingResponse(self)

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
    ) -> NetworkDomain:
        """
        Get network domain with a given id

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
            f"/iaas/api/network-domains/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, network_domain_retrieve_params.NetworkDomainRetrieveParams
                ),
            ),
            cast_to=NetworkDomain,
        )

    async def retrieve_network_domains(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkDomainRetrieveNetworkDomainsResponse:
        """
        Get all network domains.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/network-domains",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    network_domain_retrieve_network_domains_params.NetworkDomainRetrieveNetworkDomainsParams,
                ),
            ),
            cast_to=NetworkDomainRetrieveNetworkDomainsResponse,
        )


class NetworkDomainsResourceWithRawResponse:
    def __init__(self, network_domains: NetworkDomainsResource) -> None:
        self._network_domains = network_domains

        self.retrieve = to_raw_response_wrapper(
            network_domains.retrieve,
        )
        self.retrieve_network_domains = to_raw_response_wrapper(
            network_domains.retrieve_network_domains,
        )


class AsyncNetworkDomainsResourceWithRawResponse:
    def __init__(self, network_domains: AsyncNetworkDomainsResource) -> None:
        self._network_domains = network_domains

        self.retrieve = async_to_raw_response_wrapper(
            network_domains.retrieve,
        )
        self.retrieve_network_domains = async_to_raw_response_wrapper(
            network_domains.retrieve_network_domains,
        )


class NetworkDomainsResourceWithStreamingResponse:
    def __init__(self, network_domains: NetworkDomainsResource) -> None:
        self._network_domains = network_domains

        self.retrieve = to_streamed_response_wrapper(
            network_domains.retrieve,
        )
        self.retrieve_network_domains = to_streamed_response_wrapper(
            network_domains.retrieve_network_domains,
        )


class AsyncNetworkDomainsResourceWithStreamingResponse:
    def __init__(self, network_domains: AsyncNetworkDomainsResource) -> None:
        self._network_domains = network_domains

        self.retrieve = async_to_streamed_response_wrapper(
            network_domains.retrieve,
        )
        self.retrieve_network_domains = async_to_streamed_response_wrapper(
            network_domains.retrieve_network_domains,
        )
