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
from ....types.iaas.api import (
    fabric_vsphere_storage_policy_retrieve_params,
    fabric_vsphere_storage_policy_retrieve_fabric_vsphere_storage_policies_params,
)
from ....types.iaas.api.fabric_vsphere_storage_policy import FabricVsphereStoragePolicy
from ....types.iaas.api.fabric_vsphere_storage_policy_retrieve_fabric_vsphere_storage_policies_response import (
    FabricVsphereStoragePolicyRetrieveFabricVsphereStoragePoliciesResponse,
)

__all__ = ["FabricVsphereStoragePoliciesResource", "AsyncFabricVsphereStoragePoliciesResource"]


class FabricVsphereStoragePoliciesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FabricVsphereStoragePoliciesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return FabricVsphereStoragePoliciesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FabricVsphereStoragePoliciesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return FabricVsphereStoragePoliciesResourceWithStreamingResponse(self)

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
    ) -> FabricVsphereStoragePolicy:
        """
        Get fabric vSphere storage policy with a given id

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
            f"/iaas/api/fabric-vsphere-storage-policies/{id}",
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
                    fabric_vsphere_storage_policy_retrieve_params.FabricVsphereStoragePolicyRetrieveParams,
                ),
            ),
            cast_to=FabricVsphereStoragePolicy,
        )

    def retrieve_fabric_vsphere_storage_policies(
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
    ) -> FabricVsphereStoragePolicyRetrieveFabricVsphereStoragePoliciesResponse:
        """
        Get all fabric vSphere storage polices.

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
            "/iaas/api/fabric-vsphere-storage-policies",
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
                    fabric_vsphere_storage_policy_retrieve_fabric_vsphere_storage_policies_params.FabricVsphereStoragePolicyRetrieveFabricVsphereStoragePoliciesParams,
                ),
            ),
            cast_to=FabricVsphereStoragePolicyRetrieveFabricVsphereStoragePoliciesResponse,
        )


class AsyncFabricVsphereStoragePoliciesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFabricVsphereStoragePoliciesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFabricVsphereStoragePoliciesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFabricVsphereStoragePoliciesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncFabricVsphereStoragePoliciesResourceWithStreamingResponse(self)

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
    ) -> FabricVsphereStoragePolicy:
        """
        Get fabric vSphere storage policy with a given id

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
            f"/iaas/api/fabric-vsphere-storage-policies/{id}",
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
                    fabric_vsphere_storage_policy_retrieve_params.FabricVsphereStoragePolicyRetrieveParams,
                ),
            ),
            cast_to=FabricVsphereStoragePolicy,
        )

    async def retrieve_fabric_vsphere_storage_policies(
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
    ) -> FabricVsphereStoragePolicyRetrieveFabricVsphereStoragePoliciesResponse:
        """
        Get all fabric vSphere storage polices.

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
            "/iaas/api/fabric-vsphere-storage-policies",
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
                    fabric_vsphere_storage_policy_retrieve_fabric_vsphere_storage_policies_params.FabricVsphereStoragePolicyRetrieveFabricVsphereStoragePoliciesParams,
                ),
            ),
            cast_to=FabricVsphereStoragePolicyRetrieveFabricVsphereStoragePoliciesResponse,
        )


class FabricVsphereStoragePoliciesResourceWithRawResponse:
    def __init__(self, fabric_vsphere_storage_policies: FabricVsphereStoragePoliciesResource) -> None:
        self._fabric_vsphere_storage_policies = fabric_vsphere_storage_policies

        self.retrieve = to_raw_response_wrapper(
            fabric_vsphere_storage_policies.retrieve,
        )
        self.retrieve_fabric_vsphere_storage_policies = to_raw_response_wrapper(
            fabric_vsphere_storage_policies.retrieve_fabric_vsphere_storage_policies,
        )


class AsyncFabricVsphereStoragePoliciesResourceWithRawResponse:
    def __init__(self, fabric_vsphere_storage_policies: AsyncFabricVsphereStoragePoliciesResource) -> None:
        self._fabric_vsphere_storage_policies = fabric_vsphere_storage_policies

        self.retrieve = async_to_raw_response_wrapper(
            fabric_vsphere_storage_policies.retrieve,
        )
        self.retrieve_fabric_vsphere_storage_policies = async_to_raw_response_wrapper(
            fabric_vsphere_storage_policies.retrieve_fabric_vsphere_storage_policies,
        )


class FabricVsphereStoragePoliciesResourceWithStreamingResponse:
    def __init__(self, fabric_vsphere_storage_policies: FabricVsphereStoragePoliciesResource) -> None:
        self._fabric_vsphere_storage_policies = fabric_vsphere_storage_policies

        self.retrieve = to_streamed_response_wrapper(
            fabric_vsphere_storage_policies.retrieve,
        )
        self.retrieve_fabric_vsphere_storage_policies = to_streamed_response_wrapper(
            fabric_vsphere_storage_policies.retrieve_fabric_vsphere_storage_policies,
        )


class AsyncFabricVsphereStoragePoliciesResourceWithStreamingResponse:
    def __init__(self, fabric_vsphere_storage_policies: AsyncFabricVsphereStoragePoliciesResource) -> None:
        self._fabric_vsphere_storage_policies = fabric_vsphere_storage_policies

        self.retrieve = async_to_streamed_response_wrapper(
            fabric_vsphere_storage_policies.retrieve,
        )
        self.retrieve_fabric_vsphere_storage_policies = async_to_streamed_response_wrapper(
            fabric_vsphere_storage_policies.retrieve_fabric_vsphere_storage_policies,
        )
