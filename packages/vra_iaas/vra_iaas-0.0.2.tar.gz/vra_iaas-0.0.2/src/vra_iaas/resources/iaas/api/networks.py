# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable

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
    network_list_params,
    network_create_params,
    network_delete_params,
    network_retrieve_params,
    network_retrieve_network_ip_ranges_params,
)
from ....types.iaas.api.network import Network
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.network_list_response import NetworkListResponse
from ....types.iaas.api.projects.request_tracker import RequestTracker
from ....types.iaas.api.placement_constraint_param import PlacementConstraintParam

__all__ = ["NetworksResource", "AsyncNetworksResource"]


class NetworksResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> NetworksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return NetworksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> NetworksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return NetworksResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        name: str,
        project_id: str,
        api_version: str | Omit = omit,
        constraints: Iterable[PlacementConstraintParam] | Omit = omit,
        create_gateway: bool | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        deployment_id: str | Omit = omit,
        description: str | Omit = omit,
        outbound_access: bool | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """Provision a new network based on the passed in constraints.

        The network should
        be destroyed after the machine is destroyed to free up resources.

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          project_id: The id of the project the current user belongs to.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          constraints: Constraints that are used to drive placement policies for the network that is
              produced from this specification, related with the network profile. Constraint
              expressions are matched against tags on existing placement targets.

          create_gateway: Flag to indicate if the network creation should create a gateway. Default is
              true.

          custom_properties: Additional custom properties that may be used to extend this resource.

          deployment_id: The id of the deployment that is associated with this resource

          description: A human-friendly description.

          outbound_access: Flag to indicate if the network needs to have outbound access or not. Default is
              true. This field will be ignored if there is proper input for networkType
              customProperty

          tags: A set of tag keys and optional values that should be set on any resource that is
              produced from this specification.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/networks",
            body=maybe_transform(
                {
                    "name": name,
                    "project_id": project_id,
                    "constraints": constraints,
                    "create_gateway": create_gateway,
                    "custom_properties": custom_properties,
                    "deployment_id": deployment_id,
                    "description": description,
                    "outbound_access": outbound_access,
                    "tags": tags,
                },
                network_create_params.NetworkCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, network_create_params.NetworkCreateParams),
            ),
            cast_to=RequestTracker,
        )

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
    ) -> Network:
        """
        Get network with a given id

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
            f"/iaas/api/networks/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, network_retrieve_params.NetworkRetrieveParams),
            ),
            cast_to=Network,
        )

    def list(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkListResponse:
        """
        Get all networks

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/networks",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, network_list_params.NetworkListParams),
            ),
            cast_to=NetworkListResponse,
        )

    def delete(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        force_delete: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Delete a network with a given id

        Args:
          api_version: Controls whether this is a force delete operation. If true, best effort is made
              for deleting this network. Use with caution as force deleting may cause
              inconsistencies between the cloud provider and VMware Aria Automation.

          force_delete: Controls whether this is a force delete operation. If true, best effort is made
              for deleting this network. Use with caution as force deleting may cause
              inconsistencies between the cloud provider and VMware Aria Automation..

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            f"/iaas/api/networks/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_version": api_version,
                        "force_delete": force_delete,
                    },
                    network_delete_params.NetworkDeleteParams,
                ),
            ),
            cast_to=RequestTracker,
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
    ) -> Network:
        """
        Get associated network IP ranges for a network with a given id

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
            f"/iaas/api/networks/{id}/network-ip-ranges",
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
                    network_retrieve_network_ip_ranges_params.NetworkRetrieveNetworkIPRangesParams,
                ),
            ),
            cast_to=Network,
        )


class AsyncNetworksResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncNetworksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncNetworksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncNetworksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncNetworksResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        name: str,
        project_id: str,
        api_version: str | Omit = omit,
        constraints: Iterable[PlacementConstraintParam] | Omit = omit,
        create_gateway: bool | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        deployment_id: str | Omit = omit,
        description: str | Omit = omit,
        outbound_access: bool | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """Provision a new network based on the passed in constraints.

        The network should
        be destroyed after the machine is destroyed to free up resources.

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          project_id: The id of the project the current user belongs to.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          constraints: Constraints that are used to drive placement policies for the network that is
              produced from this specification, related with the network profile. Constraint
              expressions are matched against tags on existing placement targets.

          create_gateway: Flag to indicate if the network creation should create a gateway. Default is
              true.

          custom_properties: Additional custom properties that may be used to extend this resource.

          deployment_id: The id of the deployment that is associated with this resource

          description: A human-friendly description.

          outbound_access: Flag to indicate if the network needs to have outbound access or not. Default is
              true. This field will be ignored if there is proper input for networkType
              customProperty

          tags: A set of tag keys and optional values that should be set on any resource that is
              produced from this specification.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/networks",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "project_id": project_id,
                    "constraints": constraints,
                    "create_gateway": create_gateway,
                    "custom_properties": custom_properties,
                    "deployment_id": deployment_id,
                    "description": description,
                    "outbound_access": outbound_access,
                    "tags": tags,
                },
                network_create_params.NetworkCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, network_create_params.NetworkCreateParams
                ),
            ),
            cast_to=RequestTracker,
        )

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
    ) -> Network:
        """
        Get network with a given id

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
            f"/iaas/api/networks/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, network_retrieve_params.NetworkRetrieveParams
                ),
            ),
            cast_to=Network,
        )

    async def list(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> NetworkListResponse:
        """
        Get all networks

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/networks",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"api_version": api_version}, network_list_params.NetworkListParams),
            ),
            cast_to=NetworkListResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        force_delete: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Delete a network with a given id

        Args:
          api_version: Controls whether this is a force delete operation. If true, best effort is made
              for deleting this network. Use with caution as force deleting may cause
              inconsistencies between the cloud provider and VMware Aria Automation.

          force_delete: Controls whether this is a force delete operation. If true, best effort is made
              for deleting this network. Use with caution as force deleting may cause
              inconsistencies between the cloud provider and VMware Aria Automation..

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            f"/iaas/api/networks/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_version": api_version,
                        "force_delete": force_delete,
                    },
                    network_delete_params.NetworkDeleteParams,
                ),
            ),
            cast_to=RequestTracker,
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
    ) -> Network:
        """
        Get associated network IP ranges for a network with a given id

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
            f"/iaas/api/networks/{id}/network-ip-ranges",
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
                    network_retrieve_network_ip_ranges_params.NetworkRetrieveNetworkIPRangesParams,
                ),
            ),
            cast_to=Network,
        )


class NetworksResourceWithRawResponse:
    def __init__(self, networks: NetworksResource) -> None:
        self._networks = networks

        self.create = to_raw_response_wrapper(
            networks.create,
        )
        self.retrieve = to_raw_response_wrapper(
            networks.retrieve,
        )
        self.list = to_raw_response_wrapper(
            networks.list,
        )
        self.delete = to_raw_response_wrapper(
            networks.delete,
        )
        self.retrieve_network_ip_ranges = to_raw_response_wrapper(
            networks.retrieve_network_ip_ranges,
        )


class AsyncNetworksResourceWithRawResponse:
    def __init__(self, networks: AsyncNetworksResource) -> None:
        self._networks = networks

        self.create = async_to_raw_response_wrapper(
            networks.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            networks.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            networks.list,
        )
        self.delete = async_to_raw_response_wrapper(
            networks.delete,
        )
        self.retrieve_network_ip_ranges = async_to_raw_response_wrapper(
            networks.retrieve_network_ip_ranges,
        )


class NetworksResourceWithStreamingResponse:
    def __init__(self, networks: NetworksResource) -> None:
        self._networks = networks

        self.create = to_streamed_response_wrapper(
            networks.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            networks.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            networks.list,
        )
        self.delete = to_streamed_response_wrapper(
            networks.delete,
        )
        self.retrieve_network_ip_ranges = to_streamed_response_wrapper(
            networks.retrieve_network_ip_ranges,
        )


class AsyncNetworksResourceWithStreamingResponse:
    def __init__(self, networks: AsyncNetworksResource) -> None:
        self._networks = networks

        self.create = async_to_streamed_response_wrapper(
            networks.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            networks.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            networks.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            networks.delete,
        )
        self.retrieve_network_ip_ranges = async_to_streamed_response_wrapper(
            networks.retrieve_network_ip_ranges,
        )
