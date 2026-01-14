# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api.storage_profiles import (
    StorageProfileAssociationUpdateStorageProfileAssociationsResponse,
    StorageProfileAssociationRetrieveStorageProfileAssociationsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestStorageProfileAssociations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_storage_profile_associations(self, client: VraIaas) -> None:
        storage_profile_association = (
            client.iaas.api.storage_profiles.storage_profile_associations.retrieve_storage_profile_associations(
                id="id",
            )
        )
        assert_matches_type(
            StorageProfileAssociationRetrieveStorageProfileAssociationsResponse,
            storage_profile_association,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_storage_profile_associations_with_all_params(self, client: VraIaas) -> None:
        storage_profile_association = (
            client.iaas.api.storage_profiles.storage_profile_associations.retrieve_storage_profile_associations(
                id="id",
                api_version="apiVersion",
                page=0,
                size=0,
            )
        )
        assert_matches_type(
            StorageProfileAssociationRetrieveStorageProfileAssociationsResponse,
            storage_profile_association,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_storage_profile_associations(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles.storage_profile_associations.with_raw_response.retrieve_storage_profile_associations(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profile_association = response.parse()
        assert_matches_type(
            StorageProfileAssociationRetrieveStorageProfileAssociationsResponse,
            storage_profile_association,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_storage_profile_associations(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles.storage_profile_associations.with_streaming_response.retrieve_storage_profile_associations(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profile_association = response.parse()
            assert_matches_type(
                StorageProfileAssociationRetrieveStorageProfileAssociationsResponse,
                storage_profile_association,
                path=["response"],
            )

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_storage_profile_associations(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.storage_profiles.storage_profile_associations.with_raw_response.retrieve_storage_profile_associations(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_storage_profile_associations(self, client: VraIaas) -> None:
        storage_profile_association = (
            client.iaas.api.storage_profiles.storage_profile_associations.update_storage_profile_associations(
                id="id",
                region_id="31186",
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
            )
        )
        assert_matches_type(
            StorageProfileAssociationUpdateStorageProfileAssociationsResponse,
            storage_profile_association,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_storage_profile_associations_with_all_params(self, client: VraIaas) -> None:
        storage_profile_association = (
            client.iaas.api.storage_profiles.storage_profile_associations.update_storage_profile_associations(
                id="id",
                region_id="31186",
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
                api_version="apiVersion",
            )
        )
        assert_matches_type(
            StorageProfileAssociationUpdateStorageProfileAssociationsResponse,
            storage_profile_association,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_storage_profile_associations(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles.storage_profile_associations.with_raw_response.update_storage_profile_associations(
            id="id",
            region_id="31186",
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
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profile_association = response.parse()
        assert_matches_type(
            StorageProfileAssociationUpdateStorageProfileAssociationsResponse,
            storage_profile_association,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_storage_profile_associations(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles.storage_profile_associations.with_streaming_response.update_storage_profile_associations(
            id="id",
            region_id="31186",
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
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profile_association = response.parse()
            assert_matches_type(
                StorageProfileAssociationUpdateStorageProfileAssociationsResponse,
                storage_profile_association,
                path=["response"],
            )

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_storage_profile_associations(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.storage_profiles.storage_profile_associations.with_raw_response.update_storage_profile_associations(
                id="",
                region_id="31186",
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
            )


class TestAsyncStorageProfileAssociations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_storage_profile_associations(self, async_client: AsyncVraIaas) -> None:
        storage_profile_association = await async_client.iaas.api.storage_profiles.storage_profile_associations.retrieve_storage_profile_associations(
            id="id",
        )
        assert_matches_type(
            StorageProfileAssociationRetrieveStorageProfileAssociationsResponse,
            storage_profile_association,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_storage_profile_associations_with_all_params(
        self, async_client: AsyncVraIaas
    ) -> None:
        storage_profile_association = await async_client.iaas.api.storage_profiles.storage_profile_associations.retrieve_storage_profile_associations(
            id="id",
            api_version="apiVersion",
            page=0,
            size=0,
        )
        assert_matches_type(
            StorageProfileAssociationRetrieveStorageProfileAssociationsResponse,
            storage_profile_association,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_storage_profile_associations(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles.storage_profile_associations.with_raw_response.retrieve_storage_profile_associations(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profile_association = await response.parse()
        assert_matches_type(
            StorageProfileAssociationRetrieveStorageProfileAssociationsResponse,
            storage_profile_association,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_storage_profile_associations(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles.storage_profile_associations.with_streaming_response.retrieve_storage_profile_associations(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profile_association = await response.parse()
            assert_matches_type(
                StorageProfileAssociationRetrieveStorageProfileAssociationsResponse,
                storage_profile_association,
                path=["response"],
            )

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_storage_profile_associations(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.storage_profiles.storage_profile_associations.with_raw_response.retrieve_storage_profile_associations(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_storage_profile_associations(self, async_client: AsyncVraIaas) -> None:
        storage_profile_association = await async_client.iaas.api.storage_profiles.storage_profile_associations.update_storage_profile_associations(
            id="id",
            region_id="31186",
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
        )
        assert_matches_type(
            StorageProfileAssociationUpdateStorageProfileAssociationsResponse,
            storage_profile_association,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_storage_profile_associations_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profile_association = await async_client.iaas.api.storage_profiles.storage_profile_associations.update_storage_profile_associations(
            id="id",
            region_id="31186",
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
            api_version="apiVersion",
        )
        assert_matches_type(
            StorageProfileAssociationUpdateStorageProfileAssociationsResponse,
            storage_profile_association,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_storage_profile_associations(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles.storage_profile_associations.with_raw_response.update_storage_profile_associations(
            id="id",
            region_id="31186",
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
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profile_association = await response.parse()
        assert_matches_type(
            StorageProfileAssociationUpdateStorageProfileAssociationsResponse,
            storage_profile_association,
            path=["response"],
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_storage_profile_associations(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles.storage_profile_associations.with_streaming_response.update_storage_profile_associations(
            id="id",
            region_id="31186",
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
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profile_association = await response.parse()
            assert_matches_type(
                StorageProfileAssociationUpdateStorageProfileAssociationsResponse,
                storage_profile_association,
                path=["response"],
            )

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_storage_profile_associations(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.storage_profiles.storage_profile_associations.with_raw_response.update_storage_profile_associations(
                id="",
                region_id="31186",
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
            )
