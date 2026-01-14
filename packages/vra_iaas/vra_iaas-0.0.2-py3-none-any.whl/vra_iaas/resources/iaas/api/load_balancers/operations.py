# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable

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
from .....types.iaas.api.tag_param import TagParam
from .....types.iaas.api.load_balancers import operation_scale_params, operation_delete_params
from .....types.iaas.api.projects.request_tracker import RequestTracker
from .....types.iaas.api.load_balancers.route_configuration_param import RouteConfigurationParam
from .....types.iaas.api.machines.network_interface_specification_param import NetworkInterfaceSpecificationParam

__all__ = ["OperationsResource", "AsyncOperationsResource"]


class OperationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OperationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return OperationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OperationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return OperationsResourceWithStreamingResponse(self)

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
        Second day delete operation for load balancer

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
        return self._post(
            f"/iaas/api/load-balancers/{id}/operations/delete",
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
                    operation_delete_params.OperationDeleteParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def scale(
        self,
        id: str,
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
        Second day scale operation for load balancer

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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._post(
            f"/iaas/api/load-balancers/{id}/operations/scale",
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
                operation_scale_params.OperationScaleParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, operation_scale_params.OperationScaleParams),
            ),
            cast_to=RequestTracker,
        )


class AsyncOperationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOperationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncOperationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOperationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncOperationsResourceWithStreamingResponse(self)

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
        Second day delete operation for load balancer

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
        return await self._post(
            f"/iaas/api/load-balancers/{id}/operations/delete",
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
                    operation_delete_params.OperationDeleteParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def scale(
        self,
        id: str,
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
        Second day scale operation for load balancer

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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._post(
            f"/iaas/api/load-balancers/{id}/operations/scale",
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
                operation_scale_params.OperationScaleParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, operation_scale_params.OperationScaleParams
                ),
            ),
            cast_to=RequestTracker,
        )


class OperationsResourceWithRawResponse:
    def __init__(self, operations: OperationsResource) -> None:
        self._operations = operations

        self.delete = to_raw_response_wrapper(
            operations.delete,
        )
        self.scale = to_raw_response_wrapper(
            operations.scale,
        )


class AsyncOperationsResourceWithRawResponse:
    def __init__(self, operations: AsyncOperationsResource) -> None:
        self._operations = operations

        self.delete = async_to_raw_response_wrapper(
            operations.delete,
        )
        self.scale = async_to_raw_response_wrapper(
            operations.scale,
        )


class OperationsResourceWithStreamingResponse:
    def __init__(self, operations: OperationsResource) -> None:
        self._operations = operations

        self.delete = to_streamed_response_wrapper(
            operations.delete,
        )
        self.scale = to_streamed_response_wrapper(
            operations.scale,
        )


class AsyncOperationsResourceWithStreamingResponse:
    def __init__(self, operations: AsyncOperationsResource) -> None:
        self._operations = operations

        self.delete = async_to_streamed_response_wrapper(
            operations.delete,
        )
        self.scale = async_to_streamed_response_wrapper(
            operations.scale,
        )
