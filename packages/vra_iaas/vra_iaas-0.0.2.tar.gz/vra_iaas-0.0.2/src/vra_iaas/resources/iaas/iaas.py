# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .api.api import (
    APIResource,
    AsyncAPIResource as APIAsyncAPIResource,
    APIResourceWithRawResponse,
    AsyncAPIResourceWithRawResponse,
    APIResourceWithStreamingResponse,
    AsyncAPIResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource as _ResourceAsyncAPIResource

__all__ = ["IaasResource", "AsyncIaasResource"]


class IaasResource(SyncAPIResource):
    @cached_property
    def api(self) -> APIResource:
        return APIResource(self._client)

    @cached_property
    def with_raw_response(self) -> IaasResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return IaasResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IaasResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return IaasResourceWithStreamingResponse(self)


class AsyncIaasResource(_ResourceAsyncAPIResource):
    @cached_property
    def api(self) -> APIAsyncAPIResource:
        return APIAsyncAPIResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncIaasResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#accessing-raw-response-data-eg-headers
        """
        return AsyncIaasResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIaasResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/imtrinity94/vra-iaas-mcp-python#with_streaming_response
        """
        return AsyncIaasResourceWithStreamingResponse(self)


class IaasResourceWithRawResponse:
    def __init__(self, iaas: IaasResource) -> None:
        self._iaas = iaas

    @cached_property
    def api(self) -> APIResourceWithRawResponse:
        return APIResourceWithRawResponse(self._iaas.api)


class AsyncIaasResourceWithRawResponse:
    def __init__(self, iaas: AsyncIaasResource) -> None:
        self._iaas = iaas

    @cached_property
    def api(self) -> AsyncAPIResourceWithRawResponse:
        return AsyncAPIResourceWithRawResponse(self._iaas.api)


class IaasResourceWithStreamingResponse:
    def __init__(self, iaas: IaasResource) -> None:
        self._iaas = iaas

    @cached_property
    def api(self) -> APIResourceWithStreamingResponse:
        return APIResourceWithStreamingResponse(self._iaas.api)


class AsyncIaasResourceWithStreamingResponse:
    def __init__(self, iaas: AsyncIaasResource) -> None:
        self._iaas = iaas

    @cached_property
    def api(self) -> AsyncAPIResourceWithStreamingResponse:
        return AsyncAPIResourceWithStreamingResponse(self._iaas.api)
