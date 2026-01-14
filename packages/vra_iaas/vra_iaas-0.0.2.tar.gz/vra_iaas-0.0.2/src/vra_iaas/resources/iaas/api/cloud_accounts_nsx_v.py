# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
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
    cloud_accounts_nsx_v_delete_params,
    cloud_accounts_nsx_v_update_params,
    cloud_accounts_nsx_v_retrieve_params,
    cloud_accounts_nsx_v_cloud_accounts_nsx_v_params,
    cloud_accounts_nsx_v_retrieve_cloud_accounts_nsx_v_params,
)
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.cloud_account_nsx_v import CloudAccountNsxV
from ....types.iaas.api.projects.request_tracker import RequestTracker
from ....types.iaas.api.certificate_info_specification_param import CertificateInfoSpecificationParam
from ....types.iaas.api.cloud_accounts_nsx_v_retrieve_cloud_accounts_nsx_v_response import (
    CloudAccountsNsxVRetrieveCloudAccountsNsxVResponse,
)

__all__ = ["CloudAccountsNsxVResource", "AsyncCloudAccountsNsxVResource"]


class CloudAccountsNsxVResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CloudAccountsNsxVResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return CloudAccountsNsxVResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CloudAccountsNsxVResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return CloudAccountsNsxVResourceWithStreamingResponse(self)

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
    ) -> CloudAccountNsxV:
        """
        Get an NSX-V cloud account with a given id

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
            f"/iaas/api/cloud-accounts-nsx-v/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_nsx_v_retrieve_params.CloudAccountsNsxVRetrieveParams
                ),
            ),
            cast_to=CloudAccountNsxV,
        )

    def update(
        self,
        id: str,
        *,
        api_version: str,
        dcid: str,
        host_name: str,
        name: str,
        password: str,
        username: str,
        accept_self_signed_certificate: bool | Omit = omit,
        associated_cloud_account_ids: SequenceNotStr[str] | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
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
        Update NSX-V cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          dcid: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors. Note: Data
              collector endpoints are not available in VMware Aria Automation (on-prem)
              release and hence the data collector Id is optional for VMware Aria Automation
              (on-prem).

          host_name: Host name for the NSX-v endpoint

          name: A human-friendly name used as an identifier in APIs that support this option.

          password: Password for the user used to authenticate with the cloud Account

          username: Username to authenticate with the cloud account

          accept_self_signed_certificate: Accept self signed certificate when connecting.

          associated_cloud_account_ids: vSphere cloud account associated with this NSX-V cloud account. NSX-V cloud
              account can be associated with a single vSphere cloud account.

          certificate_info: Specification for certificate for a cloud account.

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
            f"/iaas/api/cloud-accounts-nsx-v/{id}",
            body=maybe_transform(
                {
                    "dcid": dcid,
                    "host_name": host_name,
                    "name": name,
                    "password": password,
                    "username": username,
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "associated_cloud_account_ids": associated_cloud_account_ids,
                    "certificate_info": certificate_info,
                    "description": description,
                    "tags": tags,
                },
                cloud_accounts_nsx_v_update_params.CloudAccountsNsxVUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_nsx_v_update_params.CloudAccountsNsxVUpdateParams
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
        Delete a NSV-V cloud account with a given id

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
            f"/iaas/api/cloud-accounts-nsx-v/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_nsx_v_delete_params.CloudAccountsNsxVDeleteParams
                ),
            ),
            cast_to=RequestTracker,
        )

    def cloud_accounts_nsx_v(
        self,
        *,
        api_version: str,
        dcid: str,
        host_name: str,
        name: str,
        password: str,
        username: str,
        validate_only: str | Omit = omit,
        accept_self_signed_certificate: bool | Omit = omit,
        associated_cloud_account_ids: SequenceNotStr[str] | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
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

          dcid: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors. Note: Data
              collector endpoints are not available in VMware Aria Automation (on-prem)
              release and hence the data collector Id is optional for VMware Aria Automation
              (on-prem).

          host_name: Host name for the NSX-v endpoint

          name: A human-friendly name used as an identifier in APIs that support this option.

          password: Password for the user used to authenticate with the cloud Account

          username: Username to authenticate with the cloud account

          validate_only: If provided, it only validates the credentials in the Cloud Account
              Specification, and cloud account will not be created.

          accept_self_signed_certificate: Accept self signed certificate when connecting.

          associated_cloud_account_ids: vSphere cloud account associated with this NSX-V cloud account. NSX-V cloud
              account can be associated with a single vSphere cloud account.

          certificate_info: Specification for certificate for a cloud account.

          description: A human-friendly description.

          tags: A set of tag keys and optional values to set on the Cloud Account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/cloud-accounts-nsx-v",
            body=maybe_transform(
                {
                    "dcid": dcid,
                    "host_name": host_name,
                    "name": name,
                    "password": password,
                    "username": username,
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "associated_cloud_account_ids": associated_cloud_account_ids,
                    "certificate_info": certificate_info,
                    "description": description,
                    "tags": tags,
                },
                cloud_accounts_nsx_v_cloud_accounts_nsx_v_params.CloudAccountsNsxVCloudAccountsNsxVParams,
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
                    cloud_accounts_nsx_v_cloud_accounts_nsx_v_params.CloudAccountsNsxVCloudAccountsNsxVParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def retrieve_cloud_accounts_nsx_v(
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
    ) -> CloudAccountsNsxVRetrieveCloudAccountsNsxVResponse:
        """
        Get all NSX-V cloud accounts within the current organization

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
            "/iaas/api/cloud-accounts-nsx-v",
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
                    cloud_accounts_nsx_v_retrieve_cloud_accounts_nsx_v_params.CloudAccountsNsxVRetrieveCloudAccountsNsxVParams,
                ),
            ),
            cast_to=CloudAccountsNsxVRetrieveCloudAccountsNsxVResponse,
        )


class AsyncCloudAccountsNsxVResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCloudAccountsNsxVResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCloudAccountsNsxVResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCloudAccountsNsxVResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncCloudAccountsNsxVResourceWithStreamingResponse(self)

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
    ) -> CloudAccountNsxV:
        """
        Get an NSX-V cloud account with a given id

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
            f"/iaas/api/cloud-accounts-nsx-v/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_nsx_v_retrieve_params.CloudAccountsNsxVRetrieveParams
                ),
            ),
            cast_to=CloudAccountNsxV,
        )

    async def update(
        self,
        id: str,
        *,
        api_version: str,
        dcid: str,
        host_name: str,
        name: str,
        password: str,
        username: str,
        accept_self_signed_certificate: bool | Omit = omit,
        associated_cloud_account_ids: SequenceNotStr[str] | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
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
        Update NSX-V cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          dcid: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors. Note: Data
              collector endpoints are not available in VMware Aria Automation (on-prem)
              release and hence the data collector Id is optional for VMware Aria Automation
              (on-prem).

          host_name: Host name for the NSX-v endpoint

          name: A human-friendly name used as an identifier in APIs that support this option.

          password: Password for the user used to authenticate with the cloud Account

          username: Username to authenticate with the cloud account

          accept_self_signed_certificate: Accept self signed certificate when connecting.

          associated_cloud_account_ids: vSphere cloud account associated with this NSX-V cloud account. NSX-V cloud
              account can be associated with a single vSphere cloud account.

          certificate_info: Specification for certificate for a cloud account.

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
            f"/iaas/api/cloud-accounts-nsx-v/{id}",
            body=await async_maybe_transform(
                {
                    "dcid": dcid,
                    "host_name": host_name,
                    "name": name,
                    "password": password,
                    "username": username,
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "associated_cloud_account_ids": associated_cloud_account_ids,
                    "certificate_info": certificate_info,
                    "description": description,
                    "tags": tags,
                },
                cloud_accounts_nsx_v_update_params.CloudAccountsNsxVUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_nsx_v_update_params.CloudAccountsNsxVUpdateParams
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
        Delete a NSV-V cloud account with a given id

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
            f"/iaas/api/cloud-accounts-nsx-v/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_nsx_v_delete_params.CloudAccountsNsxVDeleteParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def cloud_accounts_nsx_v(
        self,
        *,
        api_version: str,
        dcid: str,
        host_name: str,
        name: str,
        password: str,
        username: str,
        validate_only: str | Omit = omit,
        accept_self_signed_certificate: bool | Omit = omit,
        associated_cloud_account_ids: SequenceNotStr[str] | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
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

          dcid: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors. Note: Data
              collector endpoints are not available in VMware Aria Automation (on-prem)
              release and hence the data collector Id is optional for VMware Aria Automation
              (on-prem).

          host_name: Host name for the NSX-v endpoint

          name: A human-friendly name used as an identifier in APIs that support this option.

          password: Password for the user used to authenticate with the cloud Account

          username: Username to authenticate with the cloud account

          validate_only: If provided, it only validates the credentials in the Cloud Account
              Specification, and cloud account will not be created.

          accept_self_signed_certificate: Accept self signed certificate when connecting.

          associated_cloud_account_ids: vSphere cloud account associated with this NSX-V cloud account. NSX-V cloud
              account can be associated with a single vSphere cloud account.

          certificate_info: Specification for certificate for a cloud account.

          description: A human-friendly description.

          tags: A set of tag keys and optional values to set on the Cloud Account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/cloud-accounts-nsx-v",
            body=await async_maybe_transform(
                {
                    "dcid": dcid,
                    "host_name": host_name,
                    "name": name,
                    "password": password,
                    "username": username,
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "associated_cloud_account_ids": associated_cloud_account_ids,
                    "certificate_info": certificate_info,
                    "description": description,
                    "tags": tags,
                },
                cloud_accounts_nsx_v_cloud_accounts_nsx_v_params.CloudAccountsNsxVCloudAccountsNsxVParams,
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
                    cloud_accounts_nsx_v_cloud_accounts_nsx_v_params.CloudAccountsNsxVCloudAccountsNsxVParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def retrieve_cloud_accounts_nsx_v(
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
    ) -> CloudAccountsNsxVRetrieveCloudAccountsNsxVResponse:
        """
        Get all NSX-V cloud accounts within the current organization

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
            "/iaas/api/cloud-accounts-nsx-v",
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
                    cloud_accounts_nsx_v_retrieve_cloud_accounts_nsx_v_params.CloudAccountsNsxVRetrieveCloudAccountsNsxVParams,
                ),
            ),
            cast_to=CloudAccountsNsxVRetrieveCloudAccountsNsxVResponse,
        )


