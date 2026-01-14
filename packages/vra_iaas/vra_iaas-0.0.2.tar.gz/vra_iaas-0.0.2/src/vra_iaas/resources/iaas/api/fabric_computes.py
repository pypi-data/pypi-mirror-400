# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

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
    fabric_compute_update_params,
    fabric_compute_retrieve_params,
    fabric_compute_retrieve_fabric_computes_params,
)
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.fabric_compute import FabricCompute
from ....types.iaas.api.fabric_compute_result import FabricComputeResult

__all__ = ["FabricComputesResource", "AsyncFabricComputesResource"]


class FabricComputesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FabricComputesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return FabricComputesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FabricComputesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return FabricComputesResourceWithStreamingResponse(self)

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
    ) -> FabricCompute:
        """
        Get fabric compute with a given id

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
            f"/iaas/api/fabric-computes/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, fabric_compute_retrieve_params.FabricComputeRetrieveParams
                ),
            ),
            cast_to=FabricCompute,
        )

    def update(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        maximum_allowed_cpu_allocation_percent: int | Omit = omit,
        maximum_allowed_memory_allocation_percent: int | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FabricCompute:
        """Update fabric compute.

        Only tag updates are supported.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          maximum_allowed_cpu_allocation_percent: What percent of the total available vcPu on the compute will be used for VM
              provisioning.This value can be more than 100. e.g. If the compute has 100 vCPUs
              and this value is set to80, then VMware Aria Automation will act as if this
              compute has only 80 vCPUs. If it is 120, then VMware Aria Automation will act as
              if this compute has 120 vCPUs thus allowing 20 vCPUs overallocation. Applies
              only for private cloud computes.

          maximum_allowed_memory_allocation_percent: What percent of the total available memory on the compute will be used for VM
              provisioning.This value can be more than 100. e.g. If the compute has 100gb of
              memory and this value is set to80, then VMware Aria Automation will act as if
              this compute has only 80gb. If it is 120, then VMware Aria Automation will act
              as if this compute has 120gb thus allowing 20gb overallocation. Applies only for
              private cloud computes.

          tags: A set of tag keys and optional values that were set on this resource instance.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/fabric-computes/{id}",
            body=maybe_transform(
                {
                    "maximum_allowed_cpu_allocation_percent": maximum_allowed_cpu_allocation_percent,
                    "maximum_allowed_memory_allocation_percent": maximum_allowed_memory_allocation_percent,
                    "tags": tags,
                },
                fabric_compute_update_params.FabricComputeUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, fabric_compute_update_params.FabricComputeUpdateParams
                ),
            ),
            cast_to=FabricCompute,
        )

    def retrieve_fabric_computes(
        self,
        *,
        count: bool | Omit = omit,
        filter: str | Omit = omit,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FabricComputeResult:
        """
        Get all fabric computes.

        Args:
          count: Flag which when specified, regardless of the assigned value, shows the total
              number of records. If the collection has a filter it shows the number of records
              matching the filter.

          filter: Filter the results by a specified predicate expression. Operators: eq, ne, and,
              or.

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
            "/iaas/api/fabric-computes",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "count": count,
                        "filter": filter,
                        "skip": skip,
                        "top": top,
                        "api_version": api_version,
                    },
                    fabric_compute_retrieve_fabric_computes_params.FabricComputeRetrieveFabricComputesParams,
                ),
            ),
            cast_to=FabricComputeResult,
        )


class AsyncFabricComputesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFabricComputesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFabricComputesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFabricComputesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncFabricComputesResourceWithStreamingResponse(self)

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
    ) -> FabricCompute:
        """
        Get fabric compute with a given id

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
            f"/iaas/api/fabric-computes/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, fabric_compute_retrieve_params.FabricComputeRetrieveParams
                ),
            ),
            cast_to=FabricCompute,
        )

    async def update(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        maximum_allowed_cpu_allocation_percent: int | Omit = omit,
        maximum_allowed_memory_allocation_percent: int | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FabricCompute:
        """Update fabric compute.

        Only tag updates are supported.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          maximum_allowed_cpu_allocation_percent: What percent of the total available vcPu on the compute will be used for VM
              provisioning.This value can be more than 100. e.g. If the compute has 100 vCPUs
              and this value is set to80, then VMware Aria Automation will act as if this
              compute has only 80 vCPUs. If it is 120, then VMware Aria Automation will act as
              if this compute has 120 vCPUs thus allowing 20 vCPUs overallocation. Applies
              only for private cloud computes.

          maximum_allowed_memory_allocation_percent: What percent of the total available memory on the compute will be used for VM
              provisioning.This value can be more than 100. e.g. If the compute has 100gb of
              memory and this value is set to80, then VMware Aria Automation will act as if
              this compute has only 80gb. If it is 120, then VMware Aria Automation will act
              as if this compute has 120gb thus allowing 20gb overallocation. Applies only for
              private cloud computes.

          tags: A set of tag keys and optional values that were set on this resource instance.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/fabric-computes/{id}",
            body=await async_maybe_transform(
                {
                    "maximum_allowed_cpu_allocation_percent": maximum_allowed_cpu_allocation_percent,
                    "maximum_allowed_memory_allocation_percent": maximum_allowed_memory_allocation_percent,
                    "tags": tags,
                },
                fabric_compute_update_params.FabricComputeUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, fabric_compute_update_params.FabricComputeUpdateParams
                ),
            ),
            cast_to=FabricCompute,
        )

    async def retrieve_fabric_computes(
        self,
        *,
        count: bool | Omit = omit,
        filter: str | Omit = omit,
        skip: int | Omit = omit,
        top: int | Omit = omit,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FabricComputeResult:
        """
        Get all fabric computes.

        Args:
          count: Flag which when specified, regardless of the assigned value, shows the total
              number of records. If the collection has a filter it shows the number of records
              matching the filter.

          filter: Filter the results by a specified predicate expression. Operators: eq, ne, and,
              or.

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
            "/iaas/api/fabric-computes",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "count": count,
                        "filter": filter,
                        "skip": skip,
                        "top": top,
                        "api_version": api_version,
                    },
                    fabric_compute_retrieve_fabric_computes_params.FabricComputeRetrieveFabricComputesParams,
                ),
            ),
            cast_to=FabricComputeResult,
        )


