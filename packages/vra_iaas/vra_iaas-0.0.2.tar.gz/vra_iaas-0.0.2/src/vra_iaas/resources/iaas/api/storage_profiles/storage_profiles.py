# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal

import httpx

from ....._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
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
from .....types.iaas.api import (
    storage_profile_delete_params,
    storage_profile_update_params,
    storage_profile_retrieve_params,
    storage_profile_storage_profiles_params,
    storage_profile_retrieve_storage_profiles_params,
)
from .....types.iaas.api.tag_param import TagParam
from .storage_profile_associations import (
    StorageProfileAssociationsResource,
    AsyncStorageProfileAssociationsResource,
    StorageProfileAssociationsResourceWithRawResponse,
    AsyncStorageProfileAssociationsResourceWithRawResponse,
    StorageProfileAssociationsResourceWithStreamingResponse,
    AsyncStorageProfileAssociationsResourceWithStreamingResponse,
)
from .....types.iaas.api.storage_profile import StorageProfile
from .....types.iaas.api.storage_profile_associations_param import StorageProfileAssociationsParam
from .....types.iaas.api.storage_profile_retrieve_storage_profiles_response import (
    StorageProfileRetrieveStorageProfilesResponse,
)

__all__ = ["StorageProfilesResource", "AsyncStorageProfilesResource"]


