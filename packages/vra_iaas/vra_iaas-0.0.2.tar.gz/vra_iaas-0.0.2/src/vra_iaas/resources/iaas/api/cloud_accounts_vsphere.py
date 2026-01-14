# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal

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
    cloud_accounts_vsphere_delete_params,
    cloud_accounts_vsphere_update_params,
    cloud_accounts_vsphere_retrieve_params,
    cloud_accounts_vsphere_region_enumeration_params,
    cloud_accounts_vsphere_cloud_accounts_vsphere_params,
    cloud_accounts_vsphere_private_image_enumeration_params,
    cloud_accounts_vsphere_retrieve_cloud_accounts_vsphere_params,
)
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.cloud_account_vsphere import CloudAccountVsphere
from ....types.iaas.api.projects.request_tracker import RequestTracker
from ....types.iaas.api.region_specification_param import RegionSpecificationParam
from ....types.iaas.api.certificate_info_specification_param import CertificateInfoSpecificationParam
from ....types.iaas.api.cloud_accounts_vsphere_retrieve_cloud_accounts_vsphere_response import (
    CloudAccountsVsphereRetrieveCloudAccountsVsphereResponse,
)

__all__ = ["CloudAccountsVsphereResource", "AsyncCloudAccountsVsphereResource"]


class CloudAccountsVsphereResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CloudAccountsVsphereResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return CloudAccountsVsphereResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CloudAccountsVsphereResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return CloudAccountsVsphereResourceWithStreamingResponse(self)

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
    ) -> CloudAccountVsphere:
        """
        Get an vSphere cloud account with a given id

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
            f"/iaas/api/cloud-accounts-vsphere/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_vsphere_retrieve_params.CloudAccountsVsphereRetrieveParams,
                ),
            ),
            cast_to=CloudAccountVsphere,
        )

    def update(
        self,
        id: str,
        *,
        api_version: str,
        host_name: str,
        name: str,
        regions: Iterable[RegionSpecificationParam],
        accept_self_signed_certificate: bool | Omit = omit,
        associated_cloud_account_ids: SequenceNotStr[str] | Omit = omit,
        associated_mobility_cloud_account_ids: Dict[str, Literal["UNIDIRECTIONAL", "BIDIRECTIONAL"]] | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        create_default_zones: bool | Omit = omit,
        dcid: str | Omit = omit,
        description: str | Omit = omit,
        environment: str | Omit = omit,
        password: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        username: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Update vSphere cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          host_name: Host name for the vSphere endpoint

          name: A human-friendly name used as an identifier in APIs that support this option.

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          accept_self_signed_certificate: Accept self signed certificate when connecting to vSphere

          associated_cloud_account_ids: NSX-V or NSX-T account to associate with this vSphere cloud account. vSphere
              cloud account can be a single NSX-V cloud account or a single NSX-T cloud
              account.

          associated_mobility_cloud_account_ids: Cloud account IDs and directionalities create associations to other vSphere
              cloud accounts that can be used for workload mobility. ID refers to an
              associated cloud account, and directionality can be unidirectional or
              bidirectional.

          certificate_info: Specification for certificate for a cloud account.

          create_default_zones: Create default cloud zones for the enabled regions.

          dcid: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors. Note: Data
              collector endpoints are not available in VMware Aria Automation (on-prem)
              release.

          description: A human-friendly description.

          environment: The environment where data collectors are deployed. When the data collectors are
              deployed on an aap-based cloud gateway appliance, use "aap".

          password: Password for the user used to authenticate with the cloud Account.

          tags: A set of tag keys and optional values to set on the Cloud Account

          username: Username to authenticate with the cloud account.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/cloud-accounts-vsphere/{id}",
            body=maybe_transform(
                {
                    "host_name": host_name,
                    "name": name,
                    "regions": regions,
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "associated_cloud_account_ids": associated_cloud_account_ids,
                    "associated_mobility_cloud_account_ids": associated_mobility_cloud_account_ids,
                    "certificate_info": certificate_info,
                    "create_default_zones": create_default_zones,
                    "dcid": dcid,
                    "description": description,
                    "environment": environment,
                    "password": password,
                    "tags": tags,
                    "username": username,
                },
                cloud_accounts_vsphere_update_params.CloudAccountsVsphereUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_vsphere_update_params.CloudAccountsVsphereUpdateParams
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
        Delete a vSphere Cloud Account with a given id

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
            f"/iaas/api/cloud-accounts-vsphere/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_vsphere_delete_params.CloudAccountsVsphereDeleteParams
                ),
            ),
            cast_to=RequestTracker,
        )

    def cloud_accounts_vsphere(
        self,
        *,
        api_version: str,
        host_name: str,
        name: str,
        regions: Iterable[RegionSpecificationParam],
        validate_only: str | Omit = omit,
        accept_self_signed_certificate: bool | Omit = omit,
        associated_cloud_account_ids: SequenceNotStr[str] | Omit = omit,
        associated_mobility_cloud_account_ids: Dict[str, Literal["UNIDIRECTIONAL", "BIDIRECTIONAL"]] | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        create_default_zones: bool | Omit = omit,
        dcid: str | Omit = omit,
        description: str | Omit = omit,
        environment: str | Omit = omit,
        password: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        username: str | Omit = omit,
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

          host_name: Host name for the vSphere endpoint

          name: A human-friendly name used as an identifier in APIs that support this option.

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          validate_only: If provided, it only validates the credentials in the Cloud Account
              Specification, and cloud account will not be created.

          accept_self_signed_certificate: Accept self signed certificate when connecting to vSphere

          associated_cloud_account_ids: NSX-V or NSX-T account to associate with this vSphere cloud account. vSphere
              cloud account can be a single NSX-V cloud account or a single NSX-T cloud
              account.

          associated_mobility_cloud_account_ids: Cloud account IDs and directionalities create associations to other vSphere
              cloud accounts that can be used for workload mobility. ID refers to an
              associated cloud account, and directionality can be unidirectional or
              bidirectional.

          certificate_info: Specification for certificate for a cloud account.

          create_default_zones: Create default cloud zones for the enabled regions.

          dcid: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors. Note: Data
              collector endpoints are not available in VMware Aria Automation (on-prem)
              release.

          description: A human-friendly description.

          environment: The environment where data collectors are deployed. When the data collectors are
              deployed on an aap-based cloud gateway appliance, use "aap".

          password: Password for the user used to authenticate with the cloud Account.

          tags: A set of tag keys and optional values to set on the Cloud Account

          username: Username to authenticate with the cloud account.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/cloud-accounts-vsphere",
            body=maybe_transform(
                {
                    "host_name": host_name,
                    "name": name,
                    "regions": regions,
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "associated_cloud_account_ids": associated_cloud_account_ids,
                    "associated_mobility_cloud_account_ids": associated_mobility_cloud_account_ids,
                    "certificate_info": certificate_info,
                    "create_default_zones": create_default_zones,
                    "dcid": dcid,
                    "description": description,
                    "environment": environment,
                    "password": password,
                    "tags": tags,
                    "username": username,
                },
                cloud_accounts_vsphere_cloud_accounts_vsphere_params.CloudAccountsVsphereCloudAccountsVsphereParams,
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
                    cloud_accounts_vsphere_cloud_accounts_vsphere_params.CloudAccountsVsphereCloudAccountsVsphereParams,
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
        Enumerate all private images for enabled regions of the specified vSphere
        account

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
            f"/iaas/api/cloud-accounts-vsphere/{id}/private-image-enumeration",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_vsphere_private_image_enumeration_params.CloudAccountsVspherePrivateImageEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def region_enumeration(
        self,
        *,
        api_version: str,
        accept_self_signed_certificate: bool | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        cloud_account_id: str | Omit = omit,
        dcid: str | Omit = omit,
        environment: str | Omit = omit,
        host_name: str | Omit = omit,
        password: str | Omit = omit,
        username: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Get the available regions for specified vSphere cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          accept_self_signed_certificate: Accept self signed certificate when connecting to vSphere

          certificate_info: Specification for certificate for a cloud account.

          cloud_account_id: Existing cloud account id. Either provide existing cloud account Id, or
              hostName, username, password.

          dcid: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors. Note: Data
              collector endpoints are not available in VMware Aria Automation (on-prem)
              release.

          environment: The environment where data collectors are deployed. When the data collectors are
              deployed on a cloud gateway appliance, use "aap".

          host_name: Host name for the vSphere endpoint. Either provide hostName or provide a
              cloudAccountId of an existing account.

          password: Password for the user used to authenticate with the cloud Account. Either
              provide password or provide a cloudAccountId of an existing account.

          username: Username to authenticate with the cloud account. Either provide username or
              provide a cloudAccountId of an existing account.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/cloud-accounts-vsphere/region-enumeration",
            body=maybe_transform(
                {
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "certificate_info": certificate_info,
                    "cloud_account_id": cloud_account_id,
                    "dcid": dcid,
                    "environment": environment,
                    "host_name": host_name,
                    "password": password,
                    "username": username,
                },
                cloud_accounts_vsphere_region_enumeration_params.CloudAccountsVsphereRegionEnumerationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_vsphere_region_enumeration_params.CloudAccountsVsphereRegionEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def retrieve_cloud_accounts_vsphere(
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
    ) -> CloudAccountsVsphereRetrieveCloudAccountsVsphereResponse:
        """
        Get all vSphere cloud accounts within the current organization

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
            "/iaas/api/cloud-accounts-vsphere",
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
                    cloud_accounts_vsphere_retrieve_cloud_accounts_vsphere_params.CloudAccountsVsphereRetrieveCloudAccountsVsphereParams,
                ),
            ),
            cast_to=CloudAccountsVsphereRetrieveCloudAccountsVsphereResponse,
        )


class AsyncCloudAccountsVsphereResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCloudAccountsVsphereResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCloudAccountsVsphereResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCloudAccountsVsphereResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncCloudAccountsVsphereResourceWithStreamingResponse(self)

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
    ) -> CloudAccountVsphere:
        """
        Get an vSphere cloud account with a given id

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
            f"/iaas/api/cloud-accounts-vsphere/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_vsphere_retrieve_params.CloudAccountsVsphereRetrieveParams,
                ),
            ),
            cast_to=CloudAccountVsphere,
        )

    async def update(
        self,
        id: str,
        *,
        api_version: str,
        host_name: str,
        name: str,
        regions: Iterable[RegionSpecificationParam],
        accept_self_signed_certificate: bool | Omit = omit,
        associated_cloud_account_ids: SequenceNotStr[str] | Omit = omit,
        associated_mobility_cloud_account_ids: Dict[str, Literal["UNIDIRECTIONAL", "BIDIRECTIONAL"]] | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        create_default_zones: bool | Omit = omit,
        dcid: str | Omit = omit,
        description: str | Omit = omit,
        environment: str | Omit = omit,
        password: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        username: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Update vSphere cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          host_name: Host name for the vSphere endpoint

          name: A human-friendly name used as an identifier in APIs that support this option.

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          accept_self_signed_certificate: Accept self signed certificate when connecting to vSphere

          associated_cloud_account_ids: NSX-V or NSX-T account to associate with this vSphere cloud account. vSphere
              cloud account can be a single NSX-V cloud account or a single NSX-T cloud
              account.

          associated_mobility_cloud_account_ids: Cloud account IDs and directionalities create associations to other vSphere
              cloud accounts that can be used for workload mobility. ID refers to an
              associated cloud account, and directionality can be unidirectional or
              bidirectional.

          certificate_info: Specification for certificate for a cloud account.

          create_default_zones: Create default cloud zones for the enabled regions.

          dcid: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors. Note: Data
              collector endpoints are not available in VMware Aria Automation (on-prem)
              release.

          description: A human-friendly description.

          environment: The environment where data collectors are deployed. When the data collectors are
              deployed on an aap-based cloud gateway appliance, use "aap".

          password: Password for the user used to authenticate with the cloud Account.

          tags: A set of tag keys and optional values to set on the Cloud Account

          username: Username to authenticate with the cloud account.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/cloud-accounts-vsphere/{id}",
            body=await async_maybe_transform(
                {
                    "host_name": host_name,
                    "name": name,
                    "regions": regions,
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "associated_cloud_account_ids": associated_cloud_account_ids,
                    "associated_mobility_cloud_account_ids": associated_mobility_cloud_account_ids,
                    "certificate_info": certificate_info,
                    "create_default_zones": create_default_zones,
                    "dcid": dcid,
                    "description": description,
                    "environment": environment,
                    "password": password,
                    "tags": tags,
                    "username": username,
                },
                cloud_accounts_vsphere_update_params.CloudAccountsVsphereUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_vsphere_update_params.CloudAccountsVsphereUpdateParams
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
        Delete a vSphere Cloud Account with a given id

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
            f"/iaas/api/cloud-accounts-vsphere/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_vsphere_delete_params.CloudAccountsVsphereDeleteParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def cloud_accounts_vsphere(
        self,
        *,
        api_version: str,
        host_name: str,
        name: str,
        regions: Iterable[RegionSpecificationParam],
        validate_only: str | Omit = omit,
        accept_self_signed_certificate: bool | Omit = omit,
        associated_cloud_account_ids: SequenceNotStr[str] | Omit = omit,
        associated_mobility_cloud_account_ids: Dict[str, Literal["UNIDIRECTIONAL", "BIDIRECTIONAL"]] | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        create_default_zones: bool | Omit = omit,
        dcid: str | Omit = omit,
        description: str | Omit = omit,
        environment: str | Omit = omit,
        password: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        username: str | Omit = omit,
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

          host_name: Host name for the vSphere endpoint

          name: A human-friendly name used as an identifier in APIs that support this option.

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          validate_only: If provided, it only validates the credentials in the Cloud Account
              Specification, and cloud account will not be created.

          accept_self_signed_certificate: Accept self signed certificate when connecting to vSphere

          associated_cloud_account_ids: NSX-V or NSX-T account to associate with this vSphere cloud account. vSphere
              cloud account can be a single NSX-V cloud account or a single NSX-T cloud
              account.

          associated_mobility_cloud_account_ids: Cloud account IDs and directionalities create associations to other vSphere
              cloud accounts that can be used for workload mobility. ID refers to an
              associated cloud account, and directionality can be unidirectional or
              bidirectional.

          certificate_info: Specification for certificate for a cloud account.

          create_default_zones: Create default cloud zones for the enabled regions.

          dcid: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors. Note: Data
              collector endpoints are not available in VMware Aria Automation (on-prem)
              release.

          description: A human-friendly description.

          environment: The environment where data collectors are deployed. When the data collectors are
              deployed on an aap-based cloud gateway appliance, use "aap".

          password: Password for the user used to authenticate with the cloud Account.

          tags: A set of tag keys and optional values to set on the Cloud Account

          username: Username to authenticate with the cloud account.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/cloud-accounts-vsphere",
            body=await async_maybe_transform(
                {
                    "host_name": host_name,
                    "name": name,
                    "regions": regions,
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "associated_cloud_account_ids": associated_cloud_account_ids,
                    "associated_mobility_cloud_account_ids": associated_mobility_cloud_account_ids,
                    "certificate_info": certificate_info,
                    "create_default_zones": create_default_zones,
                    "dcid": dcid,
                    "description": description,
                    "environment": environment,
                    "password": password,
                    "tags": tags,
                    "username": username,
                },
                cloud_accounts_vsphere_cloud_accounts_vsphere_params.CloudAccountsVsphereCloudAccountsVsphereParams,
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
                    cloud_accounts_vsphere_cloud_accounts_vsphere_params.CloudAccountsVsphereCloudAccountsVsphereParams,
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
        Enumerate all private images for enabled regions of the specified vSphere
        account

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
            f"/iaas/api/cloud-accounts-vsphere/{id}/private-image-enumeration",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_vsphere_private_image_enumeration_params.CloudAccountsVspherePrivateImageEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def region_enumeration(
        self,
        *,
        api_version: str,
        accept_self_signed_certificate: bool | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        cloud_account_id: str | Omit = omit,
        dcid: str | Omit = omit,
        environment: str | Omit = omit,
        host_name: str | Omit = omit,
        password: str | Omit = omit,
        username: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Get the available regions for specified vSphere cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          accept_self_signed_certificate: Accept self signed certificate when connecting to vSphere

          certificate_info: Specification for certificate for a cloud account.

          cloud_account_id: Existing cloud account id. Either provide existing cloud account Id, or
              hostName, username, password.

          dcid: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors. Note: Data
              collector endpoints are not available in VMware Aria Automation (on-prem)
              release.

          environment: The environment where data collectors are deployed. When the data collectors are
              deployed on a cloud gateway appliance, use "aap".

          host_name: Host name for the vSphere endpoint. Either provide hostName or provide a
              cloudAccountId of an existing account.

          password: Password for the user used to authenticate with the cloud Account. Either
              provide password or provide a cloudAccountId of an existing account.

          username: Username to authenticate with the cloud account. Either provide username or
              provide a cloudAccountId of an existing account.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/cloud-accounts-vsphere/region-enumeration",
            body=await async_maybe_transform(
                {
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "certificate_info": certificate_info,
                    "cloud_account_id": cloud_account_id,
                    "dcid": dcid,
                    "environment": environment,
                    "host_name": host_name,
                    "password": password,
                    "username": username,
                },
                cloud_accounts_vsphere_region_enumeration_params.CloudAccountsVsphereRegionEnumerationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_vsphere_region_enumeration_params.CloudAccountsVsphereRegionEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def retrieve_cloud_accounts_vsphere(
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
    ) -> CloudAccountsVsphereRetrieveCloudAccountsVsphereResponse:
        """
        Get all vSphere cloud accounts within the current organization

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
            "/iaas/api/cloud-accounts-vsphere",
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
                    cloud_accounts_vsphere_retrieve_cloud_accounts_vsphere_params.CloudAccountsVsphereRetrieveCloudAccountsVsphereParams,
                ),
            ),
            cast_to=CloudAccountsVsphereRetrieveCloudAccountsVsphereResponse,
        )


