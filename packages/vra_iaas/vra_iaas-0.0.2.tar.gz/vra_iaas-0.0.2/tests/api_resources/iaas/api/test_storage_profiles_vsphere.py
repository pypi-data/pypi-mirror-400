# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    VsphereStorageProfile,
    StorageProfilesVsphereRetrieveStorageProfilesVsphereResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestStorageProfilesVsphere:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        storage_profiles_vsphere = client.iaas.api.storage_profiles_vsphere.retrieve(
            id="id",
        )
        assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        storage_profiles_vsphere = client.iaas.api.storage_profiles_vsphere.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles_vsphere.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_vsphere = response.parse()
        assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles_vsphere.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_vsphere = response.parse()
            assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.storage_profiles_vsphere.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        storage_profiles_vsphere = client.iaas.api.storage_profiles_vsphere.update(
            id="id",
            default_item=True,
            name="name",
            region_id="31186",
        )
        assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        storage_profiles_vsphere = client.iaas.api.storage_profiles_vsphere.update(
            id="id",
            default_item=True,
            name="name",
            region_id="31186",
            api_version="apiVersion",
            compute_host_id="8c4ba7aa-3520-344d-b118-4a2108aaabb8",
            datastore_id="08d28",
            description="description",
            disk_mode="undefined / independent-persistent / independent-nonpersistent",
            disk_type="standard / firstClass",
            limit_iops="1000",
            priority=2,
            provisioning_type="thin / thick / eagerZeroedThick",
            shares="2000",
            shares_level="low / normal / high / custom",
            storage_filter_type="MANUAL",
            storage_policy_id="6b59743af31d",
            storage_profile_associations=[
                {
                    "associations": [
                        {
                            "data_store_id": "a42d016e-6b0e-4265-9881-692e90b76684",
                            "priority": 0,
                        }
                    ],
                    "request_type": "CREATE",
                }
            ],
            supports_encryption=False,
            tags=[
                {
                    "key": "tier",
                    "value": "silver",
                }
            ],
            tags_to_match=[
                {
                    "key": "tag1",
                    "value": "value1",
                }
            ],
        )
        assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles_vsphere.with_raw_response.update(
            id="id",
            default_item=True,
            name="name",
            region_id="31186",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_vsphere = response.parse()
        assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles_vsphere.with_streaming_response.update(
            id="id",
            default_item=True,
            name="name",
            region_id="31186",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_vsphere = response.parse()
            assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.storage_profiles_vsphere.with_raw_response.update(
                id="",
                default_item=True,
                name="name",
                region_id="31186",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        storage_profiles_vsphere = client.iaas.api.storage_profiles_vsphere.delete(
            id="id",
        )
        assert storage_profiles_vsphere is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: VraIaas) -> None:
        storage_profiles_vsphere = client.iaas.api.storage_profiles_vsphere.delete(
            id="id",
            api_version="apiVersion",
        )
        assert storage_profiles_vsphere is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles_vsphere.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_vsphere = response.parse()
        assert storage_profiles_vsphere is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles_vsphere.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_vsphere = response.parse()
            assert storage_profiles_vsphere is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.storage_profiles_vsphere.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_storage_profiles_vsphere(self, client: VraIaas) -> None:
        storage_profiles_vsphere = client.iaas.api.storage_profiles_vsphere.retrieve_storage_profiles_vsphere()
        assert_matches_type(
            StorageProfilesVsphereRetrieveStorageProfilesVsphereResponse, storage_profiles_vsphere, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_storage_profiles_vsphere_with_all_params(self, client: VraIaas) -> None:
        storage_profiles_vsphere = client.iaas.api.storage_profiles_vsphere.retrieve_storage_profiles_vsphere(
            api_version="apiVersion",
        )
        assert_matches_type(
            StorageProfilesVsphereRetrieveStorageProfilesVsphereResponse, storage_profiles_vsphere, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_storage_profiles_vsphere(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles_vsphere.with_raw_response.retrieve_storage_profiles_vsphere()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_vsphere = response.parse()
        assert_matches_type(
            StorageProfilesVsphereRetrieveStorageProfilesVsphereResponse, storage_profiles_vsphere, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_storage_profiles_vsphere(self, client: VraIaas) -> None:
        with (
            client.iaas.api.storage_profiles_vsphere.with_streaming_response.retrieve_storage_profiles_vsphere()
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_vsphere = response.parse()
            assert_matches_type(
                StorageProfilesVsphereRetrieveStorageProfilesVsphereResponse,
                storage_profiles_vsphere,
                path=["response"],
            )

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_storage_profiles_vsphere(self, client: VraIaas) -> None:
        storage_profiles_vsphere = client.iaas.api.storage_profiles_vsphere.storage_profiles_vsphere(
            default_item=True,
            name="name",
            region_id="31186",
        )
        assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_storage_profiles_vsphere_with_all_params(self, client: VraIaas) -> None:
        storage_profiles_vsphere = client.iaas.api.storage_profiles_vsphere.storage_profiles_vsphere(
            default_item=True,
            name="name",
            region_id="31186",
            api_version="apiVersion",
            compute_host_id="8c4ba7aa-3520-344d-b118-4a2108aaabb8",
            datastore_id="08d28",
            description="description",
            disk_mode="undefined / independent-persistent / independent-nonpersistent",
            disk_type="standard / firstClass",
            limit_iops="1000",
            priority=2,
            provisioning_type="thin / thick / eagerZeroedThick",
            shares="2000",
            shares_level="low / normal / high / custom",
            storage_filter_type="MANUAL",
            storage_policy_id="6b59743af31d",
            storage_profile_associations=[
                {
                    "associations": [
                        {
                            "data_store_id": "a42d016e-6b0e-4265-9881-692e90b76684",
                            "priority": 0,
                        }
                    ],
                    "request_type": "CREATE",
                }
            ],
            supports_encryption=False,
            tags=[
                {
                    "key": "tier",
                    "value": "silver",
                }
            ],
            tags_to_match=[
                {
                    "key": "tag1",
                    "value": "value1",
                }
            ],
        )
        assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_storage_profiles_vsphere(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles_vsphere.with_raw_response.storage_profiles_vsphere(
            default_item=True,
            name="name",
            region_id="31186",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_vsphere = response.parse()
        assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_storage_profiles_vsphere(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles_vsphere.with_streaming_response.storage_profiles_vsphere(
            default_item=True,
            name="name",
            region_id="31186",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_vsphere = response.parse()
            assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncStorageProfilesVsphere:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_vsphere = await async_client.iaas.api.storage_profiles_vsphere.retrieve(
            id="id",
        )
        assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_vsphere = await async_client.iaas.api.storage_profiles_vsphere.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles_vsphere.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_vsphere = await response.parse()
        assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles_vsphere.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_vsphere = await response.parse()
            assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.storage_profiles_vsphere.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_vsphere = await async_client.iaas.api.storage_profiles_vsphere.update(
            id="id",
            default_item=True,
            name="name",
            region_id="31186",
        )
        assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_vsphere = await async_client.iaas.api.storage_profiles_vsphere.update(
            id="id",
            default_item=True,
            name="name",
            region_id="31186",
            api_version="apiVersion",
            compute_host_id="8c4ba7aa-3520-344d-b118-4a2108aaabb8",
            datastore_id="08d28",
            description="description",
            disk_mode="undefined / independent-persistent / independent-nonpersistent",
            disk_type="standard / firstClass",
            limit_iops="1000",
            priority=2,
            provisioning_type="thin / thick / eagerZeroedThick",
            shares="2000",
            shares_level="low / normal / high / custom",
            storage_filter_type="MANUAL",
            storage_policy_id="6b59743af31d",
            storage_profile_associations=[
                {
                    "associations": [
                        {
                            "data_store_id": "a42d016e-6b0e-4265-9881-692e90b76684",
                            "priority": 0,
                        }
                    ],
                    "request_type": "CREATE",
                }
            ],
            supports_encryption=False,
            tags=[
                {
                    "key": "tier",
                    "value": "silver",
                }
            ],
            tags_to_match=[
                {
                    "key": "tag1",
                    "value": "value1",
                }
            ],
        )
        assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles_vsphere.with_raw_response.update(
            id="id",
            default_item=True,
            name="name",
            region_id="31186",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_vsphere = await response.parse()
        assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles_vsphere.with_streaming_response.update(
            id="id",
            default_item=True,
            name="name",
            region_id="31186",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_vsphere = await response.parse()
            assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.storage_profiles_vsphere.with_raw_response.update(
                id="",
                default_item=True,
                name="name",
                region_id="31186",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_vsphere = await async_client.iaas.api.storage_profiles_vsphere.delete(
            id="id",
        )
        assert storage_profiles_vsphere is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_vsphere = await async_client.iaas.api.storage_profiles_vsphere.delete(
            id="id",
            api_version="apiVersion",
        )
        assert storage_profiles_vsphere is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles_vsphere.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_vsphere = await response.parse()
        assert storage_profiles_vsphere is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles_vsphere.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_vsphere = await response.parse()
            assert storage_profiles_vsphere is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.storage_profiles_vsphere.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_storage_profiles_vsphere(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_vsphere = (
            await async_client.iaas.api.storage_profiles_vsphere.retrieve_storage_profiles_vsphere()
        )
        assert_matches_type(
            StorageProfilesVsphereRetrieveStorageProfilesVsphereResponse, storage_profiles_vsphere, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_storage_profiles_vsphere_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_vsphere = (
            await async_client.iaas.api.storage_profiles_vsphere.retrieve_storage_profiles_vsphere(
                api_version="apiVersion",
            )
        )
        assert_matches_type(
            StorageProfilesVsphereRetrieveStorageProfilesVsphereResponse, storage_profiles_vsphere, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_storage_profiles_vsphere(self, async_client: AsyncVraIaas) -> None:
        response = (
            await async_client.iaas.api.storage_profiles_vsphere.with_raw_response.retrieve_storage_profiles_vsphere()
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_vsphere = await response.parse()
        assert_matches_type(
            StorageProfilesVsphereRetrieveStorageProfilesVsphereResponse, storage_profiles_vsphere, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_storage_profiles_vsphere(self, async_client: AsyncVraIaas) -> None:
        async with (
            async_client.iaas.api.storage_profiles_vsphere.with_streaming_response.retrieve_storage_profiles_vsphere()
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_vsphere = await response.parse()
            assert_matches_type(
                StorageProfilesVsphereRetrieveStorageProfilesVsphereResponse,
                storage_profiles_vsphere,
                path=["response"],
            )

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_storage_profiles_vsphere(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_vsphere = await async_client.iaas.api.storage_profiles_vsphere.storage_profiles_vsphere(
            default_item=True,
            name="name",
            region_id="31186",
        )
        assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_storage_profiles_vsphere_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profiles_vsphere = await async_client.iaas.api.storage_profiles_vsphere.storage_profiles_vsphere(
            default_item=True,
            name="name",
            region_id="31186",
            api_version="apiVersion",
            compute_host_id="8c4ba7aa-3520-344d-b118-4a2108aaabb8",
            datastore_id="08d28",
            description="description",
            disk_mode="undefined / independent-persistent / independent-nonpersistent",
            disk_type="standard / firstClass",
            limit_iops="1000",
            priority=2,
            provisioning_type="thin / thick / eagerZeroedThick",
            shares="2000",
            shares_level="low / normal / high / custom",
            storage_filter_type="MANUAL",
            storage_policy_id="6b59743af31d",
            storage_profile_associations=[
                {
                    "associations": [
                        {
                            "data_store_id": "a42d016e-6b0e-4265-9881-692e90b76684",
                            "priority": 0,
                        }
                    ],
                    "request_type": "CREATE",
                }
            ],
            supports_encryption=False,
            tags=[
                {
                    "key": "tier",
                    "value": "silver",
                }
            ],
            tags_to_match=[
                {
                    "key": "tag1",
                    "value": "value1",
                }
            ],
        )
        assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_storage_profiles_vsphere(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles_vsphere.with_raw_response.storage_profiles_vsphere(
            default_item=True,
            name="name",
            region_id="31186",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profiles_vsphere = await response.parse()
        assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_storage_profiles_vsphere(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles_vsphere.with_streaming_response.storage_profiles_vsphere(
            default_item=True,
            name="name",
            region_id="31186",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profiles_vsphere = await response.parse()
            assert_matches_type(VsphereStorageProfile, storage_profiles_vsphere, path=["response"])

        assert cast(Any, response.is_closed) is True
