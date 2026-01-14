# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    NetworkIPRangeBase,
    NetworkIPRangeRetrieveResponse,
    NetworkIPRangeRetrieveNetworkIPRangesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestNetworkIPRanges:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        network_ip_range = client.iaas.api.network_ip_ranges.retrieve(
            id="id",
        )
        assert_matches_type(NetworkIPRangeRetrieveResponse, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        network_ip_range = client.iaas.api.network_ip_ranges.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(NetworkIPRangeRetrieveResponse, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.network_ip_ranges.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_ip_range = response.parse()
        assert_matches_type(NetworkIPRangeRetrieveResponse, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.network_ip_ranges.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_ip_range = response.parse()
            assert_matches_type(NetworkIPRangeRetrieveResponse, network_ip_range, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.network_ip_ranges.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        network_ip_range = client.iaas.api.network_ip_ranges.update(
            id="id",
            end_ip_address="endIPAddress",
            name="name",
            start_ip_address="startIPAddress",
        )
        assert_matches_type(NetworkIPRangeBase, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        network_ip_range = client.iaas.api.network_ip_ranges.update(
            id="id",
            end_ip_address="endIPAddress",
            name="name",
            start_ip_address="startIPAddress",
            api_version="apiVersion",
            description="description",
            fabric_network_ids=["string"],
            ip_version="IPv4",
            tags=[
                {
                    "key": "fast-network",
                    "value": "true",
                }
            ],
        )
        assert_matches_type(NetworkIPRangeBase, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.network_ip_ranges.with_raw_response.update(
            id="id",
            end_ip_address="endIPAddress",
            name="name",
            start_ip_address="startIPAddress",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_ip_range = response.parse()
        assert_matches_type(NetworkIPRangeBase, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.network_ip_ranges.with_streaming_response.update(
            id="id",
            end_ip_address="endIPAddress",
            name="name",
            start_ip_address="startIPAddress",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_ip_range = response.parse()
            assert_matches_type(NetworkIPRangeBase, network_ip_range, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.network_ip_ranges.with_raw_response.update(
                id="",
                end_ip_address="endIPAddress",
                name="name",
                start_ip_address="startIPAddress",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        network_ip_range = client.iaas.api.network_ip_ranges.delete(
            id="id",
        )
        assert network_ip_range is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: VraIaas) -> None:
        network_ip_range = client.iaas.api.network_ip_ranges.delete(
            id="id",
            api_version="apiVersion",
        )
        assert network_ip_range is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.network_ip_ranges.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_ip_range = response.parse()
        assert network_ip_range is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.network_ip_ranges.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_ip_range = response.parse()
            assert network_ip_range is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.network_ip_ranges.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_network_ip_ranges(self, client: VraIaas) -> None:
        network_ip_range = client.iaas.api.network_ip_ranges.network_ip_ranges(
            end_ip_address="endIPAddress",
            name="name",
            start_ip_address="startIPAddress",
        )
        assert_matches_type(NetworkIPRangeBase, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_network_ip_ranges_with_all_params(self, client: VraIaas) -> None:
        network_ip_range = client.iaas.api.network_ip_ranges.network_ip_ranges(
            end_ip_address="endIPAddress",
            name="name",
            start_ip_address="startIPAddress",
            api_version="apiVersion",
            description="description",
            fabric_network_ids=["string"],
            ip_version="IPv4",
            tags=[
                {
                    "key": "fast-network",
                    "value": "true",
                }
            ],
        )
        assert_matches_type(NetworkIPRangeBase, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_network_ip_ranges(self, client: VraIaas) -> None:
        response = client.iaas.api.network_ip_ranges.with_raw_response.network_ip_ranges(
            end_ip_address="endIPAddress",
            name="name",
            start_ip_address="startIPAddress",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_ip_range = response.parse()
        assert_matches_type(NetworkIPRangeBase, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_network_ip_ranges(self, client: VraIaas) -> None:
        with client.iaas.api.network_ip_ranges.with_streaming_response.network_ip_ranges(
            end_ip_address="endIPAddress",
            name="name",
            start_ip_address="startIPAddress",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_ip_range = response.parse()
            assert_matches_type(NetworkIPRangeBase, network_ip_range, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_network_ip_ranges(self, client: VraIaas) -> None:
        network_ip_range = client.iaas.api.network_ip_ranges.retrieve_network_ip_ranges()
        assert_matches_type(NetworkIPRangeRetrieveNetworkIPRangesResponse, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_network_ip_ranges_with_all_params(self, client: VraIaas) -> None:
        network_ip_range = client.iaas.api.network_ip_ranges.retrieve_network_ip_ranges(
            api_version="apiVersion",
        )
        assert_matches_type(NetworkIPRangeRetrieveNetworkIPRangesResponse, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_network_ip_ranges(self, client: VraIaas) -> None:
        response = client.iaas.api.network_ip_ranges.with_raw_response.retrieve_network_ip_ranges()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_ip_range = response.parse()
        assert_matches_type(NetworkIPRangeRetrieveNetworkIPRangesResponse, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_network_ip_ranges(self, client: VraIaas) -> None:
        with client.iaas.api.network_ip_ranges.with_streaming_response.retrieve_network_ip_ranges() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_ip_range = response.parse()
            assert_matches_type(NetworkIPRangeRetrieveNetworkIPRangesResponse, network_ip_range, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncNetworkIPRanges:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        network_ip_range = await async_client.iaas.api.network_ip_ranges.retrieve(
            id="id",
        )
        assert_matches_type(NetworkIPRangeRetrieveResponse, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        network_ip_range = await async_client.iaas.api.network_ip_ranges.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(NetworkIPRangeRetrieveResponse, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.network_ip_ranges.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_ip_range = await response.parse()
        assert_matches_type(NetworkIPRangeRetrieveResponse, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.network_ip_ranges.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_ip_range = await response.parse()
            assert_matches_type(NetworkIPRangeRetrieveResponse, network_ip_range, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.network_ip_ranges.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        network_ip_range = await async_client.iaas.api.network_ip_ranges.update(
            id="id",
            end_ip_address="endIPAddress",
            name="name",
            start_ip_address="startIPAddress",
        )
        assert_matches_type(NetworkIPRangeBase, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        network_ip_range = await async_client.iaas.api.network_ip_ranges.update(
            id="id",
            end_ip_address="endIPAddress",
            name="name",
            start_ip_address="startIPAddress",
            api_version="apiVersion",
            description="description",
            fabric_network_ids=["string"],
            ip_version="IPv4",
            tags=[
                {
                    "key": "fast-network",
                    "value": "true",
                }
            ],
        )
        assert_matches_type(NetworkIPRangeBase, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.network_ip_ranges.with_raw_response.update(
            id="id",
            end_ip_address="endIPAddress",
            name="name",
            start_ip_address="startIPAddress",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_ip_range = await response.parse()
        assert_matches_type(NetworkIPRangeBase, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.network_ip_ranges.with_streaming_response.update(
            id="id",
            end_ip_address="endIPAddress",
            name="name",
            start_ip_address="startIPAddress",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_ip_range = await response.parse()
            assert_matches_type(NetworkIPRangeBase, network_ip_range, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.network_ip_ranges.with_raw_response.update(
                id="",
                end_ip_address="endIPAddress",
                name="name",
                start_ip_address="startIPAddress",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        network_ip_range = await async_client.iaas.api.network_ip_ranges.delete(
            id="id",
        )
        assert network_ip_range is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncVraIaas) -> None:
        network_ip_range = await async_client.iaas.api.network_ip_ranges.delete(
            id="id",
            api_version="apiVersion",
        )
        assert network_ip_range is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.network_ip_ranges.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_ip_range = await response.parse()
        assert network_ip_range is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.network_ip_ranges.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_ip_range = await response.parse()
            assert network_ip_range is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.network_ip_ranges.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_network_ip_ranges(self, async_client: AsyncVraIaas) -> None:
        network_ip_range = await async_client.iaas.api.network_ip_ranges.network_ip_ranges(
            end_ip_address="endIPAddress",
            name="name",
            start_ip_address="startIPAddress",
        )
        assert_matches_type(NetworkIPRangeBase, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_network_ip_ranges_with_all_params(self, async_client: AsyncVraIaas) -> None:
        network_ip_range = await async_client.iaas.api.network_ip_ranges.network_ip_ranges(
            end_ip_address="endIPAddress",
            name="name",
            start_ip_address="startIPAddress",
            api_version="apiVersion",
            description="description",
            fabric_network_ids=["string"],
            ip_version="IPv4",
            tags=[
                {
                    "key": "fast-network",
                    "value": "true",
                }
            ],
        )
        assert_matches_type(NetworkIPRangeBase, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_network_ip_ranges(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.network_ip_ranges.with_raw_response.network_ip_ranges(
            end_ip_address="endIPAddress",
            name="name",
            start_ip_address="startIPAddress",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_ip_range = await response.parse()
        assert_matches_type(NetworkIPRangeBase, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_network_ip_ranges(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.network_ip_ranges.with_streaming_response.network_ip_ranges(
            end_ip_address="endIPAddress",
            name="name",
            start_ip_address="startIPAddress",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_ip_range = await response.parse()
            assert_matches_type(NetworkIPRangeBase, network_ip_range, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_network_ip_ranges(self, async_client: AsyncVraIaas) -> None:
        network_ip_range = await async_client.iaas.api.network_ip_ranges.retrieve_network_ip_ranges()
        assert_matches_type(NetworkIPRangeRetrieveNetworkIPRangesResponse, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_network_ip_ranges_with_all_params(self, async_client: AsyncVraIaas) -> None:
        network_ip_range = await async_client.iaas.api.network_ip_ranges.retrieve_network_ip_ranges(
            api_version="apiVersion",
        )
        assert_matches_type(NetworkIPRangeRetrieveNetworkIPRangesResponse, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_network_ip_ranges(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.network_ip_ranges.with_raw_response.retrieve_network_ip_ranges()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_ip_range = await response.parse()
        assert_matches_type(NetworkIPRangeRetrieveNetworkIPRangesResponse, network_ip_range, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_network_ip_ranges(self, async_client: AsyncVraIaas) -> None:
        async with (
            async_client.iaas.api.network_ip_ranges.with_streaming_response.retrieve_network_ip_ranges()
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_ip_range = await response.parse()
            assert_matches_type(NetworkIPRangeRetrieveNetworkIPRangesResponse, network_ip_range, path=["response"])

        assert cast(Any, response.is_closed) is True
