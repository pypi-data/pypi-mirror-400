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
    storage_profiles_aw_delete_params,
    storage_profiles_aw_update_params,
    storage_profiles_aw_retrieve_params,
    storage_profiles_aw_storage_profiles_aws_params,
    storage_profiles_aw_retrieve_storage_profiles_aws_params,
)
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.aws_storage_profile import AwsStorageProfile
from ....types.iaas.api.storage_profiles_aw_retrieve_storage_profiles_aws_response import (
    StorageProfilesAwRetrieveStorageProfilesAwsResponse,
)

__all__ = ["StorageProfilesAwsResource", "AsyncStorageProfilesAwsResource"]


class StorageProfilesAwsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> StorageProfilesAwsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return StorageProfilesAwsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StorageProfilesAwsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return StorageProfilesAwsResourceWithStreamingResponse(self)

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
    ) -> AwsStorageProfile:
        """
        Get AWS storage profile with a given id

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
            f"/iaas/api/storage-profiles-aws/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, storage_profiles_aw_retrieve_params.StorageProfilesAwRetrieveParams
                ),
            ),
            cast_to=AwsStorageProfile,
        )

    def update(
        self,
        id: str,
        *,
        device_type: str,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        default_item: bool | Omit = omit,
        description: str | Omit = omit,
        iops: str | Omit = omit,
        supports_encryption: bool | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        volume_type: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AwsStorageProfile:
        """
        Update AWS storage profile

        Args:
          device_type: Indicates the type of storage.

          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: A link to the region that is associated with the storage profile.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          default_item: Indicates if a storage profile is default or not.

          description: A human-friendly description.

          iops: Indicates maximum I/O operations per second.

          supports_encryption: Indicates whether this storage profile supports encryption or not.

          tags: A list of tags that represent the capabilities of this storage profile

          volume_type: Indicates the type of volume associated with type of storage.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/storage-profiles-aws/{id}",
            body=maybe_transform(
                {
                    "device_type": device_type,
                    "name": name,
                    "region_id": region_id,
                    "default_item": default_item,
                    "description": description,
                    "iops": iops,
                    "supports_encryption": supports_encryption,
                    "tags": tags,
                    "volume_type": volume_type,
                },
                storage_profiles_aw_update_params.StorageProfilesAwUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, storage_profiles_aw_update_params.StorageProfilesAwUpdateParams
                ),
            ),
            cast_to=AwsStorageProfile,
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
        Delete AWS storage profile with a given id

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
            f"/iaas/api/storage-profiles-aws/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, storage_profiles_aw_delete_params.StorageProfilesAwDeleteParams
                ),
            ),
            cast_to=NoneType,
        )

    def retrieve_storage_profiles_aws(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageProfilesAwRetrieveStorageProfilesAwsResponse:
        """
        Get all AWS storage profiles

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/storage-profiles-aws",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_aw_retrieve_storage_profiles_aws_params.StorageProfilesAwRetrieveStorageProfilesAwsParams,
                ),
            ),
            cast_to=StorageProfilesAwRetrieveStorageProfilesAwsResponse,
        )

    def storage_profiles_aws(
        self,
        *,
        device_type: str,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        default_item: bool | Omit = omit,
        description: str | Omit = omit,
        iops: str | Omit = omit,
        supports_encryption: bool | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        volume_type: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AwsStorageProfile:
        """
        Create AWS storage profile

        Args:
          device_type: Indicates the type of storage.

          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: A link to the region that is associated with the storage profile.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          default_item: Indicates if a storage profile is default or not.

          description: A human-friendly description.

          iops: Indicates maximum I/O operations per second.

          supports_encryption: Indicates whether this storage profile supports encryption or not.

          tags: A list of tags that represent the capabilities of this storage profile

          volume_type: Indicates the type of volume associated with type of storage.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/storage-profiles-aws",
            body=maybe_transform(
                {
                    "device_type": device_type,
                    "name": name,
                    "region_id": region_id,
                    "default_item": default_item,
                    "description": description,
                    "iops": iops,
                    "supports_encryption": supports_encryption,
                    "tags": tags,
                    "volume_type": volume_type,
                },
                storage_profiles_aw_storage_profiles_aws_params.StorageProfilesAwStorageProfilesAwsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_aw_storage_profiles_aws_params.StorageProfilesAwStorageProfilesAwsParams,
                ),
            ),
            cast_to=AwsStorageProfile,
        )


class AsyncStorageProfilesAwsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncStorageProfilesAwsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncStorageProfilesAwsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStorageProfilesAwsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncStorageProfilesAwsResourceWithStreamingResponse(self)

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
    ) -> AwsStorageProfile:
        """
        Get AWS storage profile with a given id

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
            f"/iaas/api/storage-profiles-aws/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, storage_profiles_aw_retrieve_params.StorageProfilesAwRetrieveParams
                ),
            ),
            cast_to=AwsStorageProfile,
        )

    async def update(
        self,
        id: str,
        *,
        device_type: str,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        default_item: bool | Omit = omit,
        description: str | Omit = omit,
        iops: str | Omit = omit,
        supports_encryption: bool | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        volume_type: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AwsStorageProfile:
        """
        Update AWS storage profile

        Args:
          device_type: Indicates the type of storage.

          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: A link to the region that is associated with the storage profile.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          default_item: Indicates if a storage profile is default or not.

          description: A human-friendly description.

          iops: Indicates maximum I/O operations per second.

          supports_encryption: Indicates whether this storage profile supports encryption or not.

          tags: A list of tags that represent the capabilities of this storage profile

          volume_type: Indicates the type of volume associated with type of storage.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/storage-profiles-aws/{id}",
            body=await async_maybe_transform(
                {
                    "device_type": device_type,
                    "name": name,
                    "region_id": region_id,
                    "default_item": default_item,
                    "description": description,
                    "iops": iops,
                    "supports_encryption": supports_encryption,
                    "tags": tags,
                    "volume_type": volume_type,
                },
                storage_profiles_aw_update_params.StorageProfilesAwUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, storage_profiles_aw_update_params.StorageProfilesAwUpdateParams
                ),
            ),
            cast_to=AwsStorageProfile,
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
        Delete AWS storage profile with a given id

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
            f"/iaas/api/storage-profiles-aws/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, storage_profiles_aw_delete_params.StorageProfilesAwDeleteParams
                ),
            ),
            cast_to=NoneType,
        )

    async def retrieve_storage_profiles_aws(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageProfilesAwRetrieveStorageProfilesAwsResponse:
        """
        Get all AWS storage profiles

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/storage-profiles-aws",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_aw_retrieve_storage_profiles_aws_params.StorageProfilesAwRetrieveStorageProfilesAwsParams,
                ),
            ),
            cast_to=StorageProfilesAwRetrieveStorageProfilesAwsResponse,
        )

    async def storage_profiles_aws(
        self,
        *,
        device_type: str,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        default_item: bool | Omit = omit,
        description: str | Omit = omit,
        iops: str | Omit = omit,
        supports_encryption: bool | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        volume_type: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AwsStorageProfile:
        """
        Create AWS storage profile

        Args:
          device_type: Indicates the type of storage.

          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: A link to the region that is associated with the storage profile.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          default_item: Indicates if a storage profile is default or not.

          description: A human-friendly description.

          iops: Indicates maximum I/O operations per second.

          supports_encryption: Indicates whether this storage profile supports encryption or not.

          tags: A list of tags that represent the capabilities of this storage profile

          volume_type: Indicates the type of volume associated with type of storage.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/storage-profiles-aws",
            body=await async_maybe_transform(
                {
                    "device_type": device_type,
                    "name": name,
                    "region_id": region_id,
                    "default_item": default_item,
                    "description": description,
                    "iops": iops,
                    "supports_encryption": supports_encryption,
                    "tags": tags,
                    "volume_type": volume_type,
                },
                storage_profiles_aw_storage_profiles_aws_params.StorageProfilesAwStorageProfilesAwsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_aw_storage_profiles_aws_params.StorageProfilesAwStorageProfilesAwsParams,
                ),
            ),
            cast_to=AwsStorageProfile,
        )


class StorageProfilesAwsResourceWithRawResponse:
    def __init__(self, storage_profiles_aws: StorageProfilesAwsResource) -> None:
        self._storage_profiles_aws = storage_profiles_aws

        self.retrieve = to_raw_response_wrapper(
            storage_profiles_aws.retrieve,
        )
        self.update = to_raw_response_wrapper(
            storage_profiles_aws.update,
        )
        self.delete = to_raw_response_wrapper(
            storage_profiles_aws.delete,
        )
        self.retrieve_storage_profiles_aws = to_raw_response_wrapper(
            storage_profiles_aws.retrieve_storage_profiles_aws,
        )
        self.storage_profiles_aws = to_raw_response_wrapper(
            storage_profiles_aws.storage_profiles_aws,
        )


class AsyncStorageProfilesAwsResourceWithRawResponse:
    def __init__(self, storage_profiles_aws: AsyncStorageProfilesAwsResource) -> None:
        self._storage_profiles_aws = storage_profiles_aws

        self.retrieve = async_to_raw_response_wrapper(
            storage_profiles_aws.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            storage_profiles_aws.update,
        )
        self.delete = async_to_raw_response_wrapper(
            storage_profiles_aws.delete,
        )
        self.retrieve_storage_profiles_aws = async_to_raw_response_wrapper(
            storage_profiles_aws.retrieve_storage_profiles_aws,
        )
        self.storage_profiles_aws = async_to_raw_response_wrapper(
            storage_profiles_aws.storage_profiles_aws,
        )


class StorageProfilesAwsResourceWithStreamingResponse:
    def __init__(self, storage_profiles_aws: StorageProfilesAwsResource) -> None:
        self._storage_profiles_aws = storage_profiles_aws

        self.retrieve = to_streamed_response_wrapper(
            storage_profiles_aws.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            storage_profiles_aws.update,
        )
        self.delete = to_streamed_response_wrapper(
            storage_profiles_aws.delete,
        )
        self.retrieve_storage_profiles_aws = to_streamed_response_wrapper(
            storage_profiles_aws.retrieve_storage_profiles_aws,
        )
        self.storage_profiles_aws = to_streamed_response_wrapper(
            storage_profiles_aws.storage_profiles_aws,
        )


class AsyncStorageProfilesAwsResourceWithStreamingResponse:
    def __init__(self, storage_profiles_aws: AsyncStorageProfilesAwsResource) -> None:
        self._storage_profiles_aws = storage_profiles_aws

        self.retrieve = async_to_streamed_response_wrapper(
            storage_profiles_aws.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            storage_profiles_aws.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            storage_profiles_aws.delete,
        )
        self.retrieve_storage_profiles_aws = async_to_streamed_response_wrapper(
            storage_profiles_aws.retrieve_storage_profiles_aws,
        )
        self.storage_profiles_aws = async_to_streamed_response_wrapper(
            storage_profiles_aws.storage_profiles_aws,
        )