class StorageProfilesResource(SyncAPIResource):
    @cached_property
    def storage_profile_associations(self) -> StorageProfileAssociationsResource:
        return StorageProfileAssociationsResource(self._client)

    @cached_property
    def with_raw_response(self) -> StorageProfilesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return StorageProfilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StorageProfilesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return StorageProfilesResourceWithStreamingResponse(self)

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
    ) -> StorageProfile:
        """
        Get storage profile with a given id

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
            f"/iaas/api/storage-profiles/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, storage_profile_retrieve_params.StorageProfileRetrieveParams
                ),
            ),
            cast_to=StorageProfile,
        )

    def update(
        self,
        id: str,
        *,
        default_item: bool,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        compute_host_id: str | Omit = omit,
        description: str | Omit = omit,
        disk_properties: Dict[str, str] | Omit = omit,
        disk_target_properties: Dict[str, str] | Omit = omit,
        priority: int | Omit = omit,
        storage_filter_type: Literal["INCLUDE_ALL", "TAG_BASED", "MANUAL"] | Omit = omit,
        storage_profile_associations: Iterable[StorageProfileAssociationsParam] | Omit = omit,
        supports_encryption: bool | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        tags_to_match: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageProfile:
        """
        Replace storage profile with a given id

        Args:
          default_item: Indicates if a storage profile is a default profile.

          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The Id of the region that is associated with the storage profile.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          compute_host_id: The compute host Id to be associated with the storage profile.

          description: A human-friendly description.

          disk_properties: Map of storage properties that are to be applied on disk while provisioning.

          disk_target_properties: Map of storage placements to know where the disk is provisioned. 'datastoreId'
              is deprecated, instead use 'storageProfileAssociations' parameter to associate
              datastores with the storage profile.

          priority: Defines the priority of the storage profile with the highest priority being 0.
              Defaults to the value of 1.

          storage_filter_type: Defines filter type for adding storage objects (datastores) to the storage
              profile. Defaults to INCLUDE_ALL. For INCLUDE_ALL and TAG_BASED all the valid
              Data stores will be associated with the priority 1.

          storage_profile_associations: Defines a specification of Storage Profile datastore associations.

          supports_encryption: Indicates whether this storage profile supports encryption or not.

          tags: A list of tags that represent the capabilities of this storage profile

          tags_to_match: A set of tag keys and optional values to be set on datastores to be included in
              this storage profile based on the storageFilterType: TAG_BASED.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._put(
            f"/iaas/api/storage-profiles/{id}",
            body=maybe_transform(
                {
                    "default_item": default_item,
                    "name": name,
                    "region_id": region_id,
                    "compute_host_id": compute_host_id,
                    "description": description,
                    "disk_properties": disk_properties,
                    "disk_target_properties": disk_target_properties,
                    "priority": priority,
                    "storage_filter_type": storage_filter_type,
                    "storage_profile_associations": storage_profile_associations,
                    "supports_encryption": supports_encryption,
                    "tags": tags,
                    "tags_to_match": tags_to_match,
                },
                storage_profile_update_params.StorageProfileUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, storage_profile_update_params.StorageProfileUpdateParams
                ),
            ),
            cast_to=StorageProfile,
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
        Delete storage profile with a given id

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
            f"/iaas/api/storage-profiles/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, storage_profile_delete_params.StorageProfileDeleteParams
                ),
            ),
            cast_to=NoneType,
        )

    def retrieve_storage_profiles(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageProfileRetrieveStorageProfilesResponse:
        """
        Get all storage profiles

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/storage-profiles",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    storage_profile_retrieve_storage_profiles_params.StorageProfileRetrieveStorageProfilesParams,
                ),
            ),
            cast_to=StorageProfileRetrieveStorageProfilesResponse,
        )

    def storage_profiles(
        self,
        *,
        default_item: bool,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        compute_host_id: str | Omit = omit,
        description: str | Omit = omit,
        disk_properties: Dict[str, str] | Omit = omit,
        disk_target_properties: Dict[str, str] | Omit = omit,
        priority: int | Omit = omit,
        storage_filter_type: Literal["INCLUDE_ALL", "TAG_BASED", "MANUAL"] | Omit = omit,
        storage_profile_associations: Iterable[StorageProfileAssociationsParam] | Omit = omit,
        supports_encryption: bool | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        tags_to_match: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageProfile:
        """
        Create storage profile

        Args:
          default_item: Indicates if a storage profile is a default profile.

          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The Id of the region that is associated with the storage profile.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          compute_host_id: The compute host Id to be associated with the storage profile.

          description: A human-friendly description.

          disk_properties: Map of storage properties that are to be applied on disk while provisioning.

          disk_target_properties: Map of storage placements to know where the disk is provisioned. 'datastoreId'
              is deprecated, instead use 'storageProfileAssociations' parameter to associate
              datastores with the storage profile.

          priority: Defines the priority of the storage profile with the highest priority being 0.
              Defaults to the value of 1.

          storage_filter_type: Defines filter type for adding storage objects (datastores) to the storage
              profile. Defaults to INCLUDE_ALL. For INCLUDE_ALL and TAG_BASED all the valid
              Data stores will be associated with the priority 1.

          storage_profile_associations: Defines a specification of Storage Profile datastore associations.

          supports_encryption: Indicates whether this storage profile supports encryption or not.

          tags: A list of tags that represent the capabilities of this storage profile

          tags_to_match: A set of tag keys and optional values to be set on datastores to be included in
              this storage profile based on the storageFilterType: TAG_BASED.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/storage-profiles",
            body=maybe_transform(
                {
                    "default_item": default_item,
                    "name": name,
                    "region_id": region_id,
                    "compute_host_id": compute_host_id,
                    "description": description,
                    "disk_properties": disk_properties,
                    "disk_target_properties": disk_target_properties,
                    "priority": priority,
                    "storage_filter_type": storage_filter_type,
                    "storage_profile_associations": storage_profile_associations,
                    "supports_encryption": supports_encryption,
                    "tags": tags,
                    "tags_to_match": tags_to_match,
                },
                storage_profile_storage_profiles_params.StorageProfileStorageProfilesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    storage_profile_storage_profiles_params.StorageProfileStorageProfilesParams,
                ),
            ),
            cast_to=StorageProfile,
        )


