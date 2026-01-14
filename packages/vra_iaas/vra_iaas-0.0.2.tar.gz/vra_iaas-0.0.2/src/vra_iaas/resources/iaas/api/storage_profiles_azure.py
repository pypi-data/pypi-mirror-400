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
    storage_profiles_azure_delete_params,
    storage_profiles_azure_update_params,
    storage_profiles_azure_retrieve_params,
    storage_profiles_azure_storage_profiles_azure_params,
    storage_profiles_azure_retrieve_storage_profiles_azure_params,
)
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.azure_storage_profile import AzureStorageProfile
from ....types.iaas.api.storage_profiles_azure_retrieve_storage_profiles_azure_response import (
    StorageProfilesAzureRetrieveStorageProfilesAzureResponse,
)

__all__ = ["StorageProfilesAzureResource", "AsyncStorageProfilesAzureResource"]


class StorageProfilesAzureResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> StorageProfilesAzureResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return StorageProfilesAzureResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StorageProfilesAzureResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return StorageProfilesAzureResourceWithStreamingResponse(self)

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
    ) -> AzureStorageProfile:
        """
        Get Azure storage profile with a given id

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
            f"/iaas/api/storage-profiles-azure/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_azure_retrieve_params.StorageProfilesAzureRetrieveParams,
                ),
            ),
            cast_to=AzureStorageProfile,
        )

    def update(
        self,
        id: str,
        *,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        data_disk_caching: str | Omit = omit,
        default_item: bool | Omit = omit,
        description: str | Omit = omit,
        disk_encryption_set_id: str | Omit = omit,
        disk_type: str | Omit = omit,
        os_disk_caching: str | Omit = omit,
        storage_account_id: str | Omit = omit,
        supports_encryption: bool | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AzureStorageProfile:
        """
        Update Azure storage profile

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The If of the region that is associated with the storage profile.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          data_disk_caching: Indicates the caching mechanism for additional disk.

          default_item: Indicates if a storage policy contains default storage properties.

          description: A human-friendly description.

          disk_encryption_set_id: Indicates the id of disk encryption set.

          disk_type: Indicates the performance tier for the storage type. Premium disks are SSD
              backed and Standard disks are HDD backed.

          os_disk_caching: Indicates the caching mechanism for OS disk. Default policy for OS disks is
              Read/Write.

          storage_account_id: Id of a storage account where in the disk is placed.

          supports_encryption: Indicates whether this storage policy should support encryption or not.

          tags: A set of tag keys and optional values for a storage policy which define set of
              specifications for creating a disk.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/storage-profiles-azure/{id}",
            body=maybe_transform(
                {
                    "name": name,
                    "region_id": region_id,
                    "data_disk_caching": data_disk_caching,
                    "default_item": default_item,
                    "description": description,
                    "disk_encryption_set_id": disk_encryption_set_id,
                    "disk_type": disk_type,
                    "os_disk_caching": os_disk_caching,
                    "storage_account_id": storage_account_id,
                    "supports_encryption": supports_encryption,
                    "tags": tags,
                },
                storage_profiles_azure_update_params.StorageProfilesAzureUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, storage_profiles_azure_update_params.StorageProfilesAzureUpdateParams
                ),
            ),
            cast_to=AzureStorageProfile,
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
        Delete Azure storage profile with a given id

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
            f"/iaas/api/storage-profiles-azure/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, storage_profiles_azure_delete_params.StorageProfilesAzureDeleteParams
                ),
            ),
            cast_to=NoneType,
        )

    def retrieve_storage_profiles_azure(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageProfilesAzureRetrieveStorageProfilesAzureResponse:
        """
        Get all Azure storage profiles

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/storage-profiles-azure",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_azure_retrieve_storage_profiles_azure_params.StorageProfilesAzureRetrieveStorageProfilesAzureParams,
                ),
            ),
            cast_to=StorageProfilesAzureRetrieveStorageProfilesAzureResponse,
        )

    def storage_profiles_azure(
        self,
        *,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        data_disk_caching: str | Omit = omit,
        default_item: bool | Omit = omit,
        description: str | Omit = omit,
        disk_encryption_set_id: str | Omit = omit,
        disk_type: str | Omit = omit,
        os_disk_caching: str | Omit = omit,
        storage_account_id: str | Omit = omit,
        supports_encryption: bool | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AzureStorageProfile:
        """
        Create Azure storage profile

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The If of the region that is associated with the storage profile.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          data_disk_caching: Indicates the caching mechanism for additional disk.

          default_item: Indicates if a storage policy contains default storage properties.

          description: A human-friendly description.

          disk_encryption_set_id: Indicates the id of disk encryption set.

          disk_type: Indicates the performance tier for the storage type. Premium disks are SSD
              backed and Standard disks are HDD backed.

          os_disk_caching: Indicates the caching mechanism for OS disk. Default policy for OS disks is
              Read/Write.

          storage_account_id: Id of a storage account where in the disk is placed.

          supports_encryption: Indicates whether this storage policy should support encryption or not.

          tags: A set of tag keys and optional values for a storage policy which define set of
              specifications for creating a disk.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/storage-profiles-azure",
            body=maybe_transform(
                {
                    "name": name,
                    "region_id": region_id,
                    "data_disk_caching": data_disk_caching,
                    "default_item": default_item,
                    "description": description,
                    "disk_encryption_set_id": disk_encryption_set_id,
                    "disk_type": disk_type,
                    "os_disk_caching": os_disk_caching,
                    "storage_account_id": storage_account_id,
                    "supports_encryption": supports_encryption,
                    "tags": tags,
                },
                storage_profiles_azure_storage_profiles_azure_params.StorageProfilesAzureStorageProfilesAzureParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_azure_storage_profiles_azure_params.StorageProfilesAzureStorageProfilesAzureParams,
                ),
            ),
            cast_to=AzureStorageProfile,
        )


class AsyncStorageProfilesAzureResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncStorageProfilesAzureResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncStorageProfilesAzureResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStorageProfilesAzureResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncStorageProfilesAzureResourceWithStreamingResponse(self)

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
    ) -> AzureStorageProfile:
        """
        Get Azure storage profile with a given id

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
            f"/iaas/api/storage-profiles-azure/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_azure_retrieve_params.StorageProfilesAzureRetrieveParams,
                ),
            ),
            cast_to=AzureStorageProfile,
        )

    async def update(
        self,
        id: str,
        *,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        data_disk_caching: str | Omit = omit,
        default_item: bool | Omit = omit,
        description: str | Omit = omit,
        disk_encryption_set_id: str | Omit = omit,
        disk_type: str | Omit = omit,
        os_disk_caching: str | Omit = omit,
        storage_account_id: str | Omit = omit,
        supports_encryption: bool | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AzureStorageProfile:
        """
        Update Azure storage profile

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The If of the region that is associated with the storage profile.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          data_disk_caching: Indicates the caching mechanism for additional disk.

          default_item: Indicates if a storage policy contains default storage properties.

          description: A human-friendly description.

          disk_encryption_set_id: Indicates the id of disk encryption set.

          disk_type: Indicates the performance tier for the storage type. Premium disks are SSD
              backed and Standard disks are HDD backed.

          os_disk_caching: Indicates the caching mechanism for OS disk. Default policy for OS disks is
              Read/Write.

          storage_account_id: Id of a storage account where in the disk is placed.

          supports_encryption: Indicates whether this storage policy should support encryption or not.

          tags: A set of tag keys and optional values for a storage policy which define set of
              specifications for creating a disk.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/storage-profiles-azure/{id}",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "region_id": region_id,
                    "data_disk_caching": data_disk_caching,
                    "default_item": default_item,
                    "description": description,
                    "disk_encryption_set_id": disk_encryption_set_id,
                    "disk_type": disk_type,
                    "os_disk_caching": os_disk_caching,
                    "storage_account_id": storage_account_id,
                    "supports_encryption": supports_encryption,
                    "tags": tags,
                },
                storage_profiles_azure_update_params.StorageProfilesAzureUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, storage_profiles_azure_update_params.StorageProfilesAzureUpdateParams
                ),
            ),
            cast_to=AzureStorageProfile,
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
        Delete Azure storage profile with a given id

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
            f"/iaas/api/storage-profiles-azure/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, storage_profiles_azure_delete_params.StorageProfilesAzureDeleteParams
                ),
            ),
            cast_to=NoneType,
        )

    async def retrieve_storage_profiles_azure(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageProfilesAzureRetrieveStorageProfilesAzureResponse:
        """
        Get all Azure storage profiles

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/storage-profiles-azure",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_azure_retrieve_storage_profiles_azure_params.StorageProfilesAzureRetrieveStorageProfilesAzureParams,
                ),
            ),
            cast_to=StorageProfilesAzureRetrieveStorageProfilesAzureResponse,
        )

    async def storage_profiles_azure(
        self,
        *,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        data_disk_caching: str | Omit = omit,
        default_item: bool | Omit = omit,
        description: str | Omit = omit,
        disk_encryption_set_id: str | Omit = omit,
        disk_type: str | Omit = omit,
        os_disk_caching: str | Omit = omit,
        storage_account_id: str | Omit = omit,
        supports_encryption: bool | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AzureStorageProfile:
        """
        Create Azure storage profile

        Args:
          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The If of the region that is associated with the storage profile.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          data_disk_caching: Indicates the caching mechanism for additional disk.

          default_item: Indicates if a storage policy contains default storage properties.

          description: A human-friendly description.

          disk_encryption_set_id: Indicates the id of disk encryption set.

          disk_type: Indicates the performance tier for the storage type. Premium disks are SSD
              backed and Standard disks are HDD backed.

          os_disk_caching: Indicates the caching mechanism for OS disk. Default policy for OS disks is
              Read/Write.

          storage_account_id: Id of a storage account where in the disk is placed.

          supports_encryption: Indicates whether this storage policy should support encryption or not.

          tags: A set of tag keys and optional values for a storage policy which define set of
              specifications for creating a disk.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/storage-profiles-azure",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "region_id": region_id,
                    "data_disk_caching": data_disk_caching,
                    "default_item": default_item,
                    "description": description,
                    "disk_encryption_set_id": disk_encryption_set_id,
                    "disk_type": disk_type,
                    "os_disk_caching": os_disk_caching,
                    "storage_account_id": storage_account_id,
                    "supports_encryption": supports_encryption,
                    "tags": tags,
                },
                storage_profiles_azure_storage_profiles_azure_params.StorageProfilesAzureStorageProfilesAzureParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_azure_storage_profiles_azure_params.StorageProfilesAzureStorageProfilesAzureParams,
                ),
            ),
            cast_to=AzureStorageProfile,
        )


