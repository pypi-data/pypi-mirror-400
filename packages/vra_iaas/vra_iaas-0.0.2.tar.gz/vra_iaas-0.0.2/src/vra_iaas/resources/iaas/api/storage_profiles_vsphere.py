# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal

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
    storage_profiles_vsphere_delete_params,
    storage_profiles_vsphere_update_params,
    storage_profiles_vsphere_retrieve_params,
    storage_profiles_vsphere_storage_profiles_vsphere_params,
    storage_profiles_vsphere_retrieve_storage_profiles_vsphere_params,
)
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.vsphere_storage_profile import VsphereStorageProfile
from ....types.iaas.api.storage_profile_associations_param import StorageProfileAssociationsParam
from ....types.iaas.api.storage_profiles_vsphere_retrieve_storage_profiles_vsphere_response import (
    StorageProfilesVsphereRetrieveStorageProfilesVsphereResponse,
)

__all__ = ["StorageProfilesVsphereResource", "AsyncStorageProfilesVsphereResource"]


class StorageProfilesVsphereResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> StorageProfilesVsphereResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return StorageProfilesVsphereResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StorageProfilesVsphereResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return StorageProfilesVsphereResourceWithStreamingResponse(self)

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
    ) -> VsphereStorageProfile:
        """
        Get vSphere storage profile with a given id

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
            f"/iaas/api/storage-profiles-vsphere/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_vsphere_retrieve_params.StorageProfilesVsphereRetrieveParams,
                ),
            ),
            cast_to=VsphereStorageProfile,
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
        datastore_id: str | Omit = omit,
        description: str | Omit = omit,
        disk_mode: str | Omit = omit,
        disk_type: str | Omit = omit,
        limit_iops: str | Omit = omit,
        priority: int | Omit = omit,
        provisioning_type: str | Omit = omit,
        shares: str | Omit = omit,
        shares_level: str | Omit = omit,
        storage_filter_type: Literal["INCLUDE_ALL", "TAG_BASED", "MANUAL"] | Omit = omit,
        storage_policy_id: str | Omit = omit,
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
    ) -> VsphereStorageProfile:
        """
        Update vSphere storage profile

        Args:
          default_item: Indicates if a storage profile acts as a default storage profile for a disk.

          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The Id of the region that is associated with the storage profile.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          compute_host_id: The compute host Id to be associated with the storage profile.

          datastore_id: Id of the vSphere Datastore for placing disk and VM. Deprecated, instead use
              'storageProfileAssociations' parameter to associate datastores with the storage
              profile.

          description: A human-friendly description.

          disk_mode: Type of mode for the disk

          disk_type: Disk types are specified as

              Standard - Simple vSphere virtual disks which cannot be managed independently
              without an attached VM. First Class - Improved version of standard virtual
              disks, designed to be fully mananged independent storage objects.

              Empty value is considered as Standard

          limit_iops: The upper bound for the I/O operations per second allocated for each virtual
              disk.

          priority: Defines the priority of the storage profile with the highest priority being 0.
              Defaults to the value of 1.

          provisioning_type: Type of provisioning policy for the disk.

          shares: A specific number of shares assigned to each virtual machine.

          shares_level: Shares are specified as High, Normal, Low or Custom and these values specify
              share values with a 4:2:1 ratio, respectively.

          storage_filter_type: Defines filter type for adding storage objects (data stores) to the storage
              profile. Defaults to INCLUDE_ALL.

          storage_policy_id: Id of the vSphere Storage Policy to be applied.

          storage_profile_associations: Defines a specification of Storage Profile datastore associations.

          supports_encryption: Indicates whether this storage profile supports encryption or not.

          tags: A list of tags that represent the capabilities of this storage profile.

          tags_to_match: A set of tag keys and optional values to be set on data stores to be included in
              this storage profile based on the storageFilterType: TAG_BASED.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/storage-profiles-vsphere/{id}",
            body=maybe_transform(
                {
                    "default_item": default_item,
                    "name": name,
                    "region_id": region_id,
                    "compute_host_id": compute_host_id,
                    "datastore_id": datastore_id,
                    "description": description,
                    "disk_mode": disk_mode,
                    "disk_type": disk_type,
                    "limit_iops": limit_iops,
                    "priority": priority,
                    "provisioning_type": provisioning_type,
                    "shares": shares,
                    "shares_level": shares_level,
                    "storage_filter_type": storage_filter_type,
                    "storage_policy_id": storage_policy_id,
                    "storage_profile_associations": storage_profile_associations,
                    "supports_encryption": supports_encryption,
                    "tags": tags,
                    "tags_to_match": tags_to_match,
                },
                storage_profiles_vsphere_update_params.StorageProfilesVsphereUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_vsphere_update_params.StorageProfilesVsphereUpdateParams,
                ),
            ),
            cast_to=VsphereStorageProfile,
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
        Delete vSphere storage profile with a given id

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
            f"/iaas/api/storage-profiles-vsphere/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_vsphere_delete_params.StorageProfilesVsphereDeleteParams,
                ),
            ),
            cast_to=NoneType,
        )

    def retrieve_storage_profiles_vsphere(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageProfilesVsphereRetrieveStorageProfilesVsphereResponse:
        """
        Get all vSphere storage profiles

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/iaas/api/storage-profiles-vsphere",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_vsphere_retrieve_storage_profiles_vsphere_params.StorageProfilesVsphereRetrieveStorageProfilesVsphereParams,
                ),
            ),
            cast_to=StorageProfilesVsphereRetrieveStorageProfilesVsphereResponse,
        )

    def storage_profiles_vsphere(
        self,
        *,
        default_item: bool,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        compute_host_id: str | Omit = omit,
        datastore_id: str | Omit = omit,
        description: str | Omit = omit,
        disk_mode: str | Omit = omit,
        disk_type: str | Omit = omit,
        limit_iops: str | Omit = omit,
        priority: int | Omit = omit,
        provisioning_type: str | Omit = omit,
        shares: str | Omit = omit,
        shares_level: str | Omit = omit,
        storage_filter_type: Literal["INCLUDE_ALL", "TAG_BASED", "MANUAL"] | Omit = omit,
        storage_policy_id: str | Omit = omit,
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
    ) -> VsphereStorageProfile:
        """
        Create vSphere storage profile

        Args:
          default_item: Indicates if a storage profile acts as a default storage profile for a disk.

          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The Id of the region that is associated with the storage profile.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          compute_host_id: The compute host Id to be associated with the storage profile.

          datastore_id: Id of the vSphere Datastore for placing disk and VM. Deprecated, instead use
              'storageProfileAssociations' parameter to associate datastores with the storage
              profile.

          description: A human-friendly description.

          disk_mode: Type of mode for the disk

          disk_type: Disk types are specified as

              Standard - Simple vSphere virtual disks which cannot be managed independently
              without an attached VM. First Class - Improved version of standard virtual
              disks, designed to be fully mananged independent storage objects.

              Empty value is considered as Standard

          limit_iops: The upper bound for the I/O operations per second allocated for each virtual
              disk.

          priority: Defines the priority of the storage profile with the highest priority being 0.
              Defaults to the value of 1.

          provisioning_type: Type of provisioning policy for the disk.

          shares: A specific number of shares assigned to each virtual machine.

          shares_level: Shares are specified as High, Normal, Low or Custom and these values specify
              share values with a 4:2:1 ratio, respectively.

          storage_filter_type: Defines filter type for adding storage objects (data stores) to the storage
              profile. Defaults to INCLUDE_ALL.

          storage_policy_id: Id of the vSphere Storage Policy to be applied.

          storage_profile_associations: Defines a specification of Storage Profile datastore associations.

          supports_encryption: Indicates whether this storage profile supports encryption or not.

          tags: A list of tags that represent the capabilities of this storage profile.

          tags_to_match: A set of tag keys and optional values to be set on data stores to be included in
              this storage profile based on the storageFilterType: TAG_BASED.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/storage-profiles-vsphere",
            body=maybe_transform(
                {
                    "default_item": default_item,
                    "name": name,
                    "region_id": region_id,
                    "compute_host_id": compute_host_id,
                    "datastore_id": datastore_id,
                    "description": description,
                    "disk_mode": disk_mode,
                    "disk_type": disk_type,
                    "limit_iops": limit_iops,
                    "priority": priority,
                    "provisioning_type": provisioning_type,
                    "shares": shares,
                    "shares_level": shares_level,
                    "storage_filter_type": storage_filter_type,
                    "storage_policy_id": storage_policy_id,
                    "storage_profile_associations": storage_profile_associations,
                    "supports_encryption": supports_encryption,
                    "tags": tags,
                    "tags_to_match": tags_to_match,
                },
                storage_profiles_vsphere_storage_profiles_vsphere_params.StorageProfilesVsphereStorageProfilesVsphereParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_vsphere_storage_profiles_vsphere_params.StorageProfilesVsphereStorageProfilesVsphereParams,
                ),
            ),
            cast_to=VsphereStorageProfile,
        )


class AsyncStorageProfilesVsphereResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncStorageProfilesVsphereResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncStorageProfilesVsphereResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStorageProfilesVsphereResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncStorageProfilesVsphereResourceWithStreamingResponse(self)

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
    ) -> VsphereStorageProfile:
        """
        Get vSphere storage profile with a given id

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
            f"/iaas/api/storage-profiles-vsphere/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_vsphere_retrieve_params.StorageProfilesVsphereRetrieveParams,
                ),
            ),
            cast_to=VsphereStorageProfile,
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
        datastore_id: str | Omit = omit,
        description: str | Omit = omit,
        disk_mode: str | Omit = omit,
        disk_type: str | Omit = omit,
        limit_iops: str | Omit = omit,
        priority: int | Omit = omit,
        provisioning_type: str | Omit = omit,
        shares: str | Omit = omit,
        shares_level: str | Omit = omit,
        storage_filter_type: Literal["INCLUDE_ALL", "TAG_BASED", "MANUAL"] | Omit = omit,
        storage_policy_id: str | Omit = omit,
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
    ) -> VsphereStorageProfile:
        """
        Update vSphere storage profile

        Args:
          default_item: Indicates if a storage profile acts as a default storage profile for a disk.

          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The Id of the region that is associated with the storage profile.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          compute_host_id: The compute host Id to be associated with the storage profile.

          datastore_id: Id of the vSphere Datastore for placing disk and VM. Deprecated, instead use
              'storageProfileAssociations' parameter to associate datastores with the storage
              profile.

          description: A human-friendly description.

          disk_mode: Type of mode for the disk

          disk_type: Disk types are specified as

              Standard - Simple vSphere virtual disks which cannot be managed independently
              without an attached VM. First Class - Improved version of standard virtual
              disks, designed to be fully mananged independent storage objects.

              Empty value is considered as Standard

          limit_iops: The upper bound for the I/O operations per second allocated for each virtual
              disk.

          priority: Defines the priority of the storage profile with the highest priority being 0.
              Defaults to the value of 1.

          provisioning_type: Type of provisioning policy for the disk.

          shares: A specific number of shares assigned to each virtual machine.

          shares_level: Shares are specified as High, Normal, Low or Custom and these values specify
              share values with a 4:2:1 ratio, respectively.

          storage_filter_type: Defines filter type for adding storage objects (data stores) to the storage
              profile. Defaults to INCLUDE_ALL.

          storage_policy_id: Id of the vSphere Storage Policy to be applied.

          storage_profile_associations: Defines a specification of Storage Profile datastore associations.

          supports_encryption: Indicates whether this storage profile supports encryption or not.

          tags: A list of tags that represent the capabilities of this storage profile.

          tags_to_match: A set of tag keys and optional values to be set on data stores to be included in
              this storage profile based on the storageFilterType: TAG_BASED.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/storage-profiles-vsphere/{id}",
            body=await async_maybe_transform(
                {
                    "default_item": default_item,
                    "name": name,
                    "region_id": region_id,
                    "compute_host_id": compute_host_id,
                    "datastore_id": datastore_id,
                    "description": description,
                    "disk_mode": disk_mode,
                    "disk_type": disk_type,
                    "limit_iops": limit_iops,
                    "priority": priority,
                    "provisioning_type": provisioning_type,
                    "shares": shares,
                    "shares_level": shares_level,
                    "storage_filter_type": storage_filter_type,
                    "storage_policy_id": storage_policy_id,
                    "storage_profile_associations": storage_profile_associations,
                    "supports_encryption": supports_encryption,
                    "tags": tags,
                    "tags_to_match": tags_to_match,
                },
                storage_profiles_vsphere_update_params.StorageProfilesVsphereUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_vsphere_update_params.StorageProfilesVsphereUpdateParams,
                ),
            ),
            cast_to=VsphereStorageProfile,
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
        Delete vSphere storage profile with a given id

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
            f"/iaas/api/storage-profiles-vsphere/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_vsphere_delete_params.StorageProfilesVsphereDeleteParams,
                ),
            ),
            cast_to=NoneType,
        )

    async def retrieve_storage_profiles_vsphere(
        self,
        *,
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageProfilesVsphereRetrieveStorageProfilesVsphereResponse:
        """
        Get all vSphere storage profiles

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/iaas/api/storage-profiles-vsphere",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_vsphere_retrieve_storage_profiles_vsphere_params.StorageProfilesVsphereRetrieveStorageProfilesVsphereParams,
                ),
            ),
            cast_to=StorageProfilesVsphereRetrieveStorageProfilesVsphereResponse,
        )

    async def storage_profiles_vsphere(
        self,
        *,
        default_item: bool,
        name: str,
        region_id: str,
        api_version: str | Omit = omit,
        compute_host_id: str | Omit = omit,
        datastore_id: str | Omit = omit,
        description: str | Omit = omit,
        disk_mode: str | Omit = omit,
        disk_type: str | Omit = omit,
        limit_iops: str | Omit = omit,
        priority: int | Omit = omit,
        provisioning_type: str | Omit = omit,
        shares: str | Omit = omit,
        shares_level: str | Omit = omit,
        storage_filter_type: Literal["INCLUDE_ALL", "TAG_BASED", "MANUAL"] | Omit = omit,
        storage_policy_id: str | Omit = omit,
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
    ) -> VsphereStorageProfile:
        """
        Create vSphere storage profile

        Args:
          default_item: Indicates if a storage profile acts as a default storage profile for a disk.

          name: A human-friendly name used as an identifier in APIs that support this option.

          region_id: The Id of the region that is associated with the storage profile.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          compute_host_id: The compute host Id to be associated with the storage profile.

          datastore_id: Id of the vSphere Datastore for placing disk and VM. Deprecated, instead use
              'storageProfileAssociations' parameter to associate datastores with the storage
              profile.

          description: A human-friendly description.

          disk_mode: Type of mode for the disk

          disk_type: Disk types are specified as

              Standard - Simple vSphere virtual disks which cannot be managed independently
              without an attached VM. First Class - Improved version of standard virtual
              disks, designed to be fully mananged independent storage objects.

              Empty value is considered as Standard

          limit_iops: The upper bound for the I/O operations per second allocated for each virtual
              disk.

          priority: Defines the priority of the storage profile with the highest priority being 0.
              Defaults to the value of 1.

          provisioning_type: Type of provisioning policy for the disk.

          shares: A specific number of shares assigned to each virtual machine.

          shares_level: Shares are specified as High, Normal, Low or Custom and these values specify
              share values with a 4:2:1 ratio, respectively.

          storage_filter_type: Defines filter type for adding storage objects (data stores) to the storage
              profile. Defaults to INCLUDE_ALL.

          storage_policy_id: Id of the vSphere Storage Policy to be applied.

          storage_profile_associations: Defines a specification of Storage Profile datastore associations.

          supports_encryption: Indicates whether this storage profile supports encryption or not.

          tags: A list of tags that represent the capabilities of this storage profile.

          tags_to_match: A set of tag keys and optional values to be set on data stores to be included in
              this storage profile based on the storageFilterType: TAG_BASED.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/storage-profiles-vsphere",
            body=await async_maybe_transform(
                {
                    "default_item": default_item,
                    "name": name,
                    "region_id": region_id,
                    "compute_host_id": compute_host_id,
                    "datastore_id": datastore_id,
                    "description": description,
                    "disk_mode": disk_mode,
                    "disk_type": disk_type,
                    "limit_iops": limit_iops,
                    "priority": priority,
                    "provisioning_type": provisioning_type,
                    "shares": shares,
                    "shares_level": shares_level,
                    "storage_filter_type": storage_filter_type,
                    "storage_policy_id": storage_policy_id,
                    "storage_profile_associations": storage_profile_associations,
                    "supports_encryption": supports_encryption,
                    "tags": tags,
                    "tags_to_match": tags_to_match,
                },
                storage_profiles_vsphere_storage_profiles_vsphere_params.StorageProfilesVsphereStorageProfilesVsphereParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    storage_profiles_vsphere_storage_profiles_vsphere_params.StorageProfilesVsphereStorageProfilesVsphereParams,
                ),
            ),
            cast_to=VsphereStorageProfile,
        )


