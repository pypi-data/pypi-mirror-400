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
    fabric_vsphere_datastore_update_params,
    fabric_vsphere_datastore_retrieve_params,
    fabric_vsphere_datastore_retrieve_fabric_vsphere_datastores_params,
)
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.fabric_vsphere_datastore import FabricVsphereDatastore
from ....types.iaas.api.fabric_vsphere_datastore_retrieve_fabric_vsphere_datastores_response import (
    FabricVsphereDatastoreRetrieveFabricVsphereDatastoresResponse,
)

__all__ = ["FabricVsphereDatastoresResource", "AsyncFabricVsphereDatastoresResource"]


class FabricVsphereDatastoresResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FabricVsphereDatastoresResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return FabricVsphereDatastoresResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FabricVsphereDatastoresResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return FabricVsphereDatastoresResourceWithStreamingResponse(self)

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
    ) -> FabricVsphereDatastore:
        """
        Get fabric vSphere datastore with a given id

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
            f"/iaas/api/fabric-vsphere-datastores/{id}",
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
                    fabric_vsphere_datastore_retrieve_params.FabricVsphereDatastoreRetrieveParams,
                ),
            ),
            cast_to=FabricVsphereDatastore,
        )

    def update(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        allocated_non_disk_storage_space_bytes: int | Omit = omit,
        maximum_allowed_storage_allocation_percent: int | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FabricVsphereDatastore:
        """Update Fabric vSphere Datastore.

        Only tag updates are supported.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          allocated_non_disk_storage_space_bytes: What byte amount is the space occupied by items that are NOT disks on the data
              store.This property is NOT calculated or updated by VMware Aria Automation. It
              is a static config propertypopulated by the customer if it is needed (e.g. in
              the case of a big content library).

          maximum_allowed_storage_allocation_percent: What percent of the total available storage on the datastore will be used for
              disk provisioning.This value can be more than 100. e.g. If the datastore has
              100gb of storage and this value is set to 80, then VMware Aria Automation will
              act as if this datastore has only 80gb. If it is 120, then VMware Aria
              Automation will act as if this datastore has 120g thus allowing 20gb
              overallocation.

          tags: A set of tag keys and optional values that were set on this resource instance.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/fabric-vsphere-datastores/{id}",
            body=maybe_transform(
                {
                    "allocated_non_disk_storage_space_bytes": allocated_non_disk_storage_space_bytes,
                    "maximum_allowed_storage_allocation_percent": maximum_allowed_storage_allocation_percent,
                    "tags": tags,
                },
                fabric_vsphere_datastore_update_params.FabricVsphereDatastoreUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    fabric_vsphere_datastore_update_params.FabricVsphereDatastoreUpdateParams,
                ),
            ),
            cast_to=FabricVsphereDatastore,
        )

    def retrieve_fabric_vsphere_datastores(
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
    ) -> FabricVsphereDatastoreRetrieveFabricVsphereDatastoresResponse:
        """
        Get all fabric vSphere datastores.

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
            "/iaas/api/fabric-vsphere-datastores",
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
                    fabric_vsphere_datastore_retrieve_fabric_vsphere_datastores_params.FabricVsphereDatastoreRetrieveFabricVsphereDatastoresParams,
                ),
            ),
            cast_to=FabricVsphereDatastoreRetrieveFabricVsphereDatastoresResponse,
        )


class AsyncFabricVsphereDatastoresResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFabricVsphereDatastoresResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFabricVsphereDatastoresResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFabricVsphereDatastoresResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncFabricVsphereDatastoresResourceWithStreamingResponse(self)

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
    ) -> FabricVsphereDatastore:
        """
        Get fabric vSphere datastore with a given id

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
            f"/iaas/api/fabric-vsphere-datastores/{id}",
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
                    fabric_vsphere_datastore_retrieve_params.FabricVsphereDatastoreRetrieveParams,
                ),
            ),
            cast_to=FabricVsphereDatastore,
        )

    async def update(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        allocated_non_disk_storage_space_bytes: int | Omit = omit,
        maximum_allowed_storage_allocation_percent: int | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FabricVsphereDatastore:
        """Update Fabric vSphere Datastore.

        Only tag updates are supported.

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          allocated_non_disk_storage_space_bytes: What byte amount is the space occupied by items that are NOT disks on the data
              store.This property is NOT calculated or updated by VMware Aria Automation. It
              is a static config propertypopulated by the customer if it is needed (e.g. in
              the case of a big content library).

          maximum_allowed_storage_allocation_percent: What percent of the total available storage on the datastore will be used for
              disk provisioning.This value can be more than 100. e.g. If the datastore has
              100gb of storage and this value is set to 80, then VMware Aria Automation will
              act as if this datastore has only 80gb. If it is 120, then VMware Aria
              Automation will act as if this datastore has 120g thus allowing 20gb
              overallocation.

          tags: A set of tag keys and optional values that were set on this resource instance.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/fabric-vsphere-datastores/{id}",
            body=await async_maybe_transform(
                {
                    "allocated_non_disk_storage_space_bytes": allocated_non_disk_storage_space_bytes,
                    "maximum_allowed_storage_allocation_percent": maximum_allowed_storage_allocation_percent,
                    "tags": tags,
                },
                fabric_vsphere_datastore_update_params.FabricVsphereDatastoreUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    fabric_vsphere_datastore_update_params.FabricVsphereDatastoreUpdateParams,
                ),
            ),
            cast_to=FabricVsphereDatastore,
        )

    async def retrieve_fabric_vsphere_datastores(
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
    ) -> FabricVsphereDatastoreRetrieveFabricVsphereDatastoresResponse:
        """
        Get all fabric vSphere datastores.

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
            "/iaas/api/fabric-vsphere-datastores",
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
                    fabric_vsphere_datastore_retrieve_fabric_vsphere_datastores_params.FabricVsphereDatastoreRetrieveFabricVsphereDatastoresParams,
                ),
            ),
            cast_to=FabricVsphereDatastoreRetrieveFabricVsphereDatastoresResponse,
        )


