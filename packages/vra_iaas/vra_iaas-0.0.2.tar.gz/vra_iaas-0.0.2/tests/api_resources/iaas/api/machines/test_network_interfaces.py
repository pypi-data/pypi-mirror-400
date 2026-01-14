# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api.machines import (
    NetworkInterface,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestNetworkInterfaces:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        network_interface = client.iaas.api.machines.network_interfaces.retrieve(
            network_id="networkId",
            id="id",
        )
        assert_matches_type(NetworkInterface, network_interface, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        network_interface = client.iaas.api.machines.network_interfaces.retrieve(
            network_id="networkId",
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(NetworkInterface, network_interface, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.network_interfaces.with_raw_response.retrieve(
            network_id="networkId",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_interface = response.parse()
        assert_matches_type(NetworkInterface, network_interface, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.machines.network_interfaces.with_streaming_response.retrieve(
            network_id="networkId",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_interface = response.parse()
            assert_matches_type(NetworkInterface, network_interface, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.machines.network_interfaces.with_raw_response.retrieve(
                network_id="networkId",
                id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `network_id` but received ''"):
            client.iaas.api.machines.network_interfaces.with_raw_response.retrieve(
                network_id="",
                id="id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        network_interface = client.iaas.api.machines.network_interfaces.update(
            network_id="networkId",
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(NetworkInterface, network_interface, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        network_interface = client.iaas.api.machines.network_interfaces.update(
            network_id="networkId",
            id="id",
            api_version="apiVersion",
            address="address",
            custom_properties={"foo": "string"},
            description="description",
            name="name",
        )
        assert_matches_type(NetworkInterface, network_interface, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.network_interfaces.with_raw_response.update(
            network_id="networkId",
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_interface = response.parse()
        assert_matches_type(NetworkInterface, network_interface, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.machines.network_interfaces.with_streaming_response.update(
            network_id="networkId",
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_interface = response.parse()
            assert_matches_type(NetworkInterface, network_interface, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.machines.network_interfaces.with_raw_response.update(
                network_id="networkId",
                id="",
                api_version="apiVersion",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `network_id` but received ''"):
            client.iaas.api.machines.network_interfaces.with_raw_response.update(
                network_id="",
                id="id",
                api_version="apiVersion",
            )


class TestAsyncNetworkInterfaces:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        network_interface = await async_client.iaas.api.machines.network_interfaces.retrieve(
            network_id="networkId",
            id="id",
        )
        assert_matches_type(NetworkInterface, network_interface, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        network_interface = await async_client.iaas.api.machines.network_interfaces.retrieve(
            network_id="networkId",
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(NetworkInterface, network_interface, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.network_interfaces.with_raw_response.retrieve(
            network_id="networkId",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_interface = await response.parse()
        assert_matches_type(NetworkInterface, network_interface, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.network_interfaces.with_streaming_response.retrieve(
            network_id="networkId",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_interface = await response.parse()
            assert_matches_type(NetworkInterface, network_interface, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.machines.network_interfaces.with_raw_response.retrieve(
                network_id="networkId",
                id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `network_id` but received ''"):
            await async_client.iaas.api.machines.network_interfaces.with_raw_response.retrieve(
                network_id="",
                id="id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        network_interface = await async_client.iaas.api.machines.network_interfaces.update(
            network_id="networkId",
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(NetworkInterface, network_interface, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        network_interface = await async_client.iaas.api.machines.network_interfaces.update(
            network_id="networkId",
            id="id",
            api_version="apiVersion",
            address="address",
            custom_properties={"foo": "string"},
            description="description",
            name="name",
        )
        assert_matches_type(NetworkInterface, network_interface, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.network_interfaces.with_raw_response.update(
            network_id="networkId",
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network_interface = await response.parse()
        assert_matches_type(NetworkInterface, network_interface, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.network_interfaces.with_streaming_response.update(
            network_id="networkId",
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network_interface = await response.parse()
            assert_matches_type(NetworkInterface, network_interface, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.machines.network_interfaces.with_raw_response.update(
                network_id="networkId",
                id="",
                api_version="apiVersion",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `network_id` but received ''"):
            await async_client.iaas.api.machines.network_interfaces.with_raw_response.update(
                network_id="",
                id="id",
                api_version="apiVersion",
            )
