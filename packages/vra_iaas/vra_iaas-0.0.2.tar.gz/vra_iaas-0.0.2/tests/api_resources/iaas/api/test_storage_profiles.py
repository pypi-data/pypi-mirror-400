# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    StorageProfile,
    StorageProfileRetrieveStorageProfilesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestStorageProfiles:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        storage_profile = client.iaas.api.storage_profiles.retrieve(
            id="id",
        )
        assert_matches_type(StorageProfile, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        storage_profile = client.iaas.api.storage_profiles.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(StorageProfile, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profile = response.parse()
        assert_matches_type(StorageProfile, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profile = response.parse()
            assert_matches_type(StorageProfile, storage_profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.storage_profiles.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        storage_profile = client.iaas.api.storage_profiles.update(
            id="id",
            default_item=True,
            name="name",
            region_id="31186",
        )
        assert_matches_type(StorageProfile, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        storage_profile = client.iaas.api.storage_profiles.update(
            id="id",
            default_item=True,
            name="name",
            region_id="31186",
            api_version="apiVersion",
            compute_host_id="8c4ba7aa-3520-344d-b118-4a2108aaabb8",
            description="description",
            disk_properties={
                "0": "{",
                "1": " ",
                "2": '"',
                "3": "d",
                "4": "i",
                "5": "s",
                "6": "k",
                "7": "P",
                "8": "r",
                "9": "o",
                "10": "p",
                "11": "e",
                "12": "r",
                "13": "t",
                "14": "i",
                "15": "e",
                "16": "s",
                "17": '"',
                "18": ":",
                "19": " ",
                "20": "{",
                "21": "\n",
                "22": " ",
                "23": " ",
                "24": " ",
                "25": " ",
                "26": " ",
                "27": " ",
                "28": " ",
                "29": " ",
                "30": " ",
                "31": " ",
                "32": " ",
                "33": " ",
                "34": " ",
                "35": " ",
                "36": " ",
                "37": " ",
                "38": " ",
                "39": " ",
                "40": " ",
                "41": " ",
                "42": '"',
                "43": "p",
                "44": "r",
                "45": "o",
                "46": "v",
                "47": "i",
                "48": "s",
                "49": "i",
                "50": "o",
                "51": "n",
                "52": "i",
                "53": "n",
                "54": "g",
                "55": "T",
                "56": "y",
                "57": "p",
                "58": "e",
                "59": '"',
                "60": ":",
                "61": " ",
                "62": '"',
                "63": "t",
                "64": "h",
                "65": "i",
                "66": "n",
                "67": '"',
                "68": ",",
                "69": "\n",
                "70": " ",
                "71": " ",
                "72": " ",
                "73": " ",
                "74": " ",
                "75": " ",
                "76": " ",
                "77": " ",
                "78": " ",
                "79": " ",
                "80": " ",
                "81": " ",
                "82": " ",
                "83": " ",
                "84": " ",
                "85": " ",
                "86": " ",
                "87": " ",
                "88": " ",
                "89": " ",
                "90": '"',
                "91": "s",
                "92": "h",
                "93": "a",
                "94": "r",
                "95": "e",
                "96": "s",
                "97": "L",
                "98": "e",
                "99": "v",
                "100": "e",
                "101": "l",
                "102": '"',
                "103": ":",
                "104": " ",
                "105": '"',
                "106": "l",
                "107": "o",
                "108": "w",
                "109": '"',
                "110": ",",
                "111": "\n",
                "112": " ",
                "113": " ",
                "114": " ",
                "115": " ",
                "116": " ",
                "117": " ",
                "118": " ",
                "119": " ",
                "120": " ",
                "121": " ",
                "122": " ",
                "123": " ",
                "124": " ",
                "125": " ",
                "126": " ",
                "127": " ",
                "128": " ",
                "129": " ",
                "130": " ",
                "131": " ",
                "132": '"',
                "133": "s",
                "134": "h",
                "135": "a",
                "136": "r",
                "137": "e",
                "138": "s",
                "139": '"',
                "140": ":",
                "141": " ",
                "142": '"',
                "143": "5",
                "144": "0",
                "145": "0",
                "146": '"',
                "147": ",",
                "148": "\n",
                "149": " ",
                "150": " ",
                "151": " ",
                "152": " ",
                "153": " ",
                "154": " ",
                "155": " ",
                "156": " ",
                "157": " ",
                "158": " ",
                "159": " ",
                "160": " ",
                "161": " ",
                "162": " ",
                "163": " ",
                "164": " ",
                "165": " ",
                "166": " ",
                "167": " ",
                "168": " ",
                "169": '"',
                "170": "l",
                "171": "i",
                "172": "m",
                "173": "i",
                "174": "t",
                "175": "I",
                "176": "o",
                "177": "p",
                "178": "s",
                "179": '"',
                "180": ":",
                "181": " ",
                "182": '"',
                "183": "5",
                "184": "0",
                "185": "0",
                "186": '"',
                "187": "\n",
                "188": " ",
                "189": " ",
                "190": " ",
                "191": " ",
                "192": " ",
                "193": " ",
                "194": " ",
                "195": " ",
                "196": " ",
                "197": " ",
                "198": " ",
                "199": " ",
                "200": " ",
                "201": " ",
                "202": " ",
                "203": " ",
                "204": " ",
                "205": " ",
                "206": " ",
                "207": " ",
                "208": '"',
                "209": "d",
                "210": "i",
                "211": "s",
                "212": "k",
                "213": "T",
                "214": "y",
                "215": "p",
                "216": "e",
                "217": '"',
                "218": ":",
                "219": " ",
                "220": '"',
                "221": "f",
                "222": "i",
                "223": "r",
                "224": "s",
                "225": "t",
                "226": "C",
                "227": "l",
                "228": "a",
                "229": "s",
                "230": "s",
                "231": '"',
                "232": "\n",
                "233": " ",
                "234": " ",
                "235": " ",
                "236": " ",
                "237": " ",
                "238": " ",
                "239": " ",
                "240": " ",
                "241": " ",
                "242": " ",
                "243": " ",
                "244": " ",
                "245": " ",
                "246": " ",
                "247": " ",
                "248": " ",
                "249": "}",
                "250": " ",
                "251": "}",
            },
            disk_target_properties={
                "0": "{",
                "1": " ",
                "2": '"',
                "3": "d",
                "4": "i",
                "5": "s",
                "6": "k",
                "7": "T",
                "8": "a",
                "9": "r",
                "10": "g",
                "11": "e",
                "12": "t",
                "13": "P",
                "14": "r",
                "15": "o",
                "16": "p",
                "17": "e",
                "18": "r",
                "19": "t",
                "20": "i",
                "21": "e",
                "22": "s",
                "23": '"',
                "24": ":",
                "25": " ",
                "26": "{",
                "27": "\n",
                "28": " ",
                "29": " ",
                "30": " ",
                "31": " ",
                "32": " ",
                "33": " ",
                "34": " ",
                "35": " ",
                "36": " ",
                "37": " ",
                "38": " ",
                "39": " ",
                "40": " ",
                "41": " ",
                "42": " ",
                "43": " ",
                "44": " ",
                "45": " ",
                "46": " ",
                "47": " ",
                "48": '"',
                "49": "s",
                "50": "t",
                "51": "o",
                "52": "r",
                "53": "a",
                "54": "g",
                "55": "e",
                "56": "P",
                "57": "o",
                "58": "l",
                "59": "i",
                "60": "c",
                "61": "y",
                "62": "I",
                "63": "d",
                "64": '"',
                "65": ":",
                "66": " ",
                "67": '"',
                "68": "7",
                "69": "f",
                "70": "h",
                "71": "f",
                "72": "j",
                "73": "9",
                "74": "f",
                "75": '"',
                "76": ",",
                "77": "\n",
                "78": " ",
                "79": " ",
                "80": " ",
                "81": " ",
                "82": " ",
                "83": " ",
                "84": " ",
                "85": " ",
                "86": " ",
                "87": " ",
                "88": " ",
                "89": " ",
                "90": " ",
                "91": " ",
                "92": " ",
                "93": " ",
                "94": " ",
                "95": " ",
                "96": " ",
                "97": " ",
                "98": '"',
                "99": "d",
                "100": "a",
                "101": "t",
                "102": "a",
                "103": "s",
                "104": "t",
                "105": "o",
                "106": "r",
                "107": "e",
                "108": "I",
                "109": "d",
                "110": '"',
                "111": ":",
                "112": " ",
                "113": '"',
                "114": "6",
                "115": "3",
                "116": "8",
                "117": "n",
                "118": "f",
                "119": "j",
                "120": "d",
                "121": "8",
                "122": '"',
                "123": ",",
                "124": "\n",
                "125": " ",
                "126": " ",
                "127": " ",
                "128": " ",
                "129": " ",
                "130": " ",
                "131": " ",
                "132": " ",
                "133": " ",
                "134": " ",
                "135": " ",
                "136": " ",
                "137": " ",
                "138": " ",
                "139": " ",
                "140": " ",
                "141": "}",
                "142": " ",
                "143": "}",
            },
            priority=2,
            storage_filter_type="MANUAL",
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
            supports_encryption=True,
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
        assert_matches_type(StorageProfile, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles.with_raw_response.update(
            id="id",
            default_item=True,
            name="name",
            region_id="31186",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profile = response.parse()
        assert_matches_type(StorageProfile, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles.with_streaming_response.update(
            id="id",
            default_item=True,
            name="name",
            region_id="31186",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profile = response.parse()
            assert_matches_type(StorageProfile, storage_profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.storage_profiles.with_raw_response.update(
                id="",
                default_item=True,
                name="name",
                region_id="31186",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        storage_profile = client.iaas.api.storage_profiles.delete(
            id="id",
        )
        assert storage_profile is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: VraIaas) -> None:
        storage_profile = client.iaas.api.storage_profiles.delete(
            id="id",
            api_version="apiVersion",
        )
        assert storage_profile is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profile = response.parse()
        assert storage_profile is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profile = response.parse()
            assert storage_profile is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.storage_profiles.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_storage_profiles(self, client: VraIaas) -> None:
        storage_profile = client.iaas.api.storage_profiles.retrieve_storage_profiles()
        assert_matches_type(StorageProfileRetrieveStorageProfilesResponse, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_storage_profiles_with_all_params(self, client: VraIaas) -> None:
        storage_profile = client.iaas.api.storage_profiles.retrieve_storage_profiles(
            api_version="apiVersion",
        )
        assert_matches_type(StorageProfileRetrieveStorageProfilesResponse, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_storage_profiles(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles.with_raw_response.retrieve_storage_profiles()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profile = response.parse()
        assert_matches_type(StorageProfileRetrieveStorageProfilesResponse, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_storage_profiles(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles.with_streaming_response.retrieve_storage_profiles() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profile = response.parse()
            assert_matches_type(StorageProfileRetrieveStorageProfilesResponse, storage_profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_storage_profiles(self, client: VraIaas) -> None:
        storage_profile = client.iaas.api.storage_profiles.storage_profiles(
            default_item=True,
            name="name",
            region_id="31186",
        )
        assert_matches_type(StorageProfile, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_storage_profiles_with_all_params(self, client: VraIaas) -> None:
        storage_profile = client.iaas.api.storage_profiles.storage_profiles(
            default_item=True,
            name="name",
            region_id="31186",
            api_version="apiVersion",
            compute_host_id="8c4ba7aa-3520-344d-b118-4a2108aaabb8",
            description="description",
            disk_properties={
                "0": "{",
                "1": " ",
                "2": '"',
                "3": "d",
                "4": "i",
                "5": "s",
                "6": "k",
                "7": "P",
                "8": "r",
                "9": "o",
                "10": "p",
                "11": "e",
                "12": "r",
                "13": "t",
                "14": "i",
                "15": "e",
                "16": "s",
                "17": '"',
                "18": ":",
                "19": " ",
                "20": "{",
                "21": "\n",
                "22": " ",
                "23": " ",
                "24": " ",
                "25": " ",
                "26": " ",
                "27": " ",
                "28": " ",
                "29": " ",
                "30": " ",
                "31": " ",
                "32": " ",
                "33": " ",
                "34": " ",
                "35": " ",
                "36": " ",
                "37": " ",
                "38": " ",
                "39": " ",
                "40": " ",
                "41": " ",
                "42": '"',
                "43": "p",
                "44": "r",
                "45": "o",
                "46": "v",
                "47": "i",
                "48": "s",
                "49": "i",
                "50": "o",
                "51": "n",
                "52": "i",
                "53": "n",
                "54": "g",
                "55": "T",
                "56": "y",
                "57": "p",
                "58": "e",
                "59": '"',
                "60": ":",
                "61": " ",
                "62": '"',
                "63": "t",
                "64": "h",
                "65": "i",
                "66": "n",
                "67": '"',
                "68": ",",
                "69": "\n",
                "70": " ",
                "71": " ",
                "72": " ",
                "73": " ",
                "74": " ",
                "75": " ",
                "76": " ",
                "77": " ",
                "78": " ",
                "79": " ",
                "80": " ",
                "81": " ",
                "82": " ",
                "83": " ",
                "84": " ",
                "85": " ",
                "86": " ",
                "87": " ",
                "88": " ",
                "89": " ",
                "90": '"',
                "91": "s",
                "92": "h",
                "93": "a",
                "94": "r",
                "95": "e",
                "96": "s",
                "97": "L",
                "98": "e",
                "99": "v",
                "100": "e",
                "101": "l",
                "102": '"',
                "103": ":",
                "104": " ",
                "105": '"',
                "106": "l",
                "107": "o",
                "108": "w",
                "109": '"',
                "110": ",",
                "111": "\n",
                "112": " ",
                "113": " ",
                "114": " ",
                "115": " ",
                "116": " ",
                "117": " ",
                "118": " ",
                "119": " ",
                "120": " ",
                "121": " ",
                "122": " ",
                "123": " ",
                "124": " ",
                "125": " ",
                "126": " ",
                "127": " ",
                "128": " ",
                "129": " ",
                "130": " ",
                "131": " ",
                "132": '"',
                "133": "s",
                "134": "h",
                "135": "a",
                "136": "r",
                "137": "e",
                "138": "s",
                "139": '"',
                "140": ":",
                "141": " ",
                "142": '"',
                "143": "5",
                "144": "0",
                "145": "0",
                "146": '"',
                "147": ",",
                "148": "\n",
                "149": " ",
                "150": " ",
                "151": " ",
                "152": " ",
                "153": " ",
                "154": " ",
                "155": " ",
                "156": " ",
                "157": " ",
                "158": " ",
                "159": " ",
                "160": " ",
                "161": " ",
                "162": " ",
                "163": " ",
                "164": " ",
                "165": " ",
                "166": " ",
                "167": " ",
                "168": " ",
                "169": '"',
                "170": "l",
                "171": "i",
                "172": "m",
                "173": "i",
                "174": "t",
                "175": "I",
                "176": "o",
                "177": "p",
                "178": "s",
                "179": '"',
                "180": ":",
                "181": " ",
                "182": '"',
                "183": "5",
                "184": "0",
                "185": "0",
                "186": '"',
                "187": "\n",
                "188": " ",
                "189": " ",
                "190": " ",
                "191": " ",
                "192": " ",
                "193": " ",
                "194": " ",
                "195": " ",
                "196": " ",
                "197": " ",
                "198": " ",
                "199": " ",
                "200": " ",
                "201": " ",
                "202": " ",
                "203": " ",
                "204": " ",
                "205": " ",
                "206": " ",
                "207": " ",
                "208": '"',
                "209": "d",
                "210": "i",
                "211": "s",
                "212": "k",
                "213": "T",
                "214": "y",
                "215": "p",
                "216": "e",
                "217": '"',
                "218": ":",
                "219": " ",
                "220": '"',
                "221": "f",
                "222": "i",
                "223": "r",
                "224": "s",
                "225": "t",
                "226": "C",
                "227": "l",
                "228": "a",
                "229": "s",
                "230": "s",
                "231": '"',
                "232": "\n",
                "233": " ",
                "234": " ",
                "235": " ",
                "236": " ",
                "237": " ",
                "238": " ",
                "239": " ",
                "240": " ",
                "241": " ",
                "242": " ",
                "243": " ",
                "244": " ",
                "245": " ",
                "246": " ",
                "247": " ",
                "248": " ",
                "249": "}",
                "250": " ",
                "251": "}",
            },
            disk_target_properties={
                "0": "{",
                "1": " ",
                "2": '"',
                "3": "d",
                "4": "i",
                "5": "s",
                "6": "k",
                "7": "T",
                "8": "a",
                "9": "r",
                "10": "g",
                "11": "e",
                "12": "t",
                "13": "P",
                "14": "r",
                "15": "o",
                "16": "p",
                "17": "e",
                "18": "r",
                "19": "t",
                "20": "i",
                "21": "e",
                "22": "s",
                "23": '"',
                "24": ":",
                "25": " ",
                "26": "{",
                "27": "\n",
                "28": " ",
                "29": " ",
                "30": " ",
                "31": " ",
                "32": " ",
                "33": " ",
                "34": " ",
                "35": " ",
                "36": " ",
                "37": " ",
                "38": " ",
                "39": " ",
                "40": " ",
                "41": " ",
                "42": " ",
                "43": " ",
                "44": " ",
                "45": " ",
                "46": " ",
                "47": " ",
                "48": '"',
                "49": "s",
                "50": "t",
                "51": "o",
                "52": "r",
                "53": "a",
                "54": "g",
                "55": "e",
                "56": "P",
                "57": "o",
                "58": "l",
                "59": "i",
                "60": "c",
                "61": "y",
                "62": "I",
                "63": "d",
                "64": '"',
                "65": ":",
                "66": " ",
                "67": '"',
                "68": "7",
                "69": "f",
                "70": "h",
                "71": "f",
                "72": "j",
                "73": "9",
                "74": "f",
                "75": '"',
                "76": ",",
                "77": "\n",
                "78": " ",
                "79": " ",
                "80": " ",
                "81": " ",
                "82": " ",
                "83": " ",
                "84": " ",
                "85": " ",
                "86": " ",
                "87": " ",
                "88": " ",
                "89": " ",
                "90": " ",
                "91": " ",
                "92": " ",
                "93": " ",
                "94": " ",
                "95": " ",
                "96": " ",
                "97": " ",
                "98": '"',
                "99": "d",
                "100": "a",
                "101": "t",
                "102": "a",
                "103": "s",
                "104": "t",
                "105": "o",
                "106": "r",
                "107": "e",
                "108": "I",
                "109": "d",
                "110": '"',
                "111": ":",
                "112": " ",
                "113": '"',
                "114": "6",
                "115": "3",
                "116": "8",
                "117": "n",
                "118": "f",
                "119": "j",
                "120": "d",
                "121": "8",
                "122": '"',
                "123": ",",
                "124": "\n",
                "125": " ",
                "126": " ",
                "127": " ",
                "128": " ",
                "129": " ",
                "130": " ",
                "131": " ",
                "132": " ",
                "133": " ",
                "134": " ",
                "135": " ",
                "136": " ",
                "137": " ",
                "138": " ",
                "139": " ",
                "140": " ",
                "141": "}",
                "142": " ",
                "143": "}",
            },
            priority=2,
            storage_filter_type="MANUAL",
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
            supports_encryption=True,
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
        assert_matches_type(StorageProfile, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_storage_profiles(self, client: VraIaas) -> None:
        response = client.iaas.api.storage_profiles.with_raw_response.storage_profiles(
            default_item=True,
            name="name",
            region_id="31186",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profile = response.parse()
        assert_matches_type(StorageProfile, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_storage_profiles(self, client: VraIaas) -> None:
        with client.iaas.api.storage_profiles.with_streaming_response.storage_profiles(
            default_item=True,
            name="name",
            region_id="31186",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profile = response.parse()
            assert_matches_type(StorageProfile, storage_profile, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncStorageProfiles:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        storage_profile = await async_client.iaas.api.storage_profiles.retrieve(
            id="id",
        )
        assert_matches_type(StorageProfile, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profile = await async_client.iaas.api.storage_profiles.retrieve(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(StorageProfile, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profile = await response.parse()
        assert_matches_type(StorageProfile, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profile = await response.parse()
            assert_matches_type(StorageProfile, storage_profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.storage_profiles.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        storage_profile = await async_client.iaas.api.storage_profiles.update(
            id="id",
            default_item=True,
            name="name",
            region_id="31186",
        )
        assert_matches_type(StorageProfile, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profile = await async_client.iaas.api.storage_profiles.update(
            id="id",
            default_item=True,
            name="name",
            region_id="31186",
            api_version="apiVersion",
            compute_host_id="8c4ba7aa-3520-344d-b118-4a2108aaabb8",
            description="description",
            disk_properties={
                "0": "{",
                "1": " ",
                "2": '"',
                "3": "d",
                "4": "i",
                "5": "s",
                "6": "k",
                "7": "P",
                "8": "r",
                "9": "o",
                "10": "p",
                "11": "e",
                "12": "r",
                "13": "t",
                "14": "i",
                "15": "e",
                "16": "s",
                "17": '"',
                "18": ":",
                "19": " ",
                "20": "{",
                "21": "\n",
                "22": " ",
                "23": " ",
                "24": " ",
                "25": " ",
                "26": " ",
                "27": " ",
                "28": " ",
                "29": " ",
                "30": " ",
                "31": " ",
                "32": " ",
                "33": " ",
                "34": " ",
                "35": " ",
                "36": " ",
                "37": " ",
                "38": " ",
                "39": " ",
                "40": " ",
                "41": " ",
                "42": '"',
                "43": "p",
                "44": "r",
                "45": "o",
                "46": "v",
                "47": "i",
                "48": "s",
                "49": "i",
                "50": "o",
                "51": "n",
                "52": "i",
                "53": "n",
                "54": "g",
                "55": "T",
                "56": "y",
                "57": "p",
                "58": "e",
                "59": '"',
                "60": ":",
                "61": " ",
                "62": '"',
                "63": "t",
                "64": "h",
                "65": "i",
                "66": "n",
                "67": '"',
                "68": ",",
                "69": "\n",
                "70": " ",
                "71": " ",
                "72": " ",
                "73": " ",
                "74": " ",
                "75": " ",
                "76": " ",
                "77": " ",
                "78": " ",
                "79": " ",
                "80": " ",
                "81": " ",
                "82": " ",
                "83": " ",
                "84": " ",
                "85": " ",
                "86": " ",
                "87": " ",
                "88": " ",
                "89": " ",
                "90": '"',
                "91": "s",
                "92": "h",
                "93": "a",
                "94": "r",
                "95": "e",
                "96": "s",
                "97": "L",
                "98": "e",
                "99": "v",
                "100": "e",
                "101": "l",
                "102": '"',
                "103": ":",
                "104": " ",
                "105": '"',
                "106": "l",
                "107": "o",
                "108": "w",
                "109": '"',
                "110": ",",
                "111": "\n",
                "112": " ",
                "113": " ",
                "114": " ",
                "115": " ",
                "116": " ",
                "117": " ",
                "118": " ",
                "119": " ",
                "120": " ",
                "121": " ",
                "122": " ",
                "123": " ",
                "124": " ",
                "125": " ",
                "126": " ",
                "127": " ",
                "128": " ",
                "129": " ",
                "130": " ",
                "131": " ",
                "132": '"',
                "133": "s",
                "134": "h",
                "135": "a",
                "136": "r",
                "137": "e",
                "138": "s",
                "139": '"',
                "140": ":",
                "141": " ",
                "142": '"',
                "143": "5",
                "144": "0",
                "145": "0",
                "146": '"',
                "147": ",",
                "148": "\n",
                "149": " ",
                "150": " ",
                "151": " ",
                "152": " ",
                "153": " ",
                "154": " ",
                "155": " ",
                "156": " ",
                "157": " ",
                "158": " ",
                "159": " ",
                "160": " ",
                "161": " ",
                "162": " ",
                "163": " ",
                "164": " ",
                "165": " ",
                "166": " ",
                "167": " ",
                "168": " ",
                "169": '"',
                "170": "l",
                "171": "i",
                "172": "m",
                "173": "i",
                "174": "t",
                "175": "I",
                "176": "o",
                "177": "p",
                "178": "s",
                "179": '"',
                "180": ":",
                "181": " ",
                "182": '"',
                "183": "5",
                "184": "0",
                "185": "0",
                "186": '"',
                "187": "\n",
                "188": " ",
                "189": " ",
                "190": " ",
                "191": " ",
                "192": " ",
                "193": " ",
                "194": " ",
                "195": " ",
                "196": " ",
                "197": " ",
                "198": " ",
                "199": " ",
                "200": " ",
                "201": " ",
                "202": " ",
                "203": " ",
                "204": " ",
                "205": " ",
                "206": " ",
                "207": " ",
                "208": '"',
                "209": "d",
                "210": "i",
                "211": "s",
                "212": "k",
                "213": "T",
                "214": "y",
                "215": "p",
                "216": "e",
                "217": '"',
                "218": ":",
                "219": " ",
                "220": '"',
                "221": "f",
                "222": "i",
                "223": "r",
                "224": "s",
                "225": "t",
                "226": "C",
                "227": "l",
                "228": "a",
                "229": "s",
                "230": "s",
                "231": '"',
                "232": "\n",
                "233": " ",
                "234": " ",
                "235": " ",
                "236": " ",
                "237": " ",
                "238": " ",
                "239": " ",
                "240": " ",
                "241": " ",
                "242": " ",
                "243": " ",
                "244": " ",
                "245": " ",
                "246": " ",
                "247": " ",
                "248": " ",
                "249": "}",
                "250": " ",
                "251": "}",
            },
            disk_target_properties={
                "0": "{",
                "1": " ",
                "2": '"',
                "3": "d",
                "4": "i",
                "5": "s",
                "6": "k",
                "7": "T",
                "8": "a",
                "9": "r",
                "10": "g",
                "11": "e",
                "12": "t",
                "13": "P",
                "14": "r",
                "15": "o",
                "16": "p",
                "17": "e",
                "18": "r",
                "19": "t",
                "20": "i",
                "21": "e",
                "22": "s",
                "23": '"',
                "24": ":",
                "25": " ",
                "26": "{",
                "27": "\n",
                "28": " ",
                "29": " ",
                "30": " ",
                "31": " ",
                "32": " ",
                "33": " ",
                "34": " ",
                "35": " ",
                "36": " ",
                "37": " ",
                "38": " ",
                "39": " ",
                "40": " ",
                "41": " ",
                "42": " ",
                "43": " ",
                "44": " ",
                "45": " ",
                "46": " ",
                "47": " ",
                "48": '"',
                "49": "s",
                "50": "t",
                "51": "o",
                "52": "r",
                "53": "a",
                "54": "g",
                "55": "e",
                "56": "P",
                "57": "o",
                "58": "l",
                "59": "i",
                "60": "c",
                "61": "y",
                "62": "I",
                "63": "d",
                "64": '"',
                "65": ":",
                "66": " ",
                "67": '"',
                "68": "7",
                "69": "f",
                "70": "h",
                "71": "f",
                "72": "j",
                "73": "9",
                "74": "f",
                "75": '"',
                "76": ",",
                "77": "\n",
                "78": " ",
                "79": " ",
                "80": " ",
                "81": " ",
                "82": " ",
                "83": " ",
                "84": " ",
                "85": " ",
                "86": " ",
                "87": " ",
                "88": " ",
                "89": " ",
                "90": " ",
                "91": " ",
                "92": " ",
                "93": " ",
                "94": " ",
                "95": " ",
                "96": " ",
                "97": " ",
                "98": '"',
                "99": "d",
                "100": "a",
                "101": "t",
                "102": "a",
                "103": "s",
                "104": "t",
                "105": "o",
                "106": "r",
                "107": "e",
                "108": "I",
                "109": "d",
                "110": '"',
                "111": ":",
                "112": " ",
                "113": '"',
                "114": "6",
                "115": "3",
                "116": "8",
                "117": "n",
                "118": "f",
                "119": "j",
                "120": "d",
                "121": "8",
                "122": '"',
                "123": ",",
                "124": "\n",
                "125": " ",
                "126": " ",
                "127": " ",
                "128": " ",
                "129": " ",
                "130": " ",
                "131": " ",
                "132": " ",
                "133": " ",
                "134": " ",
                "135": " ",
                "136": " ",
                "137": " ",
                "138": " ",
                "139": " ",
                "140": " ",
                "141": "}",
                "142": " ",
                "143": "}",
            },
            priority=2,
            storage_filter_type="MANUAL",
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
            supports_encryption=True,
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
        assert_matches_type(StorageProfile, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles.with_raw_response.update(
            id="id",
            default_item=True,
            name="name",
            region_id="31186",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profile = await response.parse()
        assert_matches_type(StorageProfile, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles.with_streaming_response.update(
            id="id",
            default_item=True,
            name="name",
            region_id="31186",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profile = await response.parse()
            assert_matches_type(StorageProfile, storage_profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.storage_profiles.with_raw_response.update(
                id="",
                default_item=True,
                name="name",
                region_id="31186",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        storage_profile = await async_client.iaas.api.storage_profiles.delete(
            id="id",
        )
        assert storage_profile is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profile = await async_client.iaas.api.storage_profiles.delete(
            id="id",
            api_version="apiVersion",
        )
        assert storage_profile is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profile = await response.parse()
        assert storage_profile is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profile = await response.parse()
            assert storage_profile is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.storage_profiles.with_raw_response.delete(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_storage_profiles(self, async_client: AsyncVraIaas) -> None:
        storage_profile = await async_client.iaas.api.storage_profiles.retrieve_storage_profiles()
        assert_matches_type(StorageProfileRetrieveStorageProfilesResponse, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_storage_profiles_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profile = await async_client.iaas.api.storage_profiles.retrieve_storage_profiles(
            api_version="apiVersion",
        )
        assert_matches_type(StorageProfileRetrieveStorageProfilesResponse, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_storage_profiles(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles.with_raw_response.retrieve_storage_profiles()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profile = await response.parse()
        assert_matches_type(StorageProfileRetrieveStorageProfilesResponse, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_storage_profiles(self, async_client: AsyncVraIaas) -> None:
        async with (
            async_client.iaas.api.storage_profiles.with_streaming_response.retrieve_storage_profiles()
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profile = await response.parse()
            assert_matches_type(StorageProfileRetrieveStorageProfilesResponse, storage_profile, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_storage_profiles(self, async_client: AsyncVraIaas) -> None:
        storage_profile = await async_client.iaas.api.storage_profiles.storage_profiles(
            default_item=True,
            name="name",
            region_id="31186",
        )
        assert_matches_type(StorageProfile, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_storage_profiles_with_all_params(self, async_client: AsyncVraIaas) -> None:
        storage_profile = await async_client.iaas.api.storage_profiles.storage_profiles(
            default_item=True,
            name="name",
            region_id="31186",
            api_version="apiVersion",
            compute_host_id="8c4ba7aa-3520-344d-b118-4a2108aaabb8",
            description="description",
            disk_properties={
                "0": "{",
                "1": " ",
                "2": '"',
                "3": "d",
                "4": "i",
                "5": "s",
                "6": "k",
                "7": "P",
                "8": "r",
                "9": "o",
                "10": "p",
                "11": "e",
                "12": "r",
                "13": "t",
                "14": "i",
                "15": "e",
                "16": "s",
                "17": '"',
                "18": ":",
                "19": " ",
                "20": "{",
                "21": "\n",
                "22": " ",
                "23": " ",
                "24": " ",
                "25": " ",
                "26": " ",
                "27": " ",
                "28": " ",
                "29": " ",
                "30": " ",
                "31": " ",
                "32": " ",
                "33": " ",
                "34": " ",
                "35": " ",
                "36": " ",
                "37": " ",
                "38": " ",
                "39": " ",
                "40": " ",
                "41": " ",
                "42": '"',
                "43": "p",
                "44": "r",
                "45": "o",
                "46": "v",
                "47": "i",
                "48": "s",
                "49": "i",
                "50": "o",
                "51": "n",
                "52": "i",
                "53": "n",
                "54": "g",
                "55": "T",
                "56": "y",
                "57": "p",
                "58": "e",
                "59": '"',
                "60": ":",
                "61": " ",
                "62": '"',
                "63": "t",
                "64": "h",
                "65": "i",
                "66": "n",
                "67": '"',
                "68": ",",
                "69": "\n",
                "70": " ",
                "71": " ",
                "72": " ",
                "73": " ",
                "74": " ",
                "75": " ",
                "76": " ",
                "77": " ",
                "78": " ",
                "79": " ",
                "80": " ",
                "81": " ",
                "82": " ",
                "83": " ",
                "84": " ",
                "85": " ",
                "86": " ",
                "87": " ",
                "88": " ",
                "89": " ",
                "90": '"',
                "91": "s",
                "92": "h",
                "93": "a",
                "94": "r",
                "95": "e",
                "96": "s",
                "97": "L",
                "98": "e",
                "99": "v",
                "100": "e",
                "101": "l",
                "102": '"',
                "103": ":",
                "104": " ",
                "105": '"',
                "106": "l",
                "107": "o",
                "108": "w",
                "109": '"',
                "110": ",",
                "111": "\n",
                "112": " ",
                "113": " ",
                "114": " ",
                "115": " ",
                "116": " ",
                "117": " ",
                "118": " ",
                "119": " ",
                "120": " ",
                "121": " ",
                "122": " ",
                "123": " ",
                "124": " ",
                "125": " ",
                "126": " ",
                "127": " ",
                "128": " ",
                "129": " ",
                "130": " ",
                "131": " ",
                "132": '"',
                "133": "s",
                "134": "h",
                "135": "a",
                "136": "r",
                "137": "e",
                "138": "s",
                "139": '"',
                "140": ":",
                "141": " ",
                "142": '"',
                "143": "5",
                "144": "0",
                "145": "0",
                "146": '"',
                "147": ",",
                "148": "\n",
                "149": " ",
                "150": " ",
                "151": " ",
                "152": " ",
                "153": " ",
                "154": " ",
                "155": " ",
                "156": " ",
                "157": " ",
                "158": " ",
                "159": " ",
                "160": " ",
                "161": " ",
                "162": " ",
                "163": " ",
                "164": " ",
                "165": " ",
                "166": " ",
                "167": " ",
                "168": " ",
                "169": '"',
                "170": "l",
                "171": "i",
                "172": "m",
                "173": "i",
                "174": "t",
                "175": "I",
                "176": "o",
                "177": "p",
                "178": "s",
                "179": '"',
                "180": ":",
                "181": " ",
                "182": '"',
                "183": "5",
                "184": "0",
                "185": "0",
                "186": '"',
                "187": "\n",
                "188": " ",
                "189": " ",
                "190": " ",
                "191": " ",
                "192": " ",
                "193": " ",
                "194": " ",
                "195": " ",
                "196": " ",
                "197": " ",
                "198": " ",
                "199": " ",
                "200": " ",
                "201": " ",
                "202": " ",
                "203": " ",
                "204": " ",
                "205": " ",
                "206": " ",
                "207": " ",
                "208": '"',
                "209": "d",
                "210": "i",
                "211": "s",
                "212": "k",
                "213": "T",
                "214": "y",
                "215": "p",
                "216": "e",
                "217": '"',
                "218": ":",
                "219": " ",
                "220": '"',
                "221": "f",
                "222": "i",
                "223": "r",
                "224": "s",
                "225": "t",
                "226": "C",
                "227": "l",
                "228": "a",
                "229": "s",
                "230": "s",
                "231": '"',
                "232": "\n",
                "233": " ",
                "234": " ",
                "235": " ",
                "236": " ",
                "237": " ",
                "238": " ",
                "239": " ",
                "240": " ",
                "241": " ",
                "242": " ",
                "243": " ",
                "244": " ",
                "245": " ",
                "246": " ",
                "247": " ",
                "248": " ",
                "249": "}",
                "250": " ",
                "251": "}",
            },
            disk_target_properties={
                "0": "{",
                "1": " ",
                "2": '"',
                "3": "d",
                "4": "i",
                "5": "s",
                "6": "k",
                "7": "T",
                "8": "a",
                "9": "r",
                "10": "g",
                "11": "e",
                "12": "t",
                "13": "P",
                "14": "r",
                "15": "o",
                "16": "p",
                "17": "e",
                "18": "r",
                "19": "t",
                "20": "i",
                "21": "e",
                "22": "s",
                "23": '"',
                "24": ":",
                "25": " ",
                "26": "{",
                "27": "\n",
                "28": " ",
                "29": " ",
                "30": " ",
                "31": " ",
                "32": " ",
                "33": " ",
                "34": " ",
                "35": " ",
                "36": " ",
                "37": " ",
                "38": " ",
                "39": " ",
                "40": " ",
                "41": " ",
                "42": " ",
                "43": " ",
                "44": " ",
                "45": " ",
                "46": " ",
                "47": " ",
                "48": '"',
                "49": "s",
                "50": "t",
                "51": "o",
                "52": "r",
                "53": "a",
                "54": "g",
                "55": "e",
                "56": "P",
                "57": "o",
                "58": "l",
                "59": "i",
                "60": "c",
                "61": "y",
                "62": "I",
                "63": "d",
                "64": '"',
                "65": ":",
                "66": " ",
                "67": '"',
                "68": "7",
                "69": "f",
                "70": "h",
                "71": "f",
                "72": "j",
                "73": "9",
                "74": "f",
                "75": '"',
                "76": ",",
                "77": "\n",
                "78": " ",
                "79": " ",
                "80": " ",
                "81": " ",
                "82": " ",
                "83": " ",
                "84": " ",
                "85": " ",
                "86": " ",
                "87": " ",
                "88": " ",
                "89": " ",
                "90": " ",
                "91": " ",
                "92": " ",
                "93": " ",
                "94": " ",
                "95": " ",
                "96": " ",
                "97": " ",
                "98": '"',
                "99": "d",
                "100": "a",
                "101": "t",
                "102": "a",
                "103": "s",
                "104": "t",
                "105": "o",
                "106": "r",
                "107": "e",
                "108": "I",
                "109": "d",
                "110": '"',
                "111": ":",
                "112": " ",
                "113": '"',
                "114": "6",
                "115": "3",
                "116": "8",
                "117": "n",
                "118": "f",
                "119": "j",
                "120": "d",
                "121": "8",
                "122": '"',
                "123": ",",
                "124": "\n",
                "125": " ",
                "126": " ",
                "127": " ",
                "128": " ",
                "129": " ",
                "130": " ",
                "131": " ",
                "132": " ",
                "133": " ",
                "134": " ",
                "135": " ",
                "136": " ",
                "137": " ",
                "138": " ",
                "139": " ",
                "140": " ",
                "141": "}",
                "142": " ",
                "143": "}",
            },
            priority=2,
            storage_filter_type="MANUAL",
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
            supports_encryption=True,
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
        assert_matches_type(StorageProfile, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_storage_profiles(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.storage_profiles.with_raw_response.storage_profiles(
            default_item=True,
            name="name",
            region_id="31186",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        storage_profile = await response.parse()
        assert_matches_type(StorageProfile, storage_profile, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_storage_profiles(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.storage_profiles.with_streaming_response.storage_profiles(
            default_item=True,
            name="name",
            region_id="31186",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            storage_profile = await response.parse()
            assert_matches_type(StorageProfile, storage_profile, path=["response"])

        assert cast(Any, response.is_closed) is True
