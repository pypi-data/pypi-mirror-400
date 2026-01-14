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
    cloud_accounts_nsx_t_delete_params,
    cloud_accounts_nsx_t_update_params,
    cloud_accounts_nsx_t_retrieve_params,
    cloud_accounts_nsx_t_cloud_accounts_nsx_t_params,
    cloud_accounts_nsx_t_retrieve_cloud_accounts_nsx_t_params,
)
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.cloud_account_nsx_t import CloudAccountNsxT
from ....types.iaas.api.projects.request_tracker import RequestTracker
from ....types.iaas.api.certificate_info_specification_param import CertificateInfoSpecificationParam
from ....types.iaas.api.cloud_accounts_nsx_t_retrieve_cloud_accounts_nsx_t_response import (
    CloudAccountsNsxTRetrieveCloudAccountsNsxTResponse,
)

__all__ = ["CloudAccountsNsxTResource", "AsyncCloudAccountsNsxTResource"]


class CloudAccountsNsxTResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CloudAccountsNsxTResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return CloudAccountsNsxTResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CloudAccountsNsxTResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return CloudAccountsNsxTResourceWithStreamingResponse(self)

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
    ) -> CloudAccountNsxT:
        """
        Get an NSX-T cloud account with a given id

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
            f"/iaas/api/cloud-accounts-nsx-t/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_nsx_t_retrieve_params.CloudAccountsNsxTRetrieveParams
                ),
            ),
            cast_to=CloudAccountNsxT,
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
        Update NSX-T cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          dcid: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors. Note: Data
              collector endpoints are not available in VMware Aria Automation (on-prem)
              release and hence the data collector Id is optional for VMware Aria Automation
              (on-prem).

          host_name: Host name for the NSX-T endpoint

          name: A human-friendly name used as an identifier in APIs that support this option.

          password: Password for the user used to authenticate with the cloud Account

          username: Username to authenticate with the cloud account

          accept_self_signed_certificate: Accept self signed certificate when connecting.

          associated_cloud_account_ids: vSphere cloud accounts associated with this NSX-T cloud account.

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
            f"/iaas/api/cloud-accounts-nsx-t/{id}",
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
                cloud_accounts_nsx_t_update_params.CloudAccountsNsxTUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_nsx_t_update_params.CloudAccountsNsxTUpdateParams
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
        Delete a NSX-T cloud account with a given id

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
            f"/iaas/api/cloud-accounts-nsx-t/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_nsx_t_delete_params.CloudAccountsNsxTDeleteParams
                ),
            ),
            cast_to=RequestTracker,
        )

    def cloud_accounts_nsx_t(
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
        is_global_manager: bool | Omit = omit,
        manager_mode: bool | Omit = omit,
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

          host_name: Host name for the NSX-T endpoint

          name: A human-friendly name used as an identifier in APIs that support this option.

          password: Password for the user used to authenticate with the cloud Account

          username: Username to authenticate with the cloud account

          validate_only: If provided, it only validates the credentials in the Cloud Account
              Specification, and cloud account will not be created.

          accept_self_signed_certificate: Accept self signed certificate when connecting.

          associated_cloud_account_ids: vSphere cloud accounts associated with this NSX-T cloud account.

          certificate_info: Specification for certificate for a cloud account.

          description: A human-friendly description.

          is_global_manager: Indicates whether this is an NSX-T Global Manager cloud account. NSX-T Global
              Manager can only be associated with NSX-T cloud accounts. Default value: false.

          manager_mode: Create NSX-T cloud account in Manager (legacy) mode. When set to true, NSX-T
              cloud account in created in Manager mode. Mode cannot be changed after cloud
              account is created. Default value is false.

          tags: A set of tag keys and optional values to set on the Cloud Account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/cloud-accounts-nsx-t",
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
                    "is_global_manager": is_global_manager,
                    "manager_mode": manager_mode,
                    "tags": tags,
                },
                cloud_accounts_nsx_t_cloud_accounts_nsx_t_params.CloudAccountsNsxTCloudAccountsNsxTParams,
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
                    cloud_accounts_nsx_t_cloud_accounts_nsx_t_params.CloudAccountsNsxTCloudAccountsNsxTParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def retrieve_cloud_accounts_nsx_t(
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
    ) -> CloudAccountsNsxTRetrieveCloudAccountsNsxTResponse:
        """
        Get all NSX-T cloud accounts within the current organization

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
            "/iaas/api/cloud-accounts-nsx-t",
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
                    cloud_accounts_nsx_t_retrieve_cloud_accounts_nsx_t_params.CloudAccountsNsxTRetrieveCloudAccountsNsxTParams,
                ),
            ),
            cast_to=CloudAccountsNsxTRetrieveCloudAccountsNsxTResponse,
        )


class AsyncCloudAccountsNsxTResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCloudAccountsNsxTResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCloudAccountsNsxTResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCloudAccountsNsxTResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncCloudAccountsNsxTResourceWithStreamingResponse(self)

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
    ) -> CloudAccountNsxT:
        """
        Get an NSX-T cloud account with a given id

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
            f"/iaas/api/cloud-accounts-nsx-t/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_nsx_t_retrieve_params.CloudAccountsNsxTRetrieveParams
                ),
            ),
            cast_to=CloudAccountNsxT,
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
        Update NSX-T cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          dcid: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors. Note: Data
              collector endpoints are not available in VMware Aria Automation (on-prem)
              release and hence the data collector Id is optional for VMware Aria Automation
              (on-prem).

          host_name: Host name for the NSX-T endpoint

          name: A human-friendly name used as an identifier in APIs that support this option.

          password: Password for the user used to authenticate with the cloud Account

          username: Username to authenticate with the cloud account

          accept_self_signed_certificate: Accept self signed certificate when connecting.

          associated_cloud_account_ids: vSphere cloud accounts associated with this NSX-T cloud account.

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
            f"/iaas/api/cloud-accounts-nsx-t/{id}",
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
                cloud_accounts_nsx_t_update_params.CloudAccountsNsxTUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_nsx_t_update_params.CloudAccountsNsxTUpdateParams
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
        Delete a NSX-T cloud account with a given id

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
            f"/iaas/api/cloud-accounts-nsx-t/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_nsx_t_delete_params.CloudAccountsNsxTDeleteParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def cloud_accounts_nsx_t(
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
        is_global_manager: bool | Omit = omit,
        manager_mode: bool | Omit = omit,
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

          host_name: Host name for the NSX-T endpoint

          name: A human-friendly name used as an identifier in APIs that support this option.

          password: Password for the user used to authenticate with the cloud Account

          username: Username to authenticate with the cloud account

          validate_only: If provided, it only validates the credentials in the Cloud Account
              Specification, and cloud account will not be created.

          accept_self_signed_certificate: Accept self signed certificate when connecting.

          associated_cloud_account_ids: vSphere cloud accounts associated with this NSX-T cloud account.

          certificate_info: Specification for certificate for a cloud account.

          description: A human-friendly description.

          is_global_manager: Indicates whether this is an NSX-T Global Manager cloud account. NSX-T Global
              Manager can only be associated with NSX-T cloud accounts. Default value: false.

          manager_mode: Create NSX-T cloud account in Manager (legacy) mode. When set to true, NSX-T
              cloud account in created in Manager mode. Mode cannot be changed after cloud
              account is created. Default value is false.

          tags: A set of tag keys and optional values to set on the Cloud Account

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/cloud-accounts-nsx-t",
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
                    "is_global_manager": is_global_manager,
                    "manager_mode": manager_mode,
                    "tags": tags,
                },
                cloud_accounts_nsx_t_cloud_accounts_nsx_t_params.CloudAccountsNsxTCloudAccountsNsxTParams,
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
                    cloud_accounts_nsx_t_cloud_accounts_nsx_t_params.CloudAccountsNsxTCloudAccountsNsxTParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def retrieve_cloud_accounts_nsx_t(
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
    ) -> CloudAccountsNsxTRetrieveCloudAccountsNsxTResponse:
        """
        Get all NSX-T cloud accounts within the current organization

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
            "/iaas/api/cloud-accounts-nsx-t",
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
                    cloud_accounts_nsx_t_retrieve_cloud_accounts_nsx_t_params.CloudAccountsNsxTRetrieveCloudAccountsNsxTParams,
                ),
            ),
            cast_to=CloudAccountsNsxTRetrieveCloudAccountsNsxTResponse,
        )


