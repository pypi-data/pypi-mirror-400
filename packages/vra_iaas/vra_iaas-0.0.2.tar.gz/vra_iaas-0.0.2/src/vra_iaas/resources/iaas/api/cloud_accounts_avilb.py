# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable

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
    cloud_accounts_avilb_delete_params,
    cloud_accounts_avilb_update_params,
    cloud_accounts_avilb_retrieve_params,
    cloud_accounts_avilb_cloud_accounts_avilb_params,
    cloud_accounts_avilb_retrieve_cloud_accounts_avilb_params,
)
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.cloud_account_avi_lb import CloudAccountAviLb
from ....types.iaas.api.projects.request_tracker import RequestTracker
from ....types.iaas.api.region_specification_param import RegionSpecificationParam
from ....types.iaas.api.certificate_info_specification_param import CertificateInfoSpecificationParam
from ....types.iaas.api.cloud_accounts_avilb_retrieve_cloud_accounts_avilb_response import (
    CloudAccountsAvilbRetrieveCloudAccountsAvilbResponse,
)

__all__ = ["CloudAccountsAvilbResource", "AsyncCloudAccountsAvilbResource"]


class CloudAccountsAvilbResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CloudAccountsAvilbResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return CloudAccountsAvilbResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CloudAccountsAvilbResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return CloudAccountsAvilbResourceWithStreamingResponse(self)

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
    ) -> CloudAccountAviLb:
        """
        Get an AVI Load Balancer with a given id

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
            f"/iaas/api/cloud-accounts-avilb/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_avilb_retrieve_params.CloudAccountsAvilbRetrieveParams
                ),
            ),
            cast_to=CloudAccountAviLb,
        )

    def update(
        self,
        id: str,
        *,
        api_version: str,
        host_name: str,
        name: str,
        password: str,
        regions: Iterable[RegionSpecificationParam],
        username: str,
        accept_self_signed_certificate: bool | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        cloud_account_properties: Dict[str, str] | Omit = omit,
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
        Update AVI Load Balancer cloud account asynchronously

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          host_name: Host name for the AVI Load Balancer endpoint

          name: A human-friendly name used as an identifier in APIs that support this option.

          password: Password for the user used to authenticate with the cloud Account

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          username: Username to authenticate with the cloud account

          accept_self_signed_certificate: Accept self signed certificate when connecting.

          certificate_info: Specification for certificate for a cloud account.

          cloud_account_properties: Cloud Account specific properties supplied in as name value pairs

          create_default_zones: Create default cloud zones for the enabled regions

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
            f"/iaas/api/cloud-accounts-avilb/{id}",
            body=maybe_transform(
                {
                    "host_name": host_name,
                    "name": name,
                    "password": password,
                    "regions": regions,
                    "username": username,
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "certificate_info": certificate_info,
                    "cloud_account_properties": cloud_account_properties,
                    "create_default_zones": create_default_zones,
                    "description": description,
                    "tags": tags,
                },
                cloud_accounts_avilb_update_params.CloudAccountsAvilbUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_avilb_update_params.CloudAccountsAvilbUpdateParams
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
        Delete an AVI Load Balancer cloud account with a given id

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
            f"/iaas/api/cloud-accounts-avilb/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_avilb_delete_params.CloudAccountsAvilbDeleteParams
                ),
            ),
            cast_to=RequestTracker,
        )

    def cloud_accounts_avilb(
        self,
        *,
        api_version: str,
        host_name: str,
        name: str,
        password: str,
        regions: Iterable[RegionSpecificationParam],
        username: str,
        accept_self_signed_certificate: bool | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        cloud_account_properties: Dict[str, str] | Omit = omit,
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
        Create an AVI Load Balancer cloud account in the current organization

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          host_name: Host name for the AVI Load Balancer endpoint

          name: A human-friendly name used as an identifier in APIs that support this option.

          password: Password for the user used to authenticate with the cloud Account

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          username: Username to authenticate with the cloud account

          accept_self_signed_certificate: Accept self signed certificate when connecting.

          certificate_info: Specification for certificate for a cloud account.

          cloud_account_properties: Cloud Account specific properties supplied in as name value pairs

          create_default_zones: Create default cloud zones for the enabled regions

          description: A human-friendly description.

          tags: A set of tag keys and optional values to set on the Cloud Account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/cloud-accounts-avilb",
            body=maybe_transform(
                {
                    "host_name": host_name,
                    "name": name,
                    "password": password,
                    "regions": regions,
                    "username": username,
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "certificate_info": certificate_info,
                    "cloud_account_properties": cloud_account_properties,
                    "create_default_zones": create_default_zones,
                    "description": description,
                    "tags": tags,
                },
                cloud_accounts_avilb_cloud_accounts_avilb_params.CloudAccountsAvilbCloudAccountsAvilbParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_avilb_cloud_accounts_avilb_params.CloudAccountsAvilbCloudAccountsAvilbParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def retrieve_cloud_accounts_avilb(
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
    ) -> CloudAccountsAvilbRetrieveCloudAccountsAvilbResponse:
        """
        Get all AVI Load Balancer cloud accounts within the current organization

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
            "/iaas/api/cloud-accounts-avilb",
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
                    cloud_accounts_avilb_retrieve_cloud_accounts_avilb_params.CloudAccountsAvilbRetrieveCloudAccountsAvilbParams,
                ),
            ),
            cast_to=CloudAccountsAvilbRetrieveCloudAccountsAvilbResponse,
        )


class AsyncCloudAccountsAvilbResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCloudAccountsAvilbResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCloudAccountsAvilbResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCloudAccountsAvilbResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncCloudAccountsAvilbResourceWithStreamingResponse(self)

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
    ) -> CloudAccountAviLb:
        """
        Get an AVI Load Balancer with a given id

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
            f"/iaas/api/cloud-accounts-avilb/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_avilb_retrieve_params.CloudAccountsAvilbRetrieveParams
                ),
            ),
            cast_to=CloudAccountAviLb,
        )

    async def update(
        self,
        id: str,
        *,
        api_version: str,
        host_name: str,
        name: str,
        password: str,
        regions: Iterable[RegionSpecificationParam],
        username: str,
        accept_self_signed_certificate: bool | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        cloud_account_properties: Dict[str, str] | Omit = omit,
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
        Update AVI Load Balancer cloud account asynchronously

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          host_name: Host name for the AVI Load Balancer endpoint

          name: A human-friendly name used as an identifier in APIs that support this option.

          password: Password for the user used to authenticate with the cloud Account

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          username: Username to authenticate with the cloud account

          accept_self_signed_certificate: Accept self signed certificate when connecting.

          certificate_info: Specification for certificate for a cloud account.

          cloud_account_properties: Cloud Account specific properties supplied in as name value pairs

          create_default_zones: Create default cloud zones for the enabled regions

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
            f"/iaas/api/cloud-accounts-avilb/{id}",
            body=await async_maybe_transform(
                {
                    "host_name": host_name,
                    "name": name,
                    "password": password,
                    "regions": regions,
                    "username": username,
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "certificate_info": certificate_info,
                    "cloud_account_properties": cloud_account_properties,
                    "create_default_zones": create_default_zones,
                    "description": description,
                    "tags": tags,
                },
                cloud_accounts_avilb_update_params.CloudAccountsAvilbUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_avilb_update_params.CloudAccountsAvilbUpdateParams
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
        Delete an AVI Load Balancer cloud account with a given id

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
            f"/iaas/api/cloud-accounts-avilb/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_avilb_delete_params.CloudAccountsAvilbDeleteParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def cloud_accounts_avilb(
        self,
        *,
        api_version: str,
        host_name: str,
        name: str,
        password: str,
        regions: Iterable[RegionSpecificationParam],
        username: str,
        accept_self_signed_certificate: bool | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        cloud_account_properties: Dict[str, str] | Omit = omit,
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
        Create an AVI Load Balancer cloud account in the current organization

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          host_name: Host name for the AVI Load Balancer endpoint

          name: A human-friendly name used as an identifier in APIs that support this option.

          password: Password for the user used to authenticate with the cloud Account

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          username: Username to authenticate with the cloud account

          accept_self_signed_certificate: Accept self signed certificate when connecting.

          certificate_info: Specification for certificate for a cloud account.

          cloud_account_properties: Cloud Account specific properties supplied in as name value pairs

          create_default_zones: Create default cloud zones for the enabled regions

          description: A human-friendly description.

          tags: A set of tag keys and optional values to set on the Cloud Account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/cloud-accounts-avilb",
            body=await async_maybe_transform(
                {
                    "host_name": host_name,
                    "name": name,
                    "password": password,
                    "regions": regions,
                    "username": username,
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "certificate_info": certificate_info,
                    "cloud_account_properties": cloud_account_properties,
                    "create_default_zones": create_default_zones,
                    "description": description,
                    "tags": tags,
                },
                cloud_accounts_avilb_cloud_accounts_avilb_params.CloudAccountsAvilbCloudAccountsAvilbParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_avilb_cloud_accounts_avilb_params.CloudAccountsAvilbCloudAccountsAvilbParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def retrieve_cloud_accounts_avilb(
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
    ) -> CloudAccountsAvilbRetrieveCloudAccountsAvilbResponse:
        """
        Get all AVI Load Balancer cloud accounts within the current organization

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
            "/iaas/api/cloud-accounts-avilb",
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
                    cloud_accounts_avilb_retrieve_cloud_accounts_avilb_params.CloudAccountsAvilbRetrieveCloudAccountsAvilbParams,
                ),
            ),
            cast_to=CloudAccountsAvilbRetrieveCloudAccountsAvilbResponse,
        )


