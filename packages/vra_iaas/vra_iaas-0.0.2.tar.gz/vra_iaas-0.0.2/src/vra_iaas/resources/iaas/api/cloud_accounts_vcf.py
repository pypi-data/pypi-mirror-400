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
    cloud_accounts_vcf_delete_params,
    cloud_accounts_vcf_update_params,
    cloud_accounts_vcf_retrieve_params,
    cloud_accounts_vcf_cloud_accounts_vcf_params,
    cloud_accounts_vcf_region_enumeration_params,
    cloud_accounts_vcf_private_image_enumeration_params,
    cloud_accounts_vcf_retrieve_cloud_accounts_vcf_params,
)
from ....types.iaas.api.tag_param import TagParam
from ....types.iaas.api.cloud_account_vcf import CloudAccountVcf
from ....types.iaas.api.projects.request_tracker import RequestTracker
from ....types.iaas.api.region_specification_param import RegionSpecificationParam
from ....types.iaas.api.certificate_info_specification_param import CertificateInfoSpecificationParam
from ....types.iaas.api.cloud_accounts_vcf_retrieve_cloud_accounts_vcf_response import (
    CloudAccountsVcfRetrieveCloudAccountsVcfResponse,
)

__all__ = ["CloudAccountsVcfResource", "AsyncCloudAccountsVcfResource"]


class CloudAccountsVcfResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CloudAccountsVcfResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return CloudAccountsVcfResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CloudAccountsVcfResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return CloudAccountsVcfResourceWithStreamingResponse(self)

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
    ) -> CloudAccountVcf:
        """
        Get an VCF cloud account with a given id

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
            f"/iaas/api/cloud-accounts-vcf/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_vcf_retrieve_params.CloudAccountsVcfRetrieveParams
                ),
            ),
            cast_to=CloudAccountVcf,
        )

    def update(
        self,
        id: str,
        *,
        api_version: str,
        name: str,
        nsx_host_name: str,
        nsx_password: str,
        nsx_username: str,
        regions: Iterable[RegionSpecificationParam],
        vcenter_host_name: str,
        vcenter_password: str,
        vcenter_username: str,
        workload_domain_id: str,
        workload_domain_name: str,
        accept_self_signed_certificate: bool | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        create_default_zones: bool | Omit = omit,
        dc_id: str | Omit = omit,
        description: str | Omit = omit,
        nsx_certificate: str | Omit = omit,
        sddc_manager_id: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        vcenter_certificate: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Update VCF cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          name: A human-friendly name used as an identifier in APIs that support this option.

          nsx_host_name: Host name for the NSX endpoint from the specified workload domain.

          nsx_password: Password for the user used to authenticate with the NSX-T manager in VCF cloud
              account

          nsx_username: User name for the NSX manager in the specified workload domain.

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          vcenter_host_name: Host name for the vSphere from the specified workload domain.

          vcenter_password: Password for the user used to authenticate with the vCenter in VCF cloud account

          vcenter_username: vCenter user name for the specified workload domain.The specified user requires
              CloudAdmin credentials. The user does not require CloudGlobalAdmin credentials.

          workload_domain_id: Id of the workload domain to add as VCF cloud account.

          workload_domain_name: Name of the workload domain to add as VCF cloud account.

          accept_self_signed_certificate: Accept self signed certificate when connecting to vSphere and NSX-T

          certificate_info: Specification for certificate for a cloud account.

          create_default_zones: Create default cloud zones for the enabled regions.

          dc_id: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors. Note: Data
              collector endpoints are not available in VMware Aria Automation (on-prem)
              release.

          description: A human-friendly description.

          nsx_certificate: NSX Certificate

          sddc_manager_id: SDDC manager integration id

          tags: A set of tag keys and optional values to set on the Cloud Account.Cloud account
              capability tags may enable different features.

          vcenter_certificate: vCenter Certificate

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/iaas/api/cloud-accounts-vcf/{id}",
            body=maybe_transform(
                {
                    "name": name,
                    "nsx_host_name": nsx_host_name,
                    "nsx_password": nsx_password,
                    "nsx_username": nsx_username,
                    "regions": regions,
                    "vcenter_host_name": vcenter_host_name,
                    "vcenter_password": vcenter_password,
                    "vcenter_username": vcenter_username,
                    "workload_domain_id": workload_domain_id,
                    "workload_domain_name": workload_domain_name,
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "certificate_info": certificate_info,
                    "create_default_zones": create_default_zones,
                    "dc_id": dc_id,
                    "description": description,
                    "nsx_certificate": nsx_certificate,
                    "sddc_manager_id": sddc_manager_id,
                    "tags": tags,
                    "vcenter_certificate": vcenter_certificate,
                },
                cloud_accounts_vcf_update_params.CloudAccountsVcfUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_vcf_update_params.CloudAccountsVcfUpdateParams
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
        Delete an VCF cloud account with a given id

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
            f"/iaas/api/cloud-accounts-vcf/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, cloud_accounts_vcf_delete_params.CloudAccountsVcfDeleteParams
                ),
            ),
            cast_to=RequestTracker,
        )

    def cloud_accounts_vcf(
        self,
        *,
        api_version: str,
        name: str,
        nsx_host_name: str,
        nsx_password: str,
        nsx_username: str,
        regions: Iterable[RegionSpecificationParam],
        vcenter_host_name: str,
        vcenter_password: str,
        vcenter_username: str,
        workload_domain_id: str,
        workload_domain_name: str,
        validate_only: str | Omit = omit,
        accept_self_signed_certificate: bool | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        create_default_zones: bool | Omit = omit,
        dc_id: str | Omit = omit,
        description: str | Omit = omit,
        nsx_certificate: str | Omit = omit,
        sddc_manager_id: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        vcenter_certificate: str | Omit = omit,
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

          nsx_host_name: Host name for the NSX endpoint from the specified workload domain.

          nsx_password: Password for the user used to authenticate with the NSX-T manager in VCF cloud
              account

          nsx_username: User name for the NSX manager in the specified workload domain.

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          vcenter_host_name: Host name for the vSphere from the specified workload domain.

          vcenter_password: Password for the user used to authenticate with the vCenter in VCF cloud account

          vcenter_username: vCenter user name for the specified workload domain.The specified user requires
              CloudAdmin credentials. The user does not require CloudGlobalAdmin credentials.

          workload_domain_id: Id of the workload domain to add as VCF cloud account.

          workload_domain_name: Name of the workload domain to add as VCF cloud account.

          validate_only: If provided, it only validates the credentials in the Cloud Account
              Specification, and cloud account will not be created.

          accept_self_signed_certificate: Accept self signed certificate when connecting to vSphere and NSX-T

          certificate_info: Specification for certificate for a cloud account.

          create_default_zones: Create default cloud zones for the enabled regions.

          dc_id: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors. Note: Data
              collector endpoints are not available in VMware Aria Automation (on-prem)
              release.

          description: A human-friendly description.

          nsx_certificate: NSX Certificate

          sddc_manager_id: SDDC manager integration id

          tags: A set of tag keys and optional values to set on the Cloud Account.Cloud account
              capability tags may enable different features.

          vcenter_certificate: vCenter Certificate

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/cloud-accounts-vcf",
            body=maybe_transform(
                {
                    "name": name,
                    "nsx_host_name": nsx_host_name,
                    "nsx_password": nsx_password,
                    "nsx_username": nsx_username,
                    "regions": regions,
                    "vcenter_host_name": vcenter_host_name,
                    "vcenter_password": vcenter_password,
                    "vcenter_username": vcenter_username,
                    "workload_domain_id": workload_domain_id,
                    "workload_domain_name": workload_domain_name,
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "certificate_info": certificate_info,
                    "create_default_zones": create_default_zones,
                    "dc_id": dc_id,
                    "description": description,
                    "nsx_certificate": nsx_certificate,
                    "sddc_manager_id": sddc_manager_id,
                    "tags": tags,
                    "vcenter_certificate": vcenter_certificate,
                },
                cloud_accounts_vcf_cloud_accounts_vcf_params.CloudAccountsVcfCloudAccountsVcfParams,
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
                    cloud_accounts_vcf_cloud_accounts_vcf_params.CloudAccountsVcfCloudAccountsVcfParams,
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
        Enumerate all private images for enabled regions of the specified VCF account

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
            f"/iaas/api/cloud-accounts-vcf/{id}/private-image-enumeration",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_vcf_private_image_enumeration_params.CloudAccountsVcfPrivateImageEnumerationParams,
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
        dc_id: str | Omit = omit,
        nsx_certificate: str | Omit = omit,
        nsx_host_name: str | Omit = omit,
        nsx_password: str | Omit = omit,
        nsx_username: str | Omit = omit,
        sddc_manager_id: str | Omit = omit,
        vcenter_certificate: str | Omit = omit,
        vcenter_host_name: str | Omit = omit,
        vcenter_password: str | Omit = omit,
        vcenter_username: str | Omit = omit,
        workload_domain_id: str | Omit = omit,
        workload_domain_name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Get the available regions for specified VCF cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          accept_self_signed_certificate: Accept self signed certificate when connecting to vSphere and NSX-T

          certificate_info: Specification for certificate for a cloud account.

          cloud_account_id: Existing cloud account id. Either provide existing cloud account Id, or
              workloadDomainId, workloadDomainName, vcenterHostName, vcenterUsername,
              vcenterPassword, nsxHostName, nsxUsername and nsxPassword.

          dc_id: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors. Note: Data
              collector endpoints are not available in VMware Aria Automation (on-prem)
              release.

          nsx_certificate: NSX Certificate

          nsx_host_name: Host name for the NSX endpoint from the specified workload domain. Either
              provide nsxHostName or provide a cloudAccountId of an existing account.

          nsx_password: Password for the user used to authenticate with the NSX-T manager in VCF cloud
              account. Either provide nsxPassword or provide a cloudAccountId of an existing
              account.

          nsx_username: User name for the NSX manager in the specified workload domain. Either provide
              nsxUsername or provide a cloudAccountId of an existing account.

          sddc_manager_id: SDDC manager integration id. Either provide sddcManagerId or provide a
              cloudAccountId of an existing account.

          vcenter_certificate: vCenter Certificate

          vcenter_host_name: Host name for the vSphere from the specified workload domain. Either provide
              vcenterHostName or provide a cloudAccountId of an existing account.

          vcenter_password: Password for the user used to authenticate with the vCenter in VCF cloud
              account. Either provide vcenterPassword or provide a cloudAccountId of an
              existing account.

          vcenter_username: vCenter user name for the specified workload domain.The specified user requires
              CloudAdmin credentials. The user does not require CloudGlobalAdmin credentials.

          workload_domain_id: Id of the workload domain to add as VCF cloud account. Either provide
              workloadDomainId or provide a cloudAccountId of an existing account.

          workload_domain_name: Name of the workload domain to add as VCF cloud account. Either provide
              workloadDomainName or provide a cloudAccountId of an existing account.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/iaas/api/cloud-accounts-vcf/region-enumeration",
            body=maybe_transform(
                {
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "certificate_info": certificate_info,
                    "cloud_account_id": cloud_account_id,
                    "dc_id": dc_id,
                    "nsx_certificate": nsx_certificate,
                    "nsx_host_name": nsx_host_name,
                    "nsx_password": nsx_password,
                    "nsx_username": nsx_username,
                    "sddc_manager_id": sddc_manager_id,
                    "vcenter_certificate": vcenter_certificate,
                    "vcenter_host_name": vcenter_host_name,
                    "vcenter_password": vcenter_password,
                    "vcenter_username": vcenter_username,
                    "workload_domain_id": workload_domain_id,
                    "workload_domain_name": workload_domain_name,
                },
                cloud_accounts_vcf_region_enumeration_params.CloudAccountsVcfRegionEnumerationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_vcf_region_enumeration_params.CloudAccountsVcfRegionEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    def retrieve_cloud_accounts_vcf(
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
    ) -> CloudAccountsVcfRetrieveCloudAccountsVcfResponse:
        """
        Get all VCF cloud accounts within the current organization

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
            "/iaas/api/cloud-accounts-vcf",
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
                    cloud_accounts_vcf_retrieve_cloud_accounts_vcf_params.CloudAccountsVcfRetrieveCloudAccountsVcfParams,
                ),
            ),
            cast_to=CloudAccountsVcfRetrieveCloudAccountsVcfResponse,
        )


class AsyncCloudAccountsVcfResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCloudAccountsVcfResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCloudAccountsVcfResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCloudAccountsVcfResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncCloudAccountsVcfResourceWithStreamingResponse(self)

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
    ) -> CloudAccountVcf:
        """
        Get an VCF cloud account with a given id

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
            f"/iaas/api/cloud-accounts-vcf/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_vcf_retrieve_params.CloudAccountsVcfRetrieveParams
                ),
            ),
            cast_to=CloudAccountVcf,
        )

    async def update(
        self,
        id: str,
        *,
        api_version: str,
        name: str,
        nsx_host_name: str,
        nsx_password: str,
        nsx_username: str,
        regions: Iterable[RegionSpecificationParam],
        vcenter_host_name: str,
        vcenter_password: str,
        vcenter_username: str,
        workload_domain_id: str,
        workload_domain_name: str,
        accept_self_signed_certificate: bool | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        create_default_zones: bool | Omit = omit,
        dc_id: str | Omit = omit,
        description: str | Omit = omit,
        nsx_certificate: str | Omit = omit,
        sddc_manager_id: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        vcenter_certificate: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Update VCF cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          name: A human-friendly name used as an identifier in APIs that support this option.

          nsx_host_name: Host name for the NSX endpoint from the specified workload domain.

          nsx_password: Password for the user used to authenticate with the NSX-T manager in VCF cloud
              account

          nsx_username: User name for the NSX manager in the specified workload domain.

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          vcenter_host_name: Host name for the vSphere from the specified workload domain.

          vcenter_password: Password for the user used to authenticate with the vCenter in VCF cloud account

          vcenter_username: vCenter user name for the specified workload domain.The specified user requires
              CloudAdmin credentials. The user does not require CloudGlobalAdmin credentials.

          workload_domain_id: Id of the workload domain to add as VCF cloud account.

          workload_domain_name: Name of the workload domain to add as VCF cloud account.

          accept_self_signed_certificate: Accept self signed certificate when connecting to vSphere and NSX-T

          certificate_info: Specification for certificate for a cloud account.

          create_default_zones: Create default cloud zones for the enabled regions.

          dc_id: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors. Note: Data
              collector endpoints are not available in VMware Aria Automation (on-prem)
              release.

          description: A human-friendly description.

          nsx_certificate: NSX Certificate

          sddc_manager_id: SDDC manager integration id

          tags: A set of tag keys and optional values to set on the Cloud Account.Cloud account
              capability tags may enable different features.

          vcenter_certificate: vCenter Certificate

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/iaas/api/cloud-accounts-vcf/{id}",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "nsx_host_name": nsx_host_name,
                    "nsx_password": nsx_password,
                    "nsx_username": nsx_username,
                    "regions": regions,
                    "vcenter_host_name": vcenter_host_name,
                    "vcenter_password": vcenter_password,
                    "vcenter_username": vcenter_username,
                    "workload_domain_id": workload_domain_id,
                    "workload_domain_name": workload_domain_name,
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "certificate_info": certificate_info,
                    "create_default_zones": create_default_zones,
                    "dc_id": dc_id,
                    "description": description,
                    "nsx_certificate": nsx_certificate,
                    "sddc_manager_id": sddc_manager_id,
                    "tags": tags,
                    "vcenter_certificate": vcenter_certificate,
                },
                cloud_accounts_vcf_update_params.CloudAccountsVcfUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_vcf_update_params.CloudAccountsVcfUpdateParams
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
        Delete an VCF cloud account with a given id

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
            f"/iaas/api/cloud-accounts-vcf/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, cloud_accounts_vcf_delete_params.CloudAccountsVcfDeleteParams
                ),
            ),
            cast_to=RequestTracker,
        )

    async def cloud_accounts_vcf(
        self,
        *,
        api_version: str,
        name: str,
        nsx_host_name: str,
        nsx_password: str,
        nsx_username: str,
        regions: Iterable[RegionSpecificationParam],
        vcenter_host_name: str,
        vcenter_password: str,
        vcenter_username: str,
        workload_domain_id: str,
        workload_domain_name: str,
        validate_only: str | Omit = omit,
        accept_self_signed_certificate: bool | Omit = omit,
        certificate_info: CertificateInfoSpecificationParam | Omit = omit,
        create_default_zones: bool | Omit = omit,
        dc_id: str | Omit = omit,
        description: str | Omit = omit,
        nsx_certificate: str | Omit = omit,
        sddc_manager_id: str | Omit = omit,
        tags: Iterable[TagParam] | Omit = omit,
        vcenter_certificate: str | Omit = omit,
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

          nsx_host_name: Host name for the NSX endpoint from the specified workload domain.

          nsx_password: Password for the user used to authenticate with the NSX-T manager in VCF cloud
              account

          nsx_username: User name for the NSX manager in the specified workload domain.

          regions: A set of regions to enable provisioning on.Refer to
              /iaas/api/cloud-accounts/region-enumeration.

          vcenter_host_name: Host name for the vSphere from the specified workload domain.

          vcenter_password: Password for the user used to authenticate with the vCenter in VCF cloud account

          vcenter_username: vCenter user name for the specified workload domain.The specified user requires
              CloudAdmin credentials. The user does not require CloudGlobalAdmin credentials.

          workload_domain_id: Id of the workload domain to add as VCF cloud account.

          workload_domain_name: Name of the workload domain to add as VCF cloud account.

          validate_only: If provided, it only validates the credentials in the Cloud Account
              Specification, and cloud account will not be created.

          accept_self_signed_certificate: Accept self signed certificate when connecting to vSphere and NSX-T

          certificate_info: Specification for certificate for a cloud account.

          create_default_zones: Create default cloud zones for the enabled regions.

          dc_id: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors. Note: Data
              collector endpoints are not available in VMware Aria Automation (on-prem)
              release.

          description: A human-friendly description.

          nsx_certificate: NSX Certificate

          sddc_manager_id: SDDC manager integration id

          tags: A set of tag keys and optional values to set on the Cloud Account.Cloud account
              capability tags may enable different features.

          vcenter_certificate: vCenter Certificate

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/cloud-accounts-vcf",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "nsx_host_name": nsx_host_name,
                    "nsx_password": nsx_password,
                    "nsx_username": nsx_username,
                    "regions": regions,
                    "vcenter_host_name": vcenter_host_name,
                    "vcenter_password": vcenter_password,
                    "vcenter_username": vcenter_username,
                    "workload_domain_id": workload_domain_id,
                    "workload_domain_name": workload_domain_name,
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "certificate_info": certificate_info,
                    "create_default_zones": create_default_zones,
                    "dc_id": dc_id,
                    "description": description,
                    "nsx_certificate": nsx_certificate,
                    "sddc_manager_id": sddc_manager_id,
                    "tags": tags,
                    "vcenter_certificate": vcenter_certificate,
                },
                cloud_accounts_vcf_cloud_accounts_vcf_params.CloudAccountsVcfCloudAccountsVcfParams,
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
                    cloud_accounts_vcf_cloud_accounts_vcf_params.CloudAccountsVcfCloudAccountsVcfParams,
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
        Enumerate all private images for enabled regions of the specified VCF account

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
            f"/iaas/api/cloud-accounts-vcf/{id}/private-image-enumeration",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_vcf_private_image_enumeration_params.CloudAccountsVcfPrivateImageEnumerationParams,
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
        dc_id: str | Omit = omit,
        nsx_certificate: str | Omit = omit,
        nsx_host_name: str | Omit = omit,
        nsx_password: str | Omit = omit,
        nsx_username: str | Omit = omit,
        sddc_manager_id: str | Omit = omit,
        vcenter_certificate: str | Omit = omit,
        vcenter_host_name: str | Omit = omit,
        vcenter_password: str | Omit = omit,
        vcenter_username: str | Omit = omit,
        workload_domain_id: str | Omit = omit,
        workload_domain_name: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RequestTracker:
        """
        Get the available regions for specified VCF cloud account

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          accept_self_signed_certificate: Accept self signed certificate when connecting to vSphere and NSX-T

          certificate_info: Specification for certificate for a cloud account.

          cloud_account_id: Existing cloud account id. Either provide existing cloud account Id, or
              workloadDomainId, workloadDomainName, vcenterHostName, vcenterUsername,
              vcenterPassword, nsxHostName, nsxUsername and nsxPassword.

          dc_id: Identifier of a data collector vm deployed in the on premise infrastructure.
              Refer to the data-collector API to create or list data collectors. Note: Data
              collector endpoints are not available in VMware Aria Automation (on-prem)
              release.

          nsx_certificate: NSX Certificate

          nsx_host_name: Host name for the NSX endpoint from the specified workload domain. Either
              provide nsxHostName or provide a cloudAccountId of an existing account.

          nsx_password: Password for the user used to authenticate with the NSX-T manager in VCF cloud
              account. Either provide nsxPassword or provide a cloudAccountId of an existing
              account.

          nsx_username: User name for the NSX manager in the specified workload domain. Either provide
              nsxUsername or provide a cloudAccountId of an existing account.

          sddc_manager_id: SDDC manager integration id. Either provide sddcManagerId or provide a
              cloudAccountId of an existing account.

          vcenter_certificate: vCenter Certificate

          vcenter_host_name: Host name for the vSphere from the specified workload domain. Either provide
              vcenterHostName or provide a cloudAccountId of an existing account.

          vcenter_password: Password for the user used to authenticate with the vCenter in VCF cloud
              account. Either provide vcenterPassword or provide a cloudAccountId of an
              existing account.

          vcenter_username: vCenter user name for the specified workload domain.The specified user requires
              CloudAdmin credentials. The user does not require CloudGlobalAdmin credentials.

          workload_domain_id: Id of the workload domain to add as VCF cloud account. Either provide
              workloadDomainId or provide a cloudAccountId of an existing account.

          workload_domain_name: Name of the workload domain to add as VCF cloud account. Either provide
              workloadDomainName or provide a cloudAccountId of an existing account.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/iaas/api/cloud-accounts-vcf/region-enumeration",
            body=await async_maybe_transform(
                {
                    "accept_self_signed_certificate": accept_self_signed_certificate,
                    "certificate_info": certificate_info,
                    "cloud_account_id": cloud_account_id,
                    "dc_id": dc_id,
                    "nsx_certificate": nsx_certificate,
                    "nsx_host_name": nsx_host_name,
                    "nsx_password": nsx_password,
                    "nsx_username": nsx_username,
                    "sddc_manager_id": sddc_manager_id,
                    "vcenter_certificate": vcenter_certificate,
                    "vcenter_host_name": vcenter_host_name,
                    "vcenter_password": vcenter_password,
                    "vcenter_username": vcenter_username,
                    "workload_domain_id": workload_domain_id,
                    "workload_domain_name": workload_domain_name,
                },
                cloud_accounts_vcf_region_enumeration_params.CloudAccountsVcfRegionEnumerationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version},
                    cloud_accounts_vcf_region_enumeration_params.CloudAccountsVcfRegionEnumerationParams,
                ),
            ),
            cast_to=RequestTracker,
        )

    async def retrieve_cloud_accounts_vcf(
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
    ) -> CloudAccountsVcfRetrieveCloudAccountsVcfResponse:
        """
        Get all VCF cloud accounts within the current organization

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
            "/iaas/api/cloud-accounts-vcf",
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
                    cloud_accounts_vcf_retrieve_cloud_accounts_vcf_params.CloudAccountsVcfRetrieveCloudAccountsVcfParams,
                ),
            ),
            cast_to=CloudAccountsVcfRetrieveCloudAccountsVcfResponse,
        )


class CloudAccountsVcfResourceWithRawResponse:
    def __init__(self, cloud_accounts_vcf: CloudAccountsVcfResource) -> None:
        self._cloud_accounts_vcf = cloud_accounts_vcf

        self.retrieve = to_raw_response_wrapper(
            cloud_accounts_vcf.retrieve,
        )
        self.update = to_raw_response_wrapper(
            cloud_accounts_vcf.update,
        )
        self.delete = to_raw_response_wrapper(
            cloud_accounts_vcf.delete,
        )
        self.cloud_accounts_vcf = to_raw_response_wrapper(
            cloud_accounts_vcf.cloud_accounts_vcf,
        )
        self.private_image_enumeration = to_raw_response_wrapper(
            cloud_accounts_vcf.private_image_enumeration,
        )
        self.region_enumeration = to_raw_response_wrapper(
            cloud_accounts_vcf.region_enumeration,
        )
        self.retrieve_cloud_accounts_vcf = to_raw_response_wrapper(
            cloud_accounts_vcf.retrieve_cloud_accounts_vcf,
        )


class AsyncCloudAccountsVcfResourceWithRawResponse:
    def __init__(self, cloud_accounts_vcf: AsyncCloudAccountsVcfResource) -> None:
        self._cloud_accounts_vcf = cloud_accounts_vcf

        self.retrieve = async_to_raw_response_wrapper(
            cloud_accounts_vcf.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            cloud_accounts_vcf.update,
        )
        self.delete = async_to_raw_response_wrapper(
            cloud_accounts_vcf.delete,
        )
        self.cloud_accounts_vcf = async_to_raw_response_wrapper(
            cloud_accounts_vcf.cloud_accounts_vcf,
        )
        self.private_image_enumeration = async_to_raw_response_wrapper(
            cloud_accounts_vcf.private_image_enumeration,
        )
        self.region_enumeration = async_to_raw_response_wrapper(
            cloud_accounts_vcf.region_enumeration,
        )
        self.retrieve_cloud_accounts_vcf = async_to_raw_response_wrapper(
            cloud_accounts_vcf.retrieve_cloud_accounts_vcf,
        )


class CloudAccountsVcfResourceWithStreamingResponse:
    def __init__(self, cloud_accounts_vcf: CloudAccountsVcfResource) -> None:
        self._cloud_accounts_vcf = cloud_accounts_vcf

        self.retrieve = to_streamed_response_wrapper(
            cloud_accounts_vcf.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            cloud_accounts_vcf.update,
        )
        self.delete = to_streamed_response_wrapper(
            cloud_accounts_vcf.delete,
        )
        self.cloud_accounts_vcf = to_streamed_response_wrapper(
            cloud_accounts_vcf.cloud_accounts_vcf,
        )
        self.private_image_enumeration = to_streamed_response_wrapper(
            cloud_accounts_vcf.private_image_enumeration,
        )
        self.region_enumeration = to_streamed_response_wrapper(
            cloud_accounts_vcf.region_enumeration,
        )
        self.retrieve_cloud_accounts_vcf = to_streamed_response_wrapper(
            cloud_accounts_vcf.retrieve_cloud_accounts_vcf,
        )


class AsyncCloudAccountsVcfResourceWithStreamingResponse:
    def __init__(self, cloud_accounts_vcf: AsyncCloudAccountsVcfResource) -> None:
        self._cloud_accounts_vcf = cloud_accounts_vcf

        self.retrieve = async_to_streamed_response_wrapper(
            cloud_accounts_vcf.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            cloud_accounts_vcf.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            cloud_accounts_vcf.delete,
        )
        self.cloud_accounts_vcf = async_to_streamed_response_wrapper(
            cloud_accounts_vcf.cloud_accounts_vcf,
        )
        self.private_image_enumeration = async_to_streamed_response_wrapper(
            cloud_accounts_vcf.private_image_enumeration,
        )
        self.region_enumeration = async_to_streamed_response_wrapper(
            cloud_accounts_vcf.region_enumeration,
        )
        self.retrieve_cloud_accounts_vcf = async_to_streamed_response_wrapper(
            cloud_accounts_vcf.retrieve_cloud_accounts_vcf,
        )
