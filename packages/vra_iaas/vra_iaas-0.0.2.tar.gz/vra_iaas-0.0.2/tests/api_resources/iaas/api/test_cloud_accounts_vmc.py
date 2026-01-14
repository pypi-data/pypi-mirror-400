# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    CloudAccountVmc,
    CloudAccountsVmcRetrieveCloudAccountsVmcResponse,
)
from vra_iaas.types.iaas.api.projects import RequestTracker

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCloudAccountsVmc:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        cloud_accounts_vmc = client.iaas.api.cloud_accounts_vmc.retrieve(
            id="id",
        )
        assert_matches_type(CloudAccountVmc, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_vmc = client.iaas.api.cloud_accounts_vmc.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(CloudAccountVmc, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_vmc.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_vmc = response.parse()
        assert_matches_type(CloudAccountVmc, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_vmc.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_vmc = response.parse()
            assert_matches_type(CloudAccountVmc, cloud_accounts_vmc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts_vmc.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        cloud_accounts_vmc = client.iaas.api.cloud_accounts_vmc.update(
            id="id",
            api_version="apiVersion",
            api_key="apiKey",
            dc_id="23959a1e-18bc-4f0c-ac49-b5aeb4b6eef4",
            host_name="vc1.vmware.com",
            name="name",
            nsx_host_name="nsxManager.sddc-52-12-8-145.vmwaretest.com",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "Datacenter:datacenter-3",
                    "name": "Datacenter:datacenter-3",
                }
            ],
            sddc_id="CMBU-PRD-NSXT-M8GA-090319",
            username="administrator@mycompany.com",
        )
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_vmc = client.iaas.api.cloud_accounts_vmc.update(
            id="id",
            api_version="apiVersion",
            api_key="apiKey",
            dc_id="23959a1e-18bc-4f0c-ac49-b5aeb4b6eef4",
            host_name="vc1.vmware.com",
            name="name",
            nsx_host_name="nsxManager.sddc-52-12-8-145.vmwaretest.com",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "Datacenter:datacenter-3",
                    "name": "Datacenter:datacenter-3",
                }
            ],
            sddc_id="CMBU-PRD-NSXT-M8GA-090319",
            username="administrator@mycompany.com",
            accept_self_signed_certificate=False,
            certificate_info={
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIDHjCCAoegAwIBAgIBATANBgkqhkiG9w0BAQsFADCBpjEUMBIGA1UEChMLVk13\nYXJlIEluYAAc1pw18GT3iAqQRPx0PrjzJhgjIJMla\n/1Kg4byY4FPSacNiRgY/FG2bPCqZk1yRfzmkFYCW/vU+Dg==\n-----END CERTIFICATE-----\n-"
            },
            create_default_zones=True,
            description="description",
            environment="aap",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
        )
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_vmc.with_raw_response.update(
            id="id",
            api_version="apiVersion",
            api_key="apiKey",
            dc_id="23959a1e-18bc-4f0c-ac49-b5aeb4b6eef4",
            host_name="vc1.vmware.com",
            name="name",
            nsx_host_name="nsxManager.sddc-52-12-8-145.vmwaretest.com",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "Datacenter:datacenter-3",
                    "name": "Datacenter:datacenter-3",
                }
            ],
            sddc_id="CMBU-PRD-NSXT-M8GA-090319",
            username="administrator@mycompany.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_vmc = response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_vmc.with_streaming_response.update(
            id="id",
            api_version="apiVersion",
            api_key="apiKey",
            dc_id="23959a1e-18bc-4f0c-ac49-b5aeb4b6eef4",
            host_name="vc1.vmware.com",
            name="name",
            nsx_host_name="nsxManager.sddc-52-12-8-145.vmwaretest.com",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "Datacenter:datacenter-3",
                    "name": "Datacenter:datacenter-3",
                }
            ],
            sddc_id="CMBU-PRD-NSXT-M8GA-090319",
            username="administrator@mycompany.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_vmc = response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts_vmc.with_raw_response.update(
                id="",
                api_version="apiVersion",
                api_key="apiKey",
                dc_id="23959a1e-18bc-4f0c-ac49-b5aeb4b6eef4",
                host_name="vc1.vmware.com",
                name="name",
                nsx_host_name="nsxManager.sddc-52-12-8-145.vmwaretest.com",
                password="cndhjslacd90ascdbasyoucbdh",
                regions=[
                    {
                        "external_region_id": "Datacenter:datacenter-3",
                        "name": "Datacenter:datacenter-3",
                    }
                ],
                sddc_id="CMBU-PRD-NSXT-M8GA-090319",
                username="administrator@mycompany.com",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        cloud_accounts_vmc = client.iaas.api.cloud_accounts_vmc.delete(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_vmc.with_raw_response.delete(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_vmc = response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_vmc.with_streaming_response.delete(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_vmc = response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts_vmc.with_raw_response.delete(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cloud_accounts_vmc(self, client: VraIaas) -> None:
        cloud_accounts_vmc = client.iaas.api.cloud_accounts_vmc.cloud_accounts_vmc(
            api_version="apiVersion",
            api_key="apiKey",
            dc_id="23959a1e-18bc-4f0c-ac49-b5aeb4b6eef4",
            host_name="vc1.vmware.com",
            name="name",
            nsx_host_name="nsxManager.sddc-52-12-8-145.vmwaretest.com",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "Datacenter:datacenter-3",
                    "name": "Datacenter:datacenter-3",
                }
            ],
            sddc_id="CMBU-PRD-NSXT-M8GA-090319",
            username="administrator@mycompany.com",
        )
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cloud_accounts_vmc_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_vmc = client.iaas.api.cloud_accounts_vmc.cloud_accounts_vmc(
            api_version="apiVersion",
            api_key="apiKey",
            dc_id="23959a1e-18bc-4f0c-ac49-b5aeb4b6eef4",
            host_name="vc1.vmware.com",
            name="name",
            nsx_host_name="nsxManager.sddc-52-12-8-145.vmwaretest.com",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "Datacenter:datacenter-3",
                    "name": "Datacenter:datacenter-3",
                }
            ],
            sddc_id="CMBU-PRD-NSXT-M8GA-090319",
            username="administrator@mycompany.com",
            validate_only="validateOnly",
            accept_self_signed_certificate=False,
            certificate_info={
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIDHjCCAoegAwIBAgIBATANBgkqhkiG9w0BAQsFADCBpjEUMBIGA1UEChMLVk13\nYXJlIEluYAAc1pw18GT3iAqQRPx0PrjzJhgjIJMla\n/1Kg4byY4FPSacNiRgY/FG2bPCqZk1yRfzmkFYCW/vU+Dg==\n-----END CERTIFICATE-----\n-"
            },
            create_default_zones=True,
            description="description",
            environment="aap",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
        )
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_cloud_accounts_vmc(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_vmc.with_raw_response.cloud_accounts_vmc(
            api_version="apiVersion",
            api_key="apiKey",
            dc_id="23959a1e-18bc-4f0c-ac49-b5aeb4b6eef4",
            host_name="vc1.vmware.com",
            name="name",
            nsx_host_name="nsxManager.sddc-52-12-8-145.vmwaretest.com",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "Datacenter:datacenter-3",
                    "name": "Datacenter:datacenter-3",
                }
            ],
            sddc_id="CMBU-PRD-NSXT-M8GA-090319",
            username="administrator@mycompany.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_vmc = response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_cloud_accounts_vmc(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_vmc.with_streaming_response.cloud_accounts_vmc(
            api_version="apiVersion",
            api_key="apiKey",
            dc_id="23959a1e-18bc-4f0c-ac49-b5aeb4b6eef4",
            host_name="vc1.vmware.com",
            name="name",
            nsx_host_name="nsxManager.sddc-52-12-8-145.vmwaretest.com",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "Datacenter:datacenter-3",
                    "name": "Datacenter:datacenter-3",
                }
            ],
            sddc_id="CMBU-PRD-NSXT-M8GA-090319",
            username="administrator@mycompany.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_vmc = response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_private_image_enumeration(self, client: VraIaas) -> None:
        cloud_accounts_vmc = client.iaas.api.cloud_accounts_vmc.private_image_enumeration(
            id="id",
        )
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_private_image_enumeration_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_vmc = client.iaas.api.cloud_accounts_vmc.private_image_enumeration(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_private_image_enumeration(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_vmc.with_raw_response.private_image_enumeration(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_vmc = response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_private_image_enumeration(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_vmc.with_streaming_response.private_image_enumeration(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_vmc = response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_private_image_enumeration(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts_vmc.with_raw_response.private_image_enumeration(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_region_enumeration(self, client: VraIaas) -> None:
        cloud_accounts_vmc = client.iaas.api.cloud_accounts_vmc.region_enumeration(
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_region_enumeration_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_vmc = client.iaas.api.cloud_accounts_vmc.region_enumeration(
            api_version="apiVersion",
            accept_self_signed_certificate=False,
            api_key="apiKey",
            certificate_info={
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIDHjCCAoegAwIBAgIBATANBgkqhkiG9w0BAQsFADCBpjEUMBIGA1UEChMLVk13\nYXJlIEluYAAc1pw18GT3iAqQRPx0PrjzJhgjIJMla\n/1Kg4byY4FPSacNiRgY/FG2bPCqZk1yRfzmkFYCW/vU+Dg==\n-----END CERTIFICATE-----\n-"
            },
            cloud_account_id="b8b7a918-342e-4a53-a3b0-b935da0fe601",
            csp_host_name="console-stg.cloud.vmware.com",
            dc_id="23959a1e-18bc-4f0c-ac49-b5aeb4b6eef4",
            environment="aap",
            host_name="vc1.vmware.com",
            nsx_host_name="nsxManager.sddc-52-12-8-145.vmwaretest.com",
            password="cndhjslacd90ascdbasyoucbdh",
            sddc_id="CMBU-PRD-NSXT-M8GA-090319",
            username="administrator@mycompany.com",
        )
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_region_enumeration(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_vmc.with_raw_response.region_enumeration(
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_vmc = response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_region_enumeration(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_vmc.with_streaming_response.region_enumeration(
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_vmc = response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_cloud_accounts_vmc(self, client: VraIaas) -> None:
        cloud_accounts_vmc = client.iaas.api.cloud_accounts_vmc.retrieve_cloud_accounts_vmc()
        assert_matches_type(CloudAccountsVmcRetrieveCloudAccountsVmcResponse, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_cloud_accounts_vmc_with_all_params(self, client: VraIaas) -> None:
        cloud_accounts_vmc = client.iaas.api.cloud_accounts_vmc.retrieve_cloud_accounts_vmc(
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(CloudAccountsVmcRetrieveCloudAccountsVmcResponse, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_cloud_accounts_vmc(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts_vmc.with_raw_response.retrieve_cloud_accounts_vmc()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_vmc = response.parse()
        assert_matches_type(CloudAccountsVmcRetrieveCloudAccountsVmcResponse, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_cloud_accounts_vmc(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts_vmc.with_streaming_response.retrieve_cloud_accounts_vmc() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_vmc = response.parse()
            assert_matches_type(CloudAccountsVmcRetrieveCloudAccountsVmcResponse, cloud_accounts_vmc, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCloudAccountsVmc:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_vmc = await async_client.iaas.api.cloud_accounts_vmc.retrieve(
            id="id",
        )
        assert_matches_type(CloudAccountVmc, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_vmc = await async_client.iaas.api.cloud_accounts_vmc.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(CloudAccountVmc, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_vmc.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_vmc = await response.parse()
        assert_matches_type(CloudAccountVmc, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_vmc.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_vmc = await response.parse()
            assert_matches_type(CloudAccountVmc, cloud_accounts_vmc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts_vmc.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_vmc = await async_client.iaas.api.cloud_accounts_vmc.update(
            id="id",
            api_version="apiVersion",
            api_key="apiKey",
            dc_id="23959a1e-18bc-4f0c-ac49-b5aeb4b6eef4",
            host_name="vc1.vmware.com",
            name="name",
            nsx_host_name="nsxManager.sddc-52-12-8-145.vmwaretest.com",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "Datacenter:datacenter-3",
                    "name": "Datacenter:datacenter-3",
                }
            ],
            sddc_id="CMBU-PRD-NSXT-M8GA-090319",
            username="administrator@mycompany.com",
        )
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_vmc = await async_client.iaas.api.cloud_accounts_vmc.update(
            id="id",
            api_version="apiVersion",
            api_key="apiKey",
            dc_id="23959a1e-18bc-4f0c-ac49-b5aeb4b6eef4",
            host_name="vc1.vmware.com",
            name="name",
            nsx_host_name="nsxManager.sddc-52-12-8-145.vmwaretest.com",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "Datacenter:datacenter-3",
                    "name": "Datacenter:datacenter-3",
                }
            ],
            sddc_id="CMBU-PRD-NSXT-M8GA-090319",
            username="administrator@mycompany.com",
            accept_self_signed_certificate=False,
            certificate_info={
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIDHjCCAoegAwIBAgIBATANBgkqhkiG9w0BAQsFADCBpjEUMBIGA1UEChMLVk13\nYXJlIEluYAAc1pw18GT3iAqQRPx0PrjzJhgjIJMla\n/1Kg4byY4FPSacNiRgY/FG2bPCqZk1yRfzmkFYCW/vU+Dg==\n-----END CERTIFICATE-----\n-"
            },
            create_default_zones=True,
            description="description",
            environment="aap",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
        )
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_vmc.with_raw_response.update(
            id="id",
            api_version="apiVersion",
            api_key="apiKey",
            dc_id="23959a1e-18bc-4f0c-ac49-b5aeb4b6eef4",
            host_name="vc1.vmware.com",
            name="name",
            nsx_host_name="nsxManager.sddc-52-12-8-145.vmwaretest.com",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "Datacenter:datacenter-3",
                    "name": "Datacenter:datacenter-3",
                }
            ],
            sddc_id="CMBU-PRD-NSXT-M8GA-090319",
            username="administrator@mycompany.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_vmc = await response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_vmc.with_streaming_response.update(
            id="id",
            api_version="apiVersion",
            api_key="apiKey",
            dc_id="23959a1e-18bc-4f0c-ac49-b5aeb4b6eef4",
            host_name="vc1.vmware.com",
            name="name",
            nsx_host_name="nsxManager.sddc-52-12-8-145.vmwaretest.com",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "Datacenter:datacenter-3",
                    "name": "Datacenter:datacenter-3",
                }
            ],
            sddc_id="CMBU-PRD-NSXT-M8GA-090319",
            username="administrator@mycompany.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_vmc = await response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts_vmc.with_raw_response.update(
                id="",
                api_version="apiVersion",
                api_key="apiKey",
                dc_id="23959a1e-18bc-4f0c-ac49-b5aeb4b6eef4",
                host_name="vc1.vmware.com",
                name="name",
                nsx_host_name="nsxManager.sddc-52-12-8-145.vmwaretest.com",
                password="cndhjslacd90ascdbasyoucbdh",
                regions=[
                    {
                        "external_region_id": "Datacenter:datacenter-3",
                        "name": "Datacenter:datacenter-3",
                    }
                ],
                sddc_id="CMBU-PRD-NSXT-M8GA-090319",
                username="administrator@mycompany.com",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_vmc = await async_client.iaas.api.cloud_accounts_vmc.delete(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_vmc.with_raw_response.delete(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_vmc = await response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_vmc.with_streaming_response.delete(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_vmc = await response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts_vmc.with_raw_response.delete(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cloud_accounts_vmc(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_vmc = await async_client.iaas.api.cloud_accounts_vmc.cloud_accounts_vmc(
            api_version="apiVersion",
            api_key="apiKey",
            dc_id="23959a1e-18bc-4f0c-ac49-b5aeb4b6eef4",
            host_name="vc1.vmware.com",
            name="name",
            nsx_host_name="nsxManager.sddc-52-12-8-145.vmwaretest.com",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "Datacenter:datacenter-3",
                    "name": "Datacenter:datacenter-3",
                }
            ],
            sddc_id="CMBU-PRD-NSXT-M8GA-090319",
            username="administrator@mycompany.com",
        )
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cloud_accounts_vmc_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_vmc = await async_client.iaas.api.cloud_accounts_vmc.cloud_accounts_vmc(
            api_version="apiVersion",
            api_key="apiKey",
            dc_id="23959a1e-18bc-4f0c-ac49-b5aeb4b6eef4",
            host_name="vc1.vmware.com",
            name="name",
            nsx_host_name="nsxManager.sddc-52-12-8-145.vmwaretest.com",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "Datacenter:datacenter-3",
                    "name": "Datacenter:datacenter-3",
                }
            ],
            sddc_id="CMBU-PRD-NSXT-M8GA-090319",
            username="administrator@mycompany.com",
            validate_only="validateOnly",
            accept_self_signed_certificate=False,
            certificate_info={
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIDHjCCAoegAwIBAgIBATANBgkqhkiG9w0BAQsFADCBpjEUMBIGA1UEChMLVk13\nYXJlIEluYAAc1pw18GT3iAqQRPx0PrjzJhgjIJMla\n/1Kg4byY4FPSacNiRgY/FG2bPCqZk1yRfzmkFYCW/vU+Dg==\n-----END CERTIFICATE-----\n-"
            },
            create_default_zones=True,
            description="description",
            environment="aap",
            tags=[
                {
                    "key": "env",
                    "value": "dev",
                }
            ],
        )
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_cloud_accounts_vmc(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_vmc.with_raw_response.cloud_accounts_vmc(
            api_version="apiVersion",
            api_key="apiKey",
            dc_id="23959a1e-18bc-4f0c-ac49-b5aeb4b6eef4",
            host_name="vc1.vmware.com",
            name="name",
            nsx_host_name="nsxManager.sddc-52-12-8-145.vmwaretest.com",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "Datacenter:datacenter-3",
                    "name": "Datacenter:datacenter-3",
                }
            ],
            sddc_id="CMBU-PRD-NSXT-M8GA-090319",
            username="administrator@mycompany.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_vmc = await response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_cloud_accounts_vmc(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_vmc.with_streaming_response.cloud_accounts_vmc(
            api_version="apiVersion",
            api_key="apiKey",
            dc_id="23959a1e-18bc-4f0c-ac49-b5aeb4b6eef4",
            host_name="vc1.vmware.com",
            name="name",
            nsx_host_name="nsxManager.sddc-52-12-8-145.vmwaretest.com",
            password="cndhjslacd90ascdbasyoucbdh",
            regions=[
                {
                    "external_region_id": "Datacenter:datacenter-3",
                    "name": "Datacenter:datacenter-3",
                }
            ],
            sddc_id="CMBU-PRD-NSXT-M8GA-090319",
            username="administrator@mycompany.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_vmc = await response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_private_image_enumeration(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_vmc = await async_client.iaas.api.cloud_accounts_vmc.private_image_enumeration(
            id="id",
        )
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_private_image_enumeration_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_vmc = await async_client.iaas.api.cloud_accounts_vmc.private_image_enumeration(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_private_image_enumeration(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_vmc.with_raw_response.private_image_enumeration(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_vmc = await response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_private_image_enumeration(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_vmc.with_streaming_response.private_image_enumeration(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_vmc = await response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_private_image_enumeration(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts_vmc.with_raw_response.private_image_enumeration(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_region_enumeration(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_vmc = await async_client.iaas.api.cloud_accounts_vmc.region_enumeration(
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_region_enumeration_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_vmc = await async_client.iaas.api.cloud_accounts_vmc.region_enumeration(
            api_version="apiVersion",
            accept_self_signed_certificate=False,
            api_key="apiKey",
            certificate_info={
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIDHjCCAoegAwIBAgIBATANBgkqhkiG9w0BAQsFADCBpjEUMBIGA1UEChMLVk13\nYXJlIEluYAAc1pw18GT3iAqQRPx0PrjzJhgjIJMla\n/1Kg4byY4FPSacNiRgY/FG2bPCqZk1yRfzmkFYCW/vU+Dg==\n-----END CERTIFICATE-----\n-"
            },
            cloud_account_id="b8b7a918-342e-4a53-a3b0-b935da0fe601",
            csp_host_name="console-stg.cloud.vmware.com",
            dc_id="23959a1e-18bc-4f0c-ac49-b5aeb4b6eef4",
            environment="aap",
            host_name="vc1.vmware.com",
            nsx_host_name="nsxManager.sddc-52-12-8-145.vmwaretest.com",
            password="cndhjslacd90ascdbasyoucbdh",
            sddc_id="CMBU-PRD-NSXT-M8GA-090319",
            username="administrator@mycompany.com",
        )
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_region_enumeration(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_vmc.with_raw_response.region_enumeration(
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_vmc = await response.parse()
        assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_region_enumeration(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts_vmc.with_streaming_response.region_enumeration(
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_vmc = await response.parse()
            assert_matches_type(RequestTracker, cloud_accounts_vmc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_cloud_accounts_vmc(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_vmc = await async_client.iaas.api.cloud_accounts_vmc.retrieve_cloud_accounts_vmc()
        assert_matches_type(CloudAccountsVmcRetrieveCloudAccountsVmcResponse, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_cloud_accounts_vmc_with_all_params(self, async_client: AsyncVraIaas) -> None:
        cloud_accounts_vmc = await async_client.iaas.api.cloud_accounts_vmc.retrieve_cloud_accounts_vmc(
            skip=0,
            top=0,
            api_version="apiVersion",
        )
        assert_matches_type(CloudAccountsVmcRetrieveCloudAccountsVmcResponse, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_cloud_accounts_vmc(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts_vmc.with_raw_response.retrieve_cloud_accounts_vmc()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cloud_accounts_vmc = await response.parse()
        assert_matches_type(CloudAccountsVmcRetrieveCloudAccountsVmcResponse, cloud_accounts_vmc, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_cloud_accounts_vmc(self, async_client: AsyncVraIaas) -> None:
        async with (
            async_client.iaas.api.cloud_accounts_vmc.with_streaming_response.retrieve_cloud_accounts_vmc()
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cloud_accounts_vmc = await response.parse()
            assert_matches_type(CloudAccountsVmcRetrieveCloudAccountsVmcResponse, cloud_accounts_vmc, path=["response"])

        assert cast(Any, response.is_closed) is True
