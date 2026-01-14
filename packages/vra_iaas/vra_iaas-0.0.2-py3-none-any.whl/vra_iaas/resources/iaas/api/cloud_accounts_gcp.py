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
    cloud_accounts_gcp_delete_params,
    cloud_accounts_gcp_update_params,
    cloud_accounts_gcp_retrieve_params,
    cloud_accounts_gcp_cloud_accounts_gcp_params,
    cloud_accounts_gcp_region_enumeration_params,
    cloud_accounts_gcp_private_image_enumeration_params,
    cloud_accounts_gcp_retrieve_cloud_accounts_gcp_params,
)
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.cloud_account_gcp import CloudAccountGcp
from ....types.iaas.api.projects.request_tracker import RequestTracker
from ....types.iaas.api.region_specification_param import RegionSpecificationParam
from ....types.iaas.api.cloud_accounts_gcp_retrieve_cloud_accounts_gcp_response import (
    CloudAccountsGcpRetrieveCloudAccountsGcpResponse,
)

__all__ = ["CloudAccountsGcpResource", "AsyncCloudAccountsGcpResource"]


class CloudAccountsGcpResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CloudAccountsGcpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return CloudAccountsGcpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CloudAccountsGcpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return CloudAccountsGcpResourceWithStreamingResponse(self)

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
    ) -> CloudAccountGcp:
        """
        Get an GCP cloud account with a given id

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
            f"/iaas/api/cloud-accounts-gcp/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_gcp_retrieve_params.CloudAccountsGcpRetrieveParams
                ),
            ),
            cast_to=CloudAccountGcp,
        )

    def update(
        self,
        id: str,
        *,
        api_version: str,
        client_email: str,
        name: str,
        private_key: str,
        private_key_id: str,
        project_id: str,
        regions: Iterable[RegionSpecificationParam],
        create_default_zones: bool | Omit = omit,
        description: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Update GCP cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          client_email: GCP Client email

          name: A human-friendly name used as an identifier in APIs that support this option.

          private_key: GCP Private key

          private_key_id: GCP Private key ID

          project_id: GCP Project ID

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          create_default_zones: Create default cloud zones for the enabled regions.

          description: A human-friendly description.

          tags: A set of tag keys and optional values to set on the Cloud Account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/cloud-accounts-gcp/{id}",
            body=maybe_transform(
                {
                    "client_email": client_email,
                    "name": name,
                    "private_key": private_key,
                    "private_key_id": private_key_id,
                    "project_id": project_id,
                    "regions": regions,
                    "create_default_zones": create_default_zones,
                    "description": description,
                    "tags": tags,
                },
                cloud_accounts_gcp_update_params.CloudAccountsGcpUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_gcp_update_params.CloudAccountsGcpUpdateParams
                ),
            ),
            cast_to=RequestTracker,
        )

    def delete(
        self,
        id: str,
        *,
        api_version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Delete an GCP cloud account with a given id

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
        return self._delete(
            f"/iaas/api/cloud-accounts-gcp/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_gcp_delete_params.CloudAccountsGcpDeleteParams
                ),
            ),
            cast_to=RequestTracker,
        )

    def cloud_accounts_gcp(
        self,
        *,
        api_version: str,
        client_email: str,
        name: str,
        private_key: str,
        private_key_id: str,
        project_id: str,
        regions: Iterable[RegionSpecificationParam],
        validate_only: str | Omit = omit,
        create_default_zones: bool | Omit = omit,
        description: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Create a cloud account in the current organization

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          client_email: GCP Client email

          name: A human-friendly name used as an identifier in APIs that support this option.

          private_key: GCP Private key

          private_key_id: GCP Private key ID

          project_id: GCP Project ID

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          validate_only: If provided, it only validates the credentials in the Cloud Account
              Specification, and cloud account will not be created.

          create_default_zones: Create default cloud zones for the enabled regions.

          description: A human-friendly description.

          tags: A set of tag keys and optional values to set on the Cloud Account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/cloud-accounts-gcp",
            body=maybe_transform(
                {
                    "client_email": client_email,
                    "name": name,
                    "private_key": private_key,
                    "private_key_id": private_key_id,
                    "project_id": project_id,
                    "regions": regions,
                    "create_default_zones": create_default_zones,
                    "description": description,
                    "tags": tags,
                },
                cloud_accounts_gcp_cloud_accounts_gcp_params.CloudAccountsGcpCloudAccountsGcpParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "api_version": api_version,
                        "validate_only": validate_only,
                    },
                    cloud_accounts_gcp_cloud_accounts_gcp_params.CloudAccountsGcpCloudAccountsGcpParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def private_image_enumeration(
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
    ) -> RequestTracker:
        """
        Enumerate all private images for enabled regions of the specified GCP account

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
        return self._post(
            f"/iaas/api/cloud-accounts-gcp/{id}/private-image-enumeration",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_gcp_private_image_enumeration_params.CloudAccountsGcpPrivateImageEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def region_enumeration(
        self,
        *,
        api_version: str,
        client_email: str | Omit = omit,
        cloud_account_id: str | Omit = omit,
        private_key: str | Omit = omit,
        private_key_id: str | Omit = omit,
        project_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Get the available regions for specified GCP cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          client_email: GCP Client email. Either provide clientEmail or provide a cloudAccountId of an
              existing account.

          cloud_account_id: Existing cloud account id. Either provide id of existing account, or cloud
              account credentials: projectId, privateKeyId, privateKey and clientEmail.

          private_key: GCP Private key. Either provide privateKey or provide a cloudAccountId of an
              existing account.

          private_key_id: GCP Private key ID. Either provide privateKeyId or provide a cloudAccountId of
              an existing account.

          project_id: GCP Project ID. Either provide projectId or provide a cloudAccountId of an
              existing account.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/cloud-accounts-gcp/region-enumeration",
            body=maybe_transform(
                {
                    "client_email": client_email,
                    "cloud_account_id": cloud_account_id,
                    "private_key": private_key,
                    "private_key_id": private_key_id,
                    "project_id": project_id,
                },
                cloud_accounts_gcp_region_enumeration_params.CloudAccountsGcpRegionEnumerationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_gcp_region_enumeration_params.CloudAccountsGcpRegionEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def retrieve_cloud_accounts_gcp(
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
    ) -> CloudAccountsGcpRetrieveCloudAccountsGcpResponse:
        """
        Get all GCP cloud accounts within the current organization

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
            "/iaas/api/cloud-accounts-gcp",
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
                    cloud_accounts_gcp_retrieve_cloud_accounts_gcp_params.CloudAccountsGcpRetrieveCloudAccountsGcpParams,
                ),
            ),
            cast_to=CloudAccountsGcpRetrieveCloudAccountsGcpResponse,
        )


class AsyncCloudAccountsGcpResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCloudAccountsGcpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCloudAccountsGcpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCloudAccountsGcpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncCloudAccountsGcpResourceWithStreamingResponse(self)

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
    ) -> CloudAccountGcp:
        """
        Get an GCP cloud account with a given id

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
            f"/iaas/api/cloud-accounts-gcp/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_gcp_retrieve_params.CloudAccountsGcpRetrieveParams
                ),
            ),
            cast_to=CloudAccountGcp,
        )

    async def update(
        self,
        id: str,
        *,
        api_version: str,
        client_email: str,
        name: str,
        private_key: str,
        private_key_id: str,
        project_id: str,
        regions: Iterable[RegionSpecificationParam],
        create_default_zones: bool | Omit = omit,
        description: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Update GCP cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          client_email: GCP Client email

          name: A human-friendly name used as an identifier in APIs that support this option.

          private_key: GCP Private key

          private_key_id: GCP Private key ID

          project_id: GCP Project ID

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          create_default_zones: Create default cloud zones for the enabled regions.

          description: A human-friendly description.

          tags: A set of tag keys and optional values to set on the Cloud Account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/cloud-accounts-gcp/{id}",
            body=await async_maybe_transform(
                {
                    "client_email": client_email,
                    "name": name,
                    "private_key": private_key,
                    "private_key_id": private_key_id,
                    "project_id": project_id,
                    "regions": regions,
                    "create_default_zones": create_default_zones,
                    "description": description,
                    "tags": tags,
                },
                cloud_accounts_gcp_update_params.CloudAccountsGcpUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_gcp_update_params.CloudAccountsGcpUpdateParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def delete(
        self,
        id: str,
        *,
        api_version: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Delete an GCP cloud account with a given id

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
        return await self._delete(
            f"/iaas/api/cloud-accounts-gcp/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_gcp_delete_params.CloudAccountsGcpDeleteParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def cloud_accounts_gcp(
        self,
        *,
        api_version: str,
        client_email: str,
        name: str,
        private_key: str,
        private_key_id: str,
        project_id: str,
        regions: Iterable[RegionSpecificationParam],
        validate_only: str | Omit = omit,
        create_default_zones: bool | Omit = omit,
        description: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Create a cloud account in the current organization

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          client_email: GCP Client email

          name: A human-friendly name used as an identifier in APIs that support this option.

          private_key: GCP Private key

          private_key_id: GCP Private key ID

          project_id: GCP Project ID

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          validate_only: If provided, it only validates the credentials in the Cloud Account
              Specification, and cloud account will not be created.

          create_default_zones: Create default cloud zones for the enabled regions.

          description: A human-friendly description.

          tags: A set of tag keys and optional values to set on the Cloud Account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/cloud-accounts-gcp",
            body=await async_maybe_transform(
                {
                    "client_email": client_email,
                    "name": name,
                    "private_key": private_key,
                    "private_key_id": private_key_id,
                    "project_id": project_id,
                    "regions": regions,
                    "create_default_zones": create_default_zones,
                    "description": description,
                    "tags": tags,
                },
                cloud_accounts_gcp_cloud_accounts_gcp_params.CloudAccountsGcpCloudAccountsGcpParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "api_version": api_version,
                        "validate_only": validate_only,
                    },
                    cloud_accounts_gcp_cloud_accounts_gcp_params.CloudAccountsGcpCloudAccountsGcpParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def private_image_enumeration(
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
    ) -> RequestTracker:
        """
        Enumerate all private images for enabled regions of the specified GCP account

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
        return await self._post(
            f"/iaas/api/cloud-accounts-gcp/{id}/private-image-enumeration",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_gcp_private_image_enumeration_params.CloudAccountsGcpPrivateImageEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def region_enumeration(
        self,
        *,
        api_version: str,
        client_email: str | Omit = omit,
        cloud_account_id: str | Omit = omit,
        private_key: str | Omit = omit,
        private_key_id: str | Omit = omit,
        project_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Get the available regions for specified GCP cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          client_email: GCP Client email. Either provide clientEmail or provide a cloudAccountId of an
              existing account.

          cloud_account_id: Existing cloud account id. Either provide id of existing account, or cloud
              account credentials: projectId, privateKeyId, privateKey and clientEmail.

          private_key: GCP Private key. Either provide privateKey or provide a cloudAccountId of an
              existing account.

          private_key_id: GCP Private key ID. Either provide privateKeyId or provide a cloudAccountId of
              an existing account.

          project_id: GCP Project ID. Either provide projectId or provide a cloudAccountId of an
              existing account.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/cloud-accounts-gcp/region-enumeration",
            body=await async_maybe_transform(
                {
                    "client_email": client_email,
                    "cloud_account_id": cloud_account_id,
                    "private_key": private_key,
                    "private_key_id": private_key_id,
                    "project_id": project_id,
                },
                cloud_accounts_gcp_region_enumeration_params.CloudAccountsGcpRegionEnumerationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_gcp_region_enumeration_params.CloudAccountsGcpRegionEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def retrieve_cloud_accounts_gcp(
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
    ) -> CloudAccountsGcpRetrieveCloudAccountsGcpResponse:
        """
        Get all GCP cloud accounts within the current organization

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
            "/iaas/api/cloud-accounts-gcp",
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
                    cloud_accounts_gcp_retrieve_cloud_accounts_gcp_params.CloudAccountsGcpRetrieveCloudAccountsGcpParams,
                ),
            ),
            cast_to=CloudAccountsGcpRetrieveCloudAccountsGcpResponse,
        )


class CloudAccountsGcpResourceWithRawResponse:
    def __init__(self, cloud_accounts_gcp: CloudAccountsGcpResource) -> None:
        self._cloud_accounts_gcp = cloud_accounts_gcp

        self.retrieve = to_raw_response_wrapper(
            cloud_accounts_gcp.retrieve,
        )
        self.update = to_raw_response_wrapper(
            cloud_accounts_gcp.update,
        )
        self.delete = to_raw_response_wrapper(
            cloud_accounts_gcp.delete,
        )
        self.cloud_accounts_gcp = to_raw_response_wrapper(
            cloud_accounts_gcp.cloud_accounts_gcp,
        )
        self.private_image_enumeration = to_raw_response_wrapper(
            cloud_accounts_gcp.private_image_enumeration,
        )
        self.region_enumeration = to_raw_response_wrapper(
            cloud_accounts_gcp.region_enumeration,
        )
        self.retrieve_cloud_accounts_gcp = to_raw_response_wrapper(
            cloud_accounts_gcp.retrieve_cloud_accounts_gcp,
        )


class AsyncCloudAccountsGcpResourceWithRawResponse:
    def __init__(self, cloud_accounts_gcp: AsyncCloudAccountsGcpResource) -> None:
        self._cloud_accounts_gcp = cloud_accounts_gcp

        self.retrieve = async_to_raw_response_wrapper(
            cloud_accounts_gcp.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            cloud_accounts_gcp.update,
        )
        self.delete = async_to_raw_response_wrapper(
            cloud_accounts_gcp.delete,
        )
        self.cloud_accounts_gcp = async_to_raw_response_wrapper(
            cloud_accounts_gcp.cloud_accounts_gcp,
        )
        self.private_image_enumeration = async_to_raw_response_wrapper(
            cloud_accounts_gcp.private_image_enumeration,
        )
        self.region_enumeration = async_to_raw_response_wrapper(
            cloud_accounts_gcp.region_enumeration,
        )
        self.retrieve_cloud_accounts_gcp = async_to_raw_response_wrapper(
            cloud_accounts_gcp.retrieve_cloud_accounts_gcp,
        )


class CloudAccountsGcpResourceWithStreamingResponse:
    def __init__(self, cloud_accounts_gcp: CloudAccountsGcpResource) -> None:
        self._cloud_accounts_gcp = cloud_accounts_gcp

        self.retrieve = to_streamed_response_wrapper(
            cloud_accounts_gcp.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            cloud_accounts_gcp.update,
        )
        self.delete = to_streamed_response_wrapper(
            cloud_accounts_gcp.delete,
        )
        self.cloud_accounts_gcp = to_streamed_response_wrapper(
            cloud_accounts_gcp.cloud_accounts_gcp,
        )
        self.private_image_enumeration = to_streamed_response_wrapper(
            cloud_accounts_gcp.private_image_enumeration,
        )
        self.region_enumeration = to_streamed_response_wrapper(
            cloud_accounts_gcp.region_enumeration,
        )
        self.retrieve_cloud_accounts_gcp = to_streamed_response_wrapper(
            cloud_accounts_gcp.retrieve_cloud_accounts_gcp,
        )


class AsyncCloudAccountsGcpResourceWithStreamingResponse:
    def __init__(self, cloud_accounts_gcp: AsyncCloudAccountsGcpResource) -> None:
        self._cloud_accounts_gcp = cloud_accounts_gcp

        self.retrieve = async_to_streamed_response_wrapper(
            cloud_accounts_gcp.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            cloud_accounts_gcp.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            cloud_accounts_gcp.delete,
        )
        self.cloud_accounts_gcp = async_to_streamed_response_wrapper(
            cloud_accounts_gcp.cloud_accounts_gcp,
        )
        self.private_image_enumeration = async_to_streamed_response_wrapper(
            cloud_accounts_gcp.private_image_enumeration,
        )
        self.region_enumeration = async_to_streamed_response_wrapper(
            cloud_accounts_gcp.region_enumeration,
        )
        self.retrieve_cloud_accounts_gcp = async_to_streamed_response_wrapper(
            cloud_accounts_gcp.retrieve_cloud_accounts_gcp,
        )
