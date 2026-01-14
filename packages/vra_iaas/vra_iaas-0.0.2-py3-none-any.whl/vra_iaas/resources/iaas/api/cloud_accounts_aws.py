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
    cloud_accounts_aw_delete_params,
    cloud_accounts_aw_update_params,
    cloud_accounts_aw_retrieve_params,
    cloud_accounts_aw_cloud_accounts_aws_params,
    cloud_accounts_aw_region_enumeration_params,
    cloud_accounts_aw_private_image_enumeration_params,
    cloud_accounts_aw_retrieve_cloud_accounts_aws_params,
)
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.cloud_account_aws import CloudAccountAws
from ....types.iaas.api.projects.request_tracker import RequestTracker
from ....types.iaas.api.region_specification_param import RegionSpecificationParam
from ....types.iaas.api.cloud_accounts_aw_retrieve_cloud_accounts_aws_response import (
    CloudAccountsAwRetrieveCloudAccountsAwsResponse,
)

__all__ = ["CloudAccountsAwsResource", "AsyncCloudAccountsAwsResource"]


class CloudAccountsAwsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CloudAccountsAwsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return CloudAccountsAwsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CloudAccountsAwsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return CloudAccountsAwsResourceWithStreamingResponse(self)

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
    ) -> CloudAccountAws:
        """
        Get an AWS cloud account with a given id

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
            f"/iaas/api/cloud-accounts-aws/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_aw_retrieve_params.CloudAccountsAwRetrieveParams
                ),
            ),
            cast_to=CloudAccountAws,
        )

    def update(
        self,
        id: str,
        *,
        api_version: str,
        name: str,
        access_key_id: str | Omit = omit,
        create_default_zones: bool | Omit = omit,
        description: str | Omit = omit,
        iam_role_arn: str | Omit = omit,
        regions: Iterable[RegionSpecificationParam] | Omit = omit,
        secret_access_key: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        trusted_account: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Update AWS cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          name: A human-friendly name used as an identifier in APIs that support this option.

          access_key_id: Aws Access key ID

          create_default_zones: Create default cloud zones for the enabled regions.

          description: A human-friendly description.

          iam_role_arn: Aws ARN role to be assumed by Aria Auto account

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          secret_access_key: Aws Secret Access Key

          tags: A set of tag keys and optional values to set on the Cloud Account

          trusted_account: Create the account as trusted.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/cloud-accounts-aws/{id}",
            body=maybe_transform(
                {
                    "name": name,
                    "access_key_id": access_key_id,
                    "create_default_zones": create_default_zones,
                    "description": description,
                    "iam_role_arn": iam_role_arn,
                    "regions": regions,
                    "secret_access_key": secret_access_key,
                    "tags": tags,
                    "trusted_account": trusted_account,
                },
                cloud_accounts_aw_update_params.CloudAccountsAwUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_aw_update_params.CloudAccountsAwUpdateParams
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
        Delete an AWS cloud account with a given id

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
            f"/iaas/api/cloud-accounts-aws/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_aw_delete_params.CloudAccountsAwDeleteParams
                ),
            ),
            cast_to=RequestTracker,
        )

    def cloud_accounts_aws(
        self,
        *,
        api_version: str,
        name: str,
        validate_only: str | Omit = omit,
        access_key_id: str | Omit = omit,
        create_default_zones: bool | Omit = omit,
        description: str | Omit = omit,
        iam_role_arn: str | Omit = omit,
        regions: Iterable[RegionSpecificationParam] | Omit = omit,
        secret_access_key: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        trusted_account: bool | Omit = omit,
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

          name: A human-friendly name used as an identifier in APIs that support this option.

          validate_only: If provided, it only validates the credentials in the Cloud Account
              Specification, and cloud account will not be created.

          access_key_id: Aws Access key ID

          create_default_zones: Create default cloud zones for the enabled regions.

          description: A human-friendly description.

          iam_role_arn: Aws ARN role to be assumed by Aria Auto account

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          secret_access_key: Aws Secret Access Key

          tags: A set of tag keys and optional values to set on the Cloud Account

          trusted_account: Create the account as trusted.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/cloud-accounts-aws",
            body=maybe_transform(
                {
                    "name": name,
                    "access_key_id": access_key_id,
                    "create_default_zones": create_default_zones,
                    "description": description,
                    "iam_role_arn": iam_role_arn,
                    "regions": regions,
                    "secret_access_key": secret_access_key,
                    "tags": tags,
                    "trusted_account": trusted_account,
                },
                cloud_accounts_aw_cloud_accounts_aws_params.CloudAccountsAwCloudAccountsAwsParams,
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
                    cloud_accounts_aw_cloud_accounts_aws_params.CloudAccountsAwCloudAccountsAwsParams,
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
        Enumerate all private images for enabled regions of the specified AWS account

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
            f"/iaas/api/cloud-accounts-aws/{id}/private-image-enumeration",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_aw_private_image_enumeration_params.CloudAccountsAwPrivateImageEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def region_enumeration(
        self,
        *,
        api_version: str,
        access_key_id: str | Omit = omit,
        cloud_account_id: str | Omit = omit,
        secret_access_key: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Get the available regions for specified AWS cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          access_key_id: Aws Access key ID. Either provide accessKeyId or provide a cloudAccountId of an
              existing account.

          cloud_account_id: Existing cloud account id. Either provide existing cloud account id, or
              accessKeyId/secretAccessKey credentials pair.

          secret_access_key: Aws Secret Access Key. Either provide secretAccessKey or provide a
              cloudAccountId of an existing account.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/cloud-accounts-aws/region-enumeration",
            body=maybe_transform(
                {
                    "access_key_id": access_key_id,
                    "cloud_account_id": cloud_account_id,
                    "secret_access_key": secret_access_key,
                },
                cloud_accounts_aw_region_enumeration_params.CloudAccountsAwRegionEnumerationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_aw_region_enumeration_params.CloudAccountsAwRegionEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def retrieve_cloud_accounts_aws(
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
    ) -> CloudAccountsAwRetrieveCloudAccountsAwsResponse:
        """
        Get all AWS cloud accounts within the current organization

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
            "/iaas/api/cloud-accounts-aws",
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
                    cloud_accounts_aw_retrieve_cloud_accounts_aws_params.CloudAccountsAwRetrieveCloudAccountsAwsParams,
                ),
            ),
            cast_to=CloudAccountsAwRetrieveCloudAccountsAwsResponse,
        )


class AsyncCloudAccountsAwsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCloudAccountsAwsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCloudAccountsAwsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCloudAccountsAwsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncCloudAccountsAwsResourceWithStreamingResponse(self)

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
    ) -> CloudAccountAws:
        """
        Get an AWS cloud account with a given id

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
            f"/iaas/api/cloud-accounts-aws/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_aw_retrieve_params.CloudAccountsAwRetrieveParams
                ),
            ),
            cast_to=CloudAccountAws,
        )

    async def update(
        self,
        id: str,
        *,
        api_version: str,
        name: str,
        access_key_id: str | Omit = omit,
        create_default_zones: bool | Omit = omit,
        description: str | Omit = omit,
        iam_role_arn: str | Omit = omit,
        regions: Iterable[RegionSpecificationParam] | Omit = omit,
        secret_access_key: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        trusted_account: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Update AWS cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          name: A human-friendly name used as an identifier in APIs that support this option.

          access_key_id: Aws Access key ID

          create_default_zones: Create default cloud zones for the enabled regions.

          description: A human-friendly description.

          iam_role_arn: Aws ARN role to be assumed by Aria Auto account

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          secret_access_key: Aws Secret Access Key

          tags: A set of tag keys and optional values to set on the Cloud Account

          trusted_account: Create the account as trusted.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/cloud-accounts-aws/{id}",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "access_key_id": access_key_id,
                    "create_default_zones": create_default_zones,
                    "description": description,
                    "iam_role_arn": iam_role_arn,
                    "regions": regions,
                    "secret_access_key": secret_access_key,
                    "tags": tags,
                    "trusted_account": trusted_account,
                },
                cloud_accounts_aw_update_params.CloudAccountsAwUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_aw_update_params.CloudAccountsAwUpdateParams
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
        Delete an AWS cloud account with a given id

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
            f"/iaas/api/cloud-accounts-aws/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_aw_delete_params.CloudAccountsAwDeleteParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def cloud_accounts_aws(
        self,
        *,
        api_version: str,
        name: str,
        validate_only: str | Omit = omit,
        access_key_id: str | Omit = omit,
        create_default_zones: bool | Omit = omit,
        description: str | Omit = omit,
        iam_role_arn: str | Omit = omit,
        regions: Iterable[RegionSpecificationParam] | Omit = omit,
        secret_access_key: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        trusted_account: bool | Omit = omit,
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

          name: A human-friendly name used as an identifier in APIs that support this option.

          validate_only: If provided, it only validates the credentials in the Cloud Account
              Specification, and cloud account will not be created.

          access_key_id: Aws Access key ID

          create_default_zones: Create default cloud zones for the enabled regions.

          description: A human-friendly description.

          iam_role_arn: Aws ARN role to be assumed by Aria Auto account

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          secret_access_key: Aws Secret Access Key

          tags: A set of tag keys and optional values to set on the Cloud Account

          trusted_account: Create the account as trusted.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/cloud-accounts-aws",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "access_key_id": access_key_id,
                    "create_default_zones": create_default_zones,
                    "description": description,
                    "iam_role_arn": iam_role_arn,
                    "regions": regions,
                    "secret_access_key": secret_access_key,
                    "tags": tags,
                    "trusted_account": trusted_account,
                },
                cloud_accounts_aw_cloud_accounts_aws_params.CloudAccountsAwCloudAccountsAwsParams,
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
                    cloud_accounts_aw_cloud_accounts_aws_params.CloudAccountsAwCloudAccountsAwsParams,
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
        Enumerate all private images for enabled regions of the specified AWS account

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
            f"/iaas/api/cloud-accounts-aws/{id}/private-image-enumeration",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_aw_private_image_enumeration_params.CloudAccountsAwPrivateImageEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def region_enumeration(
        self,
        *,
        api_version: str,
        access_key_id: str | Omit = omit,
        cloud_account_id: str | Omit = omit,
        secret_access_key: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Get the available regions for specified AWS cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          access_key_id: Aws Access key ID. Either provide accessKeyId or provide a cloudAccountId of an
              existing account.

          cloud_account_id: Existing cloud account id. Either provide existing cloud account id, or
              accessKeyId/secretAccessKey credentials pair.

          secret_access_key: Aws Secret Access Key. Either provide secretAccessKey or provide a
              cloudAccountId of an existing account.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/cloud-accounts-aws/region-enumeration",
            body=await async_maybe_transform(
                {
                    "access_key_id": access_key_id,
                    "cloud_account_id": cloud_account_id,
                    "secret_access_key": secret_access_key,
                },
                cloud_accounts_aw_region_enumeration_params.CloudAccountsAwRegionEnumerationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_aw_region_enumeration_params.CloudAccountsAwRegionEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def retrieve_cloud_accounts_aws(
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
    ) -> CloudAccountsAwRetrieveCloudAccountsAwsResponse:
        """
        Get all AWS cloud accounts within the current organization

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
            "/iaas/api/cloud-accounts-aws",
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
                    cloud_accounts_aw_retrieve_cloud_accounts_aws_params.CloudAccountsAwRetrieveCloudAccountsAwsParams,
                ),
            ),
            cast_to=CloudAccountsAwRetrieveCloudAccountsAwsResponse,
        )


