# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

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
    fabric_networks_vsphere_update_params,
    fabric_networks_vsphere_retrieve_params,
    fabric_networks_vsphere_retrieve_network_ip_ranges_params,
    fabric_networks_vsphere_retrieve_fabric_networks_vsphere_params,
)
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.fabric_network_vsphere import FabricNetworkVsphere
from ....types.iaas.api.fabric_networks_vsphere_retrieve_fabric_networks_vsphere_response import (
    FabricNetworksVsphereRetrieveFabricNetworksVsphereResponse,
)

__all__ = ["FabricNetworksVsphereResource", "AsyncFabricNetworksVsphereResource"]


class FabricNetworksVsphereResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FabricNetworksVsphereResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return FabricNetworksVsphereResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FabricNetworksVsphereResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return FabricNetworksVsphereResourceWithStreamingResponse(self)

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
    ) -> FabricNetworkVsphere:
        """
        Get vSphere fabric network with a given id

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
            f"/iaas/api/fabric-networks-vsphere/{id}",
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
                    fabric_networks_vsphere_retrieve_params.FabricNetworksVsphereRetrieveParams,
                ),
            ),
            cast_to=FabricNetworkVsphere,
        )

    def update(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        cidr: str | Omit = omit,
        default_gateway: str | Omit = omit,
        default_ipv6_gateway: str | Omit = omit,
        dns_search_domains: SequenceNotStr[str] | Omit = omit,
        dns_server_addresses: SequenceNotStr[str] | Omit = omit,
        domain: str | Omit = omit,
        ipv6_cidr: str | Omit = omit,
        is_default: bool | Omit = omit,
        is_public: bool | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FabricNetworkVsphere:
        """
        Update vSphere fabric network.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          cidr: Network CIDR to be used.

          default_gateway: IPv4 default gateway to be used.

          default_ipv6_gateway: IPv6 default gateway to be used.

          dns_search_domains: A list of DNS search domains that were set on this resource instance.

          dns_server_addresses: A list of DNS server addresses that were set on this resource instance.

          domain: Domain value.

          ipv6_cidr: Network IPv6 CIDR to be used.

          is_default: Indicates whether this is the default subnet for the zone.

          is_public: Indicates whether the sub-network supports public IP assignment.

          tags: A set of tag keys and optional values that were set on this resource instance.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/fabric-networks-vsphere/{id}",
            body=maybe_transform(
                {
                    "cidr": cidr,
                    "default_gateway": default_gateway,
                    "default_ipv6_gateway": default_ipv6_gateway,
                    "dns_search_domains": dns_search_domains,
                    "dns_server_addresses": dns_server_addresses,
                    "domain": domain,
                    "ipv6_cidr": ipv6_cidr,
                    "is_default": is_default,
                    "is_public": is_public,
                    "tags": tags,
                },
                fabric_networks_vsphere_update_params.FabricNetworksVsphereUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    fabric_networks_vsphere_update_params.FabricNetworksVsphereUpdateParams,
                ),
            ),
            cast_to=FabricNetworkVsphere,
        )

    def retrieve_fabric_networks_vsphere(
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
    ) -> FabricNetworksVsphereRetrieveFabricNetworksVsphereResponse:
        """
        Get all vSphere fabric networks.

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
            "/iaas/api/fabric-networks-vsphere",
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
                    fabric_networks_vsphere_retrieve_fabric_networks_vsphere_params.FabricNetworksVsphereRetrieveFabricNetworksVsphereParams,
                ),
            ),
            cast_to=FabricNetworksVsphereRetrieveFabricNetworksVsphereResponse,
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
    ) -> FabricNetworkVsphere:
        """
        Get associated fabric network IP ranges for a fabric vSphere network with a
        given id

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
            f"/iaas/api/fabric-networks-vsphere/{id}/network-ip-ranges",
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
                    fabric_networks_vsphere_retrieve_network_ip_ranges_params.FabricNetworksVsphereRetrieveNetworkIPRangesParams,
                ),
            ),
            cast_to=FabricNetworkVsphere,
        )


class AsyncFabricNetworksVsphereResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFabricNetworksVsphereResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFabricNetworksVsphereResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFabricNetworksVsphereResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncFabricNetworksVsphereResourceWithStreamingResponse(self)

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
    ) -> FabricNetworkVsphere:
        """
        Get vSphere fabric network with a given id

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
            f"/iaas/api/fabric-networks-vsphere/{id}",
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
                    fabric_networks_vsphere_retrieve_params.FabricNetworksVsphereRetrieveParams,
                ),
            ),
            cast_to=FabricNetworkVsphere,
        )

    async def update(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        cidr: str | Omit = omit,
        default_gateway: str | Omit = omit,
        default_ipv6_gateway: str | Omit = omit,
        dns_search_domains: SequenceNotStr[str] | Omit = omit,
        dns_server_addresses: SequenceNotStr[str] | Omit = omit,
        domain: str | Omit = omit,
        ipv6_cidr: str | Omit = omit,
        is_default: bool | Omit = omit,
        is_public: bool | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FabricNetworkVsphere:
        """
        Update vSphere fabric network.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          cidr: Network CIDR to be used.

          default_gateway: IPv4 default gateway to be used.

          default_ipv6_gateway: IPv6 default gateway to be used.

          dns_search_domains: A list of DNS search domains that were set on this resource instance.

          dns_server_addresses: A list of DNS server addresses that were set on this resource instance.

          domain: Domain value.

          ipv6_cidr: Network IPv6 CIDR to be used.

          is_default: Indicates whether this is the default subnet for the zone.

          is_public: Indicates whether the sub-network supports public IP assignment.

          tags: A set of tag keys and optional values that were set on this resource instance.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/fabric-networks-vsphere/{id}",
            body=await async_maybe_transform(
                {
                    "cidr": cidr,
                    "default_gateway": default_gateway,
                    "default_ipv6_gateway": default_ipv6_gateway,
                    "dns_search_domains": dns_search_domains,
                    "dns_server_addresses": dns_server_addresses,
                    "domain": domain,
                    "ipv6_cidr": ipv6_cidr,
                    "is_default": is_default,
                    "is_public": is_public,
                    "tags": tags,
                },
                fabric_networks_vsphere_update_params.FabricNetworksVsphereUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    fabric_networks_vsphere_update_params.FabricNetworksVsphereUpdateParams,
                ),
            ),
            cast_to=FabricNetworkVsphere,
        )

    async def retrieve_fabric_networks_vsphere(
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
    ) -> FabricNetworksVsphereRetrieveFabricNetworksVsphereResponse:
        """
        Get all vSphere fabric networks.

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
            "/iaas/api/fabric-networks-vsphere",
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
                    fabric_networks_vsphere_retrieve_fabric_networks_vsphere_params.FabricNetworksVsphereRetrieveFabricNetworksVsphereParams,
                ),
            ),
            cast_to=FabricNetworksVsphereRetrieveFabricNetworksVsphereResponse,
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
    ) -> FabricNetworkVsphere:
        """
        Get associated fabric network IP ranges for a fabric vSphere network with a
        given id

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
            f"/iaas/api/fabric-networks-vsphere/{id}/network-ip-ranges",
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
                    fabric_networks_vsphere_retrieve_network_ip_ranges_params.FabricNetworksVsphereRetrieveNetworkIPRangesParams,
                ),
            ),
            cast_to=FabricNetworkVsphere,
        )


class FabricNetworksVsphereResourceWithRawResponse:
    def __init__(self, fabric_networks_vsphere: FabricNetworksVsphereResource) -> None:
        self._fabric_networks_vsphere = fabric_networks_vsphere

        self.retrieve = to_raw_response_wrapper(
            fabric_networks_vsphere.retrieve,
        )
        self.update = to_raw_response_wrapper(
            fabric_networks_vsphere.update,
        )
        self.retrieve_fabric_networks_vsphere = to_raw_response_wrapper(
            fabric_networks_vsphere.retrieve_fabric_networks_vsphere,
        )
        self.retrieve_network_ip_ranges = to_raw_response_wrapper(
            fabric_networks_vsphere.retrieve_network_ip_ranges,
        )


class AsyncFabricNetworksVsphereResourceWithRawResponse:
    def __init__(self, fabric_networks_vsphere: AsyncFabricNetworksVsphereResource) -> None:
        self._fabric_networks_vsphere = fabric_networks_vsphere

        self.retrieve = async_to_raw_response_wrapper(
            fabric_networks_vsphere.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            fabric_networks_vsphere.update,
        )
        self.retrieve_fabric_networks_vsphere = async_to_raw_response_wrapper(
            fabric_networks_vsphere.retrieve_fabric_networks_vsphere,
        )
        self.retrieve_network_ip_ranges = async_to_raw_response_wrapper(
            fabric_networks_vsphere.retrieve_network_ip_ranges,
        )


class FabricNetworksVsphereResourceWithStreamingResponse:
    def __init__(self, fabric_networks_vsphere: FabricNetworksVsphereResource) -> None:
        self._fabric_networks_vsphere = fabric_networks_vsphere

        self.retrieve = to_streamed_response_wrapper(
            fabric_networks_vsphere.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            fabric_networks_vsphere.update,
        )
        self.retrieve_fabric_networks_vsphere = to_streamed_response_wrapper(
            fabric_networks_vsphere.retrieve_fabric_networks_vsphere,
        )
        self.retrieve_network_ip_ranges = to_streamed_response_wrapper(
            fabric_networks_vsphere.retrieve_network_ip_ranges,
        )


class AsyncFabricNetworksVsphereResourceWithStreamingResponse:
    def __init__(self, fabric_networks_vsphere: AsyncFabricNetworksVsphereResource) -> None:
        self._fabric_networks_vsphere = fabric_networks_vsphere

        self.retrieve = async_to_streamed_response_wrapper(
            fabric_networks_vsphere.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            fabric_networks_vsphere.update,
        )
        self.retrieve_fabric_networks_vsphere = async_to_streamed_response_wrapper(
            fabric_networks_vsphere.retrieve_fabric_networks_vsphere,
        )
        self.retrieve_network_ip_ranges = async_to_streamed_response_wrapper(
            fabric_networks_vsphere.retrieve_network_ip_ranges,
        )
