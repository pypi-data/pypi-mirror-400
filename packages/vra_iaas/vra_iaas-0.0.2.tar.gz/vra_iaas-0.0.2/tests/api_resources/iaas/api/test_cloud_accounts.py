# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    CloudAccount,
    CloudAccountRetrieveCloudAccountsResponse,
)
from vra_iaas.types.iaas.api.projects import RequestTracker

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCloudAccounts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        cloud_account = client.iaas.api.cloud_accounts.retrieve(
            id="id",
        )
        assert_matches_type(CloudAccount, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        cloud_account = client.iaas.api.cloud_accounts.retrieve(
            id="id",
            select="$select",
            api_version="apiVersion",
        )
        assert_matches_type(CloudAccount, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_account = response.parse()
        assert_matches_type(CloudAccount, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_account = response.parse()
            assert_matches_type(CloudAccount, cloud_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        cloud_account = client.iaas.api.cloud_accounts.update(
            id="id",
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
        )
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        cloud_account = client.iaas.api.cloud_accounts.update(
            id="id",
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
            associated_cloud_account_ids=["42f3e0d199d134755684cd935435a"],
            associated_mobility_cloud_account_ids={"42f3e0d199d134755684cd935435a": "BIDIRECTIONAL"},
            certificate_info={
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIDHjCCAoegAwIBAgIBATANBgkqhkiG9w0BAQsFADCBpjEUMBIGA1UEChMLVk13\nYXJlIEluYAAc1pw18GT3iAqQRPx0PrjzJhgjIJMla\n/1Kg4byY4FPSacNiRgY/FG2bPCqZk1yRfzmkFYCW/vU+Dg==\n-----END CERTIFICATE-----\n-"
            },
            create_default_zones=True,
            custom_properties={"sampleadapterProjectId": "projectId"},
            description="description",
            private_key="gfsScK345sGGaVdds222dasdfDDSSasdfdsa34fS",
            private_key_id="ACDC55DB4MFH6ADG75KK",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
        )
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts.with_raw_response.update(
            id="id",
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_account = response.parse()
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts.with_streaming_response.update(
            id="id",
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_account = response.parse()
            assert_matches_type(RequestTracker, cloud_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts.with_raw_response.update(
                id="",
                api_version="apiVersion",
                cloud_account_properties={
                    "supportPublicImages": "true",
                    "acceptSelfSignedCertificate": "true",
                },
                name="name",
                regions=[
                    {
                        "external_region_id": "eastasia",
                        "name": "East Asia",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        cloud_account = client.iaas.api.cloud_accounts.delete(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: VraIaas) -> None:
        cloud_account = client.iaas.api.cloud_accounts.delete(
            id="id",
            api_version="apiVersion",
            force_delete=True,
        )
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts.with_raw_response.delete(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_account = response.parse()
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts.with_streaming_response.delete(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_account = response.parse()
            assert_matches_type(RequestTracker, cloud_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts.with_raw_response.delete(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cloud_accounts(self, client: VraIaas) -> None:
        cloud_account = client.iaas.api.cloud_accounts.cloud_accounts(
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            cloud_account_type="vsphere, aws, azure, nsxv, nsxt, vmc, avilb",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
        )
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cloud_accounts_with_all_params(self, client: VraIaas) -> None:
        cloud_account = client.iaas.api.cloud_accounts.cloud_accounts(
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            cloud_account_type="vsphere, aws, azure, nsxv, nsxt, vmc, avilb",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
            validate_only="validateOnly",
            associated_cloud_account_ids=["42f3e0d199d134755684cd935435a"],
            associated_mobility_cloud_account_ids={"42f3e0d199d134755684cd935435a": "BIDIRECTIONAL"},
            certificate_info={
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIDHjCCAoegAwIBAgIBATANBgkqhkiG9w0BAQsFADCBpjEUMBIGA1UEChMLVk13\nYXJlIEluYAAc1pw18GT3iAqQRPx0PrjzJhgjIJMla\n/1Kg4byY4FPSacNiRgY/FG2bPCqZk1yRfzmkFYCW/vU+Dg==\n-----END CERTIFICATE-----\n-"
            },
            create_default_zones=True,
            custom_properties={"sampleadapterProjectId": "projectId"},
            description="description",
            private_key="gfsScK345sGGaVdds222dasdfDDSSasdfdsa34fS",
            private_key_id="ACDC55DB4MFH6ADG75KK",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
        )
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_cloud_accounts(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts.with_raw_response.cloud_accounts(
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            cloud_account_type="vsphere, aws, azure, nsxv, nsxt, vmc, avilb",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_account = response.parse()
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_cloud_accounts(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts.with_streaming_response.cloud_accounts(
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            cloud_account_type="vsphere, aws, azure, nsxv, nsxt, vmc, avilb",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_account = response.parse()
            assert_matches_type(RequestTracker, cloud_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_health_check(self, client: VraIaas) -> None:
        cloud_account = client.iaas.api.cloud_accounts.health_check(
            id="id",
        )
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_health_check_with_all_params(self, client: VraIaas) -> None:
        cloud_account = client.iaas.api.cloud_accounts.health_check(
            id="id",
            api_version="apiVersion",
            periodic_health_check_id="periodicHealthCheckId",
        )
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_health_check(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts.with_raw_response.health_check(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_account = response.parse()
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_health_check(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts.with_streaming_response.health_check(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_account = response.parse()
            assert_matches_type(RequestTracker, cloud_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_health_check(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts.with_raw_response.health_check(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_private_image_enumeration(self, client: VraIaas) -> None:
        cloud_account = client.iaas.api.cloud_accounts.private_image_enumeration(
            id="id",
        )
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_private_image_enumeration_with_all_params(self, client: VraIaas) -> None:
        cloud_account = client.iaas.api.cloud_accounts.private_image_enumeration(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_private_image_enumeration(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts.with_raw_response.private_image_enumeration(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_account = response.parse()
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_private_image_enumeration(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts.with_streaming_response.private_image_enumeration(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_account = response.parse()
            assert_matches_type(RequestTracker, cloud_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_private_image_enumeration(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts.with_raw_response.private_image_enumeration(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_cloud_accounts(self, client: VraIaas) -> None:
        cloud_account = client.iaas.api.cloud_accounts.retrieve_cloud_accounts()
        assert_matches_type(CloudAccountRetrieveCloudAccountsResponse, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_cloud_accounts_with_all_params(self, client: VraIaas) -> None:
        cloud_account = client.iaas.api.cloud_accounts.retrieve_cloud_accounts(
            count=True,
            filter="$filter",
            select="$select",
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(CloudAccountRetrieveCloudAccountsResponse, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_cloud_accounts(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts.with_raw_response.retrieve_cloud_accounts()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_account = response.parse()
        assert_matches_type(CloudAccountRetrieveCloudAccountsResponse, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_cloud_accounts(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts.with_streaming_response.retrieve_cloud_accounts() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_account = response.parse()
            assert_matches_type(CloudAccountRetrieveCloudAccountsResponse, cloud_account, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCloudAccounts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        cloud_account = await async_client.iaas.api.cloud_accounts.retrieve(
            id="id",
        )
        assert_matches_type(CloudAccount, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_account = await async_client.iaas.api.cloud_accounts.retrieve(
            id="id",
            select="$select",
            api_version="apiVersion",
        )
        assert_matches_type(CloudAccount, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_account = await response.parse()
        assert_matches_type(CloudAccount, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_account = await response.parse()
            assert_matches_type(CloudAccount, cloud_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        cloud_account = await async_client.iaas.api.cloud_accounts.update(
            id="id",
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
        )
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_account = await async_client.iaas.api.cloud_accounts.update(
            id="id",
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
            associated_cloud_account_ids=["42f3e0d199d134755684cd935435a"],
            associated_mobility_cloud_account_ids={"42f3e0d199d134755684cd935435a": "BIDIRECTIONAL"},
            certificate_info={
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIDHjCCAoegAwIBAgIBATANBgkqhkiG9w0BAQsFADCBpjEUMBIGA1UEChMLVk13\nYXJlIEluYAAc1pw18GT3iAqQRPx0PrjzJhgjIJMla\n/1Kg4byY4FPSacNiRgY/FG2bPCqZk1yRfzmkFYCW/vU+Dg==\n-----END CERTIFICATE-----\n-"
            },
            create_default_zones=True,
            custom_properties={"sampleadapterProjectId": "projectId"},
            description="description",
            private_key="gfsScK345sGGaVdds222dasdfDDSSasdfdsa34fS",
            private_key_id="ACDC55DB4MFH6ADG75KK",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
        )
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts.with_raw_response.update(
            id="id",
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_account = await response.parse()
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts.with_streaming_response.update(
            id="id",
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_account = await response.parse()
            assert_matches_type(RequestTracker, cloud_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts.with_raw_response.update(
                id="",
                api_version="apiVersion",
                cloud_account_properties={
                    "supportPublicImages": "true",
                    "acceptSelfSignedCertificate": "true",
                },
                name="name",
                regions=[
                    {
                        "external_region_id": "eastasia",
                        "name": "East Asia",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        cloud_account = await async_client.iaas.api.cloud_accounts.delete(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_account = await async_client.iaas.api.cloud_accounts.delete(
            id="id",
            api_version="apiVersion",
            force_delete=True,
        )
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts.with_raw_response.delete(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_account = await response.parse()
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts.with_streaming_response.delete(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_account = await response.parse()
            assert_matches_type(RequestTracker, cloud_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts.with_raw_response.delete(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cloud_accounts(self, async_client: AsyncVraIaas) -> None:
        cloud_account = await async_client.iaas.api.cloud_accounts.cloud_accounts(
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            cloud_account_type="vsphere, aws, azure, nsxv, nsxt, vmc, avilb",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
        )
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cloud_accounts_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_account = await async_client.iaas.api.cloud_accounts.cloud_accounts(
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            cloud_account_type="vsphere, aws, azure, nsxv, nsxt, vmc, avilb",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
            validate_only="validateOnly",
            associated_cloud_account_ids=["42f3e0d199d134755684cd935435a"],
            associated_mobility_cloud_account_ids={"42f3e0d199d134755684cd935435a": "BIDIRECTIONAL"},
            certificate_info={
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIDHjCCAoegAwIBAgIBATANBgkqhkiG9w0BAQsFADCBpjEUMBIGA1UEChMLVk13\nYXJlIEluYAAc1pw18GT3iAqQRPx0PrjzJhgjIJMla\n/1Kg4byY4FPSacNiRgY/FG2bPCqZk1yRfzmkFYCW/vU+Dg==\n-----END CERTIFICATE-----\n-"
            },
            create_default_zones=True,
            custom_properties={"sampleadapterProjectId": "projectId"},
            description="description",
            private_key="gfsScK345sGGaVdds222dasdfDDSSasdfdsa34fS",
            private_key_id="ACDC55DB4MFH6ADG75KK",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
        )
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_cloud_accounts(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts.with_raw_response.cloud_accounts(
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            cloud_account_type="vsphere, aws, azure, nsxv, nsxt, vmc, avilb",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_account = await response.parse()
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_cloud_accounts(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts.with_streaming_response.cloud_accounts(
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            cloud_account_type="vsphere, aws, azure, nsxv, nsxt, vmc, avilb",
            name="name",
            regions=[
                {
                    "external_region_id": "eastasia",
                    "name": "East Asia",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_account = await response.parse()
            assert_matches_type(RequestTracker, cloud_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_health_check(self, async_client: AsyncVraIaas) -> None:
        cloud_account = await async_client.iaas.api.cloud_accounts.health_check(
            id="id",
        )
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_health_check_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_account = await async_client.iaas.api.cloud_accounts.health_check(
            id="id",
            api_version="apiVersion",
            periodic_health_check_id="periodicHealthCheckId",
        )
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_health_check(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts.with_raw_response.health_check(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_account = await response.parse()
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_health_check(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts.with_streaming_response.health_check(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_account = await response.parse()
            assert_matches_type(RequestTracker, cloud_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_health_check(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts.with_raw_response.health_check(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_private_image_enumeration(self, async_client: AsyncVraIaas) -> None:
        cloud_account = await async_client.iaas.api.cloud_accounts.private_image_enumeration(
            id="id",
        )
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_private_image_enumeration_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_account = await async_client.iaas.api.cloud_accounts.private_image_enumeration(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_private_image_enumeration(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts.with_raw_response.private_image_enumeration(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_account = await response.parse()
        assert_matches_type(RequestTracker, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_private_image_enumeration(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts.with_streaming_response.private_image_enumeration(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_account = await response.parse()
            assert_matches_type(RequestTracker, cloud_account, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_private_image_enumeration(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts.with_raw_response.private_image_enumeration(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_cloud_accounts(self, async_client: AsyncVraIaas) -> None:
        cloud_account = await async_client.iaas.api.cloud_accounts.retrieve_cloud_accounts()
        assert_matches_type(CloudAccountRetrieveCloudAccountsResponse, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_cloud_accounts_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_account = await async_client.iaas.api.cloud_accounts.retrieve_cloud_accounts(
            count=True,
            filter="$filter",
            select="$select",
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(CloudAccountRetrieveCloudAccountsResponse, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_cloud_accounts(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts.with_raw_response.retrieve_cloud_accounts()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_account = await response.parse()
        assert_matches_type(CloudAccountRetrieveCloudAccountsResponse, cloud_account, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_cloud_accounts(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts.with_streaming_response.retrieve_cloud_accounts() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_account = await response.parse()
            assert_matches_type(CloudAccountRetrieveCloudAccountsResponse, cloud_account, path=["response"])

        assert cast(Any, response.is_closed) is True