class CloudAccountsAwsResourceWithRawResponse:
    def __init__(self, cloud_accounts_aws: CloudAccountsAwsResource) -> None:
        self._cloud_accounts_aws = cloud_accounts_aws

        self.retrieve = to_raw_response_wrapper(
            cloud_accounts_aws.retrieve,
        )
        self.update = to_raw_response_wrapper(
            cloud_accounts_aws.update,
        )
        self.delete = to_raw_response_wrapper(
            cloud_accounts_aws.delete,
        )
        self.cloud_accounts_aws = to_raw_response_wrapper(
            cloud_accounts_aws.cloud_accounts_aws,
        )
        self.private_image_enumeration = to_raw_response_wrapper(
            cloud_accounts_aws.private_image_enumeration,
        )
        self.region_enumeration = to_raw_response_wrapper(
            cloud_accounts_aws.region_enumeration,
        )
        self.retrieve_cloud_accounts_aws = to_raw_response_wrapper(
            cloud_accounts_aws.retrieve_cloud_accounts_aws,
        )


class AsyncCloudAccountsAwsResourceWithRawResponse:
    def __init__(self, cloud_accounts_aws: AsyncCloudAccountsAwsResource) -> None:
        self._cloud_accounts_aws = cloud_accounts_aws

        self.retrieve = async_to_raw_response_wrapper(
            cloud_accounts_aws.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            cloud_accounts_aws.update,
        )
        self.delete = async_to_raw_response_wrapper(
            cloud_accounts_aws.delete,
        )
        self.cloud_accounts_aws = async_to_raw_response_wrapper(
            cloud_accounts_aws.cloud_accounts_aws,
        )
        self.private_image_enumeration = async_to_raw_response_wrapper(
            cloud_accounts_aws.private_image_enumeration,
        )
        self.region_enumeration = async_to_raw_response_wrapper(
            cloud_accounts_aws.region_enumeration,
        )
        self.retrieve_cloud_accounts_aws = async_to_raw_response_wrapper(
            cloud_accounts_aws.retrieve_cloud_accounts_aws,
        )


