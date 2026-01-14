# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import Project
from vra_iaas.types.iaas.api.projects import (
    ResourceMetadataRetrieveResourceMetadataResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestResourceMetadata:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_resource_metadata(self, client: VraIaas) -> None:
        resource_metadata = client.iaas.api.projects.resource_metadata.retrieve_resource_metadata(
            id="id",
        )
        assert_matches_type(ResourceMetadataRetrieveResourceMetadataResponse, resource_metadata, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_resource_metadata_with_all_params(self, client: VraIaas) -> None:
        resource_metadata = client.iaas.api.projects.resource_metadata.retrieve_resource_metadata(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(ResourceMetadataRetrieveResourceMetadataResponse, resource_metadata, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_resource_metadata(self, client: VraIaas) -> None:
        response = client.iaas.api.projects.resource_metadata.with_raw_response.retrieve_resource_metadata(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        resource_metadata = response.parse()
        assert_matches_type(ResourceMetadataRetrieveResourceMetadataResponse, resource_metadata, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_resource_metadata(self, client: VraIaas) -> None:
        with client.iaas.api.projects.resource_metadata.with_streaming_response.retrieve_resource_metadata(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            resource_metadata = response.parse()
            assert_matches_type(ResourceMetadataRetrieveResourceMetadataResponse, resource_metadata, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_resource_metadata(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.projects.resource_metadata.with_raw_response.retrieve_resource_metadata(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_resource_metadata(self, client: VraIaas) -> None:
        resource_metadata = client.iaas.api.projects.resource_metadata.update_resource_metadata(
            id="id",
        )
        assert_matches_type(Project, resource_metadata, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_resource_metadata_with_all_params(self, client: VraIaas) -> None:
        resource_metadata = client.iaas.api.projects.resource_metadata.update_resource_metadata(
            id="id",
            api_version="apiVersion",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
        )
        assert_matches_type(Project, resource_metadata, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_resource_metadata(self, client: VraIaas) -> None:
        response = client.iaas.api.projects.resource_metadata.with_raw_response.update_resource_metadata(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        resource_metadata = response.parse()
        assert_matches_type(Project, resource_metadata, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_resource_metadata(self, client: VraIaas) -> None:
        with client.iaas.api.projects.resource_metadata.with_streaming_response.update_resource_metadata(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            resource_metadata = response.parse()
            assert_matches_type(Project, resource_metadata, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_resource_metadata(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.projects.resource_metadata.with_raw_response.update_resource_metadata(
                id="",
            )


class TestAsyncResourceMetadata:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_resource_metadata(self, async_client: AsyncVraIaas) -> None:
        resource_metadata = await async_client.iaas.api.projects.resource_metadata.retrieve_resource_metadata(
            id="id",
        )
        assert_matches_type(ResourceMetadataRetrieveResourceMetadataResponse, resource_metadata, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_resource_metadata_with_all_params(self, async_client: AsyncVraIaas) -> None:
        resource_metadata = await async_client.iaas.api.projects.resource_metadata.retrieve_resource_metadata(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(ResourceMetadataRetrieveResourceMetadataResponse, resource_metadata, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_resource_metadata(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.projects.resource_metadata.with_raw_response.retrieve_resource_metadata(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        resource_metadata = await response.parse()
        assert_matches_type(ResourceMetadataRetrieveResourceMetadataResponse, resource_metadata, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_resource_metadata(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.projects.resource_metadata.with_streaming_response.retrieve_resource_metadata(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            resource_metadata = await response.parse()
            assert_matches_type(ResourceMetadataRetrieveResourceMetadataResponse, resource_metadata, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_resource_metadata(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.projects.resource_metadata.with_raw_response.retrieve_resource_metadata(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_resource_metadata(self, async_client: AsyncVraIaas) -> None:
        resource_metadata = await async_client.iaas.api.projects.resource_metadata.update_resource_metadata(
            id="id",
        )
        assert_matches_type(Project, resource_metadata, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_resource_metadata_with_all_params(self, async_client: AsyncVraIaas) -> None:
        resource_metadata = await async_client.iaas.api.projects.resource_metadata.update_resource_metadata(
            id="id",
            api_version="apiVersion",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
        )
        assert_matches_type(Project, resource_metadata, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_resource_metadata(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.projects.resource_metadata.with_raw_response.update_resource_metadata(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        resource_metadata = await response.parse()
        assert_matches_type(Project, resource_metadata, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_resource_metadata(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.projects.resource_metadata.with_streaming_response.update_resource_metadata(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            resource_metadata = await response.parse()
            assert_matches_type(Project, resource_metadata, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_resource_metadata(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.projects.resource_metadata.with_raw_response.update_resource_metadata(
                id="",
            )