class FabricVsphereDatastoresResourceWithRawResponse:
    def __init__(self, fabric_vsphere_datastores: FabricVsphereDatastoresResource) -> None:
        self._fabric_vsphere_datastores = fabric_vsphere_datastores

        self.retrieve = to_raw_response_wrapper(
            fabric_vsphere_datastores.retrieve,
        )
        self.update = to_raw_response_wrapper(
            fabric_vsphere_datastores.update,
        )
        self.retrieve_fabric_vsphere_datastores = to_raw_response_wrapper(
            fabric_vsphere_datastores.retrieve_fabric_vsphere_datastores,
        )


class AsyncFabricVsphereDatastoresResourceWithRawResponse:
    def __init__(self, fabric_vsphere_datastores: AsyncFabricVsphereDatastoresResource) -> None:
        self._fabric_vsphere_datastores = fabric_vsphere_datastores

        self.retrieve = async_to_raw_response_wrapper(
            fabric_vsphere_datastores.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            fabric_vsphere_datastores.update,
        )
        self.retrieve_fabric_vsphere_datastores = async_to_raw_response_wrapper(
            fabric_vsphere_datastores.retrieve_fabric_vsphere_datastores,
        )


class FabricVsphereDatastoresResourceWithStreamingResponse:
    def __init__(self, fabric_vsphere_datastores: FabricVsphereDatastoresResource) -> None:
        self._fabric_vsphere_datastores = fabric_vsphere_datastores

        self.retrieve = to_streamed_response_wrapper(
            fabric_vsphere_datastores.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            fabric_vsphere_datastores.update,
        )
        self.retrieve_fabric_vsphere_datastores = to_streamed_response_wrapper(
            fabric_vsphere_datastores.retrieve_fabric_vsphere_datastores,
        )


class AsyncFabricVsphereDatastoresResourceWithStreamingResponse:
    def __init__(self, fabric_vsphere_datastores: AsyncFabricVsphereDatastoresResource) -> None:
        self._fabric_vsphere_datastores = fabric_vsphere_datastores

        self.retrieve = async_to_streamed_response_wrapper(
            fabric_vsphere_datastores.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            fabric_vsphere_datastores.update,
        )
        self.retrieve_fabric_vsphere_datastores = async_to_streamed_response_wrapper(
            fabric_vsphere_datastores.retrieve_fabric_vsphere_datastores,
        )