class CloudAccountsVsphereResourceWithRawResponse:
    def __init__(self, cloud_accounts_vsphere: CloudAccountsVsphereResource) -> None:
        self._cloud_accounts_vsphere = cloud_accounts_vsphere

        self.retrieve = to_raw_response_wrapper(
            cloud_accounts_vsphere.retrieve,
        )
        self.update = to_raw_response_wrapper(
            cloud_accounts_vsphere.update,
        )
        self.delete = to_raw_response_wrapper(
            cloud_accounts_vsphere.delete,
        )
        self.cloud_accounts_vsphere = to_raw_response_wrapper(
            cloud_accounts_vsphere.cloud_accounts_vsphere,
        )
        self.private_image_enumeration = to_raw_response_wrapper(
            cloud_accounts_vsphere.private_image_enumeration,
        )
        self.region_enumeration = to_raw_response_wrapper(
            cloud_accounts_vsphere.region_enumeration,
        )
        self.retrieve_cloud_accounts_vsphere = to_raw_response_wrapper(
            cloud_accounts_vsphere.retrieve_cloud_accounts_vsphere,
        )


class AsyncCloudAccountsVsphereResourceWithRawResponse:
    def __init__(self, cloud_accounts_vsphere: AsyncCloudAccountsVsphereResource) -> None:
        self._cloud_accounts_vsphere = cloud_accounts_vsphere

        self.retrieve = async_to_raw_response_wrapper(
            cloud_accounts_vsphere.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            cloud_accounts_vsphere.update,
        )
        self.delete = async_to_raw_response_wrapper(
            cloud_accounts_vsphere.delete,
        )
        self.cloud_accounts_vsphere = async_to_raw_response_wrapper(
            cloud_accounts_vsphere.cloud_accounts_vsphere,
        )
        self.private_image_enumeration = async_to_raw_response_wrapper(
            cloud_accounts_vsphere.private_image_enumeration,
        )
        self.region_enumeration = async_to_raw_response_wrapper(
            cloud_accounts_vsphere.region_enumeration,
        )
        self.retrieve_cloud_accounts_vsphere = async_to_raw_response_wrapper(
            cloud_accounts_vsphere.retrieve_cloud_accounts_vsphere,
        )


