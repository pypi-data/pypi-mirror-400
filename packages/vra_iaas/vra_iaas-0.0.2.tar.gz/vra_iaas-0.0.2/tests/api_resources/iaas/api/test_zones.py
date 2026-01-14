# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    Zone,
    ZoneListResponse,
    FabricComputeResult,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestZones:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: VraIaas) -> None:
        zone = client.iaas.api.zones.create(
            name="name",
            region_id="9.0E49",
        )
        assert_matches_type(Zone, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: VraIaas) -> None:
        zone = client.iaas.api.zones.create(
            name="name",
            region_id="9.0E49",
            api_version="apiVersion",
            compute_ids=["[ab12c]"],
            custom_properties={"__isDefaultPlacementZone": "true"},
            description="description",
            folder="test-folder",
            placement_policy="DEFAULT",
            tags=[
                {
                    "key": "production",
                    "value": " ",
                }
            ],
            tags_to_match=[
                {
                    "key": "compliance",
                    "value": "pci",
                }
            ],
        )
        assert_matches_type(Zone, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: VraIaas) -> None:
        response = client.iaas.api.zones.with_raw_response.create(
            name="name",
            region_id="9.0E49",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        zone = response.parse()
        assert_matches_type(Zone, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: VraIaas) -> None:
        with client.iaas.api.zones.with_streaming_response.create(
            name="name",
            region_id="9.0E49",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            zone = response.parse()
            assert_matches_type(Zone, zone, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        zone = client.iaas.api.zones.retrieve(
            id="id",
        )
        assert_matches_type(Zone, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        zone = client.iaas.api.zones.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(Zone, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.zones.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        zone = response.parse()
        assert_matches_type(Zone, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.zones.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            zone = response.parse()
            assert_matches_type(Zone, zone, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.zones.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        zone = client.iaas.api.zones.update(
            id="id",
            name="name",
            region_id="9.0E49",
        )
        assert_matches_type(Zone, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        zone = client.iaas.api.zones.update(
            id="id",
            name="name",
            region_id="9.0E49",
            api_version="apiVersion",
            compute_ids=["[ab12c]"],
            custom_properties={"__isDefaultPlacementZone": "true"},
            description="description",
            folder="test-folder",
            placement_policy="DEFAULT",
            tags=[
                {
                    "key": "production",
                    "value": " ",
                }
            ],
            tags_to_match=[
                {
                    "key": "compliance",
                    "value": "pci",
                }
            ],
        )
        assert_matches_type(Zone, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.zones.with_raw_response.update(
            id="id",
            name="name",
            region_id="9.0E49",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        zone = response.parse()
        assert_matches_type(Zone, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.zones.with_streaming_response.update(
            id="id",
            name="name",
            region_id="9.0E49",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            zone = response.parse()
            assert_matches_type(Zone, zone, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.zones.with_raw_response.update(
                id="",
                name="name",
                region_id="9.0E49",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: VraIaas) -> None:
        zone = client.iaas.api.zones.list()
        assert_matches_type(ZoneListResponse, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: VraIaas) -> None:
        zone = client.iaas.api.zones.list(
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(ZoneListResponse, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: VraIaas) -> None:
        response = client.iaas.api.zones.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        zone = response.parse()
        assert_matches_type(ZoneListResponse, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: VraIaas) -> None:
        with client.iaas.api.zones.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            zone = response.parse()
            assert_matches_type(ZoneListResponse, zone, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        zone = client.iaas.api.zones.delete(
            id="id",
        )
        assert zone is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: VraIaas) -> None:
        zone = client.iaas.api.zones.delete(
            id="id",
            api_version="apiVersion",
        )
        assert zone is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.zones.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        zone = response.parse()
        assert zone is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.zones.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            zone = response.parse()
            assert zone is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.zones.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_computes(self, client: VraIaas) -> None:
        zone = client.iaas.api.zones.retrieve_computes(
            id="id",
        )
        assert_matches_type(FabricComputeResult, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_computes_with_all_params(self, client: VraIaas) -> None:
        zone = client.iaas.api.zones.retrieve_computes(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(FabricComputeResult, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_computes(self, client: VraIaas) -> None:
        response = client.iaas.api.zones.with_raw_response.retrieve_computes(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        zone = response.parse()
        assert_matches_type(FabricComputeResult, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_computes(self, client: VraIaas) -> None:
        with client.iaas.api.zones.with_streaming_response.retrieve_computes(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            zone = response.parse()
            assert_matches_type(FabricComputeResult, zone, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_computes(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.zones.with_raw_response.retrieve_computes(
                id="",
            )


class TestAsyncZones:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncVraIaas) -> None:
        zone = await async_client.iaas.api.zones.create(
            name="name",
            region_id="9.0E49",
        )
        assert_matches_type(Zone, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncVraIaas) -> None:
        zone = await async_client.iaas.api.zones.create(
            name="name",
            region_id="9.0E49",
            api_version="apiVersion",
            compute_ids=["[ab12c]"],
            custom_properties={"__isDefaultPlacementZone": "true"},
            description="description",
            folder="test-folder",
            placement_policy="DEFAULT",
            tags=[
                {
                    "key": "production",
                    "value": " ",
                }
            ],
            tags_to_match=[
                {
                    "key": "compliance",
                    "value": "pci",
                }
            ],
        )
        assert_matches_type(Zone, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.zones.with_raw_response.create(
            name="name",
            region_id="9.0E49",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        zone = await response.parse()
        assert_matches_type(Zone, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.zones.with_streaming_response.create(
            name="name",
            region_id="9.0E49",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            zone = await response.parse()
            assert_matches_type(Zone, zone, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        zone = await async_client.iaas.api.zones.retrieve(
            id="id",
        )
        assert_matches_type(Zone, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        zone = await async_client.iaas.api.zones.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(Zone, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.zones.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        zone = await response.parse()
        assert_matches_type(Zone, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.zones.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            zone = await response.parse()
            assert_matches_type(Zone, zone, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.zones.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        zone = await async_client.iaas.api.zones.update(
            id="id",
            name="name",
            region_id="9.0E49",
        )
        assert_matches_type(Zone, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        zone = await async_client.iaas.api.zones.update(
            id="id",
            name="name",
            region_id="9.0E49",
            api_version="apiVersion",
            compute_ids=["[ab12c]"],
            custom_properties={"__isDefaultPlacementZone": "true"},
            description="description",
            folder="test-folder",
            placement_policy="DEFAULT",
            tags=[
                {
                    "key": "production",
                    "value": " ",
                }
            ],
            tags_to_match=[
                {
                    "key": "compliance",
                    "value": "pci",
                }
            ],
        )
        assert_matches_type(Zone, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.zones.with_raw_response.update(
            id="id",
            name="name",
            region_id="9.0E49",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        zone = await response.parse()
        assert_matches_type(Zone, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.zones.with_streaming_response.update(
            id="id",
            name="name",
            region_id="9.0E49",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            zone = await response.parse()
            assert_matches_type(Zone, zone, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.zones.with_raw_response.update(
                id="",
                name="name",
                region_id="9.0E49",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncVraIaas) -> None:
        zone = await async_client.iaas.api.zones.list()
        assert_matches_type(ZoneListResponse, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncVraIaas) -> None:
        zone = await async_client.iaas.api.zones.list(
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(ZoneListResponse, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.zones.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        zone = await response.parse()
        assert_matches_type(ZoneListResponse, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.zones.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            zone = await response.parse()
            assert_matches_type(ZoneListResponse, zone, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        zone = await async_client.iaas.api.zones.delete(
            id="id",
        )
        assert zone is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncVraIaas) -> None:
        zone = await async_client.iaas.api.zones.delete(
            id="id",
            api_version="apiVersion",
        )
        assert zone is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.zones.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        zone = await response.parse()
        assert zone is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.zones.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            zone = await response.parse()
            assert zone is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.zones.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_computes(self, async_client: AsyncVraIaas) -> None:
        zone = await async_client.iaas.api.zones.retrieve_computes(
            id="id",
        )
        assert_matches_type(FabricComputeResult, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_computes_with_all_params(self, async_client: AsyncVraIaas) -> None:
        zone = await async_client.iaas.api.zones.retrieve_computes(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(FabricComputeResult, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_computes(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.zones.with_raw_response.retrieve_computes(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        zone = await response.parse()
        assert_matches_type(FabricComputeResult, zone, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_computes(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.zones.with_streaming_response.retrieve_computes(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            zone = await response.parse()
            assert_matches_type(FabricComputeResult, zone, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_computes(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.zones.with_raw_response.retrieve_computes(
                id="",
            )