class StorageProfilesAzureResourceWithRawResponse:
    def __init__(self, storage_profiles_azure: StorageProfilesAzureResource) -> None:
        self._storage_profiles_azure = storage_profiles_azure

        self.retrieve = to_raw_response_wrapper(
            storage_profiles_azure.retrieve,
        )
        self.update = to_raw_response_wrapper(
            storage_profiles_azure.update,
        )
        self.delete = to_raw_response_wrapper(
            storage_profiles_azure.delete,
        )
        self.retrieve_storage_profiles_azure = to_raw_response_wrapper(
            storage_profiles_azure.retrieve_storage_profiles_azure,
        )
        self.storage_profiles_azure = to_raw_response_wrapper(
            storage_profiles_azure.storage_profiles_azure,
        )


class AsyncStorageProfilesAzureResourceWithRawResponse:
    def __init__(self, storage_profiles_azure: AsyncStorageProfilesAzureResource) -> None:
        self._storage_profiles_azure = storage_profiles_azure

        self.retrieve = async_to_raw_response_wrapper(
            storage_profiles_azure.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            storage_profiles_azure.update,
        )
        self.delete = async_to_raw_response_wrapper(
            storage_profiles_azure.delete,
        )
        self.retrieve_storage_profiles_azure = async_to_raw_response_wrapper(
            storage_profiles_azure.retrieve_storage_profiles_azure,
        )
        self.storage_profiles_azure = async_to_raw_response_wrapper(
            storage_profiles_azure.storage_profiles_azure,
        )


class StorageProfilesAzureResourceWithStreamingResponse:
    def __init__(self, storage_profiles_azure: StorageProfilesAzureResource) -> None:
        self._storage_profiles_azure = storage_profiles_azure

        self.retrieve = to_streamed_response_wrapper(
            storage_profiles_azure.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            storage_profiles_azure.update,
        )
        self.delete = to_streamed_response_wrapper(
            storage_profiles_azure.delete,
        )
        self.retrieve_storage_profiles_azure = to_streamed_response_wrapper(
            storage_profiles_azure.retrieve_storage_profiles_azure,
        )
        self.storage_profiles_azure = to_streamed_response_wrapper(
            storage_profiles_azure.storage_profiles_azure,
        )


class AsyncStorageProfilesAzureResourceWithStreamingResponse:
    def __init__(self, storage_profiles_azure: AsyncStorageProfilesAzureResource) -> None:
        self._storage_profiles_azure = storage_profiles_azure

        self.retrieve = async_to_streamed_response_wrapper(
            storage_profiles_azure.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            storage_profiles_azure.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            storage_profiles_azure.delete,
        )
        self.retrieve_storage_profiles_azure = async_to_streamed_response_wrapper(
            storage_profiles_azure.retrieve_storage_profiles_azure,
        )
        self.storage_profiles_azure = async_to_streamed_response_wrapper(
            storage_profiles_azure.storage_profiles_azure,
        )
