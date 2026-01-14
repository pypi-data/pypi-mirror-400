# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    CloudAccountAviLb,
    CloudAccountsAvilbRetrieveCloudAccountsAvilbResponse,
)
from vra_iaas.types.iaas.api.projects import RequestTracker

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCloudAccountsAvilb:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        cloud_accounts_avilb = client.iaas.api.cloud_accounts_avilb.retrieve(
            id="id",
        )
        assert_matches_type(CloudAccountAviLb, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_avilb = client.iaas.api.cloud_accounts_avilb.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(CloudAccountAviLb, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_avilb.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_avilb = response.parse()
        assert_matches_type(CloudAccountAviLb, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_avilb.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_avilb = response.parse()
            assert_matches_type(CloudAccountAviLb, cloud_accounts_avilb, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts_avilb.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        cloud_accounts_avilb = client.iaas.api.cloud_accounts_avilb.update(
            id="id",
            api_version="apiVersion",
            host_name="avilb.mycompany.com",
            name="name",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "europe-west2",
                    "name": "europe-west2",
                }
            ],
            username="administrator@mycompany.com",
        )
        assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_avilb = client.iaas.api.cloud_accounts_avilb.update(
            id="id",
            api_version="apiVersion",
            host_name="avilb.mycompany.com",
            name="name",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "europe-west2",
                    "name": "europe-west2",
                }
            ],
            username="administrator@mycompany.com",
            accept_self_signed_certificate=False,
            certificate_info={
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIDHjCCAoegAwIBAgIBATANBgkqhkiG9w0BAQsFADCBpjEUMBIGA1UEChMLVk13\nYXJlIEluYAAc1pw18GT3iAqQRPx0PrjzJhgjIJMla\n/1Kg4byY4FPSacNiRgY/FG2bPCqZk1yRfzmkFYCW/vU+Dg==\n-----END CERTIFICATE-----\n-"
            },
            cloud_account_properties={
                "cloud": "cloud-vsphere-connector",
                "tenant": "mytenant",
                "apiVersion": "22.0.1",
            },
            create_default_zones=False,
            description="description",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
        )
        assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_avilb.with_raw_response.update(
            id="id",
            api_version="apiVersion",
            host_name="avilb.mycompany.com",
            name="name",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "europe-west2",
                    "name": "europe-west2",
                }
            ],
            username="administrator@mycompany.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_avilb = response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_avilb.with_streaming_response.update(
            id="id",
            api_version="apiVersion",
            host_name="avilb.mycompany.com",
            name="name",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "europe-west2",
                    "name": "europe-west2",
                }
            ],
            username="administrator@mycompany.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_avilb = response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts_avilb.with_raw_response.update(
                id="",
                api_version="apiVersion",
                host_name="avilb.mycompany.com",
                name="name",
                password="cndhjslacd90ascdbasyoucbdh",
                regions=[
                    {
                        "external_region_id": "europe-west2",
                        "name": "europe-west2",
                    }
                ],
                username="administrator@mycompany.com",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        cloud_accounts_avilb = client.iaas.api.cloud_accounts_avilb.delete(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_avilb.with_raw_response.delete(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_avilb = response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_avilb.with_streaming_response.delete(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_avilb = response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts_avilb.with_raw_response.delete(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cloud_accounts_avilb(self, client: VraIaas) -> None:
        cloud_accounts_avilb = client.iaas.api.cloud_accounts_avilb.cloud_accounts_avilb(
            api_version="apiVersion",
            host_name="avilb.mycompany.com",
            name="name",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "europe-west2",
                    "name": "europe-west2",
                }
            ],
            username="administrator@mycompany.com",
        )
        assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cloud_accounts_avilb_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_avilb = client.iaas.api.cloud_accounts_avilb.cloud_accounts_avilb(
            api_version="apiVersion",
            host_name="avilb.mycompany.com",
            name="name",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "europe-west2",
                    "name": "europe-west2",
                }
            ],
            username="administrator@mycompany.com",
            accept_self_signed_certificate=False,
            certificate_info={
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIDHjCCAoegAwIBAgIBATANBgkqhkiG9w0BAQsFADCBpjEUMBIGA1UEChMLVk13\nYXJlIEluYAAc1pw18GT3iAqQRPx0PrjzJhgjIJMla\n/1Kg4byY4FPSacNiRgY/FG2bPCqZk1yRfzmkFYCW/vU+Dg==\n-----END CERTIFICATE-----\n-"
            },
            cloud_account_properties={
                "cloud": "cloud-vsphere-connector",
                "tenant": "mytenant",
                "apiVersion": "22.0.1",
            },
            create_default_zones=False,
            description="description",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
        )
        assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_cloud_accounts_avilb(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_avilb.with_raw_response.cloud_accounts_avilb(
            api_version="apiVersion",
            host_name="avilb.mycompany.com",
            name="name",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "europe-west2",
                    "name": "europe-west2",
                }
            ],
            username="administrator@mycompany.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_avilb = response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_cloud_accounts_avilb(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_avilb.with_streaming_response.cloud_accounts_avilb(
            api_version="apiVersion",
            host_name="avilb.mycompany.com",
            name="name",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "europe-west2",
                    "name": "europe-west2",
                }
            ],
            username="administrator@mycompany.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_avilb = response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_cloud_accounts_avilb(self, client: VraIaas) -> None:
        cloud_accounts_avilb = client.iaas.api.cloud_accounts_avilb.retrieve_cloud_accounts_avilb()
        assert_matches_type(
            CloudAccountsAvilbRetrieveCloudAccountsAvilbResponse, cloud_accounts_avilb, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_cloud_accounts_avilb_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_avilb = client.iaas.api.cloud_accounts_avilb.retrieve_cloud_accounts_avilb(
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(
            CloudAccountsAvilbRetrieveCloudAccountsAvilbResponse, cloud_accounts_avilb, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_cloud_accounts_avilb(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_avilb.with_raw_response.retrieve_cloud_accounts_avilb()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_avilb = response.parse()
        assert_matches_type(
            CloudAccountsAvilbRetrieveCloudAccountsAvilbResponse, cloud_accounts_avilb, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_cloud_accounts_avilb(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_avilb.with_streaming_response.retrieve_cloud_accounts_avilb() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_avilb = response.parse()
            assert_matches_type(
                CloudAccountsAvilbRetrieveCloudAccountsAvilbResponse, cloud_accounts_avilb, path=["response"]
            )

        assert cast(Any, response.is_closed) is True


class TestAsyncCloudAccountsAvilb:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_avilb = await async_client.iaas.api.cloud_accounts_avilb.retrieve(
            id="id",
        )
        assert_matches_type(CloudAccountAviLb, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_avilb = await async_client.iaas.api.cloud_accounts_avilb.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(CloudAccountAviLb, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_avilb.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_avilb = await response.parse()
        assert_matches_type(CloudAccountAviLb, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_avilb.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_avilb = await response.parse()
            assert_matches_type(CloudAccountAviLb, cloud_accounts_avilb, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts_avilb.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_avilb = await async_client.iaas.api.cloud_accounts_avilb.update(
            id="id",
            api_version="apiVersion",
            host_name="avilb.mycompany.com",
            name="name",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "europe-west2",
                    "name": "europe-west2",
                }
            ],
            username="administrator@mycompany.com",
        )
        assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_avilb = await async_client.iaas.api.cloud_accounts_avilb.update(
            id="id",
            api_version="apiVersion",
            host_name="avilb.mycompany.com",
            name="name",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "europe-west2",
                    "name": "europe-west2",
                }
            ],
            username="administrator@mycompany.com",
            accept_self_signed_certificate=False,
            certificate_info={
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIDHjCCAoegAwIBAgIBATANBgkqhkiG9w0BAQsFADCBpjEUMBIGA1UEChMLVk13\nYXJlIEluYAAc1pw18GT3iAqQRPx0PrjzJhgjIJMla\n/1Kg4byY4FPSacNiRgY/FG2bPCqZk1yRfzmkFYCW/vU+Dg==\n-----END CERTIFICATE-----\n-"
            },
            cloud_account_properties={
                "cloud": "cloud-vsphere-connector",
                "tenant": "mytenant",
                "apiVersion": "22.0.1",
            },
            create_default_zones=False,
            description="description",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
        )
        assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_avilb.with_raw_response.update(
            id="id",
            api_version="apiVersion",
            host_name="avilb.mycompany.com",
            name="name",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "europe-west2",
                    "name": "europe-west2",
                }
            ],
            username="administrator@mycompany.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_avilb = await response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_avilb.with_streaming_response.update(
            id="id",
            api_version="apiVersion",
            host_name="avilb.mycompany.com",
            name="name",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "europe-west2",
                    "name": "europe-west2",
                }
            ],
            username="administrator@mycompany.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_avilb = await response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts_avilb.with_raw_response.update(
                id="",
                api_version="apiVersion",
                host_name="avilb.mycompany.com",
                name="name",
                password="cndhjslacd90ascdbasyoucbdh",
                regions=[
                    {
                        "external_region_id": "europe-west2",
                        "name": "europe-west2",
                    }
                ],
                username="administrator@mycompany.com",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_avilb = await async_client.iaas.api.cloud_accounts_avilb.delete(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_avilb.with_raw_response.delete(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_avilb = await response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_avilb.with_streaming_response.delete(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_avilb = await response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts_avilb.with_raw_response.delete(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cloud_accounts_avilb(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_avilb = await async_client.iaas.api.cloud_accounts_avilb.cloud_accounts_avilb(
            api_version="apiVersion",
            host_name="avilb.mycompany.com",
            name="name",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "europe-west2",
                    "name": "europe-west2",
                }
            ],
            username="administrator@mycompany.com",
        )
        assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cloud_accounts_avilb_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_avilb = await async_client.iaas.api.cloud_accounts_avilb.cloud_accounts_avilb(
            api_version="apiVersion",
            host_name="avilb.mycompany.com",
            name="name",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "europe-west2",
                    "name": "europe-west2",
                }
            ],
            username="administrator@mycompany.com",
            accept_self_signed_certificate=False,
            certificate_info={
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIDHjCCAoegAwIBAgIBATANBgkqhkiG9w0BAQsFADCBpjEUMBIGA1UEChMLVk13\nYXJlIEluYAAc1pw18GT3iAqQRPx0PrjzJhgjIJMla\n/1Kg4byY4FPSacNiRgY/FG2bPCqZk1yRfzmkFYCW/vU+Dg==\n-----END CERTIFICATE-----\n-"
            },
            cloud_account_properties={
                "cloud": "cloud-vsphere-connector",
                "tenant": "mytenant",
                "apiVersion": "22.0.1",
            },
            create_default_zones=False,
            description="description",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
        )
        assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_cloud_accounts_avilb(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_avilb.with_raw_response.cloud_accounts_avilb(
            api_version="apiVersion",
            host_name="avilb.mycompany.com",
            name="name",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "europe-west2",
                    "name": "europe-west2",
                }
            ],
            username="administrator@mycompany.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_avilb = await response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_cloud_accounts_avilb(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_avilb.with_streaming_response.cloud_accounts_avilb(
            api_version="apiVersion",
            host_name="avilb.mycompany.com",
            name="name",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "europe-west2",
                    "name": "europe-west2",
                }
            ],
            username="administrator@mycompany.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_avilb = await response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_avilb, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_cloud_accounts_avilb(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_avilb = await async_client.iaas.api.cloud_accounts_avilb.retrieve_cloud_accounts_avilb()
        assert_matches_type(
            CloudAccountsAvilbRetrieveCloudAccountsAvilbResponse, cloud_accounts_avilb, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_cloud_accounts_avilb_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_avilb = await async_client.iaas.api.cloud_accounts_avilb.retrieve_cloud_accounts_avilb(
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(
            CloudAccountsAvilbRetrieveCloudAccountsAvilbResponse, cloud_accounts_avilb, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_cloud_accounts_avilb(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_avilb.with_raw_response.retrieve_cloud_accounts_avilb()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_avilb = await response.parse()
        assert_matches_type(
            CloudAccountsAvilbRetrieveCloudAccountsAvilbResponse, cloud_accounts_avilb, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_cloud_accounts_avilb(self, async_client: AsyncVraIaas) -> None:
        async with (
            async_client.iaas.api.cloud_accounts_avilb.with_streaming_response.retrieve_cloud_accounts_avilb()
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_avilb = await response.parse()
            assert_matches_type(
                CloudAccountsAvilbRetrieveCloudAccountsAvilbResponse, cloud_accounts_avilb, path=["response"]
            )

        assert cast(Any, response.is_closed) is True
