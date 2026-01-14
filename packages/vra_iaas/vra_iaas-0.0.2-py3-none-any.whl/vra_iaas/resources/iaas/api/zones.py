# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable

import httpx

from ...._types import Body, Omit, Query, Headers, NoneType, NotGiven, SequenceNotStr, omit, not_given
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
    zone_list_params,
    zone_create_params,
    zone_delete_params,
    zone_update_params,
    zone_retrieve_params,
    zone_retrieve_computes_params,
)
from ....types.iaas.api.zone import Zone
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.zone_list_response import ZoneListResponse
from ....types.iaas.api.fabric_compute_result import FabricComputeResult

__all__ = ["ZonesResource", "AsyncZonesResource"]


class ZonesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ZonesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return ZonesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ZonesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return ZonesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        compute_ids: SequenceNotStr[str] | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        folder: str | Omit = omit,
        placement_policy: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        tags_to_match: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Zone:
        """
        Create zone

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The id of the region for which this profile is created

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          compute_ids: The ids of the compute resources that will be explicitly assigned to this zone

          custom_properties: A list of key value pair of properties that will be used

          description: A human-friendly description.

          folder: The folder relative path to the datacenter where resources are deployed to.
              (only applicable for vSphere cloud zones)

          placement_policy: Placement policy for the zone. One of DEFAULT, SPREAD, BINPACK or SPREAD_MEMORY.

          tags: A set of tag keys and optional values that are effectively applied to all
              compute resources in this zone, but only in the context of this zone.

          tags_to_match: A set of tag keys and optional values that will be used

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/zones",
            body=maybe_transform(
                {
                    "name": name,
                    "region_id": region_id,
                    "compute_ids": compute_ids,
                    "custom_properties": custom_properties,
                    "description": description,
                    "folder": folder,
                    "placement_policy": placement_policy,
                    "tags": tags,
                    "tags_to_match": tags_to_match,
                },
                zone_create_params.ZoneCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, zone_create_params.ZoneCreateParams),
            ),
            cast_to=Zone,
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
    ) -> Zone:
        """
        Get zone with given id

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
            f"/iaas/api/zones/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, zone_retrieve_params.ZoneRetrieveParams),
            ),
            cast_to=Zone,
        )

    def update(
        self,
        id: str,
        *,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        compute_ids: SequenceNotStr[str] | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        folder: str | Omit = omit,
        placement_policy: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        tags_to_match: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Zone:
        """
        Update zone

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The id of the region for which this profile is created

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          compute_ids: The ids of the compute resources that will be explicitly assigned to this zone

          custom_properties: A list of key value pair of properties that will be used

          description: A human-friendly description.

          folder: The folder relative path to the datacenter where resources are deployed to.
              (only applicable for vSphere cloud zones)

          placement_policy: Placement policy for the zone. One of DEFAULT, SPREAD, BINPACK or SPREAD_MEMORY.

          tags: A set of tag keys and optional values that are effectively applied to all
              compute resources in this zone, but only in the context of this zone.

          tags_to_match: A set of tag keys and optional values that will be used

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/zones/{id}",
            body=maybe_transform(
                {
                    "name": name,
                    "region_id": region_id,
                    "compute_ids": compute_ids,
                    "custom_properties": custom_properties,
                    "description": description,
                    "folder": folder,
                    "placement_policy": placement_policy,
                    "tags": tags,
                    "tags_to_match": tags_to_match,
                },
                zone_update_params.ZoneUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, zone_update_params.ZoneUpdateParams),
            ),
            cast_to=Zone,
        )

    def list(
        self,
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
    ) -> ZoneListResponse:
        """
        Get all zones

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
        return self._get(
            "/iaas/api/zones",
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
                    zone_list_params.ZoneListParams,
                ),
            ),
            cast_to=ZoneListResponse,
        )

    def delete(
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
    ) -> None:
        """
        Delete a zone

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
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/iaas/api/zones/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"api_version": api_version}, zone_delete_params.ZoneDeleteParams),
            ),
            cast_to=NoneType,
        )

    def retrieve_computes(
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
    ) -> FabricComputeResult:
        """
        Get zone's computes by given zone ID

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
            f"/iaas/api/zones/{id}/computes",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, zone_retrieve_computes_params.ZoneRetrieveComputesParams
                ),
            ),
            cast_to=FabricComputeResult,
        )


class AsyncZonesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncZonesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncZonesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncZonesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncZonesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        compute_ids: SequenceNotStr[str] | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        folder: str | Omit = omit,
        placement_policy: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        tags_to_match: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Zone:
        """
        Create zone

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The id of the region for which this profile is created

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          compute_ids: The ids of the compute resources that will be explicitly assigned to this zone

          custom_properties: A list of key value pair of properties that will be used

          description: A human-friendly description.

          folder: The folder relative path to the datacenter where resources are deployed to.
              (only applicable for vSphere cloud zones)

          placement_policy: Placement policy for the zone. One of DEFAULT, SPREAD, BINPACK or SPREAD_MEMORY.

          tags: A set of tag keys and optional values that are effectively applied to all
              compute resources in this zone, but only in the context of this zone.

          tags_to_match: A set of tag keys and optional values that will be used

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/zones",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "region_id": region_id,
                    "compute_ids": compute_ids,
                    "custom_properties": custom_properties,
                    "description": description,
                    "folder": folder,
                    "placement_policy": placement_policy,
                    "tags": tags,
                    "tags_to_match": tags_to_match,
                },
                zone_create_params.ZoneCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"api_version": api_version}, zone_create_params.ZoneCreateParams),
            ),
            cast_to=Zone,
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
    ) -> Zone:
        """
        Get zone with given id

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
            f"/iaas/api/zones/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, zone_retrieve_params.ZoneRetrieveParams
                ),
            ),
            cast_to=Zone,
        )

    async def update(
        self,
        id: str,
        *,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        compute_ids: SequenceNotStr[str] | Omit = omit,
        custom_properties: Dict[str, str] | Omit = omit,
        description: str | Omit = omit,
        folder: str | Omit = omit,
        placement_policy: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        tags_to_match: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Zone:
        """
        Update zone

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The id of the region for which this profile is created

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          compute_ids: The ids of the compute resources that will be explicitly assigned to this zone

          custom_properties: A list of key value pair of properties that will be used

          description: A human-friendly description.

          folder: The folder relative path to the datacenter where resources are deployed to.
              (only applicable for vSphere cloud zones)

          placement_policy: Placement policy for the zone. One of DEFAULT, SPREAD, BINPACK or SPREAD_MEMORY.

          tags: A set of tag keys and optional values that are effectively applied to all
              compute resources in this zone, but only in the context of this zone.

          tags_to_match: A set of tag keys and optional values that will be used

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/zones/{id}",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "region_id": region_id,
                    "compute_ids": compute_ids,
                    "custom_properties": custom_properties,
                    "description": description,
                    "folder": folder,
                    "placement_policy": placement_policy,
                    "tags": tags,
                    "tags_to_match": tags_to_match,
                },
                zone_update_params.ZoneUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"api_version": api_version}, zone_update_params.ZoneUpdateParams),
            ),
            cast_to=Zone,
        )

    async def list(
        self,
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
    ) -> ZoneListResponse:
        """
        Get all zones

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
        return await self._get(
            "/iaas/api/zones",
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
                    zone_list_params.ZoneListParams,
                ),
            ),
            cast_to=ZoneListResponse,
        )

    async def delete(
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
    ) -> None:
        """
        Delete a zone

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
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/iaas/api/zones/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"api_version": api_version}, zone_delete_params.ZoneDeleteParams),
            ),
            cast_to=NoneType,
        )

    async def retrieve_computes(
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
    ) -> FabricComputeResult:
        """
        Get zone's computes by given zone ID

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
            f"/iaas/api/zones/{id}/computes",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, zone_retrieve_computes_params.ZoneRetrieveComputesParams
                ),
            ),
            cast_to=FabricComputeResult,
        )


class ZonesResourceWithRawResponse:
    def __init__(self, zones: ZonesResource) -> None:
        self._zones = zones

        self.create = to_raw_response_wrapper(
            zones.create,
        )
        self.retrieve = to_raw_response_wrapper(
            zones.retrieve,
        )
        self.update = to_raw_response_wrapper(
            zones.update,
        )
        self.list = to_raw_response_wrapper(
            zones.list,
        )
        self.delete = to_raw_response_wrapper(
            zones.delete,
        )
        self.retrieve_computes = to_raw_response_wrapper(
            zones.retrieve_computes,
        )


class AsyncZonesResourceWithRawResponse:
    def __init__(self, zones: AsyncZonesResource) -> None:
        self._zones = zones

        self.create = async_to_raw_response_wrapper(
            zones.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            zones.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            zones.update,
        )
        self.list = async_to_raw_response_wrapper(
            zones.list,
        )
        self.delete = async_to_raw_response_wrapper(
            zones.delete,
        )
        self.retrieve_computes = async_to_raw_response_wrapper(
            zones.retrieve_computes,
        )


class ZonesResourceWithStreamingResponse:
    def __init__(self, zones: ZonesResource) -> None:
        self._zones = zones

        self.create = to_streamed_response_wrapper(
            zones.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            zones.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            zones.update,
        )
        self.list = to_streamed_response_wrapper(
            zones.list,
        )
        self.delete = to_streamed_response_wrapper(
            zones.delete,
        )
        self.retrieve_computes = to_streamed_response_wrapper(
            zones.retrieve_computes,
        )


class AsyncZonesResourceWithStreamingResponse:
    def __init__(self, zones: AsyncZonesResource) -> None:
        self._zones = zones

        self.create = async_to_streamed_response_wrapper(
            zones.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            zones.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            zones.update,
        )
        self.list = async_to_streamed_response_wrapper(
            zones.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            zones.delete,
        )
        self.retrieve_computes = async_to_streamed_response_wrapper(
            zones.retrieve_computes,
        )