class AsyncStorageProfilesResource(AsyncAPIResource):
    @cached_property
    def storage_profile_associations(self) -> AsyncStorageProfileAssociationsResource:
        return AsyncStorageProfileAssociationsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncStorageProfilesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncStorageProfilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStorageProfilesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncStorageProfilesResourceWithStreamingResponse(self)

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
    ) -> StorageProfile:
        """
        Get storage profile with a given id

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
            f"/iaas/api/storage-profiles/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, storage_profile_retrieve_params.StorageProfileRetrieveParams
                ),
            ),
            cast_to=StorageProfile,
        )

    async def update(
        self,
        id: str,
        *,
        default_item: bool,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        compute_host_id: str | Omit = omit,
        description: str | Omit = omit,
        disk_properties: Dict[str, str] | Omit = omit,
        disk_target_properties: Dict[str, str] | Omit = omit,
        priority: int | Omit = omit,
        storage_filter_type: Literal["INCLUDE_ALL", "TAG_BASED", "MANUAL"] | Omit = omit,
        storage_profile_associations: Iterable[StorageProfileAssociationsParam] | Omit = omit,
        supports_encryption: bool | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        tags_to_match: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageProfile:
        """
        Replace storage profile with a given id

        Args:
          default_item: Indicates if a storage profile is a default profile.

          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The Id of the region that is associated with the storage profile.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          compute_host_id: The compute host Id to be associated with the storage profile.

          description: A human-friendly description.

          disk_properties: Map of storage properties that are to be applied on disk while provisioning.

          disk_target_properties: Map of storage placements to know where the disk is provisioned. 'datastoreId'
              is deprecated, instead use 'storageProfileAssociations' parameter to associate
              datastores with the storage profile.

          priority: Defines the priority of the storage profile with the highest priority being 0.
              Defaults to the value of 1.

          storage_filter_type: Defines filter type for adding storage objects (datastores) to the storage
              profile. Defaults to INCLUDE_ALL. For INCLUDE_ALL and TAG_BASED all the valid
              Data stores will be associated with the priority 1.

          storage_profile_associations: Defines a specification of Storage Profile datastore associations.

          supports_encryption: Indicates whether this storage profile supports encryption or not.

          tags: A list of tags that represent the capabilities of this storage profile

          tags_to_match: A set of tag keys and optional values to be set on datastores to be included in
              this storage profile based on the storageFilterType: TAG_BASED.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._put(
            f"/iaas/api/storage-profiles/{id}",
            body=await async_maybe_transform(
                {
                    "default_item": default_item,
                    "name": name,
                    "region_id": region_id,
                    "compute_host_id": compute_host_id,
                    "description": description,
                    "disk_properties": disk_properties,
                    "disk_target_properties": disk_target_properties,
                    "priority": priority,
                    "storage_filter_type": storage_filter_type,
                    "storage_profile_associations": storage_profile_associations,
                    "supports_encryption": supports_encryption,
                    "tags": tags,
                    "tags_to_match": tags_to_match,
                },
                storage_profile_update_params.StorageProfileUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, storage_profile_update_params.StorageProfileUpdateParams
                ),
            ),
            cast_to=StorageProfile,
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
        Delete storage profile with a given id

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
            f"/iaas/api/storage-profiles/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, storage_profile_delete_params.StorageProfileDeleteParams
                ),
            ),
            cast_to=NoneType,
        )

    async def retrieve_storage_profiles(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageProfileRetrieveStorageProfilesResponse:
        """
        Get all storage profiles

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/storage-profiles",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    storage_profile_retrieve_storage_profiles_params.StorageProfileRetrieveStorageProfilesParams,
                ),
            ),
            cast_to=StorageProfileRetrieveStorageProfilesResponse,
        )

    async def storage_profiles(
        self,
        *,
        default_item: bool,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        compute_host_id: str | Omit = omit,
        description: str | Omit = omit,
        disk_properties: Dict[str, str] | Omit = omit,
        disk_target_properties: Dict[str, str] | Omit = omit,
        priority: int | Omit = omit,
        storage_filter_type: Literal["INCLUDE_ALL", "TAG_BASED", "MANUAL"] | Omit = omit,
        storage_profile_associations: Iterable[StorageProfileAssociationsParam] | Omit = omit,
        supports_encryption: bool | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        tags_to_match: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageProfile:
        """
        Create storage profile

        Args:
          default_item: Indicates if a storage profile is a default profile.

          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The Id of the region that is associated with the storage profile.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          compute_host_id: The compute host Id to be associated with the storage profile.

          description: A human-friendly description.

          disk_properties: Map of storage properties that are to be applied on disk while provisioning.

          disk_target_properties: Map of storage placements to know where the disk is provisioned. 'datastoreId'
              is deprecated, instead use 'storageProfileAssociations' parameter to associate
              datastores with the storage profile.

          priority: Defines the priority of the storage profile with the highest priority being 0.
              Defaults to the value of 1.

          storage_filter_type: Defines filter type for adding storage objects (datastores) to the storage
              profile. Defaults to INCLUDE_ALL. For INCLUDE_ALL and TAG_BASED all the valid
              Data stores will be associated with the priority 1.

          storage_profile_associations: Defines a specification of Storage Profile datastore associations.

          supports_encryption: Indicates whether this storage profile supports encryption or not.

          tags: A list of tags that represent the capabilities of this storage profile

          tags_to_match: A set of tag keys and optional values to be set on datastores to be included in
              this storage profile based on the storageFilterType: TAG_BASED.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/storage-profiles",
            body=await async_maybe_transform(
                {
                    "default_item": default_item,
                    "name": name,
                    "region_id": region_id,
                    "compute_host_id": compute_host_id,
                    "description": description,
                    "disk_properties": disk_properties,
                    "disk_target_properties": disk_target_properties,
                    "priority": priority,
                    "storage_filter_type": storage_filter_type,
                    "storage_profile_associations": storage_profile_associations,
                    "supports_encryption": supports_encryption,
                    "tags": tags,
                    "tags_to_match": tags_to_match,
                },
                storage_profile_storage_profiles_params.StorageProfileStorageProfilesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    storage_profile_storage_profiles_params.StorageProfileStorageProfilesParams,
                ),
            ),
            cast_to=StorageProfile,
        )


