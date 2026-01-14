# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api.projects import RequestTracker

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUnregisteredIPAddresses:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_release(self, client: VraIaas) -> None:
        unregistered_ip_address = client.iaas.api.network_ip_ranges.unregistered_ip_addresses.release(
            id="id",
        )
        assert_matches_type(RequestTracker, unregistered_ip_address, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_release_with_all_params(self, client: VraIaas) -> None:
        unregistered_ip_address = client.iaas.api.network_ip_ranges.unregistered_ip_addresses.release(
            id="id",
            api_version="apiVersion",
            ip_addresses=[
                '["10.10.10.1","10.10.10.2"]or["fc00:10:118:136:fcd8:d68d:9701:8975","fc00:10:118:136:fcd8:d68d:9701:8985"]'
            ],
        )
        assert_matches_type(RequestTracker, unregistered_ip_address, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_release(self, client: VraIaas) -> None:
        response = client.iaas.api.network_ip_ranges.unregistered_ip_addresses.with_raw_response.release(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        unregistered_ip_address = response.parse()
        assert_matches_type(RequestTracker, unregistered_ip_address, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_release(self, client: VraIaas) -> None:
        with client.iaas.api.network_ip_ranges.unregistered_ip_addresses.with_streaming_response.release(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            unregistered_ip_address = response.parse()
            assert_matches_type(RequestTracker, unregistered_ip_address, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_release(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.network_ip_ranges.unregistered_ip_addresses.with_raw_response.release(
                id="",
            )


class TestAsyncUnregisteredIPAddresses:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_release(self, async_client: AsyncVraIaas) -> None:
        unregistered_ip_address = await async_client.iaas.api.network_ip_ranges.unregistered_ip_addresses.release(
            id="id",
        )
        assert_matches_type(RequestTracker, unregistered_ip_address, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_release_with_all_params(self, async_client: AsyncVraIaas) -> None:
        unregistered_ip_address = await async_client.iaas.api.network_ip_ranges.unregistered_ip_addresses.release(
            id="id",
            api_version="apiVersion",
            ip_addresses=[
                '["10.10.10.1","10.10.10.2"]or["fc00:10:118:136:fcd8:d68d:9701:8975","fc00:10:118:136:fcd8:d68d:9701:8985"]'
            ],
        )
        assert_matches_type(RequestTracker, unregistered_ip_address, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_release(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.network_ip_ranges.unregistered_ip_addresses.with_raw_response.release(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        unregistered_ip_address = await response.parse()
        assert_matches_type(RequestTracker, unregistered_ip_address, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_release(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.network_ip_ranges.unregistered_ip_addresses.with_streaming_response.release(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            unregistered_ip_address = await response.parse()
            assert_matches_type(RequestTracker, unregistered_ip_address, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_release(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.network_ip_ranges.unregistered_ip_addresses.with_raw_response.release(
                id="",
            )
