# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable

import httpx

from ....._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ....._utils import maybe_transform, async_maybe_transform
from .operations import (
    OperationsResource,
    AsyncOperationsResource,
    OperationsResourceWithRawResponse,
    AsyncOperationsResourceWithRawResponse,
    OperationsResourceWithStreamingResponse,
    AsyncOperationsResourceWithStreamingResponse,
)
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.iaas.api import (
    load_balancer_delete_params,
    load_balancer_retrieve_params,
    load_balancer_load_balancers_params,
    load_balancer_retrieve_load_balancers_params,
)
from .....types.iaas.api.tag_param import TagParam
from .....types.iaas.api.load_balancer import LoadBalancer
from .....types.iaas.api.projects.request_tracker import RequestTracker
from .....types.iaas.api.load_balancers.route_configuration_param import RouteConfigurationParam
from .....types.iaas.api.load_balancer_retrieve_load_balancers_response import LoadBalancerRetrieveLoadBalancersResponse
from .....types.iaas.api.machines.network_interface_specification_param import NetworkInterfaceSpecificationParam

__all__ = ["LoadBalancersResource", "AsyncLoadBalancersResource"]


class LoadBalancersResource(SyncAPIResource):
    @cached_property
    def operations(self) -> OperationsResource:
        return OperationsResource(self._client)

    @cached_property
    def with_raw_response(self) -> LoadBalancersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return LoadBalancersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LoadBalancersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return LoadBalancersResourceWithStreamingResponse(self)

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
    ) -> LoadBalancer:
        """
        Get load balancer with a given id

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
            f"/iaas/api/load-balancers/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, load_balancer_retrieve_params.LoadBalancerRetrieveParams
                ),
            ),
            cast_to=LoadBalancer,
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
        Delete load balancer with a given id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          force_delete: Controls whether this is a force delete operation. If true, best effort is made
              for deleting this load balancer. Use with caution as force deleting may cause
              inconsistencies between the cloud provider and VMware Aria Automation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            f"/iaas/api/load-balancers/{id}",
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
                    load_balancer_delete_params.LoadBalancerDeleteParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def load_balancers(
        self,
        *,
        name: str,
        nics: Iterable[NetworkInterfaceSpecificationParam],
        project_id: str,
        routes: Iterable[RouteConfigurationParam],
        api_version: str | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        deployment_id: str | Omit = omit,
        description: str | Omit = omit,
        internet_facing: bool | Omit = omit,
        logging_level: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        target_links: SequenceNotStr[str] | Omit = omit,
        type: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Create load balancer

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          nics: A set of network interface specifications for this load balancer.

          project_id: The id of the project the current user belongs to.

          routes: The load balancer route configuration regarding ports and protocols.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          custom_properties: Additional custom properties that may be used to extend this resource.

          deployment_id: The id of the deployment that is associated with this resource

          description: A human-friendly description.

          internet_facing: An Internet-facing load balancer has a publicly resolvable DNS name, so it can
              route requests from clients over the Internet to the instances that are
              registered with the load balancer.

          logging_level: Defines logging level for collecting load balancer traffic logs.

          tags: A set of tag keys and optional values that should be set on any resource that is
              produced from this specification.

          target_links: A list of links to target load balancer pool members. Links can be to either a
              machine or a machine's network interface.

          type: Define the type/variant of load balancer numbers e.g.for NSX the number virtual
              servers and pool members load balancer can host

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/load-balancers",
            body=maybe_transform(
                {
                    "name": name,
                    "nics": nics,
                    "project_id": project_id,
                    "routes": routes,
                    "custom_properties": custom_properties,
                    "deployment_id": deployment_id,
                    "description": description,
                    "internet_facing": internet_facing,
                    "logging_level": logging_level,
                    "tags": tags,
                    "target_links": target_links,
                    "type": type,
                },
                load_balancer_load_balancers_params.LoadBalancerLoadBalancersParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, load_balancer_load_balancers_params.LoadBalancerLoadBalancersParams
                ),
            ),
            cast_to=RequestTracker,
        )

    def retrieve_load_balancers(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> LoadBalancerRetrieveLoadBalancersResponse:
        """
        Get all load balancers

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/load-balancers",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    load_balancer_retrieve_load_balancers_params.LoadBalancerRetrieveLoadBalancersParams,
                ),
            ),
            cast_to=LoadBalancerRetrieveLoadBalancersResponse,
        )