class StorageProfilesResourceWithRawResponse:
    def __init__(self, storage_profiles: StorageProfilesResource) -> None:
        self._storage_profiles = storage_profiles

        self.retrieve = to_raw_response_wrapper(
            storage_profiles.retrieve,
        )
        self.update = to_raw_response_wrapper(
            storage_profiles.update,
        )
        self.delete = to_raw_response_wrapper(
            storage_profiles.delete,
        )
        self.retrieve_storage_profiles = to_raw_response_wrapper(
            storage_profiles.retrieve_storage_profiles,
        )
        self.storage_profiles = to_raw_response_wrapper(
            storage_profiles.storage_profiles,
        )

    @cached_property
    def storage_profile_associations(self) -> StorageProfileAssociationsResourceWithRawResponse:
        return StorageProfileAssociationsResourceWithRawResponse(self._storage_profiles.storage_profile_associations)


class AsyncStorageProfilesResourceWithRawResponse:
    def __init__(self, storage_profiles: AsyncStorageProfilesResource) -> None:
        self._storage_profiles = storage_profiles

        self.retrieve = async_to_raw_response_wrapper(
            storage_profiles.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            storage_profiles.update,
        )
        self.delete = async_to_raw_response_wrapper(
            storage_profiles.delete,
        )
        self.retrieve_storage_profiles = async_to_raw_response_wrapper(
            storage_profiles.retrieve_storage_profiles,
        )
        self.storage_profiles = async_to_raw_response_wrapper(
            storage_profiles.storage_profiles,
        )

    @cached_property
    def storage_profile_associations(self) -> AsyncStorageProfileAssociationsResourceWithRawResponse:
        return AsyncStorageProfileAssociationsResourceWithRawResponse(
            self._storage_profiles.storage_profile_associations
        )


class StorageProfilesResourceWithStreamingResponse:
    def __init__(self, storage_profiles: StorageProfilesResource) -> None:
        self._storage_profiles = storage_profiles

        self.retrieve = to_streamed_response_wrapper(
            storage_profiles.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            storage_profiles.update,
        )
        self.delete = to_streamed_response_wrapper(
            storage_profiles.delete,
        )
        self.retrieve_storage_profiles = to_streamed_response_wrapper(
            storage_profiles.retrieve_storage_profiles,
        )
        self.storage_profiles = to_streamed_response_wrapper(
            storage_profiles.storage_profiles,
        )

    @cached_property
    def storage_profile_associations(self) -> StorageProfileAssociationsResourceWithStreamingResponse:
        return StorageProfileAssociationsResourceWithStreamingResponse(
            self._storage_profiles.storage_profile_associations
        )


class AsyncStorageProfilesResourceWithStreamingResponse:
    def __init__(self, storage_profiles: AsyncStorageProfilesResource) -> None:
        self._storage_profiles = storage_profiles

        self.retrieve = async_to_streamed_response_wrapper(
            storage_profiles.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            storage_profiles.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            storage_profiles.delete,
        )
        self.retrieve_storage_profiles = async_to_streamed_response_wrapper(
            storage_profiles.retrieve_storage_profiles,
        )
        self.storage_profiles = async_to_streamed_response_wrapper(
            storage_profiles.storage_profiles,
        )

    @cached_property
    def storage_profile_associations(self) -> AsyncStorageProfileAssociationsResourceWithStreamingResponse:
        return AsyncStorageProfileAssociationsResourceWithStreamingResponse(
            self._storage_profiles.storage_profile_associations
        )