class FabricComputesResourceWithRawResponse:
    def __init__(self, fabric_computes: FabricComputesResource) -> None:
        self._fabric_computes = fabric_computes

        self.retrieve = to_raw_response_wrapper(
            fabric_computes.retrieve,
        )
        self.update = to_raw_response_wrapper(
            fabric_computes.update,
        )
        self.retrieve_fabric_computes = to_raw_response_wrapper(
            fabric_computes.retrieve_fabric_computes,
        )


class AsyncFabricComputesResourceWithRawResponse:
    def __init__(self, fabric_computes: AsyncFabricComputesResource) -> None:
        self._fabric_computes = fabric_computes

        self.retrieve = async_to_raw_response_wrapper(
            fabric_computes.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            fabric_computes.update,
        )
        self.retrieve_fabric_computes = async_to_raw_response_wrapper(
            fabric_computes.retrieve_fabric_computes,
        )


class FabricComputesResourceWithStreamingResponse:
    def __init__(self, fabric_computes: FabricComputesResource) -> None:
        self._fabric_computes = fabric_computes

        self.retrieve = to_streamed_response_wrapper(
            fabric_computes.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            fabric_computes.update,
        )
        self.retrieve_fabric_computes = to_streamed_response_wrapper(
            fabric_computes.retrieve_fabric_computes,
        )


class AsyncFabricComputesResourceWithStreamingResponse:
    def __init__(self, fabric_computes: AsyncFabricComputesResource) -> None:
        self._fabric_computes = fabric_computes

        self.retrieve = async_to_streamed_response_wrapper(
            fabric_computes.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            fabric_computes.update,
        )
        self.retrieve_fabric_computes = async_to_streamed_response_wrapper(
            fabric_computes.retrieve_fabric_computes,
        )