class AsyncLoadBalancersResource(AsyncAPIResource):
    @cached_property
    def operations(self) -> AsyncOperationsResource:
        return AsyncOperationsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncLoadBalancersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncLoadBalancersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLoadBalancersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncLoadBalancersResourceWithStreamingResponse(self)

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
    ) -> LoadBalancer:
        """
        Get load balancer with a given id

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
            f"/iaas/api/load-balancers/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, load_balancer_retrieve_params.LoadBalancerRetrieveParams
                ),
            ),
            cast_to=LoadBalancer,
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
        Delete load balancer with a given id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          force_delete: Controls whether this is a force delete operation. If true, best effort is made
              for deleting this load balancer. Use with caution as force deleting may cause
              inconsistencies between the cloud provider and VMware Aria Automation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            f"/iaas/api/load-balancers/{id}",
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
                    load_balancer_delete_params.LoadBalancerDeleteParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def load_balancers(
        self,
        *,
        name: str,
        nics: Iterable[NetworkInterfaceSpecificationParam],
        project_id: str,
        routes: Iterable[RouteConfigurationParam],
        api_version: str | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        deployment_id: str | Omit = omit,
        description: str | Omit = omit,
        internet_facing: bool | Omit = omit,
        logging_level: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        target_links: SequenceNotStr[str] | Omit = omit,
        type: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Create load balancer

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          nics: A set of network interface specifications for this load balancer.

          project_id: The id of the project the current user belongs to.

          routes: The load balancer route configuration regarding ports and protocols.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          custom_properties: Additional custom properties that may be used to extend this resource.

          deployment_id: The id of the deployment that is associated with this resource

          description: A human-friendly description.

          internet_facing: An Internet-facing load balancer has a publicly resolvable DNS name, so it can
              route requests from clients over the Internet to the instances that are
              registered with the load balancer.

          logging_level: Defines logging level for collecting load balancer traffic logs.

          tags: A set of tag keys and optional values that should be set on any resource that is
              produced from this specification.

          target_links: A list of links to target load balancer pool members. Links can be to either a
              machine or a machine's network interface.

          type: Define the type/variant of load balancer numbers e.g.for NSX the number virtual
              servers and pool members load balancer can host

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/load-balancers",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "nics": nics,
                    "project_id": project_id,
                    "routes": routes,
                    "custom_properties": custom_properties,
                    "deployment_id": deployment_id,
                    "description": description,
                    "internet_facing": internet_facing,
                    "logging_level": logging_level,
                    "tags": tags,
                    "target_links": target_links,
                    "type": type,
                },
                load_balancer_load_balancers_params.LoadBalancerLoadBalancersParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, load_balancer_load_balancers_params.LoadBalancerLoadBalancersParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def retrieve_load_balancers(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> LoadBalancerRetrieveLoadBalancersResponse:
        """
        Get all load balancers

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/load-balancers",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    load_balancer_retrieve_load_balancers_params.LoadBalancerRetrieveLoadBalancersParams,
                ),
            ),
            cast_to=LoadBalancerRetrieveLoadBalancersResponse,
        )


class LoadBalancersResourceWithRawResponse:
    def __init__(self, load_balancers: LoadBalancersResource) -> None:
        self._load_balancers = load_balancers

        self.retrieve = to_raw_response_wrapper(
            load_balancers.retrieve,
        )
        self.delete = to_raw_response_wrapper(
            load_balancers.delete,
        )
        self.load_balancers = to_raw_response_wrapper(
            load_balancers.load_balancers,
        )
        self.retrieve_load_balancers = to_raw_response_wrapper(
            load_balancers.retrieve_load_balancers,
        )

    @cached_property
    def operations(self) -> OperationsResourceWithRawResponse:
        return OperationsResourceWithRawResponse(self._load_balancers.operations)


class AsyncLoadBalancersResourceWithRawResponse:
    def __init__(self, load_balancers: AsyncLoadBalancersResource) -> None:
        self._load_balancers = load_balancers

        self.retrieve = async_to_raw_response_wrapper(
            load_balancers.retrieve,
        )
        self.delete = async_to_raw_response_wrapper(
            load_balancers.delete,
        )
        self.load_balancers = async_to_raw_response_wrapper(
            load_balancers.load_balancers,
        )
        self.retrieve_load_balancers = async_to_raw_response_wrapper(
            load_balancers.retrieve_load_balancers,
        )

    @cached_property
    def operations(self) -> AsyncOperationsResourceWithRawResponse:
        return AsyncOperationsResourceWithRawResponse(self._load_balancers.operations)


class LoadBalancersResourceWithStreamingResponse:
    def __init__(self, load_balancers: LoadBalancersResource) -> None:
        self._load_balancers = load_balancers

        self.retrieve = to_streamed_response_wrapper(
            load_balancers.retrieve,
        )
        self.delete = to_streamed_response_wrapper(
            load_balancers.delete,
        )
        self.load_balancers = to_streamed_response_wrapper(
            load_balancers.load_balancers,
        )
        self.retrieve_load_balancers = to_streamed_response_wrapper(
            load_balancers.retrieve_load_balancers,
        )

    @cached_property
    def operations(self) -> OperationsResourceWithStreamingResponse:
        return OperationsResourceWithStreamingResponse(self._load_balancers.operations)


class AsyncLoadBalancersResourceWithStreamingResponse:
    def __init__(self, load_balancers: AsyncLoadBalancersResource) -> None:
        self._load_balancers = load_balancers

        self.retrieve = async_to_streamed_response_wrapper(
            load_balancers.retrieve,
        )
        self.delete = async_to_streamed_response_wrapper(
            load_balancers.delete,
        )
        self.load_balancers = async_to_streamed_response_wrapper(
            load_balancers.load_balancers,
        )
        self.retrieve_load_balancers = async_to_streamed_response_wrapper(
            load_balancers.retrieve_load_balancers,
        )

    @cached_property
    def operations(self) -> AsyncOperationsResourceWithStreamingResponse:
        return AsyncOperationsResourceWithStreamingResponse(self._load_balancers.operations)