class CloudAccountsNsxVResourceWithRawResponse:
    def __init__(self, cloud_accounts_nsx_v: CloudAccountsNsxVResource) -> None:
        self._cloud_accounts_nsx_v = cloud_accounts_nsx_v

        self.retrieve = to_raw_response_wrapper(
            cloud_accounts_nsx_v.retrieve,
        )
        self.update = to_raw_response_wrapper(
            cloud_accounts_nsx_v.update,
        )
        self.delete = to_raw_response_wrapper(
            cloud_accounts_nsx_v.delete,
        )
        self.cloud_accounts_nsx_v = to_raw_response_wrapper(
            cloud_accounts_nsx_v.cloud_accounts_nsx_v,
        )
        self.retrieve_cloud_accounts_nsx_v = to_raw_response_wrapper(
            cloud_accounts_nsx_v.retrieve_cloud_accounts_nsx_v,
        )


class AsyncCloudAccountsNsxVResourceWithRawResponse:
    def __init__(self, cloud_accounts_nsx_v: AsyncCloudAccountsNsxVResource) -> None:
        self._cloud_accounts_nsx_v = cloud_accounts_nsx_v

        self.retrieve = async_to_raw_response_wrapper(
            cloud_accounts_nsx_v.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            cloud_accounts_nsx_v.update,
        )
        self.delete = async_to_raw_response_wrapper(
            cloud_accounts_nsx_v.delete,
        )
        self.cloud_accounts_nsx_v = async_to_raw_response_wrapper(
            cloud_accounts_nsx_v.cloud_accounts_nsx_v,
        )
        self.retrieve_cloud_accounts_nsx_v = async_to_raw_response_wrapper(
            cloud_accounts_nsx_v.retrieve_cloud_accounts_nsx_v,
        )


class CloudAccountsNsxVResourceWithStreamingResponse:
    def __init__(self, cloud_accounts_nsx_v: CloudAccountsNsxVResource) -> None:
        self._cloud_accounts_nsx_v = cloud_accounts_nsx_v

        self.retrieve = to_streamed_response_wrapper(
            cloud_accounts_nsx_v.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            cloud_accounts_nsx_v.update,
        )
        self.delete = to_streamed_response_wrapper(
            cloud_accounts_nsx_v.delete,
        )
        self.cloud_accounts_nsx_v = to_streamed_response_wrapper(
            cloud_accounts_nsx_v.cloud_accounts_nsx_v,
        )
        self.retrieve_cloud_accounts_nsx_v = to_streamed_response_wrapper(
            cloud_accounts_nsx_v.retrieve_cloud_accounts_nsx_v,
        )


class AsyncCloudAccountsNsxVResourceWithStreamingResponse:
    def __init__(self, cloud_accounts_nsx_v: AsyncCloudAccountsNsxVResource) -> None:
        self._cloud_accounts_nsx_v = cloud_accounts_nsx_v

        self.retrieve = async_to_streamed_response_wrapper(
            cloud_accounts_nsx_v.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            cloud_accounts_nsx_v.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            cloud_accounts_nsx_v.delete,
        )
        self.cloud_accounts_nsx_v = async_to_streamed_response_wrapper(
            cloud_accounts_nsx_v.cloud_accounts_nsx_v,
        )
        self.retrieve_cloud_accounts_nsx_v = async_to_streamed_response_wrapper(
            cloud_accounts_nsx_v.retrieve_cloud_accounts_nsx_v,
        )
