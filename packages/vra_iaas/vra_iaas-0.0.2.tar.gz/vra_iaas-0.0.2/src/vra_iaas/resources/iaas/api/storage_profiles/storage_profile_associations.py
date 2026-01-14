# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
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
from .....types.iaas.api.storage_profiles import (
    storage_profile_association_update_storage_profile_associations_params,
    storage_profile_association_retrieve_storage_profile_associations_params,
)
from .....types.iaas.api.storage_profile_associations_param import StorageProfileAssociationsParam
from .....types.iaas.api.storage_profiles.storage_profile_association_update_storage_profile_associations_response import (
    StorageProfileAssociationUpdateStorageProfileAssociationsResponse,
)
from .....types.iaas.api.storage_profiles.storage_profile_association_retrieve_storage_profile_associations_response import (
    StorageProfileAssociationRetrieveStorageProfileAssociationsResponse,
)

__all__ = ["StorageProfileAssociationsResource", "AsyncStorageProfileAssociationsResource"]


class StorageProfileAssociationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> StorageProfileAssociationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return StorageProfileAssociationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StorageProfileAssociationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return StorageProfileAssociationsResourceWithStreamingResponse(self)

    def retrieve_storage_profile_associations(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        page: int | Omit = omit,
        size: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageProfileAssociationRetrieveStorageProfileAssociationsResponse:
        """
        Get all storage profile Associations with a given storage profile id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          page: Results page you want to retrieve (0..N)

          size: Number of records per page.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/iaas/api/storage-profiles/{id}/storage-profile-associations",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_version": api_version,
                        "page": page,
                        "size": size,
                    },
                    storage_profile_association_retrieve_storage_profile_associations_params.StorageProfileAssociationRetrieveStorageProfileAssociationsParams,
                ),
            ),
            cast_to=StorageProfileAssociationRetrieveStorageProfileAssociationsResponse,
        )

    def update_storage_profile_associations(
        self,
        id: str,
        *,
        region_id: str,
        storage_profile_associations: Iterable[StorageProfileAssociationsParam],
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageProfileAssociationUpdateStorageProfileAssociationsResponse:
        """
        Update storage profile associations

        Args:
          region_id: The Id of the region that is associated with the storage profile.

          storage_profile_associations: Defines a specification of Storage Profile datastore associations.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/storage-profiles/{id}/storage-profile-associations",
            body=maybe_transform(
                {
                    "region_id": region_id,
                    "storage_profile_associations": storage_profile_associations,
                },
                storage_profile_association_update_storage_profile_associations_params.StorageProfileAssociationUpdateStorageProfileAssociationsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    storage_profile_association_update_storage_profile_associations_params.StorageProfileAssociationUpdateStorageProfileAssociationsParams,
                ),
            ),
            cast_to=StorageProfileAssociationUpdateStorageProfileAssociationsResponse,
        )


class AsyncStorageProfileAssociationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncStorageProfileAssociationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncStorageProfileAssociationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStorageProfileAssociationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncStorageProfileAssociationsResourceWithStreamingResponse(self)

    async def retrieve_storage_profile_associations(
        self,
        id: str,
        *,
        api_version: str | Omit = omit,
        page: int | Omit = omit,
        size: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageProfileAssociationRetrieveStorageProfileAssociationsResponse:
        """
        Get all storage profile Associations with a given storage profile id

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          page: Results page you want to retrieve (0..N)

          size: Number of records per page.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/iaas/api/storage-profiles/{id}/storage-profile-associations",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_version": api_version,
                        "page": page,
                        "size": size,
                    },
                    storage_profile_association_retrieve_storage_profile_associations_params.StorageProfileAssociationRetrieveStorageProfileAssociationsParams,
                ),
            ),
            cast_to=StorageProfileAssociationRetrieveStorageProfileAssociationsResponse,
        )

    async def update_storage_profile_associations(
        self,
        id: str,
        *,
        region_id: str,
        storage_profile_associations: Iterable[StorageProfileAssociationsParam],
        api_version: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StorageProfileAssociationUpdateStorageProfileAssociationsResponse:
        """
        Update storage profile associations

        Args:
          region_id: The Id of the region that is associated with the storage profile.

          storage_profile_associations: Defines a specification of Storage Profile datastore associations.

          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/storage-profiles/{id}/storage-profile-associations",
            body=await async_maybe_transform(
                {
                    "region_id": region_id,
                    "storage_profile_associations": storage_profile_associations,
                },
                storage_profile_association_update_storage_profile_associations_params.StorageProfileAssociationUpdateStorageProfileAssociationsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    storage_profile_association_update_storage_profile_associations_params.StorageProfileAssociationUpdateStorageProfileAssociationsParams,
                ),
            ),
            cast_to=StorageProfileAssociationUpdateStorageProfileAssociationsResponse,
        )


class StorageProfileAssociationsResourceWithRawResponse:
    def __init__(self, storage_profile_associations: StorageProfileAssociationsResource) -> None:
        self._storage_profile_associations = storage_profile_associations

        self.retrieve_storage_profile_associations = to_raw_response_wrapper(
            storage_profile_associations.retrieve_storage_profile_associations,
        )
        self.update_storage_profile_associations = to_raw_response_wrapper(
            storage_profile_associations.update_storage_profile_associations,
        )


class AsyncStorageProfileAssociationsResourceWithRawResponse:
    def __init__(self, storage_profile_associations: AsyncStorageProfileAssociationsResource) -> None:
        self._storage_profile_associations = storage_profile_associations

        self.retrieve_storage_profile_associations = async_to_raw_response_wrapper(
            storage_profile_associations.retrieve_storage_profile_associations,
        )
        self.update_storage_profile_associations = async_to_raw_response_wrapper(
            storage_profile_associations.update_storage_profile_associations,
        )


class StorageProfileAssociationsResourceWithStreamingResponse:
    def __init__(self, storage_profile_associations: StorageProfileAssociationsResource) -> None:
        self._storage_profile_associations = storage_profile_associations

        self.retrieve_storage_profile_associations = to_streamed_response_wrapper(
            storage_profile_associations.retrieve_storage_profile_associations,
        )
        self.update_storage_profile_associations = to_streamed_response_wrapper(
            storage_profile_associations.update_storage_profile_associations,
        )


class AsyncStorageProfileAssociationsResourceWithStreamingResponse:
    def __init__(self, storage_profile_associations: AsyncStorageProfileAssociationsResource) -> None:
        self._storage_profile_associations = storage_profile_associations

        self.retrieve_storage_profile_associations = async_to_streamed_response_wrapper(
            storage_profile_associations.retrieve_storage_profile_associations,
        )
        self.update_storage_profile_associations = async_to_streamed_response_wrapper(
            storage_profile_associations.update_storage_profile_associations,
        )
