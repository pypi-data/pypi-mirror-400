# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict

import httpx

from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
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
from .....types.iaas.api.machines import network_interface_update_params, network_interface_retrieve_params
from .....types.iaas.api.machines.network_interface import NetworkInterface

__all__ = ["NetworkInterfacesResource", "AsyncNetworkInterfacesResource"]


class NetworkInterfacesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> NetworkInterfacesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return NetworkInterfacesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> NetworkInterfacesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return NetworkInterfacesResourceWithStreamingResponse(self)

    def retrieve(
        self,
        network_id: str,
        *,
        id: str,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkInterface:
        """
        Get network interface with a given id for specific machine

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
        if not network_id:
            raise ValueError(f"Expected a non-empty value for `network_id` but received {network_id!r}")
        return self._get(
            f"/iaas/api/machines/{id}/network-interfaces/{network_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, network_interface_retrieve_params.NetworkInterfaceRetrieveParams
                ),
            ),
            cast_to=NetworkInterface,
        )

    def update(
        self,
        network_id: str,
        *,
        id: str,
        api_version: str,
        address: str | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkInterface:
        """Patch network interface with a given id for specific machine.

        Only name,
        description, IPv4 address and custom property updates are supported. The change
        to name and IPv4 address will not propagate to cloud endpoint for provisioned
        machines.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          address: Set IPv4 address for the machine network interface. The change will not
              propagate to cloud endpoint for provisioned machines.

          custom_properties: Additional custom properties that may be used to extend the machine. Internal
              custom properties (for example, prefixed with: "\\__\\__") can not be updated.

          description: Describes the network interface of the machine within the scope of your
              organization and is not propagated to the cloud

          name: Network interface name used during machine network interface provisioning. This
              property only takes effect if it is set before machine provisioning starts. The
              change will not propagate to cloud endpoint for provisioned machines.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        if not network_id:
            raise ValueError(f"Expected a non-empty value for `network_id` but received {network_id!r}")
        return self._patch(
            f"/iaas/api/machines/{id}/network-interfaces/{network_id}",
            body=maybe_transform(
                {
                    "address": address,
                    "custom_properties": custom_properties,
                    "description": description,
                    "name": name,
                },
                network_interface_update_params.NetworkInterfaceUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, network_interface_update_params.NetworkInterfaceUpdateParams
                ),
            ),
            cast_to=NetworkInterface,
        )


class AsyncNetworkInterfacesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncNetworkInterfacesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncNetworkInterfacesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncNetworkInterfacesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncNetworkInterfacesResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        network_id: str,
        *,
        id: str,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkInterface:
        """
        Get network interface with a given id for specific machine

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
        if not network_id:
            raise ValueError(f"Expected a non-empty value for `network_id` but received {network_id!r}")
        return await self._get(
            f"/iaas/api/machines/{id}/network-interfaces/{network_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, network_interface_retrieve_params.NetworkInterfaceRetrieveParams
                ),
            ),
            cast_to=NetworkInterface,
        )

    async def update(
        self,
        network_id: str,
        *,
        id: str,
        api_version: str,
        address: str | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkInterface:
        """Patch network interface with a given id for specific machine.

        Only name,
        description, IPv4 address and custom property updates are supported. The change
        to name and IPv4 address will not propagate to cloud endpoint for provisioned
        machines.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          address: Set IPv4 address for the machine network interface. The change will not
              propagate to cloud endpoint for provisioned machines.

          custom_properties: Additional custom properties that may be used to extend the machine. Internal
              custom properties (for example, prefixed with: "\\__\\__") can not be updated.

          description: Describes the network interface of the machine within the scope of your
              organization and is not propagated to the cloud

          name: Network interface name used during machine network interface provisioning. This
              property only takes effect if it is set before machine provisioning starts. The
              change will not propagate to cloud endpoint for provisioned machines.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        if not network_id:
            raise ValueError(f"Expected a non-empty value for `network_id` but received {network_id!r}")
        return await self._patch(
            f"/iaas/api/machines/{id}/network-interfaces/{network_id}",
            body=await async_maybe_transform(
                {
                    "address": address,
                    "custom_properties": custom_properties,
                    "description": description,
                    "name": name,
                },
                network_interface_update_params.NetworkInterfaceUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, network_interface_update_params.NetworkInterfaceUpdateParams
                ),
            ),
            cast_to=NetworkInterface,
        )


class NetworkInterfacesResourceWithRawResponse:
    def __init__(self, network_interfaces: NetworkInterfacesResource) -> None:
        self._network_interfaces = network_interfaces

        self.retrieve = to_raw_response_wrapper(
            network_interfaces.retrieve,
        )
        self.update = to_raw_response_wrapper(
            network_interfaces.update,
        )


class AsyncNetworkInterfacesResourceWithRawResponse:
    def __init__(self, network_interfaces: AsyncNetworkInterfacesResource) -> None:
        self._network_interfaces = network_interfaces

        self.retrieve = async_to_raw_response_wrapper(
            network_interfaces.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            network_interfaces.update,
        )


class NetworkInterfacesResourceWithStreamingResponse:
    def __init__(self, network_interfaces: NetworkInterfacesResource) -> None:
        self._network_interfaces = network_interfaces

        self.retrieve = to_streamed_response_wrapper(
            network_interfaces.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            network_interfaces.update,
        )


class AsyncNetworkInterfacesResourceWithStreamingResponse:
    def __init__(self, network_interfaces: AsyncNetworkInterfacesResource) -> None:
        self._network_interfaces = network_interfaces

        self.retrieve = async_to_streamed_response_wrapper(
            network_interfaces.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            network_interfaces.update,
        )