class StorageProfilesVsphereResourceWithRawResponse:
    def __init__(self, storage_profiles_vsphere: StorageProfilesVsphereResource) -> None:
        self._storage_profiles_vsphere = storage_profiles_vsphere

        self.retrieve = to_raw_response_wrapper(
            storage_profiles_vsphere.retrieve,
        )
        self.update = to_raw_response_wrapper(
            storage_profiles_vsphere.update,
        )
        self.delete = to_raw_response_wrapper(
            storage_profiles_vsphere.delete,
        )
        self.retrieve_storage_profiles_vsphere = to_raw_response_wrapper(
            storage_profiles_vsphere.retrieve_storage_profiles_vsphere,
        )
        self.storage_profiles_vsphere = to_raw_response_wrapper(
            storage_profiles_vsphere.storage_profiles_vsphere,
        )


class AsyncStorageProfilesVsphereResourceWithRawResponse:
    def __init__(self, storage_profiles_vsphere: AsyncStorageProfilesVsphereResource) -> None:
        self._storage_profiles_vsphere = storage_profiles_vsphere

        self.retrieve = async_to_raw_response_wrapper(
            storage_profiles_vsphere.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            storage_profiles_vsphere.update,
        )
        self.delete = async_to_raw_response_wrapper(
            storage_profiles_vsphere.delete,
        )
        self.retrieve_storage_profiles_vsphere = async_to_raw_response_wrapper(
            storage_profiles_vsphere.retrieve_storage_profiles_vsphere,
        )
        self.storage_profiles_vsphere = async_to_raw_response_wrapper(
            storage_profiles_vsphere.storage_profiles_vsphere,
        )


