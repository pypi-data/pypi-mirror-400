# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    DataCollector,
    DataCollectorDataCollectorsResponse,
    DataCollectorRetrieveDataCollectorsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDataCollectors:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        data_collector = client.iaas.api.data_collectors.retrieve(
            id="id",
        )
        assert_matches_type(DataCollector, data_collector, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        data_collector = client.iaas.api.data_collectors.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(DataCollector, data_collector, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.data_collectors.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_collector = response.parse()
        assert_matches_type(DataCollector, data_collector, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.data_collectors.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_collector = response.parse()
            assert_matches_type(DataCollector, data_collector, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.data_collectors.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        data_collector = client.iaas.api.data_collectors.delete(
            id="id",
        )
        assert data_collector is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: VraIaas) -> None:
        data_collector = client.iaas.api.data_collectors.delete(
            id="id",
            api_version="apiVersion",
        )
        assert data_collector is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.data_collectors.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_collector = response.parse()
        assert data_collector is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.data_collectors.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_collector = response.parse()
            assert data_collector is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.data_collectors.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_data_collectors(self, client: VraIaas) -> None:
        data_collector = client.iaas.api.data_collectors.data_collectors()
        assert_matches_type(DataCollectorDataCollectorsResponse, data_collector, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_data_collectors_with_all_params(self, client: VraIaas) -> None:
        data_collector = client.iaas.api.data_collectors.data_collectors(
            api_version="apiVersion",
        )
        assert_matches_type(DataCollectorDataCollectorsResponse, data_collector, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_data_collectors(self, client: VraIaas) -> None:
        response = client.iaas.api.data_collectors.with_raw_response.data_collectors()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_collector = response.parse()
        assert_matches_type(DataCollectorDataCollectorsResponse, data_collector, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_data_collectors(self, client: VraIaas) -> None:
        with client.iaas.api.data_collectors.with_streaming_response.data_collectors() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_collector = response.parse()
            assert_matches_type(DataCollectorDataCollectorsResponse, data_collector, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_data_collectors(self, client: VraIaas) -> None:
        data_collector = client.iaas.api.data_collectors.retrieve_data_collectors()
        assert_matches_type(DataCollectorRetrieveDataCollectorsResponse, data_collector, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_data_collectors_with_all_params(self, client: VraIaas) -> None:
        data_collector = client.iaas.api.data_collectors.retrieve_data_collectors(
            api_version="apiVersion",
            disabled=True,
        )
        assert_matches_type(DataCollectorRetrieveDataCollectorsResponse, data_collector, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_data_collectors(self, client: VraIaas) -> None:
        response = client.iaas.api.data_collectors.with_raw_response.retrieve_data_collectors()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_collector = response.parse()
        assert_matches_type(DataCollectorRetrieveDataCollectorsResponse, data_collector, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_data_collectors(self, client: VraIaas) -> None:
        with client.iaas.api.data_collectors.with_streaming_response.retrieve_data_collectors() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_collector = response.parse()
            assert_matches_type(DataCollectorRetrieveDataCollectorsResponse, data_collector, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDataCollectors:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        data_collector = await async_client.iaas.api.data_collectors.retrieve(
            id="id",
        )
        assert_matches_type(DataCollector, data_collector, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        data_collector = await async_client.iaas.api.data_collectors.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(DataCollector, data_collector, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.data_collectors.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_collector = await response.parse()
        assert_matches_type(DataCollector, data_collector, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.data_collectors.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_collector = await response.parse()
            assert_matches_type(DataCollector, data_collector, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.data_collectors.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        data_collector = await async_client.iaas.api.data_collectors.delete(
            id="id",
        )
        assert data_collector is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncVraIaas) -> None:
        data_collector = await async_client.iaas.api.data_collectors.delete(
            id="id",
            api_version="apiVersion",
        )
        assert data_collector is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.data_collectors.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_collector = await response.parse()
        assert data_collector is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.data_collectors.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_collector = await response.parse()
            assert data_collector is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.data_collectors.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_data_collectors(self, async_client: AsyncVraIaas) -> None:
        data_collector = await async_client.iaas.api.data_collectors.data_collectors()
        assert_matches_type(DataCollectorDataCollectorsResponse, data_collector, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_data_collectors_with_all_params(self, async_client: AsyncVraIaas) -> None:
        data_collector = await async_client.iaas.api.data_collectors.data_collectors(
            api_version="apiVersion",
        )
        assert_matches_type(DataCollectorDataCollectorsResponse, data_collector, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_data_collectors(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.data_collectors.with_raw_response.data_collectors()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_collector = await response.parse()
        assert_matches_type(DataCollectorDataCollectorsResponse, data_collector, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_data_collectors(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.data_collectors.with_streaming_response.data_collectors() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_collector = await response.parse()
            assert_matches_type(DataCollectorDataCollectorsResponse, data_collector, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_data_collectors(self, async_client: AsyncVraIaas) -> None:
        data_collector = await async_client.iaas.api.data_collectors.retrieve_data_collectors()
        assert_matches_type(DataCollectorRetrieveDataCollectorsResponse, data_collector, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_data_collectors_with_all_params(self, async_client: AsyncVraIaas) -> None:
        data_collector = await async_client.iaas.api.data_collectors.retrieve_data_collectors(
            api_version="apiVersion",
            disabled=True,
        )
        assert_matches_type(DataCollectorRetrieveDataCollectorsResponse, data_collector, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_data_collectors(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.data_collectors.with_raw_response.retrieve_data_collectors()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        data_collector = await response.parse()
        assert_matches_type(DataCollectorRetrieveDataCollectorsResponse, data_collector, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_data_collectors(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.data_collectors.with_streaming_response.retrieve_data_collectors() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            data_collector = await response.parse()
            assert_matches_type(DataCollectorRetrieveDataCollectorsResponse, data_collector, path=["response"])

        assert cast(Any, response.is_closed) is True