class CloudAccountsAwsResourceWithStreamingResponse:
    def __init__(self, cloud_accounts_aws: CloudAccountsAwsResource) -> None:
        self._cloud_accounts_aws = cloud_accounts_aws

        self.retrieve = to_streamed_response_wrapper(
            cloud_accounts_aws.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            cloud_accounts_aws.update,
        )
        self.delete = to_streamed_response_wrapper(
            cloud_accounts_aws.delete,
        )
        self.cloud_accounts_aws = to_streamed_response_wrapper(
            cloud_accounts_aws.cloud_accounts_aws,
        )
        self.private_image_enumeration = to_streamed_response_wrapper(
            cloud_accounts_aws.private_image_enumeration,
        )
        self.region_enumeration = to_streamed_response_wrapper(
            cloud_accounts_aws.region_enumeration,
        )
        self.retrieve_cloud_accounts_aws = to_streamed_response_wrapper(
            cloud_accounts_aws.retrieve_cloud_accounts_aws,
        )


class AsyncCloudAccountsAwsResourceWithStreamingResponse:
    def __init__(self, cloud_accounts_aws: AsyncCloudAccountsAwsResource) -> None:
        self._cloud_accounts_aws = cloud_accounts_aws

        self.retrieve = async_to_streamed_response_wrapper(
            cloud_accounts_aws.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            cloud_accounts_aws.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            cloud_accounts_aws.delete,
        )
        self.cloud_accounts_aws = async_to_streamed_response_wrapper(
            cloud_accounts_aws.cloud_accounts_aws,
        )
        self.private_image_enumeration = async_to_streamed_response_wrapper(
            cloud_accounts_aws.private_image_enumeration,
        )
        self.region_enumeration = async_to_streamed_response_wrapper(
            cloud_accounts_aws.region_enumeration,
        )
        self.retrieve_cloud_accounts_aws = async_to_streamed_response_wrapper(
            cloud_accounts_aws.retrieve_cloud_accounts_aws,
        )
