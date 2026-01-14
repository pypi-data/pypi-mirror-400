# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    Network,
    NetworkListResponse,
)
from vra_iaas.types.iaas.api.projects import RequestTracker

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestNetworks:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: VraIaas) -> None:
        network = client.iaas.api.networks.create(
            name="name",
            project_id="e058",
        )
        assert_matches_type(RequestTracker, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: VraIaas) -> None:
        network = client.iaas.api.networks.create(
            name="name",
            project_id="e058",
            api_version="apiVersion",
            constraints=[
                {
                    "expression": "ha:strong",
                    "mandatory": True,
                }
            ],
            create_gateway=True,
            custom_properties={"foo": "string"},
            deployment_id="123e4567-e89b-12d3-a456-426655440000",
            description="description",
            outbound_access=True,
            tags=[
                {
                    "key": "vmware.enumeration.type",
                    "value": "nec2_vpc",
                }
            ],
        )
        assert_matches_type(RequestTracker, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: VraIaas) -> None:
        response = client.iaas.api.networks.with_raw_response.create(
            name="name",
            project_id="e058",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network = response.parse()
        assert_matches_type(RequestTracker, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: VraIaas) -> None:
        with client.iaas.api.networks.with_streaming_response.create(
            name="name",
            project_id="e058",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network = response.parse()
            assert_matches_type(RequestTracker, network, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        network = client.iaas.api.networks.retrieve(
            id="id",
        )
        assert_matches_type(Network, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        network = client.iaas.api.networks.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(Network, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.networks.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network = response.parse()
        assert_matches_type(Network, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.networks.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network = response.parse()
            assert_matches_type(Network, network, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.networks.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: VraIaas) -> None:
        network = client.iaas.api.networks.list()
        assert_matches_type(NetworkListResponse, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: VraIaas) -> None:
        network = client.iaas.api.networks.list(
            api_version="apiVersion",
        )
        assert_matches_type(NetworkListResponse, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: VraIaas) -> None:
        response = client.iaas.api.networks.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network = response.parse()
        assert_matches_type(NetworkListResponse, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: VraIaas) -> None:
        with client.iaas.api.networks.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network = response.parse()
            assert_matches_type(NetworkListResponse, network, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        network = client.iaas.api.networks.delete(
            id="id",
        )
        assert_matches_type(RequestTracker, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: VraIaas) -> None:
        network = client.iaas.api.networks.delete(
            id="id",
            api_version="apiVersion",
            force_delete=True,
        )
        assert_matches_type(RequestTracker, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.networks.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network = response.parse()
        assert_matches_type(RequestTracker, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.networks.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network = response.parse()
            assert_matches_type(RequestTracker, network, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.networks.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_network_ip_ranges(self, client: VraIaas) -> None:
        network = client.iaas.api.networks.retrieve_network_ip_ranges(
            id="id",
        )
        assert_matches_type(Network, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_network_ip_ranges_with_all_params(self, client: VraIaas) -> None:
        network = client.iaas.api.networks.retrieve_network_ip_ranges(
            id="id",
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(Network, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_network_ip_ranges(self, client: VraIaas) -> None:
        response = client.iaas.api.networks.with_raw_response.retrieve_network_ip_ranges(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network = response.parse()
        assert_matches_type(Network, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_network_ip_ranges(self, client: VraIaas) -> None:
        with client.iaas.api.networks.with_streaming_response.retrieve_network_ip_ranges(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network = response.parse()
            assert_matches_type(Network, network, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_network_ip_ranges(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.networks.with_raw_response.retrieve_network_ip_ranges(
                id="",
            )


class TestAsyncNetworks:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncVraIaas) -> None:
        network = await async_client.iaas.api.networks.create(
            name="name",
            project_id="e058",
        )
        assert_matches_type(RequestTracker, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncVraIaas) -> None:
        network = await async_client.iaas.api.networks.create(
            name="name",
            project_id="e058",
            api_version="apiVersion",
            constraints=[
                {
                    "expression": "ha:strong",
                    "mandatory": True,
                }
            ],
            create_gateway=True,
            custom_properties={"foo": "string"},
            deployment_id="123e4567-e89b-12d3-a456-426655440000",
            description="description",
            outbound_access=True,
            tags=[
                {
                    "key": "vmware.enumeration.type",
                    "value": "nec2_vpc",
                }
            ],
        )
        assert_matches_type(RequestTracker, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.networks.with_raw_response.create(
            name="name",
            project_id="e058",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network = await response.parse()
        assert_matches_type(RequestTracker, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.networks.with_streaming_response.create(
            name="name",
            project_id="e058",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network = await response.parse()
            assert_matches_type(RequestTracker, network, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        network = await async_client.iaas.api.networks.retrieve(
            id="id",
        )
        assert_matches_type(Network, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        network = await async_client.iaas.api.networks.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(Network, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.networks.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network = await response.parse()
        assert_matches_type(Network, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.networks.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network = await response.parse()
            assert_matches_type(Network, network, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.networks.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncVraIaas) -> None:
        network = await async_client.iaas.api.networks.list()
        assert_matches_type(NetworkListResponse, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncVraIaas) -> None:
        network = await async_client.iaas.api.networks.list(
            api_version="apiVersion",
        )
        assert_matches_type(NetworkListResponse, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.networks.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network = await response.parse()
        assert_matches_type(NetworkListResponse, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.networks.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network = await response.parse()
            assert_matches_type(NetworkListResponse, network, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        network = await async_client.iaas.api.networks.delete(
            id="id",
        )
        assert_matches_type(RequestTracker, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncVraIaas) -> None:
        network = await async_client.iaas.api.networks.delete(
            id="id",
            api_version="apiVersion",
            force_delete=True,
        )
        assert_matches_type(RequestTracker, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.networks.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network = await response.parse()
        assert_matches_type(RequestTracker, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.networks.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network = await response.parse()
            assert_matches_type(RequestTracker, network, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.networks.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_network_ip_ranges(self, async_client: AsyncVraIaas) -> None:
        network = await async_client.iaas.api.networks.retrieve_network_ip_ranges(
            id="id",
        )
        assert_matches_type(Network, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_network_ip_ranges_with_all_params(self, async_client: AsyncVraIaas) -> None:
        network = await async_client.iaas.api.networks.retrieve_network_ip_ranges(
            id="id",
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(Network, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_network_ip_ranges(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.networks.with_raw_response.retrieve_network_ip_ranges(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        network = await response.parse()
        assert_matches_type(Network, network, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_network_ip_ranges(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.networks.with_streaming_response.retrieve_network_ip_ranges(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            network = await response.parse()
            assert_matches_type(Network, network, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_network_ip_ranges(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.networks.with_raw_response.retrieve_network_ip_ranges(
                id="",
            )