class CloudAccountsVsphereResourceWithStreamingResponse:
    def __init__(self, cloud_accounts_vsphere: CloudAccountsVsphereResource) -> None:
        self._cloud_accounts_vsphere = cloud_accounts_vsphere

        self.retrieve = to_streamed_response_wrapper(
            cloud_accounts_vsphere.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            cloud_accounts_vsphere.update,
        )
        self.delete = to_streamed_response_wrapper(
            cloud_accounts_vsphere.delete,
        )
        self.cloud_accounts_vsphere = to_streamed_response_wrapper(
            cloud_accounts_vsphere.cloud_accounts_vsphere,
        )
        self.private_image_enumeration = to_streamed_response_wrapper(
            cloud_accounts_vsphere.private_image_enumeration,
        )
        self.region_enumeration = to_streamed_response_wrapper(
            cloud_accounts_vsphere.region_enumeration,
        )
        self.retrieve_cloud_accounts_vsphere = to_streamed_response_wrapper(
            cloud_accounts_vsphere.retrieve_cloud_accounts_vsphere,
        )


class AsyncCloudAccountsVsphereResourceWithStreamingResponse:
    def __init__(self, cloud_accounts_vsphere: AsyncCloudAccountsVsphereResource) -> None:
        self._cloud_accounts_vsphere = cloud_accounts_vsphere

        self.retrieve = async_to_streamed_response_wrapper(
            cloud_accounts_vsphere.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            cloud_accounts_vsphere.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            cloud_accounts_vsphere.delete,
        )
        self.cloud_accounts_vsphere = async_to_streamed_response_wrapper(
            cloud_accounts_vsphere.cloud_accounts_vsphere,
        )
        self.private_image_enumeration = async_to_streamed_response_wrapper(
            cloud_accounts_vsphere.private_image_enumeration,
        )
        self.region_enumeration = async_to_streamed_response_wrapper(
            cloud_accounts_vsphere.region_enumeration,
        )
        self.retrieve_cloud_accounts_vsphere = async_to_streamed_response_wrapper(
            cloud_accounts_vsphere.retrieve_cloud_accounts_vsphere,
        )
