# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    Integration,
    IntegrationListResponse,
)
from vra_iaas.types.iaas.api.projects import RequestTracker

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestIntegrations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: VraIaas) -> None:
        integration = client.iaas.api.integrations.create(
            api_version="apiVersion",
            integration_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            integration_type="Active directory, Ansible, IPAM, vRO, GitHub",
            name="name",
        )
        assert_matches_type(RequestTracker, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: VraIaas) -> None:
        integration = client.iaas.api.integrations.create(
            api_version="apiVersion",
            integration_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            integration_type="Active directory, Ansible, IPAM, vRO, GitHub",
            name="name",
            validate_only="validateOnly",
            associated_cloud_account_ids=["42f3e0d199d134755684cd935435a"],
            certificate_info={
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIDHjCCAoegAwIBAgIBATANBgkqhkiG9w0BAQsFADCBpjEUMBIGA1UEChMLVk13\nYXJlIEluYAAc1pw18GT3iAqQRPx0PrjzJhgjIJMla\n/1Kg4byY4FPSacNiRgY/FG2bPCqZk1yRfzmkFYCW/vU+Dg==\n-----END CERTIFICATE-----\n-"
            },
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
        assert_matches_type(RequestTracker, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: VraIaas) -> None:
        response = client.iaas.api.integrations.with_raw_response.create(
            api_version="apiVersion",
            integration_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            integration_type="Active directory, Ansible, IPAM, vRO, GitHub",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        integration = response.parse()
        assert_matches_type(RequestTracker, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: VraIaas) -> None:
        with client.iaas.api.integrations.with_streaming_response.create(
            api_version="apiVersion",
            integration_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            integration_type="Active directory, Ansible, IPAM, vRO, GitHub",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            integration = response.parse()
            assert_matches_type(RequestTracker, integration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        integration = client.iaas.api.integrations.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(Integration, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        integration = client.iaas.api.integrations.retrieve(
            id="id",
            api_version="apiVersion",
            select="$select",
        )
        assert_matches_type(Integration, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.integrations.with_raw_response.retrieve(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        integration = response.parse()
        assert_matches_type(Integration, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.integrations.with_streaming_response.retrieve(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            integration = response.parse()
            assert_matches_type(Integration, integration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.integrations.with_raw_response.retrieve(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        integration = client.iaas.api.integrations.update(
            id="id",
            api_version="apiVersion",
            integration_properties={"providerId": "providerID"},
            name="name",
        )
        assert_matches_type(RequestTracker, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        integration = client.iaas.api.integrations.update(
            id="id",
            api_version="apiVersion",
            integration_properties={"providerId": "providerID"},
            name="name",
            associated_cloud_account_ids=["42f3e0d199d134755684cd935435a"],
            certificate_info={
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIDHjCCAoegAwIBAgIBATANBgkqhkiG9w0BAQsFADCBpjEUMBIGA1UEChMLVk13\nYXJlIEluYAAc1pw18GT3iAqQRPx0PrjzJhgjIJMla\n/1Kg4byY4FPSacNiRgY/FG2bPCqZk1yRfzmkFYCW/vU+Dg==\n-----END CERTIFICATE-----\n-"
            },
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
        assert_matches_type(RequestTracker, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.integrations.with_raw_response.update(
            id="id",
            api_version="apiVersion",
            integration_properties={"providerId": "providerID"},
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        integration = response.parse()
        assert_matches_type(RequestTracker, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.integrations.with_streaming_response.update(
            id="id",
            api_version="apiVersion",
            integration_properties={"providerId": "providerID"},
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            integration = response.parse()
            assert_matches_type(RequestTracker, integration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.integrations.with_raw_response.update(
                id="",
                api_version="apiVersion",
                integration_properties={"providerId": "providerID"},
                name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: VraIaas) -> None:
        integration = client.iaas.api.integrations.list(
            api_version="apiVersion",
        )
        assert_matches_type(IntegrationListResponse, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: VraIaas) -> None:
        integration = client.iaas.api.integrations.list(
            api_version="apiVersion",
            count=True,
            filter="$filter",
            select="$select",
            skip=0,
            top=0,
        )
        assert_matches_type(IntegrationListResponse, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: VraIaas) -> None:
        response = client.iaas.api.integrations.with_raw_response.list(
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        integration = response.parse()
        assert_matches_type(IntegrationListResponse, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: VraIaas) -> None:
        with client.iaas.api.integrations.with_streaming_response.list(
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            integration = response.parse()
            assert_matches_type(IntegrationListResponse, integration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        integration = client.iaas.api.integrations.delete(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.integrations.with_raw_response.delete(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        integration = response.parse()
        assert_matches_type(RequestTracker, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.integrations.with_streaming_response.delete(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            integration = response.parse()
            assert_matches_type(RequestTracker, integration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.integrations.with_raw_response.delete(
                id="",
                api_version="apiVersion",
            )


class TestAsyncIntegrations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncVraIaas) -> None:
        integration = await async_client.iaas.api.integrations.create(
            api_version="apiVersion",
            integration_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            integration_type="Active directory, Ansible, IPAM, vRO, GitHub",
            name="name",
        )
        assert_matches_type(RequestTracker, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncVraIaas) -> None:
        integration = await async_client.iaas.api.integrations.create(
            api_version="apiVersion",
            integration_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            integration_type="Active directory, Ansible, IPAM, vRO, GitHub",
            name="name",
            validate_only="validateOnly",
            associated_cloud_account_ids=["42f3e0d199d134755684cd935435a"],
            certificate_info={
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIDHjCCAoegAwIBAgIBATANBgkqhkiG9w0BAQsFADCBpjEUMBIGA1UEChMLVk13\nYXJlIEluYAAc1pw18GT3iAqQRPx0PrjzJhgjIJMla\n/1Kg4byY4FPSacNiRgY/FG2bPCqZk1yRfzmkFYCW/vU+Dg==\n-----END CERTIFICATE-----\n-"
            },
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
        assert_matches_type(RequestTracker, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.integrations.with_raw_response.create(
            api_version="apiVersion",
            integration_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            integration_type="Active directory, Ansible, IPAM, vRO, GitHub",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        integration = await response.parse()
        assert_matches_type(RequestTracker, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.integrations.with_streaming_response.create(
            api_version="apiVersion",
            integration_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            integration_type="Active directory, Ansible, IPAM, vRO, GitHub",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            integration = await response.parse()
            assert_matches_type(RequestTracker, integration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        integration = await async_client.iaas.api.integrations.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(Integration, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        integration = await async_client.iaas.api.integrations.retrieve(
            id="id",
            api_version="apiVersion",
            select="$select",
        )
        assert_matches_type(Integration, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.integrations.with_raw_response.retrieve(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        integration = await response.parse()
        assert_matches_type(Integration, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.integrations.with_streaming_response.retrieve(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            integration = await response.parse()
            assert_matches_type(Integration, integration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.integrations.with_raw_response.retrieve(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        integration = await async_client.iaas.api.integrations.update(
            id="id",
            api_version="apiVersion",
            integration_properties={"providerId": "providerID"},
            name="name",
        )
        assert_matches_type(RequestTracker, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        integration = await async_client.iaas.api.integrations.update(
            id="id",
            api_version="apiVersion",
            integration_properties={"providerId": "providerID"},
            name="name",
            associated_cloud_account_ids=["42f3e0d199d134755684cd935435a"],
            certificate_info={
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIDHjCCAoegAwIBAgIBATANBgkqhkiG9w0BAQsFADCBpjEUMBIGA1UEChMLVk13\nYXJlIEluYAAc1pw18GT3iAqQRPx0PrjzJhgjIJMla\n/1Kg4byY4FPSacNiRgY/FG2bPCqZk1yRfzmkFYCW/vU+Dg==\n-----END CERTIFICATE-----\n-"
            },
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
        assert_matches_type(RequestTracker, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.integrations.with_raw_response.update(
            id="id",
            api_version="apiVersion",
            integration_properties={"providerId": "providerID"},
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        integration = await response.parse()
        assert_matches_type(RequestTracker, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.integrations.with_streaming_response.update(
            id="id",
            api_version="apiVersion",
            integration_properties={"providerId": "providerID"},
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            integration = await response.parse()
            assert_matches_type(RequestTracker, integration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.integrations.with_raw_response.update(
                id="",
                api_version="apiVersion",
                integration_properties={"providerId": "providerID"},
                name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncVraIaas) -> None:
        integration = await async_client.iaas.api.integrations.list(
            api_version="apiVersion",
        )
        assert_matches_type(IntegrationListResponse, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncVraIaas) -> None:
        integration = await async_client.iaas.api.integrations.list(
            api_version="apiVersion",
            count=True,
            filter="$filter",
            select="$select",
            skip=0,
            top=0,
        )
        assert_matches_type(IntegrationListResponse, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.integrations.with_raw_response.list(
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        integration = await response.parse()
        assert_matches_type(IntegrationListResponse, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.integrations.with_streaming_response.list(
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            integration = await response.parse()
            assert_matches_type(IntegrationListResponse, integration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        integration = await async_client.iaas.api.integrations.delete(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.integrations.with_raw_response.delete(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        integration = await response.parse()
        assert_matches_type(RequestTracker, integration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.integrations.with_streaming_response.delete(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            integration = await response.parse()
            assert_matches_type(RequestTracker, integration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.integrations.with_raw_response.delete(
                id="",
                api_version="apiVersion",
            )
