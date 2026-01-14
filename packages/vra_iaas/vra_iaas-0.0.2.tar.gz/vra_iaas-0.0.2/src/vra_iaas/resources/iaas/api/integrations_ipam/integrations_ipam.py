# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from .package_import import (
    PackageImportResource,
    AsyncPackageImportResource,
    PackageImportResourceWithRawResponse,
    AsyncPackageImportResourceWithRawResponse,
    PackageImportResourceWithStreamingResponse,
    AsyncPackageImportResourceWithStreamingResponse,
)

__all__ = ["IntegrationsIpamResource", "AsyncIntegrationsIpamResource"]


class IntegrationsIpamResource(SyncAPIResource):
    @cached_property
    def package_import(self) -> PackageImportResource:
        return PackageImportResource(self._client)

    @cached_property
    def with_raw_response(self) -> IntegrationsIpamResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return IntegrationsIpamResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IntegrationsIpamResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return IntegrationsIpamResourceWithStreamingResponse(self)


class AsyncIntegrationsIpamResource(AsyncAPIResource):
    @cached_property
    def package_import(self) -> AsyncPackageImportResource:
        return AsyncPackageImportResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncIntegrationsIpamResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncIntegrationsIpamResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIntegrationsIpamResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncIntegrationsIpamResourceWithStreamingResponse(self)


class IntegrationsIpamResourceWithRawResponse:
    def __init__(self, integrations_ipam: IntegrationsIpamResource) -> None:
        self._integrations_ipam = integrations_ipam

    @cached_property
    def package_import(self) -> PackageImportResourceWithRawResponse:
        return PackageImportResourceWithRawResponse(self._integrations_ipam.package_import)


class AsyncIntegrationsIpamResourceWithRawResponse:
    def __init__(self, integrations_ipam: AsyncIntegrationsIpamResource) -> None:
        self._integrations_ipam = integrations_ipam

    @cached_property
    def package_import(self) -> AsyncPackageImportResourceWithRawResponse:
        return AsyncPackageImportResourceWithRawResponse(self._integrations_ipam.package_import)


class IntegrationsIpamResourceWithStreamingResponse:
    def __init__(self, integrations_ipam: IntegrationsIpamResource) -> None:
        self._integrations_ipam = integrations_ipam

    @cached_property
    def package_import(self) -> PackageImportResourceWithStreamingResponse:
        return PackageImportResourceWithStreamingResponse(self._integrations_ipam.package_import)


class AsyncIntegrationsIpamResourceWithStreamingResponse:
    def __init__(self, integrations_ipam: AsyncIntegrationsIpamResource) -> None:
        self._integrations_ipam = integrations_ipam

    @cached_property
    def package_import(self) -> AsyncPackageImportResourceWithStreamingResponse:
        return AsyncPackageImportResourceWithStreamingResponse(self._integrations_ipam.package_import)
