# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vra_iaas import VraIaas, AsyncVraIaas
from tests.utils import assert_matches_type
from vra_iaas.types.iaas.api import (
    Machine,
    MachineListResponse,
)
from vra_iaas.types.iaas.api.projects import RequestTracker

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMachines:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: VraIaas) -> None:
        machine = client.iaas.api.machines.create(
            flavor="small, medium, large",
            flavor_ref="t2.micro",
            image="vmware-gold-master, ubuntu-latest, rhel-compliant, windows",
            image_ref="ami-f6795a8c",
            name="name",
            project_id="e058",
        )
        assert_matches_type(RequestTracker, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: VraIaas) -> None:
        machine = client.iaas.api.machines.create(
            flavor="small, medium, large",
            flavor_ref="t2.micro",
            image="vmware-gold-master, ubuntu-latest, rhel-compliant, windows",
            image_ref="ami-f6795a8c",
            name="name",
            project_id="e058",
            api_version="apiVersion",
            boot_config={
                "content": "#cloud-config\nrepo_update: true\nrepo_upgrade: all\n\npackages:\n - mysql-server\n\nruncmd:\n - sed -e '/bind-address/ s/^#*/#/' -i /etc/mysql/mysql.conf.d/mysqld.cnf\n - service mysql restart\n - mysql -e \"GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'mysqlpassword';\"\n - mysql -e \"FLUSH PRIVILEGES;\"\n"
            },
            boot_config_settings={
                "deployment_fail_on_cloud_config_runtime_error": True,
                "phone_home_fail_on_timeout": False,
                "phone_home_should_wait": True,
                "phone_home_timeout_seconds": 100,
            },
            constraints=[
                {
                    "expression": "ha:strong",
                    "mandatory": True,
                }
            ],
            custom_properties={"foo": "string"},
            deployment_id="123e4567-e89b-12d3-a456-426655440000",
            description="description",
            disks=[
                {
                    "block_device_id": "1298765",
                    "description": "description",
                    "disk_attachment_properties": {
                        "scsiController": "SCSI_Controller_0",
                        "unitNumber": "2",
                    },
                    "name": "name",
                    "scsi_controller": "SCSI_Controller_0, SCSI_Controller_1, SCSI_Controller_2, SCSI_Controller_3",
                    "unit_number": "0",
                }
            ],
            image_disk_constraints=[
                {
                    "expression": "environment:prod",
                    "mandatory": True,
                },
                {
                    "expression": "pci",
                    "mandatory": True,
                },
            ],
            machine_count=3,
            nics=[
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
            remote_access={
                "authentication": "publicPrivateKey",
                "key_pair": "keyPair",
                "password": "password",
                "skip_user_creation": True,
                "ssh_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCu74dLkAGGYIgNuszEAM0HaS2Y6boTPw+HqsFmtPSOpxPQoosws/OWGZlW1uue6Y4lIvdRqZOaLK+2di5512etY67ZwFHc5h1kx4az433DsnoZhIzXEKKI+EXfH/w72CIyG/uVhIzmA4FvRVQKXinE1vaVen6v1CBQEZibx9RXrVRP1VRibsKFRXYxywNEl1VtPK7KaxCEYO9IXi4SKVulSAhOVequwjlo5E8bKNT61/g/YyMvwCbaTTPPeCpS/7i+JHYY3QZ8fQY/Syn+bOFpKCCHl+7VpsL8gjWe6fI4bUp6KUiW7ZkQpL/47rxawKnRMKKEU9P0ICp3RRB39lXT",
                "username": "username",
            },
            salt_configuration={
                "additional_auth_params": {"foo": "string"},
                "additional_minion_params": {"foo": "string"},
                "installer_file_name": "installerFileName",
                "master_id": "masterId",
                "minion_id": "minionId",
                "pillar_environment": "pillarEnvironment",
                "salt_environment": "saltEnvironment",
                "state_files": ["string"],
                "variables": {"foo": "string"},
            },
            tags=[
                {
                    "key": "ownedBy",
                    "value": "Rainpole",
                }
            ],
        )
        assert_matches_type(RequestTracker, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.with_raw_response.create(
            flavor="small, medium, large",
            flavor_ref="t2.micro",
            image="vmware-gold-master, ubuntu-latest, rhel-compliant, windows",
            image_ref="ami-f6795a8c",
            name="name",
            project_id="e058",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        machine = response.parse()
        assert_matches_type(RequestTracker, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: VraIaas) -> None:
        with client.iaas.api.machines.with_streaming_response.create(
            flavor="small, medium, large",
            flavor_ref="t2.micro",
            image="vmware-gold-master, ubuntu-latest, rhel-compliant, windows",
            image_ref="ami-f6795a8c",
            name="name",
            project_id="e058",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            machine = response.parse()
            assert_matches_type(RequestTracker, machine, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: VraIaas) -> None:
        machine = client.iaas.api.machines.retrieve(
            id="id",
        )
        assert_matches_type(Machine, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: VraIaas) -> None:
        machine = client.iaas.api.machines.retrieve(
            id="id",
            select="$select",
            api_version="apiVersion",
        )
        assert_matches_type(Machine, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        machine = response.parse()
        assert_matches_type(Machine, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: VraIaas) -> None:
        with client.iaas.api.machines.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            machine = response.parse()
            assert_matches_type(Machine, machine, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.machines.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: VraIaas) -> None:
        machine = client.iaas.api.machines.update(
            id="id",
        )
        assert_matches_type(Machine, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: VraIaas) -> None:
        machine = client.iaas.api.machines.update(
            id="id",
            api_version="apiVersion",
            boot_config={
                "content": "#cloud-config\nrepo_update: true\nrepo_upgrade: all\n\npackages:\n - mysql-server\n\nruncmd:\n - sed -e '/bind-address/ s/^#*/#/' -i /etc/mysql/mysql.conf.d/mysqld.cnf\n - service mysql restart\n - mysql -e \"GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'mysqlpassword';\"\n - mysql -e \"FLUSH PRIVILEGES;\"\n"
            },
            custom_properties={"foo": "string"},
            description="description",
            tags=[
                {
                    "key": "ownedBy",
                    "value": "Rainpole",
                }
            ],
        )
        assert_matches_type(Machine, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        machine = response.parse()
        assert_matches_type(Machine, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: VraIaas) -> None:
        with client.iaas.api.machines.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            machine = response.parse()
            assert_matches_type(Machine, machine, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.machines.with_raw_response.update(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: VraIaas) -> None:
        machine = client.iaas.api.machines.list()
        assert_matches_type(MachineListResponse, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: VraIaas) -> None:
        machine = client.iaas.api.machines.list(
            count=True,
            filter="$filter",
            select="$select",
            skip=0,
            top=0,
            api_version="apiVersion",
            skip_operation_links=True,
        )
        assert_matches_type(MachineListResponse, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        machine = response.parse()
        assert_matches_type(MachineListResponse, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: VraIaas) -> None:
        with client.iaas.api.machines.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            machine = response.parse()
            assert_matches_type(MachineListResponse, machine, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: VraIaas) -> None:
        machine = client.iaas.api.machines.delete(
            id="id",
        )
        assert_matches_type(RequestTracker, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: VraIaas) -> None:
        machine = client.iaas.api.machines.delete(
            id="id",
            api_version="apiVersion",
            force_delete=True,
        )
        assert_matches_type(RequestTracker, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: VraIaas) -> None:
        response = client.iaas.api.machines.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        machine = response.parse()
        assert_matches_type(RequestTracker, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: VraIaas) -> None:
        with client.iaas.api.machines.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            machine = response.parse()
            assert_matches_type(RequestTracker, machine, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: VraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.iaas.api.machines.with_raw_response.delete(
                id="",
            )


class TestAsyncMachines:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncVraIaas) -> None:
        machine = await async_client.iaas.api.machines.create(
            flavor="small, medium, large",
            flavor_ref="t2.micro",
            image="vmware-gold-master, ubuntu-latest, rhel-compliant, windows",
            image_ref="ami-f6795a8c",
            name="name",
            project_id="e058",
        )
        assert_matches_type(RequestTracker, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncVraIaas) -> None:
        machine = await async_client.iaas.api.machines.create(
            flavor="small, medium, large",
            flavor_ref="t2.micro",
            image="vmware-gold-master, ubuntu-latest, rhel-compliant, windows",
            image_ref="ami-f6795a8c",
            name="name",
            project_id="e058",
            api_version="apiVersion",
            boot_config={
                "content": "#cloud-config\nrepo_update: true\nrepo_upgrade: all\n\npackages:\n - mysql-server\n\nruncmd:\n - sed -e '/bind-address/ s/^#*/#/' -i /etc/mysql/mysql.conf.d/mysqld.cnf\n - service mysql restart\n - mysql -e \"GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'mysqlpassword';\"\n - mysql -e \"FLUSH PRIVILEGES;\"\n"
            },
            boot_config_settings={
                "deployment_fail_on_cloud_config_runtime_error": True,
                "phone_home_fail_on_timeout": False,
                "phone_home_should_wait": True,
                "phone_home_timeout_seconds": 100,
            },
            constraints=[
                {
                    "expression": "ha:strong",
                    "mandatory": True,
                }
            ],
            custom_properties={"foo": "string"},
            deployment_id="123e4567-e89b-12d3-a456-426655440000",
            description="description",
            disks=[
                {
                    "block_device_id": "1298765",
                    "description": "description",
                    "disk_attachment_properties": {
                        "scsiController": "SCSI_Controller_0",
                        "unitNumber": "2",
                    },
                    "name": "name",
                    "scsi_controller": "SCSI_Controller_0, SCSI_Controller_1, SCSI_Controller_2, SCSI_Controller_3",
                    "unit_number": "0",
                }
            ],
            image_disk_constraints=[
                {
                    "expression": "environment:prod",
                    "mandatory": True,
                },
                {
                    "expression": "pci",
                    "mandatory": True,
                },
            ],
            machine_count=3,
            nics=[
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
            remote_access={
                "authentication": "publicPrivateKey",
                "key_pair": "keyPair",
                "password": "password",
                "skip_user_creation": True,
                "ssh_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCu74dLkAGGYIgNuszEAM0HaS2Y6boTPw+HqsFmtPSOpxPQoosws/OWGZlW1uue6Y4lIvdRqZOaLK+2di5512etY67ZwFHc5h1kx4az433DsnoZhIzXEKKI+EXfH/w72CIyG/uVhIzmA4FvRVQKXinE1vaVen6v1CBQEZibx9RXrVRP1VRibsKFRXYxywNEl1VtPK7KaxCEYO9IXi4SKVulSAhOVequwjlo5E8bKNT61/g/YyMvwCbaTTPPeCpS/7i+JHYY3QZ8fQY/Syn+bOFpKCCHl+7VpsL8gjWe6fI4bUp6KUiW7ZkQpL/47rxawKnRMKKEU9P0ICp3RRB39lXT",
                "username": "username",
            },
            salt_configuration={
                "additional_auth_params": {"foo": "string"},
                "additional_minion_params": {"foo": "string"},
                "installer_file_name": "installerFileName",
                "master_id": "masterId",
                "minion_id": "minionId",
                "pillar_environment": "pillarEnvironment",
                "salt_environment": "saltEnvironment",
                "state_files": ["string"],
                "variables": {"foo": "string"},
            },
            tags=[
                {
                    "key": "ownedBy",
                    "value": "Rainpole",
                }
            ],
        )
        assert_matches_type(RequestTracker, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.with_raw_response.create(
            flavor="small, medium, large",
            flavor_ref="t2.micro",
            image="vmware-gold-master, ubuntu-latest, rhel-compliant, windows",
            image_ref="ami-f6795a8c",
            name="name",
            project_id="e058",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        machine = await response.parse()
        assert_matches_type(RequestTracker, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.with_streaming_response.create(
            flavor="small, medium, large",
            flavor_ref="t2.micro",
            image="vmware-gold-master, ubuntu-latest, rhel-compliant, windows",
            image_ref="ami-f6795a8c",
            name="name",
            project_id="e058",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            machine = await response.parse()
            assert_matches_type(RequestTracker, machine, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVraIaas) -> None:
        machine = await async_client.iaas.api.machines.retrieve(
            id="id",
        )
        assert_matches_type(Machine, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncVraIaas) -> None:
        machine = await async_client.iaas.api.machines.retrieve(
            id="id",
            select="$select",
            api_version="apiVersion",
        )
        assert_matches_type(Machine, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        machine = await response.parse()
        assert_matches_type(Machine, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            machine = await response.parse()
            assert_matches_type(Machine, machine, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.machines.with_raw_response.retrieve(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncVraIaas) -> None:
        machine = await async_client.iaas.api.machines.update(
            id="id",
        )
        assert_matches_type(Machine, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncVraIaas) -> None:
        machine = await async_client.iaas.api.machines.update(
            id="id",
            api_version="apiVersion",
            boot_config={
                "content": "#cloud-config\nrepo_update: true\nrepo_upgrade: all\n\npackages:\n - mysql-server\n\nruncmd:\n - sed -e '/bind-address/ s/^#*/#/' -i /etc/mysql/mysql.conf.d/mysqld.cnf\n - service mysql restart\n - mysql -e \"GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'mysqlpassword';\"\n - mysql -e \"FLUSH PRIVILEGES;\"\n"
            },
            custom_properties={"foo": "string"},
            description="description",
            tags=[
                {
                    "key": "ownedBy",
                    "value": "Rainpole",
                }
            ],
        )
        assert_matches_type(Machine, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        machine = await response.parse()
        assert_matches_type(Machine, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            machine = await response.parse()
            assert_matches_type(Machine, machine, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.machines.with_raw_response.update(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncVraIaas) -> None:
        machine = await async_client.iaas.api.machines.list()
        assert_matches_type(MachineListResponse, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncVraIaas) -> None:
        machine = await async_client.iaas.api.machines.list(
            count=True,
            filter="$filter",
            select="$select",
            skip=0,
            top=0,
            api_version="apiVersion",
            skip_operation_links=True,
        )
        assert_matches_type(MachineListResponse, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        machine = await response.parse()
        assert_matches_type(MachineListResponse, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            machine = await response.parse()
            assert_matches_type(MachineListResponse, machine, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncVraIaas) -> None:
        machine = await async_client.iaas.api.machines.delete(
            id="id",
        )
        assert_matches_type(RequestTracker, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncVraIaas) -> None:
        machine = await async_client.iaas.api.machines.delete(
            id="id",
            api_version="apiVersion",
            force_delete=True,
        )
        assert_matches_type(RequestTracker, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncVraIaas) -> None:
        response = await async_client.iaas.api.machines.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        machine = await response.parse()
        assert_matches_type(RequestTracker, machine, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncVraIaas) -> None:
        async with async_client.iaas.api.machines.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            machine = await response.parse()
            assert_matches_type(RequestTracker, machine, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncVraIaas) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.iaas.api.machines.with_raw_response.delete(
                id="",
            )
