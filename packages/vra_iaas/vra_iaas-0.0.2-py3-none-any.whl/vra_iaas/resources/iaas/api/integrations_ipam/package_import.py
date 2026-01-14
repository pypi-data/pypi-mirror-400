# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from typing_extensions import Literal

import httpx

from ....._types import (
    Body,
    Omit,
    Query,
    Headers,
    NoneType,
    NotGiven,
    FileTypes,
    Base64FileInput,
    omit,
    not_given,
)
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
from .....types.iaas.api.integrations_ipam import package_import_update_params, package_import_package_import_params
from .....types.iaas.api.integrations_ipam.package_import_package_import_response import (
    PackageImportPackageImportResponse,
)

__all__ = ["PackageImportResource", "AsyncPackageImportResource"]


class PackageImportResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PackageImportResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return PackageImportResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PackageImportResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return PackageImportResourceWithStreamingResponse(self)

    def update(
        self,
        id: str,
        *,
        tus_resumable: str,
        upload_offset: str,
        api_version: str | Omit = omit,
        body: FileTypes | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Import IPAM package on chunks of specified size.

        This API implements the TUS
        RFC: https://github.com/tus/tus-resumable-upload-protocol/blob/main/protocol.md

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
        extra_headers.update({"Tus-Resumable": tus_resumable, "Upload-Offset": upload_offset})
        return self._patch(
            f"/iaas/api/integrations-ipam/package-import/{id}",
            body=maybe_transform(body, package_import_update_params.PackageImportUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, package_import_update_params.PackageImportUpdateParams
                ),
            ),
            cast_to=NoneType,
        )

    def package_import(
        self,
        *,
        tus_resumable: str,
        upload_length: str,
        api_version: str | Omit = omit,
        bundle_id: str | Omit = omit,
        compressed_bundle: Union[str, Base64FileInput] | Omit = omit,
        option: Literal["FAIL", "OVERWRITE"] | Omit = omit,
        properties: Dict[str, str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PackageImportPackageImportResponse:
        """This operation has two purposes:

        1.

        Make initial request for importing package. Location of the new package is
           returned as a response header if body is not provided.
        2. Finalize the import when all batches are sent to the server if bundleIdis
           provided or make the complete import if compressedBundle is provided

        This API implements the TUS RFC:
        https://github.com/tus/tus-resumable-upload-protocol/blob/main/protocol.md

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Tus-Resumable": tus_resumable, "Upload-Length": upload_length, **(extra_headers or {})}
        return self._post(
            "/iaas/api/integrations-ipam/package-import",
            body=maybe_transform(
                {
                    "bundle_id": bundle_id,
                    "compressed_bundle": compressed_bundle,
                    "option": option,
                    "properties": properties,
                },
                package_import_package_import_params.PackageImportPackageImportParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"api_version": api_version}, package_import_package_import_params.PackageImportPackageImportParams
                ),
            ),
            cast_to=PackageImportPackageImportResponse,
        )


class AsyncPackageImportResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPackageImportResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPackageImportResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPackageImportResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncPackageImportResourceWithStreamingResponse(self)

    async def update(
        self,
        id: str,
        *,
        tus_resumable: str,
        upload_offset: str,
        api_version: str | Omit = omit,
        body: FileTypes | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Import IPAM package on chunks of specified size.

        This API implements the TUS
        RFC: https://github.com/tus/tus-resumable-upload-protocol/blob/main/protocol.md

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
        extra_headers.update({"Tus-Resumable": tus_resumable, "Upload-Offset": upload_offset})
        return await self._patch(
            f"/iaas/api/integrations-ipam/package-import/{id}",
            body=await async_maybe_transform(body, package_import_update_params.PackageImportUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, package_import_update_params.PackageImportUpdateParams
                ),
            ),
            cast_to=NoneType,
        )

    async def package_import(
        self,
        *,
        tus_resumable: str,
        upload_length: str,
        api_version: str | Omit = omit,
        bundle_id: str | Omit = omit,
        compressed_bundle: Union[str, Base64FileInput] | Omit = omit,
        option: Literal["FAIL", "OVERWRITE"] | Omit = omit,
        properties: Dict[str, str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PackageImportPackageImportResponse:
        """This operation has two purposes:

        1.

        Make initial request for importing package. Location of the new package is
           returned as a response header if body is not provided.
        2. Finalize the import when all batches are sent to the server if bundleIdis
           provided or make the complete import if compressedBundle is provided

        This API implements the TUS RFC:
        https://github.com/tus/tus-resumable-upload-protocol/blob/main/protocol.md

        Args:
          api_version: The version of the API in yyyy-MM-dd format (UTC). For versioning information
              refer to /iaas/api/about

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Tus-Resumable": tus_resumable, "Upload-Length": upload_length, **(extra_headers or {})}
        return await self._post(
            "/iaas/api/integrations-ipam/package-import",
            body=await async_maybe_transform(
                {
                    "bundle_id": bundle_id,
                    "compressed_bundle": compressed_bundle,
                    "option": option,
                    "properties": properties,
                },
                package_import_package_import_params.PackageImportPackageImportParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"api_version": api_version}, package_import_package_import_params.PackageImportPackageImportParams
                ),
            ),
            cast_to=PackageImportPackageImportResponse,
        )


class PackageImportResourceWithRawResponse:
    def __init__(self, package_import: PackageImportResource) -> None:
        self._package_import = package_import

        self.update = to_raw_response_wrapper(
            package_import.update,
        )
        self.package_import = to_raw_response_wrapper(
            package_import.package_import,
        )


class AsyncPackageImportResourceWithRawResponse:
    def __init__(self, package_import: AsyncPackageImportResource) -> None:
        self._package_import = package_import

        self.update = async_to_raw_response_wrapper(
            package_import.update,
        )
        self.package_import = async_to_raw_response_wrapper(
            package_import.package_import,
        )


class PackageImportResourceWithStreamingResponse:
    def __init__(self, package_import: PackageImportResource) -> None:
        self._package_import = package_import

        self.update = to_streamed_response_wrapper(
            package_import.update,
        )
        self.package_import = to_streamed_response_wrapper(
            package_import.package_import,
        )


class AsyncPackageImportResourceWithStreamingResponse:
    def __init__(self, package_import: AsyncPackageImportResource) -> None:
        self._package_import = package_import

        self.update = async_to_streamed_response_wrapper(
            package_import.update,
        )
        self.package_import = async_to_streamed_response_wrapper(
            package_import.package_import,
        )
