# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ...._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
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
    storage_profiles_gcp_delete_params,
    storage_profiles_gcp_update_params,
    storage_profiles_gcp_retrieve_params,
    storage_profiles_gcp_storage_profiles_gcp_params,
    storage_profiles_gcp_retrieve_storage_profiles_gcp_params,
)
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.gcp_storage_profile import GcpStorageProfile
from ....types.iaas.api.storage_profiles_gcp_retrieve_storage_profiles_gcp_response import (
    StorageProfilesGcpRetrieveStorageProfilesGcpResponse,
)

__all__ = ["StorageProfilesGcpResource", "AsyncStorageProfilesGcpResource"]


class StorageProfilesGcpResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> StorageProfilesGcpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return StorageProfilesGcpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StorageProfilesGcpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return StorageProfilesGcpResourceWithStreamingResponse(self)

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
    ) -> GcpStorageProfile:
        """
        Get GCP storage profile with a given id

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
            f"/iaas/api/storage-profiles-gcp/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, storage_profiles_gcp_retrieve_params.StorageProfilesGcpRetrieveParams
                ),
            ),
            cast_to=GcpStorageProfile,
        )

    def update(
        self,
        id: str,
        *,
        name: str,
        persistent_disk_type: str,
        region_id: str,
        api_version: str | Omit = omit,
        default_item: bool | Omit = omit,
        description: str | Omit = omit,
        supports_encryption: bool | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GcpStorageProfile:
        """
        Update GCP storage profile

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          persistent_disk_type: Indicates the type of disk.

          region_id: A link to the region that is associated with the storage profile.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          default_item: Indicates if a storage profile is default or not.

          description: A human-friendly description.

          supports_encryption: Indicates whether this storage profile supports encryption or not.

          tags: A list of tags that represent the capabilities of this storage profile

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/storage-profiles-gcp/{id}",
            body=maybe_transform(
                {
                    "name": name,
                    "persistent_disk_type": persistent_disk_type,
                    "region_id": region_id,
                    "default_item": default_item,
                    "description": description,
                    "supports_encryption": supports_encryption,
                    "tags": tags,
                },
                storage_profiles_gcp_update_params.StorageProfilesGcpUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, storage_profiles_gcp_update_params.StorageProfilesGcpUpdateParams
                ),
            ),
            cast_to=GcpStorageProfile,
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
        Delete GCP storage profile with a given id

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
            f"/iaas/api/storage-profiles-gcp/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, storage_profiles_gcp_delete_params.StorageProfilesGcpDeleteParams
                ),
            ),
            cast_to=NoneType,
        )

    def retrieve_storage_profiles_gcp(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageProfilesGcpRetrieveStorageProfilesGcpResponse:
        """
        Get all GCP storage profiles

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/storage-profiles-gcp",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_gcp_retrieve_storage_profiles_gcp_params.StorageProfilesGcpRetrieveStorageProfilesGcpParams,
                ),
            ),
            cast_to=StorageProfilesGcpRetrieveStorageProfilesGcpResponse,
        )

    def storage_profiles_gcp(
        self,
        *,
        name: str,
        persistent_disk_type: str,
        region_id: str,
        api_version: str | Omit = omit,
        default_item: bool | Omit = omit,
        description: str | Omit = omit,
        supports_encryption: bool | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GcpStorageProfile:
        """
        Create GCP storage profile

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          persistent_disk_type: Indicates the type of disk.

          region_id: A link to the region that is associated with the storage profile.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          default_item: Indicates if a storage profile is default or not.

          description: A human-friendly description.

          supports_encryption: Indicates whether this storage profile supports encryption or not.

          tags: A list of tags that represent the capabilities of this storage profile

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/storage-profiles-gcp",
            body=maybe_transform(
                {
                    "name": name,
                    "persistent_disk_type": persistent_disk_type,
                    "region_id": region_id,
                    "default_item": default_item,
                    "description": description,
                    "supports_encryption": supports_encryption,
                    "tags": tags,
                },
                storage_profiles_gcp_storage_profiles_gcp_params.StorageProfilesGcpStorageProfilesGcpParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_gcp_storage_profiles_gcp_params.StorageProfilesGcpStorageProfilesGcpParams,
                ),
            ),
            cast_to=GcpStorageProfile,
        )


class AsyncStorageProfilesGcpResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncStorageProfilesGcpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncStorageProfilesGcpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStorageProfilesGcpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncStorageProfilesGcpResourceWithStreamingResponse(self)

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
    ) -> GcpStorageProfile:
        """
        Get GCP storage profile with a given id

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
            f"/iaas/api/storage-profiles-gcp/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, storage_profiles_gcp_retrieve_params.StorageProfilesGcpRetrieveParams
                ),
            ),
            cast_to=GcpStorageProfile,
        )

    async def update(
        self,
        id: str,
        *,
        name: str,
        persistent_disk_type: str,
        region_id: str,
        api_version: str | Omit = omit,
        default_item: bool | Omit = omit,
        description: str | Omit = omit,
        supports_encryption: bool | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GcpStorageProfile:
        """
        Update GCP storage profile

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          persistent_disk_type: Indicates the type of disk.

          region_id: A link to the region that is associated with the storage profile.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          default_item: Indicates if a storage profile is default or not.

          description: A human-friendly description.

          supports_encryption: Indicates whether this storage profile supports encryption or not.

          tags: A list of tags that represent the capabilities of this storage profile

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/storage-profiles-gcp/{id}",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "persistent_disk_type": persistent_disk_type,
                    "region_id": region_id,
                    "default_item": default_item,
                    "description": description,
                    "supports_encryption": supports_encryption,
                    "tags": tags,
                },
                storage_profiles_gcp_update_params.StorageProfilesGcpUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, storage_profiles_gcp_update_params.StorageProfilesGcpUpdateParams
                ),
            ),
            cast_to=GcpStorageProfile,
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
        Delete GCP storage profile with a given id

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
            f"/iaas/api/storage-profiles-gcp/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, storage_profiles_gcp_delete_params.StorageProfilesGcpDeleteParams
                ),
            ),
            cast_to=NoneType,
        )

    async def retrieve_storage_profiles_gcp(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageProfilesGcpRetrieveStorageProfilesGcpResponse:
        """
        Get all GCP storage profiles

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/storage-profiles-gcp",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_gcp_retrieve_storage_profiles_gcp_params.StorageProfilesGcpRetrieveStorageProfilesGcpParams,
                ),
            ),
            cast_to=StorageProfilesGcpRetrieveStorageProfilesGcpResponse,
        )

    async def storage_profiles_gcp(
        self,
        *,
        name: str,
        persistent_disk_type: str,
        region_id: str,
        api_version: str | Omit = omit,
        default_item: bool | Omit = omit,
        description: str | Omit = omit,
        supports_encryption: bool | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> GcpStorageProfile:
        """
        Create GCP storage profile

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          persistent_disk_type: Indicates the type of disk.

          region_id: A link to the region that is associated with the storage profile.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          default_item: Indicates if a storage profile is default or not.

          description: A human-friendly description.

          supports_encryption: Indicates whether this storage profile supports encryption or not.

          tags: A list of tags that represent the capabilities of this storage profile

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/storage-profiles-gcp",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "persistent_disk_type": persistent_disk_type,
                    "region_id": region_id,
                    "default_item": default_item,
                    "description": description,
                    "supports_encryption": supports_encryption,
                    "tags": tags,
                },
                storage_profiles_gcp_storage_profiles_gcp_params.StorageProfilesGcpStorageProfilesGcpParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_gcp_storage_profiles_gcp_params.StorageProfilesGcpStorageProfilesGcpParams,
                ),
            ),
            cast_to=GcpStorageProfile,
        )


class StorageProfilesGcpResourceWithRawResponse:
    def __init__(self, storage_profiles_gcp: StorageProfilesGcpResource) -> None:
        self._storage_profiles_gcp = storage_profiles_gcp

        self.retrieve = to_raw_response_wrapper(
            storage_profiles_gcp.retrieve,
        )
        self.update = to_raw_response_wrapper(
            storage_profiles_gcp.update,
        )
        self.delete = to_raw_response_wrapper(
            storage_profiles_gcp.delete,
        )
        self.retrieve_storage_profiles_gcp = to_raw_response_wrapper(
            storage_profiles_gcp.retrieve_storage_profiles_gcp,
        )
        self.storage_profiles_gcp = to_raw_response_wrapper(
            storage_profiles_gcp.storage_profiles_gcp,
        )


class AsyncStorageProfilesGcpResourceWithRawResponse:
    def __init__(self, storage_profiles_gcp: AsyncStorageProfilesGcpResource) -> None:
        self._storage_profiles_gcp = storage_profiles_gcp

        self.retrieve = async_to_raw_response_wrapper(
            storage_profiles_gcp.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            storage_profiles_gcp.update,
        )
        self.delete = async_to_raw_response_wrapper(
            storage_profiles_gcp.delete,
        )
        self.retrieve_storage_profiles_gcp = async_to_raw_response_wrapper(
            storage_profiles_gcp.retrieve_storage_profiles_gcp,
        )
        self.storage_profiles_gcp = async_to_raw_response_wrapper(
            storage_profiles_gcp.storage_profiles_gcp,
        )


class StorageProfilesGcpResourceWithStreamingResponse:
    def __init__(self, storage_profiles_gcp: StorageProfilesGcpResource) -> None:
        self._storage_profiles_gcp = storage_profiles_gcp

        self.retrieve = to_streamed_response_wrapper(
            storage_profiles_gcp.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            storage_profiles_gcp.update,
        )
        self.delete = to_streamed_response_wrapper(
            storage_profiles_gcp.delete,
        )
        self.retrieve_storage_profiles_gcp = to_streamed_response_wrapper(
            storage_profiles_gcp.retrieve_storage_profiles_gcp,
        )
        self.storage_profiles_gcp = to_streamed_response_wrapper(
            storage_profiles_gcp.storage_profiles_gcp,
        )


class AsyncStorageProfilesGcpResourceWithStreamingResponse:
    def __init__(self, storage_profiles_gcp: AsyncStorageProfilesGcpResource) -> None:
        self._storage_profiles_gcp = storage_profiles_gcp

        self.retrieve = async_to_streamed_response_wrapper(
            storage_profiles_gcp.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            storage_profiles_gcp.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            storage_profiles_gcp.delete,
        )
        self.retrieve_storage_profiles_gcp = async_to_streamed_response_wrapper(
            storage_profiles_gcp.retrieve_storage_profiles_gcp,
        )
        self.storage_profiles_gcp = async_to_streamed_response_wrapper(
            storage_profiles_gcp.storage_profiles_gcp,
        )
