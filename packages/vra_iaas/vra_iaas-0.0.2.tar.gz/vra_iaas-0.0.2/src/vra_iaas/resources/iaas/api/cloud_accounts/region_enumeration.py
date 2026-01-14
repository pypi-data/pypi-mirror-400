# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict

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
from .....types.iaas.api.cloud_accounts import (
    region_enumeration_retrieve_params,
    region_enumeration_region_enumeration_params,
)
from .....types.iaas.api.projects.request_tracker import RequestTracker
from .....types.iaas.api.certificate_info_specification_param import CertificateInfoSpecificationParam
from .....types.iaas.api.cloud_accounts.region_enumeration_retrieve_response import RegionEnumerationRetrieveResponse

__all__ = ["RegionEnumerationResource", "AsyncRegionEnumerationResource"]


class RegionEnumerationResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RegionEnumerationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return RegionEnumerationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RegionEnumerationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return RegionEnumerationResourceWithStreamingResponse(self)

    def retrieve(
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
    ) -> RegionEnumerationRetrieveResponse:
        """
        Get region enumeration response for a given id

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
            f"/iaas/api/cloud-accounts/region-enumeration/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, region_enumeration_retrieve_params.RegionEnumerationRetrieveParams
                ),
            ),
            cast_to=RegionEnumerationRetrieveResponse,
        )

    def region_enumeration(
        self,
        *,
        api_version: str,
        cloud_account_properties: Dict[str, str],
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        cloud_account_id: str | Omit = omit,
        cloud_account_type: str | Omit = omit,
        private_key: str | Omit = omit,
        private_key_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Get the available regions for specified cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          cloud_account_properties: Cloud Account specific properties supplied in as name value pairs.

          certificate_info: Specification for certificate for a cloud account.

          cloud_account_id: Existing cloud account id. Either provide existing cloud account Id, or
              privateKeyId/privateKey credentials pair.

          cloud_account_type: Cloud account type

          private_key: Secret access key or password to be used to authenticate with the cloud account.
              Either provide privateKey or provide a cloudAccountId of an existing account.

          private_key_id: Access key id or username to be used to authenticate with the cloud account.
              Either provide privateKeyId or provide a cloudAccountId of an existing account.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/cloud-accounts/region-enumeration",
            body=maybe_transform(
                {
                    "cloud_account_properties": cloud_account_properties,
                    "certificate_info": certificate_info,
                    "cloud_account_id": cloud_account_id,
                    "cloud_account_type": cloud_account_type,
                    "private_key": private_key,
                    "private_key_id": private_key_id,
                },
                region_enumeration_region_enumeration_params.RegionEnumerationRegionEnumerationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    region_enumeration_region_enumeration_params.RegionEnumerationRegionEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )


class AsyncRegionEnumerationResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRegionEnumerationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRegionEnumerationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRegionEnumerationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncRegionEnumerationResourceWithStreamingResponse(self)

    async def retrieve(
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
    ) -> RegionEnumerationRetrieveResponse:
        """
        Get region enumeration response for a given id

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
            f"/iaas/api/cloud-accounts/region-enumeration/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, region_enumeration_retrieve_params.RegionEnumerationRetrieveParams
                ),
            ),
            cast_to=RegionEnumerationRetrieveResponse,
        )

    async def region_enumeration(
        self,
        *,
        api_version: str,
        cloud_account_properties: Dict[str, str],
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        cloud_account_id: str | Omit = omit,
        cloud_account_type: str | Omit = omit,
        private_key: str | Omit = omit,
        private_key_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Get the available regions for specified cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          cloud_account_properties: Cloud Account specific properties supplied in as name value pairs.

          certificate_info: Specification for certificate for a cloud account.

          cloud_account_id: Existing cloud account id. Either provide existing cloud account Id, or
              privateKeyId/privateKey credentials pair.

          cloud_account_type: Cloud account type

          private_key: Secret access key or password to be used to authenticate with the cloud account.
              Either provide privateKey or provide a cloudAccountId of an existing account.

          private_key_id: Access key id or username to be used to authenticate with the cloud account.
              Either provide privateKeyId or provide a cloudAccountId of an existing account.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/cloud-accounts/region-enumeration",
            body=await async_maybe_transform(
                {
                    "cloud_account_properties": cloud_account_properties,
                    "certificate_info": certificate_info,
                    "cloud_account_id": cloud_account_id,
                    "cloud_account_type": cloud_account_type,
                    "private_key": private_key,
                    "private_key_id": private_key_id,
                },
                region_enumeration_region_enumeration_params.RegionEnumerationRegionEnumerationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    region_enumeration_region_enumeration_params.RegionEnumerationRegionEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )


class RegionEnumerationResourceWithRawResponse:
    def __init__(self, region_enumeration: RegionEnumerationResource) -> None:
        self._region_enumeration = region_enumeration

        self.retrieve = to_raw_response_wrapper(
            region_enumeration.retrieve,
        )
        self.region_enumeration = to_raw_response_wrapper(
            region_enumeration.region_enumeration,
        )


class AsyncRegionEnumerationResourceWithRawResponse:
    def __init__(self, region_enumeration: AsyncRegionEnumerationResource) -> None:
        self._region_enumeration = region_enumeration

        self.retrieve = async_to_raw_response_wrapper(
            region_enumeration.retrieve,
        )
        self.region_enumeration = async_to_raw_response_wrapper(
            region_enumeration.region_enumeration,
        )


class RegionEnumerationResourceWithStreamingResponse:
    def __init__(self, region_enumeration: RegionEnumerationResource) -> None:
        self._region_enumeration = region_enumeration

        self.retrieve = to_streamed_response_wrapper(
            region_enumeration.retrieve,
        )
        self.region_enumeration = to_streamed_response_wrapper(
            region_enumeration.region_enumeration,
        )


class AsyncRegionEnumerationResourceWithStreamingResponse:
    def __init__(self, region_enumeration: AsyncRegionEnumerationResource) -> None:
        self._region_enumeration = region_enumeration

        self.retrieve = async_to_streamed_response_wrapper(
            region_enumeration.retrieve,
        )
        self.region_enumeration = async_to_streamed_response_wrapper(
            region_enumeration.region_enumeration,
        )
