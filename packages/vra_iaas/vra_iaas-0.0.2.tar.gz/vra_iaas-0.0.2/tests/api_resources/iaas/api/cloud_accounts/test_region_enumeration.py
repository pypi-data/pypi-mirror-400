# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api.projects import RequestTracker
from vra_iaas.types.iaas.api.cloud_accounts import (
    RegionEnumerationRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRegionEnumeration:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        region_enumeration = client.iaas.api.cloud_accounts.region_enumeration.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RegionEnumerationRetrieveResponse, region_enumeration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts.region_enumeration.with_raw_response.retrieve(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        region_enumeration = response.parse()
        assert_matches_type(RegionEnumerationRetrieveResponse, region_enumeration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts.region_enumeration.with_streaming_response.retrieve(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            region_enumeration = response.parse()
            assert_matches_type(RegionEnumerationRetrieveResponse, region_enumeration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.cloud_accounts.region_enumeration.with_raw_response.retrieve(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_region_enumeration(self, client: VraIaas) -> None:
        region_enumeration = client.iaas.api.cloud_accounts.region_enumeration.region_enumeration(
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
        )
        assert_matches_type(RequestTracker, region_enumeration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_region_enumeration_with_all_params(self, client: VraIaas) -> None:
        region_enumeration = client.iaas.api.cloud_accounts.region_enumeration.region_enumeration(
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            certificate_info={
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIDHjCCAoegAwIBAgIBATANBgkqhkiG9w0BAQsFADCBpjEUMBIGA1UEChMLVk13\nYXJlIEluYAAc1pw18GT3iAqQRPx0PrjzJhgjIJMla\n/1Kg4byY4FPSacNiRgY/FG2bPCqZk1yRfzmkFYCW/vU+Dg==\n-----END CERTIFICATE-----\n-"
            },
            cloud_account_id="b8b7a918-342e-4a53-a3b0-b935da0fe601",
            cloud_account_type="vsphere, aws, azure, nsxv, nsxt",
            private_key="gfsScK345sGGaVdds222dasdfDDSSasdfdsa34fS",
            private_key_id="ACDC55DB4MFH6ADG75KK",
        )
        assert_matches_type(RequestTracker, region_enumeration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_region_enumeration(self, client: VraIaas) -> None:
        response = client.iaas.api.cloud_accounts.region_enumeration.with_raw_response.region_enumeration(
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        region_enumeration = response.parse()
        assert_matches_type(RequestTracker, region_enumeration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_region_enumeration(self, client: VraIaas) -> None:
        with client.iaas.api.cloud_accounts.region_enumeration.with_streaming_response.region_enumeration(
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            region_enumeration = response.parse()
            assert_matches_type(RequestTracker, region_enumeration, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRegionEnumeration:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        region_enumeration = await async_client.iaas.api.cloud_accounts.region_enumeration.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RegionEnumerationRetrieveResponse, region_enumeration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts.region_enumeration.with_raw_response.retrieve(
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        region_enumeration = await response.parse()
        assert_matches_type(RegionEnumerationRetrieveResponse, region_enumeration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts.region_enumeration.with_streaming_response.retrieve(
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            region_enumeration = await response.parse()
            assert_matches_type(RegionEnumerationRetrieveResponse, region_enumeration, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.cloud_accounts.region_enumeration.with_raw_response.retrieve(
                id="",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_region_enumeration(self, async_client: AsyncVraIaas) -> None:
        region_enumeration = await async_client.iaas.api.cloud_accounts.region_enumeration.region_enumeration(
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
        )
        assert_matches_type(RequestTracker, region_enumeration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_region_enumeration_with_all_params(self, async_client: AsyncVraIaas) -> None:
        region_enumeration = await async_client.iaas.api.cloud_accounts.region_enumeration.region_enumeration(
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
            certificate_info={
                "certificate": "-----BEGIN CERTIFICATE-----\nMIIDHjCCAoegAwIBAgIBATANBgkqhkiG9w0BAQsFADCBpjEUMBIGA1UEChMLVk13\nYXJlIEluYAAc1pw18GT3iAqQRPx0PrjzJhgjIJMla\n/1Kg4byY4FPSacNiRgY/FG2bPCqZk1yRfzmkFYCW/vU+Dg==\n-----END CERTIFICATE-----\n-"
            },
            cloud_account_id="b8b7a918-342e-4a53-a3b0-b935da0fe601",
            cloud_account_type="vsphere, aws, azure, nsxv, nsxt",
            private_key="gfsScK345sGGaVdds222dasdfDDSSasdfdsa34fS",
            private_key_id="ACDC55DB4MFH6ADG75KK",
        )
        assert_matches_type(RequestTracker, region_enumeration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_region_enumeration(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.cloud_accounts.region_enumeration.with_raw_response.region_enumeration(
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        region_enumeration = await response.parse()
        assert_matches_type(RequestTracker, region_enumeration, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_region_enumeration(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.cloud_accounts.region_enumeration.with_streaming_response.region_enumeration(
            api_version="apiVersion",
            cloud_account_properties={
                "supportPublicImages": "true",
                "acceptSelfSignedCertificate": "true",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            region_enumeration = await response.parse()
            assert_matches_type(RequestTracker, region_enumeration, path=["response"])

        assert cast(Any, response.is_closed) is True