class CloudAccountsNsxTResourceWithRawResponse:
    def __init__(self, cloud_accounts_nsx_t: CloudAccountsNsxTResource) -> None:
        self._cloud_accounts_nsx_t = cloud_accounts_nsx_t

        self.retrieve = to_raw_response_wrapper(
            cloud_accounts_nsx_t.retrieve,
        )
        self.update = to_raw_response_wrapper(
            cloud_accounts_nsx_t.update,
        )
        self.delete = to_raw_response_wrapper(
            cloud_accounts_nsx_t.delete,
        )
        self.cloud_accounts_nsx_t = to_raw_response_wrapper(
            cloud_accounts_nsx_t.cloud_accounts_nsx_t,
        )
        self.retrieve_cloud_accounts_nsx_t = to_raw_response_wrapper(
            cloud_accounts_nsx_t.retrieve_cloud_accounts_nsx_t,
        )


class AsyncCloudAccountsNsxTResourceWithRawResponse:
    def __init__(self, cloud_accounts_nsx_t: AsyncCloudAccountsNsxTResource) -> None:
        self._cloud_accounts_nsx_t = cloud_accounts_nsx_t

        self.retrieve = async_to_raw_response_wrapper(
            cloud_accounts_nsx_t.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            cloud_accounts_nsx_t.update,
        )
        self.delete = async_to_raw_response_wrapper(
            cloud_accounts_nsx_t.delete,
        )
        self.cloud_accounts_nsx_t = async_to_raw_response_wrapper(
            cloud_accounts_nsx_t.cloud_accounts_nsx_t,
        )
        self.retrieve_cloud_accounts_nsx_t = async_to_raw_response_wrapper(
            cloud_accounts_nsx_t.retrieve_cloud_accounts_nsx_t,
        )


class CloudAccountsNsxTResourceWithStreamingResponse:
    def __init__(self, cloud_accounts_nsx_t: CloudAccountsNsxTResource) -> None:
        self._cloud_accounts_nsx_t = cloud_accounts_nsx_t

        self.retrieve = to_streamed_response_wrapper(
            cloud_accounts_nsx_t.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            cloud_accounts_nsx_t.update,
        )
        self.delete = to_streamed_response_wrapper(
            cloud_accounts_nsx_t.delete,
        )
        self.cloud_accounts_nsx_t = to_streamed_response_wrapper(
            cloud_accounts_nsx_t.cloud_accounts_nsx_t,
        )
        self.retrieve_cloud_accounts_nsx_t = to_streamed_response_wrapper(
            cloud_accounts_nsx_t.retrieve_cloud_accounts_nsx_t,
        )


class AsyncCloudAccountsNsxTResourceWithStreamingResponse:
    def __init__(self, cloud_accounts_nsx_t: AsyncCloudAccountsNsxTResource) -> None:
        self._cloud_accounts_nsx_t = cloud_accounts_nsx_t

        self.retrieve = async_to_streamed_response_wrapper(
            cloud_accounts_nsx_t.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            cloud_accounts_nsx_t.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            cloud_accounts_nsx_t.delete,
        )
        self.cloud_accounts_nsx_t = async_to_streamed_response_wrapper(
            cloud_accounts_nsx_t.cloud_accounts_nsx_t,
        )
        self.retrieve_cloud_accounts_nsx_t = async_to_streamed_response_wrapper(
            cloud_accounts_nsx_t.retrieve_cloud_accounts_nsx_t,
        )