class StorageProfilesVsphereResourceWithStreamingResponse:
    def __init__(self, storage_profiles_vsphere: StorageProfilesVsphereResource) -> None:
        self._storage_profiles_vsphere = storage_profiles_vsphere

        self.retrieve = to_streamed_response_wrapper(
            storage_profiles_vsphere.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            storage_profiles_vsphere.update,
        )
        self.delete = to_streamed_response_wrapper(
            storage_profiles_vsphere.delete,
        )
        self.retrieve_storage_profiles_vsphere = to_streamed_response_wrapper(
            storage_profiles_vsphere.retrieve_storage_profiles_vsphere,
        )
        self.storage_profiles_vsphere = to_streamed_response_wrapper(
            storage_profiles_vsphere.storage_profiles_vsphere,
        )


class AsyncStorageProfilesVsphereResourceWithStreamingResponse:
    def __init__(self, storage_profiles_vsphere: AsyncStorageProfilesVsphereResource) -> None:
        self._storage_profiles_vsphere = storage_profiles_vsphere

        self.retrieve = async_to_streamed_response_wrapper(
            storage_profiles_vsphere.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            storage_profiles_vsphere.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            storage_profiles_vsphere.delete,
        )
        self.retrieve_storage_profiles_vsphere = async_to_streamed_response_wrapper(
            storage_profiles_vsphere.retrieve_storage_profiles_vsphere,
        )
        self.storage_profiles_vsphere = async_to_streamed_response_wrapper(
            storage_profiles_vsphere.storage_profiles_vsphere,
        )
