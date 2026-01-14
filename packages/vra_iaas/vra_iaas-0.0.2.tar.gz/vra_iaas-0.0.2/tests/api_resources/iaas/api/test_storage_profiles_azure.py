# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    AzureStorageProfile,
    StorageProfilesAzureRetrieveStorageProfilesAzureResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestStorageProfilesAzure:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        storage_profiles_azure = client.iaas.api.storage_profiles_azure.retrieve(
            id="id",
        )
        assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        storage_profiles_azure = client.iaas.api.storage_profiles_azure.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles_azure.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_azure = response.parse()
        assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles_azure.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_azure = response.parse()
            assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.storage_profiles_azure.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        storage_profiles_azure = client.iaas.api.storage_profiles_azure.update(
            id="id",
            name="name",
            region_id="31186",
        )
        assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        storage_profiles_azure = client.iaas.api.storage_profiles_azure.update(
            id="id",
            name="name",
            region_id="31186",
            api_version="apiVersion",
            data_disk_caching="None / ReadOnly / ReadWrite",
            default_item=True,
            description="description",
            disk_encryption_set_id="/subscriptions/b8ef63/resourceGroups/DiskEncryptionSets/providers/Microsoft.Compute/diskEncryptionSets/MyDES",
            disk_type="Standard_LRS / Premium_LRS",
            os_disk_caching="None / ReadOnly / ReadWrite",
            storage_account_id="aaa82",
            supports_encryption=False,
            tags=[
                {
                    "key": "tier",
                    "value": "silver",
                }
            ],
        )
        assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles_azure.with_raw_response.update(
            id="id",
            name="name",
            region_id="31186",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_azure = response.parse()
        assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles_azure.with_streaming_response.update(
            id="id",
            name="name",
            region_id="31186",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_azure = response.parse()
            assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.storage_profiles_azure.with_raw_response.update(
                id="",
                name="name",
                region_id="31186",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        storage_profiles_azure = client.iaas.api.storage_profiles_azure.delete(
            id="id",
        )
        assert storage_profiles_azure is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: VraIaas) -> None:
        storage_profiles_azure = client.iaas.api.storage_profiles_azure.delete(
            id="id",
            api_version="apiVersion",
        )
        assert storage_profiles_azure is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles_azure.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_azure = response.parse()
        assert storage_profiles_azure is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles_azure.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_azure = response.parse()
            assert storage_profiles_azure is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.storage_profiles_azure.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_storage_profiles_azure(self, client: VraIaas) -> None:
        storage_profiles_azure = client.iaas.api.storage_profiles_azure.retrieve_storage_profiles_azure()
        assert_matches_type(
            StorageProfilesAzureRetrieveStorageProfilesAzureResponse, storage_profiles_azure, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_storage_profiles_azure_with_all_params(self, client: VraIaas) -> None:
        storage_profiles_azure = client.iaas.api.storage_profiles_azure.retrieve_storage_profiles_azure(
            api_version="apiVersion",
        )
        assert_matches_type(
            StorageProfilesAzureRetrieveStorageProfilesAzureResponse, storage_profiles_azure, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_storage_profiles_azure(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles_azure.with_raw_response.retrieve_storage_profiles_azure()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_azure = response.parse()
        assert_matches_type(
            StorageProfilesAzureRetrieveStorageProfilesAzureResponse, storage_profiles_azure, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_storage_profiles_azure(self, client: VraIaas) -> None:
        with (
            client.iaas.api.storage_profiles_azure.with_streaming_response.retrieve_storage_profiles_azure()
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_azure = response.parse()
            assert_matches_type(
                StorageProfilesAzureRetrieveStorageProfilesAzureResponse, storage_profiles_azure, path=["response"]
            )

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_storage_profiles_azure(self, client: VraIaas) -> None:
        storage_profiles_azure = client.iaas.api.storage_profiles_azure.storage_profiles_azure(
            name="name",
            region_id="31186",
        )
        assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_storage_profiles_azure_with_all_params(self, client: VraIaas) -> None:
        storage_profiles_azure = client.iaas.api.storage_profiles_azure.storage_profiles_azure(
            name="name",
            region_id="31186",
            api_version="apiVersion",
            data_disk_caching="None / ReadOnly / ReadWrite",
            default_item=True,
            description="description",
            disk_encryption_set_id="/subscriptions/b8ef63/resourceGroups/DiskEncryptionSets/providers/Microsoft.Compute/diskEncryptionSets/MyDES",
            disk_type="Standard_LRS / Premium_LRS",
            os_disk_caching="None / ReadOnly / ReadWrite",
            storage_account_id="aaa82",
            supports_encryption=False,
            tags=[
                {
                    "key": "tier",
                    "value": "silver",
                }
            ],
        )
        assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_storage_profiles_azure(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles_azure.with_raw_response.storage_profiles_azure(
            name="name",
            region_id="31186",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_azure = response.parse()
        assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_storage_profiles_azure(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles_azure.with_streaming_response.storage_profiles_azure(
            name="name",
            region_id="31186",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_azure = response.parse()
            assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncStorageProfilesAzure:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_azure = await async_client.iaas.api.storage_profiles_azure.retrieve(
            id="id",
        )
        assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_azure = await async_client.iaas.api.storage_profiles_azure.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles_azure.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_azure = await response.parse()
        assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles_azure.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_azure = await response.parse()
            assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.storage_profiles_azure.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_azure = await async_client.iaas.api.storage_profiles_azure.update(
            id="id",
            name="name",
            region_id="31186",
        )
        assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_azure = await async_client.iaas.api.storage_profiles_azure.update(
            id="id",
            name="name",
            region_id="31186",
            api_version="apiVersion",
            data_disk_caching="None / ReadOnly / ReadWrite",
            default_item=True,
            description="description",
            disk_encryption_set_id="/subscriptions/b8ef63/resourceGroups/DiskEncryptionSets/providers/Microsoft.Compute/diskEncryptionSets/MyDES",
            disk_type="Standard_LRS / Premium_LRS",
            os_disk_caching="None / ReadOnly / ReadWrite",
            storage_account_id="aaa82",
            supports_encryption=False,
            tags=[
                {
                    "key": "tier",
                    "value": "silver",
                }
            ],
        )
        assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles_azure.with_raw_response.update(
            id="id",
            name="name",
            region_id="31186",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_azure = await response.parse()
        assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles_azure.with_streaming_response.update(
            id="id",
            name="name",
            region_id="31186",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_azure = await response.parse()
            assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.storage_profiles_azure.with_raw_response.update(
                id="",
                name="name",
                region_id="31186",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_azure = await async_client.iaas.api.storage_profiles_azure.delete(
            id="id",
        )
        assert storage_profiles_azure is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_azure = await async_client.iaas.api.storage_profiles_azure.delete(
            id="id",
            api_version="apiVersion",
        )
        assert storage_profiles_azure is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles_azure.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_azure = await response.parse()
        assert storage_profiles_azure is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles_azure.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_azure = await response.parse()
            assert storage_profiles_azure is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.storage_profiles_azure.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_storage_profiles_azure(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_azure = await async_client.iaas.api.storage_profiles_azure.retrieve_storage_profiles_azure()
        assert_matches_type(
            StorageProfilesAzureRetrieveStorageProfilesAzureResponse, storage_profiles_azure, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_storage_profiles_azure_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_azure = await async_client.iaas.api.storage_profiles_azure.retrieve_storage_profiles_azure(
            api_version="apiVersion",
        )
        assert_matches_type(
            StorageProfilesAzureRetrieveStorageProfilesAzureResponse, storage_profiles_azure, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_storage_profiles_azure(self, async_client: AsyncVraIaas) -> None:
        response = (
            await async_client.iaas.api.storage_profiles_azure.with_raw_response.retrieve_storage_profiles_azure()
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_azure = await response.parse()
        assert_matches_type(
            StorageProfilesAzureRetrieveStorageProfilesAzureResponse, storage_profiles_azure, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_storage_profiles_azure(self, async_client: AsyncVraIaas) -> None:
        async with (
            async_client.iaas.api.storage_profiles_azure.with_streaming_response.retrieve_storage_profiles_azure()
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_azure = await response.parse()
            assert_matches_type(
                StorageProfilesAzureRetrieveStorageProfilesAzureResponse, storage_profiles_azure, path=["response"]
            )

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_storage_profiles_azure(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_azure = await async_client.iaas.api.storage_profiles_azure.storage_profiles_azure(
            name="name",
            region_id="31186",
        )
        assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_storage_profiles_azure_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_azure = await async_client.iaas.api.storage_profiles_azure.storage_profiles_azure(
            name="name",
            region_id="31186",
            api_version="apiVersion",
            data_disk_caching="None / ReadOnly / ReadWrite",
            default_item=True,
            description="description",
            disk_encryption_set_id="/subscriptions/b8ef63/resourceGroups/DiskEncryptionSets/providers/Microsoft.Compute/diskEncryptionSets/MyDES",
            disk_type="Standard_LRS / Premium_LRS",
            os_disk_caching="None / ReadOnly / ReadWrite",
            storage_account_id="aaa82",
            supports_encryption=False,
            tags=[
                {
                    "key": "tier",
                    "value": "silver",
                }
            ],
        )
        assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_storage_profiles_azure(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles_azure.with_raw_response.storage_profiles_azure(
            name="name",
            region_id="31186",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_azure = await response.parse()
        assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_storage_profiles_azure(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles_azure.with_streaming_response.storage_profiles_azure(
            name="name",
            region_id="31186",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_azure = await response.parse()
            assert_matches_type(AzureStorageProfile, storage_profiles_azure, path=["response"])

        assert cast(Any, response.is_closed) is True
