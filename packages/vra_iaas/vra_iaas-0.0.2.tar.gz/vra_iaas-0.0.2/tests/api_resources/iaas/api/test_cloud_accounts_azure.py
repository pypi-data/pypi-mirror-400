# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    CloudAccountAzure,
    CloudAccountsAzureRetrieveCloudAccountsAzureResponse,
)
from vra_iaas.types.iaas.api.projects import RequestTracker

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCloudAccountsAzure:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        cloud_accounts_azure = client.iaas.api.cloud_accounts_azure.retrieve(
            id="id",
        )
        assert_matches_type(CloudAccountAzure, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_azure = client.iaas.api.cloud_accounts_azure.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(CloudAccountAzure, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_azure.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_azure = response.parse()
        assert_matches_type(CloudAccountAzure, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_azure.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_azure = response.parse()
            assert_matches_type(CloudAccountAzure, cloud_accounts_azure, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts_azure.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        cloud_accounts_azure = client.iaas.api.cloud_accounts_azure.update(
            id="id",
            api_version="apiVersion",
            client_application_id="3287dd6e-76d8-41b7-9856-2584969e7739",
            client_application_secret_key="GDfdasDasdASFas321das32cas2x3dsXCSA76xdcasg=",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
            subscription_id="064865b2-e914-4717-b415-8806d17948f7",
            tenant_id="9a13d920-4691-4e2d-b5d5-9c4c1279bc9a",
        )
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_azure = client.iaas.api.cloud_accounts_azure.update(
            id="id",
            api_version="apiVersion",
            client_application_id="3287dd6e-76d8-41b7-9856-2584969e7739",
            client_application_secret_key="GDfdasDasdASFas321das32cas2x3dsXCSA76xdcasg=",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
            subscription_id="064865b2-e914-4717-b415-8806d17948f7",
            tenant_id="9a13d920-4691-4e2d-b5d5-9c4c1279bc9a",
            create_default_zones=True,
            description="description",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
        )
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_azure.with_raw_response.update(
            id="id",
            api_version="apiVersion",
            client_application_id="3287dd6e-76d8-41b7-9856-2584969e7739",
            client_application_secret_key="GDfdasDasdASFas321das32cas2x3dsXCSA76xdcasg=",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
            subscription_id="064865b2-e914-4717-b415-8806d17948f7",
            tenant_id="9a13d920-4691-4e2d-b5d5-9c4c1279bc9a",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_azure = response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_azure.with_streaming_response.update(
            id="id",
            api_version="apiVersion",
            client_application_id="3287dd6e-76d8-41b7-9856-2584969e7739",
            client_application_secret_key="GDfdasDasdASFas321das32cas2x3dsXCSA76xdcasg=",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
            subscription_id="064865b2-e914-4717-b415-8806d17948f7",
            tenant_id="9a13d920-4691-4e2d-b5d5-9c4c1279bc9a",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_azure = response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts_azure.with_raw_response.update(
                id="",
                api_version="apiVersion",
                client_application_id="3287dd6e-76d8-41b7-9856-2584969e7739",
                client_application_secret_key="GDfdasDasdASFas321das32cas2x3dsXCSA76xdcasg=",
                name="name",
                regions=[
                    {
                        "external_region_id": "eastasia",
                        "name": "East Asia",
                    }
                ],
                subscription_id="064865b2-e914-4717-b415-8806d17948f7",
                tenant_id="9a13d920-4691-4e2d-b5d5-9c4c1279bc9a",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        cloud_accounts_azure = client.iaas.api.cloud_accounts_azure.delete(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_azure.with_raw_response.delete(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_azure = response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_azure.with_streaming_response.delete(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_azure = response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts_azure.with_raw_response.delete(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cloud_accounts_azure(self, client: VraIaas) -> None:
        cloud_accounts_azure = client.iaas.api.cloud_accounts_azure.cloud_accounts_azure(
            api_version="apiVersion",
            client_application_id="3287dd6e-76d8-41b7-9856-2584969e7739",
            client_application_secret_key="GDfdasDasdASFas321das32cas2x3dsXCSA76xdcasg=",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
            subscription_id="064865b2-e914-4717-b415-8806d17948f7",
            tenant_id="9a13d920-4691-4e2d-b5d5-9c4c1279bc9a",
        )
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cloud_accounts_azure_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_azure = client.iaas.api.cloud_accounts_azure.cloud_accounts_azure(
            api_version="apiVersion",
            client_application_id="3287dd6e-76d8-41b7-9856-2584969e7739",
            client_application_secret_key="GDfdasDasdASFas321das32cas2x3dsXCSA76xdcasg=",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
            subscription_id="064865b2-e914-4717-b415-8806d17948f7",
            tenant_id="9a13d920-4691-4e2d-b5d5-9c4c1279bc9a",
            validate_only="validateOnly",
            create_default_zones=True,
            description="description",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
        )
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_cloud_accounts_azure(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_azure.with_raw_response.cloud_accounts_azure(
            api_version="apiVersion",
            client_application_id="3287dd6e-76d8-41b7-9856-2584969e7739",
            client_application_secret_key="GDfdasDasdASFas321das32cas2x3dsXCSA76xdcasg=",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
            subscription_id="064865b2-e914-4717-b415-8806d17948f7",
            tenant_id="9a13d920-4691-4e2d-b5d5-9c4c1279bc9a",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_azure = response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_cloud_accounts_azure(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_azure.with_streaming_response.cloud_accounts_azure(
            api_version="apiVersion",
            client_application_id="3287dd6e-76d8-41b7-9856-2584969e7739",
            client_application_secret_key="GDfdasDasdASFas321das32cas2x3dsXCSA76xdcasg=",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
            subscription_id="064865b2-e914-4717-b415-8806d17948f7",
            tenant_id="9a13d920-4691-4e2d-b5d5-9c4c1279bc9a",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_azure = response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_private_image_enumeration(self, client: VraIaas) -> None:
        cloud_accounts_azure = client.iaas.api.cloud_accounts_azure.private_image_enumeration(
            id="id",
        )
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_private_image_enumeration_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_azure = client.iaas.api.cloud_accounts_azure.private_image_enumeration(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_private_image_enumeration(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_azure.with_raw_response.private_image_enumeration(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_azure = response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_private_image_enumeration(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_azure.with_streaming_response.private_image_enumeration(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_azure = response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_private_image_enumeration(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts_azure.with_raw_response.private_image_enumeration(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_region_enumeration(self, client: VraIaas) -> None:
        cloud_accounts_azure = client.iaas.api.cloud_accounts_azure.region_enumeration(
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_region_enumeration_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_azure = client.iaas.api.cloud_accounts_azure.region_enumeration(
            api_version="apiVersion",
            client_application_id="3287dd6e-76d8-41b7-9856-2584969e7739",
            client_application_secret_key="GDfdasDasdASFas321das32cas2x3dsXCSA76xdcasg=",
            cloud_account_id="b8b7a918-342e-4a53-a3b0-b935da0fe601",
            subscription_id="064865b2-e914-4717-b415-8806d17948f7",
            tenant_id="9a13d920-4691-4e2d-b5d5-9c4c1279bc9a",
        )
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_region_enumeration(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_azure.with_raw_response.region_enumeration(
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_azure = response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_region_enumeration(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_azure.with_streaming_response.region_enumeration(
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_azure = response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_cloud_accounts_azure(self, client: VraIaas) -> None:
        cloud_accounts_azure = client.iaas.api.cloud_accounts_azure.retrieve_cloud_accounts_azure()
        assert_matches_type(
            CloudAccountsAzureRetrieveCloudAccountsAzureResponse, cloud_accounts_azure, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_cloud_accounts_azure_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_azure = client.iaas.api.cloud_accounts_azure.retrieve_cloud_accounts_azure(
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(
            CloudAccountsAzureRetrieveCloudAccountsAzureResponse, cloud_accounts_azure, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_cloud_accounts_azure(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_azure.with_raw_response.retrieve_cloud_accounts_azure()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_azure = response.parse()
        assert_matches_type(
            CloudAccountsAzureRetrieveCloudAccountsAzureResponse, cloud_accounts_azure, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_cloud_accounts_azure(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_azure.with_streaming_response.retrieve_cloud_accounts_azure() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_azure = response.parse()
            assert_matches_type(
                CloudAccountsAzureRetrieveCloudAccountsAzureResponse, cloud_accounts_azure, path=["response"]
            )

        assert cast(Any, response.is_closed) is True


class TestAsyncCloudAccountsAzure:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_azure = await async_client.iaas.api.cloud_accounts_azure.retrieve(
            id="id",
        )
        assert_matches_type(CloudAccountAzure, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_azure = await async_client.iaas.api.cloud_accounts_azure.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(CloudAccountAzure, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_azure.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_azure = await response.parse()
        assert_matches_type(CloudAccountAzure, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_azure.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_azure = await response.parse()
            assert_matches_type(CloudAccountAzure, cloud_accounts_azure, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts_azure.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_azure = await async_client.iaas.api.cloud_accounts_azure.update(
            id="id",
            api_version="apiVersion",
            client_application_id="3287dd6e-76d8-41b7-9856-2584969e7739",
            client_application_secret_key="GDfdasDasdASFas321das32cas2x3dsXCSA76xdcasg=",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
            subscription_id="064865b2-e914-4717-b415-8806d17948f7",
            tenant_id="9a13d920-4691-4e2d-b5d5-9c4c1279bc9a",
        )
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_azure = await async_client.iaas.api.cloud_accounts_azure.update(
            id="id",
            api_version="apiVersion",
            client_application_id="3287dd6e-76d8-41b7-9856-2584969e7739",
            client_application_secret_key="GDfdasDasdASFas321das32cas2x3dsXCSA76xdcasg=",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
            subscription_id="064865b2-e914-4717-b415-8806d17948f7",
            tenant_id="9a13d920-4691-4e2d-b5d5-9c4c1279bc9a",
            create_default_zones=True,
            description="description",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
        )
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_azure.with_raw_response.update(
            id="id",
            api_version="apiVersion",
            client_application_id="3287dd6e-76d8-41b7-9856-2584969e7739",
            client_application_secret_key="GDfdasDasdASFas321das32cas2x3dsXCSA76xdcasg=",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
            subscription_id="064865b2-e914-4717-b415-8806d17948f7",
            tenant_id="9a13d920-4691-4e2d-b5d5-9c4c1279bc9a",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_azure = await response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_azure.with_streaming_response.update(
            id="id",
            api_version="apiVersion",
            client_application_id="3287dd6e-76d8-41b7-9856-2584969e7739",
            client_application_secret_key="GDfdasDasdASFas321das32cas2x3dsXCSA76xdcasg=",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
            subscription_id="064865b2-e914-4717-b415-8806d17948f7",
            tenant_id="9a13d920-4691-4e2d-b5d5-9c4c1279bc9a",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_azure = await response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts_azure.with_raw_response.update(
                id="",
                api_version="apiVersion",
                client_application_id="3287dd6e-76d8-41b7-9856-2584969e7739",
                client_application_secret_key="GDfdasDasdASFas321das32cas2x3dsXCSA76xdcasg=",
                name="name",
                regions=[
                    {
                        "external_region_id": "eastasia",
                        "name": "East Asia",
                    }
                ],
                subscription_id="064865b2-e914-4717-b415-8806d17948f7",
                tenant_id="9a13d920-4691-4e2d-b5d5-9c4c1279bc9a",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_azure = await async_client.iaas.api.cloud_accounts_azure.delete(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_azure.with_raw_response.delete(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_azure = await response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_azure.with_streaming_response.delete(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_azure = await response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts_azure.with_raw_response.delete(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cloud_accounts_azure(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_azure = await async_client.iaas.api.cloud_accounts_azure.cloud_accounts_azure(
            api_version="apiVersion",
            client_application_id="3287dd6e-76d8-41b7-9856-2584969e7739",
            client_application_secret_key="GDfdasDasdASFas321das32cas2x3dsXCSA76xdcasg=",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
            subscription_id="064865b2-e914-4717-b415-8806d17948f7",
            tenant_id="9a13d920-4691-4e2d-b5d5-9c4c1279bc9a",
        )
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cloud_accounts_azure_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_azure = await async_client.iaas.api.cloud_accounts_azure.cloud_accounts_azure(
            api_version="apiVersion",
            client_application_id="3287dd6e-76d8-41b7-9856-2584969e7739",
            client_application_secret_key="GDfdasDasdASFas321das32cas2x3dsXCSA76xdcasg=",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
            subscription_id="064865b2-e914-4717-b415-8806d17948f7",
            tenant_id="9a13d920-4691-4e2d-b5d5-9c4c1279bc9a",
            validate_only="validateOnly",
            create_default_zones=True,
            description="description",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
        )
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_cloud_accounts_azure(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_azure.with_raw_response.cloud_accounts_azure(
            api_version="apiVersion",
            client_application_id="3287dd6e-76d8-41b7-9856-2584969e7739",
            client_application_secret_key="GDfdasDasdASFas321das32cas2x3dsXCSA76xdcasg=",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
            subscription_id="064865b2-e914-4717-b415-8806d17948f7",
            tenant_id="9a13d920-4691-4e2d-b5d5-9c4c1279bc9a",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_azure = await response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_cloud_accounts_azure(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_azure.with_streaming_response.cloud_accounts_azure(
            api_version="apiVersion",
            client_application_id="3287dd6e-76d8-41b7-9856-2584969e7739",
            client_application_secret_key="GDfdasDasdASFas321das32cas2x3dsXCSA76xdcasg=",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
            subscription_id="064865b2-e914-4717-b415-8806d17948f7",
            tenant_id="9a13d920-4691-4e2d-b5d5-9c4c1279bc9a",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_azure = await response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_private_image_enumeration(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_azure = await async_client.iaas.api.cloud_accounts_azure.private_image_enumeration(
            id="id",
        )
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_private_image_enumeration_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_azure = await async_client.iaas.api.cloud_accounts_azure.private_image_enumeration(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_private_image_enumeration(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_azure.with_raw_response.private_image_enumeration(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_azure = await response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_private_image_enumeration(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_azure.with_streaming_response.private_image_enumeration(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_azure = await response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_private_image_enumeration(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts_azure.with_raw_response.private_image_enumeration(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_region_enumeration(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_azure = await async_client.iaas.api.cloud_accounts_azure.region_enumeration(
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_region_enumeration_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_azure = await async_client.iaas.api.cloud_accounts_azure.region_enumeration(
            api_version="apiVersion",
            client_application_id="3287dd6e-76d8-41b7-9856-2584969e7739",
            client_application_secret_key="GDfdasDasdASFas321das32cas2x3dsXCSA76xdcasg=",
            cloud_account_id="b8b7a918-342e-4a53-a3b0-b935da0fe601",
            subscription_id="064865b2-e914-4717-b415-8806d17948f7",
            tenant_id="9a13d920-4691-4e2d-b5d5-9c4c1279bc9a",
        )
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_region_enumeration(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_azure.with_raw_response.region_enumeration(
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_azure = await response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_region_enumeration(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_azure.with_streaming_response.region_enumeration(
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_azure = await response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_azure, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_cloud_accounts_azure(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_azure = await async_client.iaas.api.cloud_accounts_azure.retrieve_cloud_accounts_azure()
        assert_matches_type(
            CloudAccountsAzureRetrieveCloudAccountsAzureResponse, cloud_accounts_azure, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_cloud_accounts_azure_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_azure = await async_client.iaas.api.cloud_accounts_azure.retrieve_cloud_accounts_azure(
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(
            CloudAccountsAzureRetrieveCloudAccountsAzureResponse, cloud_accounts_azure, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_cloud_accounts_azure(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_azure.with_raw_response.retrieve_cloud_accounts_azure()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_azure = await response.parse()
        assert_matches_type(
            CloudAccountsAzureRetrieveCloudAccountsAzureResponse, cloud_accounts_azure, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_cloud_accounts_azure(self, async_client: AsyncVraIaas) -> None:
        async with (
            async_client.iaas.api.cloud_accounts_azure.with_streaming_response.retrieve_cloud_accounts_azure()
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_azure = await response.parse()
            assert_matches_type(
                CloudAccountsAzureRetrieveCloudAccountsAzureResponse, cloud_accounts_azure, path=["response"]
            )

        assert cast(Any, response.is_closed) is True