class CloudAccountsAvilbResourceWithRawResponse:
    def __init__(self, cloud_accounts_avilb: CloudAccountsAvilbResource) -> None:
        self._cloud_accounts_avilb = cloud_accounts_avilb

        self.retrieve = to_raw_response_wrapper(
            cloud_accounts_avilb.retrieve,
        )
        self.update = to_raw_response_wrapper(
            cloud_accounts_avilb.update,
        )
        self.delete = to_raw_response_wrapper(
            cloud_accounts_avilb.delete,
        )
        self.cloud_accounts_avilb = to_raw_response_wrapper(
            cloud_accounts_avilb.cloud_accounts_avilb,
        )
        self.retrieve_cloud_accounts_avilb = to_raw_response_wrapper(
            cloud_accounts_avilb.retrieve_cloud_accounts_avilb,
        )


class AsyncCloudAccountsAvilbResourceWithRawResponse:
    def __init__(self, cloud_accounts_avilb: AsyncCloudAccountsAvilbResource) -> None:
        self._cloud_accounts_avilb = cloud_accounts_avilb

        self.retrieve = async_to_raw_response_wrapper(
            cloud_accounts_avilb.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            cloud_accounts_avilb.update,
        )
        self.delete = async_to_raw_response_wrapper(
            cloud_accounts_avilb.delete,
        )
        self.cloud_accounts_avilb = async_to_raw_response_wrapper(
            cloud_accounts_avilb.cloud_accounts_avilb,
        )
        self.retrieve_cloud_accounts_avilb = async_to_raw_response_wrapper(
            cloud_accounts_avilb.retrieve_cloud_accounts_avilb,
        )


class CloudAccountsAvilbResourceWithStreamingResponse:
    def __init__(self, cloud_accounts_avilb: CloudAccountsAvilbResource) -> None:
        self._cloud_accounts_avilb = cloud_accounts_avilb

        self.retrieve = to_streamed_response_wrapper(
            cloud_accounts_avilb.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            cloud_accounts_avilb.update,
        )
        self.delete = to_streamed_response_wrapper(
            cloud_accounts_avilb.delete,
        )
        self.cloud_accounts_avilb = to_streamed_response_wrapper(
            cloud_accounts_avilb.cloud_accounts_avilb,
        )
        self.retrieve_cloud_accounts_avilb = to_streamed_response_wrapper(
            cloud_accounts_avilb.retrieve_cloud_accounts_avilb,
        )


class AsyncCloudAccountsAvilbResourceWithStreamingResponse:
    def __init__(self, cloud_accounts_avilb: AsyncCloudAccountsAvilbResource) -> None:
        self._cloud_accounts_avilb = cloud_accounts_avilb

        self.retrieve = async_to_streamed_response_wrapper(
            cloud_accounts_avilb.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            cloud_accounts_avilb.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            cloud_accounts_avilb.delete,
        )
        self.cloud_accounts_avilb = async_to_streamed_response_wrapper(
            cloud_accounts_avilb.cloud_accounts_avilb,
        )
        self.retrieve_cloud_accounts_avilb = async_to_streamed_response_wrapper(
            cloud_accounts_avilb.retrieve_cloud_accounts_avilb,
        )
