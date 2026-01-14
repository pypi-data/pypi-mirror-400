# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    GcpStorageProfile,
    StorageProfilesGcpRetrieveStorageProfilesGcpResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestStorageProfilesGcp:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        storage_profiles_gcp = client.iaas.api.storage_profiles_gcp.retrieve(
            id="id",
        )
        assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        storage_profiles_gcp = client.iaas.api.storage_profiles_gcp.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles_gcp.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_gcp = response.parse()
        assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles_gcp.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_gcp = response.parse()
            assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.storage_profiles_gcp.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        storage_profiles_gcp = client.iaas.api.storage_profiles_gcp.update(
            id="id",
            name="name",
            persistent_disk_type="pd-standard / pd-ssd / pd-balanced / pd-extreme",
            region_id="31186",
        )
        assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        storage_profiles_gcp = client.iaas.api.storage_profiles_gcp.update(
            id="id",
            name="name",
            persistent_disk_type="pd-standard / pd-ssd / pd-balanced / pd-extreme",
            region_id="31186",
            api_version="apiVersion",
            default_item=True,
            description="description",
            supports_encryption=False,
            tags=[
                {
                    "key": "tier",
                    "value": "silver",
                }
            ],
        )
        assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles_gcp.with_raw_response.update(
            id="id",
            name="name",
            persistent_disk_type="pd-standard / pd-ssd / pd-balanced / pd-extreme",
            region_id="31186",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_gcp = response.parse()
        assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles_gcp.with_streaming_response.update(
            id="id",
            name="name",
            persistent_disk_type="pd-standard / pd-ssd / pd-balanced / pd-extreme",
            region_id="31186",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_gcp = response.parse()
            assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.storage_profiles_gcp.with_raw_response.update(
                id="",
                name="name",
                persistent_disk_type="pd-standard / pd-ssd / pd-balanced / pd-extreme",
                region_id="31186",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        storage_profiles_gcp = client.iaas.api.storage_profiles_gcp.delete(
            id="id",
        )
        assert storage_profiles_gcp is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: VraIaas) -> None:
        storage_profiles_gcp = client.iaas.api.storage_profiles_gcp.delete(
            id="id",
            api_version="apiVersion",
        )
        assert storage_profiles_gcp is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles_gcp.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_gcp = response.parse()
        assert storage_profiles_gcp is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles_gcp.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_gcp = response.parse()
            assert storage_profiles_gcp is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.storage_profiles_gcp.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_storage_profiles_gcp(self, client: VraIaas) -> None:
        storage_profiles_gcp = client.iaas.api.storage_profiles_gcp.retrieve_storage_profiles_gcp()
        assert_matches_type(
            StorageProfilesGcpRetrieveStorageProfilesGcpResponse, storage_profiles_gcp, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_storage_profiles_gcp_with_all_params(self, client: VraIaas) -> None:
        storage_profiles_gcp = client.iaas.api.storage_profiles_gcp.retrieve_storage_profiles_gcp(
            api_version="apiVersion",
        )
        assert_matches_type(
            StorageProfilesGcpRetrieveStorageProfilesGcpResponse, storage_profiles_gcp, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_storage_profiles_gcp(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles_gcp.with_raw_response.retrieve_storage_profiles_gcp()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_gcp = response.parse()
        assert_matches_type(
            StorageProfilesGcpRetrieveStorageProfilesGcpResponse, storage_profiles_gcp, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_storage_profiles_gcp(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles_gcp.with_streaming_response.retrieve_storage_profiles_gcp() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_gcp = response.parse()
            assert_matches_type(
                StorageProfilesGcpRetrieveStorageProfilesGcpResponse, storage_profiles_gcp, path=["response"]
            )

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_storage_profiles_gcp(self, client: VraIaas) -> None:
        storage_profiles_gcp = client.iaas.api.storage_profiles_gcp.storage_profiles_gcp(
            name="name",
            persistent_disk_type="pd-standard / pd-ssd / pd-balanced / pd-extreme",
            region_id="31186",
        )
        assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_storage_profiles_gcp_with_all_params(self, client: VraIaas) -> None:
        storage_profiles_gcp = client.iaas.api.storage_profiles_gcp.storage_profiles_gcp(
            name="name",
            persistent_disk_type="pd-standard / pd-ssd / pd-balanced / pd-extreme",
            region_id="31186",
            api_version="apiVersion",
            default_item=True,
            description="description",
            supports_encryption=False,
            tags=[
                {
                    "key": "tier",
                    "value": "silver",
                }
            ],
        )
        assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_storage_profiles_gcp(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles_gcp.with_raw_response.storage_profiles_gcp(
            name="name",
            persistent_disk_type="pd-standard / pd-ssd / pd-balanced / pd-extreme",
            region_id="31186",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_gcp = response.parse()
        assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_storage_profiles_gcp(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles_gcp.with_streaming_response.storage_profiles_gcp(
            name="name",
            persistent_disk_type="pd-standard / pd-ssd / pd-balanced / pd-extreme",
            region_id="31186",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_gcp = response.parse()
            assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncStorageProfilesGcp:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_gcp = await async_client.iaas.api.storage_profiles_gcp.retrieve(
            id="id",
        )
        assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_gcp = await async_client.iaas.api.storage_profiles_gcp.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles_gcp.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_gcp = await response.parse()
        assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles_gcp.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_gcp = await response.parse()
            assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.storage_profiles_gcp.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_gcp = await async_client.iaas.api.storage_profiles_gcp.update(
            id="id",
            name="name",
            persistent_disk_type="pd-standard / pd-ssd / pd-balanced / pd-extreme",
            region_id="31186",
        )
        assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_gcp = await async_client.iaas.api.storage_profiles_gcp.update(
            id="id",
            name="name",
            persistent_disk_type="pd-standard / pd-ssd / pd-balanced / pd-extreme",
            region_id="31186",
            api_version="apiVersion",
            default_item=True,
            description="description",
            supports_encryption=False,
            tags=[
                {
                    "key": "tier",
                    "value": "silver",
                }
            ],
        )
        assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles_gcp.with_raw_response.update(
            id="id",
            name="name",
            persistent_disk_type="pd-standard / pd-ssd / pd-balanced / pd-extreme",
            region_id="31186",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_gcp = await response.parse()
        assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles_gcp.with_streaming_response.update(
            id="id",
            name="name",
            persistent_disk_type="pd-standard / pd-ssd / pd-balanced / pd-extreme",
            region_id="31186",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_gcp = await response.parse()
            assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.storage_profiles_gcp.with_raw_response.update(
                id="",
                name="name",
                persistent_disk_type="pd-standard / pd-ssd / pd-balanced / pd-extreme",
                region_id="31186",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_gcp = await async_client.iaas.api.storage_profiles_gcp.delete(
            id="id",
        )
        assert storage_profiles_gcp is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_gcp = await async_client.iaas.api.storage_profiles_gcp.delete(
            id="id",
            api_version="apiVersion",
        )
        assert storage_profiles_gcp is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles_gcp.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_gcp = await response.parse()
        assert storage_profiles_gcp is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles_gcp.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_gcp = await response.parse()
            assert storage_profiles_gcp is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.storage_profiles_gcp.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_storage_profiles_gcp(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_gcp = await async_client.iaas.api.storage_profiles_gcp.retrieve_storage_profiles_gcp()
        assert_matches_type(
            StorageProfilesGcpRetrieveStorageProfilesGcpResponse, storage_profiles_gcp, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_storage_profiles_gcp_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_gcp = await async_client.iaas.api.storage_profiles_gcp.retrieve_storage_profiles_gcp(
            api_version="apiVersion",
        )
        assert_matches_type(
            StorageProfilesGcpRetrieveStorageProfilesGcpResponse, storage_profiles_gcp, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_storage_profiles_gcp(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles_gcp.with_raw_response.retrieve_storage_profiles_gcp()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_gcp = await response.parse()
        assert_matches_type(
            StorageProfilesGcpRetrieveStorageProfilesGcpResponse, storage_profiles_gcp, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_storage_profiles_gcp(self, async_client: AsyncVraIaas) -> None:
        async with (
            async_client.iaas.api.storage_profiles_gcp.with_streaming_response.retrieve_storage_profiles_gcp()
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_gcp = await response.parse()
            assert_matches_type(
                StorageProfilesGcpRetrieveStorageProfilesGcpResponse, storage_profiles_gcp, path=["response"]
            )

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_storage_profiles_gcp(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_gcp = await async_client.iaas.api.storage_profiles_gcp.storage_profiles_gcp(
            name="name",
            persistent_disk_type="pd-standard / pd-ssd / pd-balanced / pd-extreme",
            region_id="31186",
        )
        assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_storage_profiles_gcp_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_gcp = await async_client.iaas.api.storage_profiles_gcp.storage_profiles_gcp(
            name="name",
            persistent_disk_type="pd-standard / pd-ssd / pd-balanced / pd-extreme",
            region_id="31186",
            api_version="apiVersion",
            default_item=True,
            description="description",
            supports_encryption=False,
            tags=[
                {
                    "key": "tier",
                    "value": "silver",
                }
            ],
        )
        assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_storage_profiles_gcp(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles_gcp.with_raw_response.storage_profiles_gcp(
            name="name",
            persistent_disk_type="pd-standard / pd-ssd / pd-balanced / pd-extreme",
            region_id="31186",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_gcp = await response.parse()
        assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_storage_profiles_gcp(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles_gcp.with_streaming_response.storage_profiles_gcp(
            name="name",
            persistent_disk_type="pd-standard / pd-ssd / pd-balanced / pd-extreme",
            region_id="31186",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_gcp = await response.parse()
            assert_matches_type(GcpStorageProfile, storage_profiles_gcp, path=["response"])

        assert cast(Any, response.is_closed) is True
