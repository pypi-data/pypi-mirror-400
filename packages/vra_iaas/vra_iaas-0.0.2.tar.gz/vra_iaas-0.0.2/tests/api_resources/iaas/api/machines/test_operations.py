# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api.projects import RequestTracker

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOperations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.update(
            snapshot_id="snapshotId",
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.operations.with_raw_response.update(
            snapshot_id="snapshotId",
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.machines.operations.with_streaming_response.update(
            snapshot_id="snapshotId",
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.machines.operations.with_raw_response.update(
                snapshot_id="snapshotId",
                id="",
                api_version="apiVersion",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `snapshot_id` but received ''"):
            client.iaas.api.machines.operations.with_raw_response.update(
                snapshot_id="",
                id="id",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_change_security_groups(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.change_security_groups(
            path_id="id",
            body_id="9.0E49",
            _links={},
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_change_security_groups_with_all_params(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.change_security_groups(
            path_id="id",
            body_id="9.0E49",
            _links={"empty": True},
            api_version="apiVersion",
            created_at="2012-09-27",
            description="my-description",
            name="my-name",
            network_interface_specifications=[
                {
                    "addresses": ["10.1.2.190"],
                    "custom_properties": {"awaitIp": "true"},
                    "description": "description",
                    "device_index": 1,
                    "fabric_network_id": "54097407-4532-460c-94a8-8f9e18f4c925",
                    "mac_address": '["00:50:56:99:d8:34"]',
                    "name": "name",
                    "network_id": "54097407-4532-460c-94a8-8f9e18f4c925",
                    "security_group_ids": ["string"],
                }
            ],
            org_id="42413b31-1716-477e-9a88-9dc1c3cb1cdf",
            owner="csp@vmware.com",
            owner_type="ad_group",
            updated_at="2012-09-27",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_change_security_groups(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.operations.with_raw_response.change_security_groups(
            path_id="id",
            body_id="9.0E49",
            _links={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_change_security_groups(self, client: VraIaas) -> None:
        with client.iaas.api.machines.operations.with_streaming_response.change_security_groups(
            path_id="id",
            body_id="9.0E49",
            _links={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_change_security_groups(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_id` but received ''"):
            client.iaas.api.machines.operations.with_raw_response.change_security_groups(
                path_id="",
                body_id="9.0E49",
                _links={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_power_off(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.power_off(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_power_off_with_all_params(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.power_off(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_power_off(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.operations.with_raw_response.power_off(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_power_off(self, client: VraIaas) -> None:
        with client.iaas.api.machines.operations.with_streaming_response.power_off(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_power_off(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.machines.operations.with_raw_response.power_off(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_power_on(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.power_on(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_power_on_with_all_params(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.power_on(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_power_on(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.operations.with_raw_response.power_on(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_power_on(self, client: VraIaas) -> None:
        with client.iaas.api.machines.operations.with_streaming_response.power_on(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_power_on(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.machines.operations.with_raw_response.power_on(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_reboot(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.reboot(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_reboot_with_all_params(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.reboot(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_reboot(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.operations.with_raw_response.reboot(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_reboot(self, client: VraIaas) -> None:
        with client.iaas.api.machines.operations.with_streaming_response.reboot(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_reboot(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.machines.operations.with_raw_response.reboot(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_reset(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.reset(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_reset_with_all_params(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.reset(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_reset(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.operations.with_raw_response.reset(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_reset(self, client: VraIaas) -> None:
        with client.iaas.api.machines.operations.with_streaming_response.reset(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_reset(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.machines.operations.with_raw_response.reset(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_resize(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.resize(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_resize_with_all_params(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.resize(
            id="id",
            api_version="apiVersion",
            core_count="coreCount",
            cpu_count="cpuCount",
            flavor_name="flavorName",
            memory_in_mb="memoryInMB",
            reboot_machine=True,
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_resize(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.operations.with_raw_response.resize(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_resize(self, client: VraIaas) -> None:
        with client.iaas.api.machines.operations.with_streaming_response.resize(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_resize(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.machines.operations.with_raw_response.resize(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_restart(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.restart(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_restart_with_all_params(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.restart(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_restart(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.operations.with_raw_response.restart(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_restart(self, client: VraIaas) -> None:
        with client.iaas.api.machines.operations.with_streaming_response.restart(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_restart(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.machines.operations.with_raw_response.restart(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_shutdown(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.shutdown(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_shutdown_with_all_params(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.shutdown(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_shutdown(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.operations.with_raw_response.shutdown(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_shutdown(self, client: VraIaas) -> None:
        with client.iaas.api.machines.operations.with_streaming_response.shutdown(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_shutdown(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.machines.operations.with_raw_response.shutdown(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_snapshots(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.snapshots(
            path_id="id",
            body_id="9.0E49",
            _links={},
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_snapshots_with_all_params(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.snapshots(
            path_id="id",
            body_id="9.0E49",
            _links={"empty": True},
            api_version="apiVersion",
            created_at="2012-09-27",
            custom_properties={"foo": "string"},
            description="my-description",
            name="my-name",
            org_id="42413b31-1716-477e-9a88-9dc1c3cb1cdf",
            owner="csp@vmware.com",
            owner_type="ad_group",
            snapshot_memory=True,
            updated_at="2012-09-27",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_snapshots(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.operations.with_raw_response.snapshots(
            path_id="id",
            body_id="9.0E49",
            _links={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_snapshots(self, client: VraIaas) -> None:
        with client.iaas.api.machines.operations.with_streaming_response.snapshots(
            path_id="id",
            body_id="9.0E49",
            _links={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_snapshots(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_id` but received ''"):
            client.iaas.api.machines.operations.with_raw_response.snapshots(
                path_id="",
                body_id="9.0E49",
                _links={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_suspend(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.suspend(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_suspend_with_all_params(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.suspend(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_suspend(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.operations.with_raw_response.suspend(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_suspend(self, client: VraIaas) -> None:
        with client.iaas.api.machines.operations.with_streaming_response.suspend(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_suspend(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.machines.operations.with_raw_response.suspend(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_unregister(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.unregister(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_unregister_with_all_params(self, client: VraIaas) -> None:
        operation = client.iaas.api.machines.operations.unregister(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_unregister(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.operations.with_raw_response.unregister(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_unregister(self, client: VraIaas) -> None:
        with client.iaas.api.machines.operations.with_streaming_response.unregister(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_unregister(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.machines.operations.with_raw_response.unregister(
                id="",
            )


class TestAsyncOperations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.update(
            snapshot_id="snapshotId",
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.operations.with_raw_response.update(
            snapshot_id="snapshotId",
            id="id",
            api_version="apiVersion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.operations.with_streaming_response.update(
            snapshot_id="snapshotId",
            id="id",
            api_version="apiVersion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.machines.operations.with_raw_response.update(
                snapshot_id="snapshotId",
                id="",
                api_version="apiVersion",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `snapshot_id` but received ''"):
            await async_client.iaas.api.machines.operations.with_raw_response.update(
                snapshot_id="",
                id="id",
                api_version="apiVersion",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_change_security_groups(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.change_security_groups(
            path_id="id",
            body_id="9.0E49",
            _links={},
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_change_security_groups_with_all_params(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.change_security_groups(
            path_id="id",
            body_id="9.0E49",
            _links={"empty": True},
            api_version="apiVersion",
            created_at="2012-09-27",
            description="my-description",
            name="my-name",
            network_interface_specifications=[
                {
                    "addresses": ["10.1.2.190"],
                    "custom_properties": {"awaitIp": "true"},
                    "description": "description",
                    "device_index": 1,
                    "fabric_network_id": "54097407-4532-460c-94a8-8f9e18f4c925",
                    "mac_address": '["00:50:56:99:d8:34"]',
                    "name": "name",
                    "network_id": "54097407-4532-460c-94a8-8f9e18f4c925",
                    "security_group_ids": ["string"],
                }
            ],
            org_id="42413b31-1716-477e-9a88-9dc1c3cb1cdf",
            owner="csp@vmware.com",
            owner_type="ad_group",
            updated_at="2012-09-27",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_change_security_groups(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.operations.with_raw_response.change_security_groups(
            path_id="id",
            body_id="9.0E49",
            _links={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_change_security_groups(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.operations.with_streaming_response.change_security_groups(
            path_id="id",
            body_id="9.0E49",
            _links={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_change_security_groups(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_id` but received ''"):
            await async_client.iaas.api.machines.operations.with_raw_response.change_security_groups(
                path_id="",
                body_id="9.0E49",
                _links={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_power_off(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.power_off(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_power_off_with_all_params(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.power_off(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_power_off(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.operations.with_raw_response.power_off(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_power_off(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.operations.with_streaming_response.power_off(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_power_off(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.machines.operations.with_raw_response.power_off(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_power_on(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.power_on(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_power_on_with_all_params(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.power_on(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_power_on(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.operations.with_raw_response.power_on(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_power_on(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.operations.with_streaming_response.power_on(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_power_on(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.machines.operations.with_raw_response.power_on(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reboot(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.reboot(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reboot_with_all_params(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.reboot(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_reboot(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.operations.with_raw_response.reboot(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_reboot(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.operations.with_streaming_response.reboot(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_reboot(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.machines.operations.with_raw_response.reboot(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reset(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.reset(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reset_with_all_params(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.reset(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_reset(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.operations.with_raw_response.reset(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_reset(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.operations.with_streaming_response.reset(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_reset(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.machines.operations.with_raw_response.reset(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_resize(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.resize(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_resize_with_all_params(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.resize(
            id="id",
            api_version="apiVersion",
            core_count="coreCount",
            cpu_count="cpuCount",
            flavor_name="flavorName",
            memory_in_mb="memoryInMB",
            reboot_machine=True,
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_resize(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.operations.with_raw_response.resize(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_resize(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.operations.with_streaming_response.resize(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_resize(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.machines.operations.with_raw_response.resize(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_restart(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.restart(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_restart_with_all_params(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.restart(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_restart(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.operations.with_raw_response.restart(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_restart(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.operations.with_streaming_response.restart(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_restart(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.machines.operations.with_raw_response.restart(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_shutdown(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.shutdown(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_shutdown_with_all_params(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.shutdown(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_shutdown(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.operations.with_raw_response.shutdown(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_shutdown(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.operations.with_streaming_response.shutdown(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_shutdown(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.machines.operations.with_raw_response.shutdown(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_snapshots(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.snapshots(
            path_id="id",
            body_id="9.0E49",
            _links={},
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_snapshots_with_all_params(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.snapshots(
            path_id="id",
            body_id="9.0E49",
            _links={"empty": True},
            api_version="apiVersion",
            created_at="2012-09-27",
            custom_properties={"foo": "string"},
            description="my-description",
            name="my-name",
            org_id="42413b31-1716-477e-9a88-9dc1c3cb1cdf",
            owner="csp@vmware.com",
            owner_type="ad_group",
            snapshot_memory=True,
            updated_at="2012-09-27",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_snapshots(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.operations.with_raw_response.snapshots(
            path_id="id",
            body_id="9.0E49",
            _links={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_snapshots(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.operations.with_streaming_response.snapshots(
            path_id="id",
            body_id="9.0E49",
            _links={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_snapshots(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_id` but received ''"):
            await async_client.iaas.api.machines.operations.with_raw_response.snapshots(
                path_id="",
                body_id="9.0E49",
                _links={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_suspend(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.suspend(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_suspend_with_all_params(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.suspend(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_suspend(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.operations.with_raw_response.suspend(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_suspend(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.operations.with_streaming_response.suspend(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_suspend(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.machines.operations.with_raw_response.suspend(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_unregister(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.unregister(
            id="id",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_unregister_with_all_params(self, async_client: AsyncVraIaas) -> None:
        operation = await async_client.iaas.api.machines.operations.unregister(
            id="id",
            api_version="apiVersion",
        )
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_unregister(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.operations.with_raw_response.unregister(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(RequestTracker, operation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_unregister(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.operations.with_streaming_response.unregister(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(RequestTracker, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_unregister(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.machines.operations.with_raw_response.unregister(
                id="",
            )
