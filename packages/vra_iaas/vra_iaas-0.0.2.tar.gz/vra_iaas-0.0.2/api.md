# Iaas

## API

Types:

```python
from vra_iaas.types.iaas import (
    APIRetrieveResponse,
    APILoginResponse,
    APIRetrieveAboutResponse,
    APIRetrieveEventLogsResponse,
    APIRetrieveFabricAwsVolumeTypesResponse,
    APIRetrieveFabricAzureDiskEncryptionSetsResponse,
    APIRetrieveFabricFlavorsResponse,
    APIRetrieveFlavorsResponse,
    APIRetrieveFoldersResponse,
    APIRetrieveImagesResponse,
    APIRetrieveRequestGraphResponse,
)
```

Methods:

- <code title="get /iaas/api/certificates/{id}">client.iaas.api.<a href="./src/vra_iaas/resources/iaas/api/api.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api_retrieve_response.py">APIRetrieveResponse</a></code>
- <code title="post /iaas/api/login">client.iaas.api.<a href="./src/vra_iaas/resources/iaas/api/api.py">login</a>(\*\*<a href="src/vra_iaas/types/iaas/api_login_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api_login_response.py">APILoginResponse</a></code>
- <code title="get /iaas/api/about">client.iaas.api.<a href="./src/vra_iaas/resources/iaas/api/api.py">retrieve_about</a>() -> <a href="./src/vra_iaas/types/iaas/api_retrieve_about_response.py">APIRetrieveAboutResponse</a></code>
- <code title="get /iaas/api/event-logs">client.iaas.api.<a href="./src/vra_iaas/resources/iaas/api/api.py">retrieve_event_logs</a>(\*\*<a href="src/vra_iaas/types/iaas/api_retrieve_event_logs_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api_retrieve_event_logs_response.py">APIRetrieveEventLogsResponse</a></code>
- <code title="get /iaas/api/fabric-aws-volume-types">client.iaas.api.<a href="./src/vra_iaas/resources/iaas/api/api.py">retrieve_fabric_aws_volume_types</a>(\*\*<a href="src/vra_iaas/types/iaas/api_retrieve_fabric_aws_volume_types_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api_retrieve_fabric_aws_volume_types_response.py">APIRetrieveFabricAwsVolumeTypesResponse</a></code>
- <code title="get /iaas/api/fabric-azure-disk-encryption-sets">client.iaas.api.<a href="./src/vra_iaas/resources/iaas/api/api.py">retrieve_fabric_azure_disk_encryption_sets</a>(\*\*<a href="src/vra_iaas/types/iaas/api_retrieve_fabric_azure_disk_encryption_sets_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api_retrieve_fabric_azure_disk_encryption_sets_response.py">APIRetrieveFabricAzureDiskEncryptionSetsResponse</a></code>
- <code title="get /iaas/api/fabric-flavors">client.iaas.api.<a href="./src/vra_iaas/resources/iaas/api/api.py">retrieve_fabric_flavors</a>(\*\*<a href="src/vra_iaas/types/iaas/api_retrieve_fabric_flavors_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api_retrieve_fabric_flavors_response.py">APIRetrieveFabricFlavorsResponse</a></code>
- <code title="get /iaas/api/flavors">client.iaas.api.<a href="./src/vra_iaas/resources/iaas/api/api.py">retrieve_flavors</a>(\*\*<a href="src/vra_iaas/types/iaas/api_retrieve_flavors_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api_retrieve_flavors_response.py">APIRetrieveFlavorsResponse</a></code>
- <code title="get /iaas/api/folders">client.iaas.api.<a href="./src/vra_iaas/resources/iaas/api/api.py">retrieve_folders</a>(\*\*<a href="src/vra_iaas/types/iaas/api_retrieve_folders_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api_retrieve_folders_response.py">APIRetrieveFoldersResponse</a></code>
- <code title="get /iaas/api/images">client.iaas.api.<a href="./src/vra_iaas/resources/iaas/api/api.py">retrieve_images</a>(\*\*<a href="src/vra_iaas/types/iaas/api_retrieve_images_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api_retrieve_images_response.py">APIRetrieveImagesResponse</a></code>
- <code title="get /iaas/api/request-graph">client.iaas.api.<a href="./src/vra_iaas/resources/iaas/api/api.py">retrieve_request_graph</a>(\*\*<a href="src/vra_iaas/types/iaas/api_retrieve_request_graph_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api_retrieve_request_graph_response.py">APIRetrieveRequestGraphResponse</a></code>

### StorageProfiles

Types:

```python
from vra_iaas.types.iaas.api import (
    StorageProfile,
    StorageProfileAssociations,
    StorageProfileSpecification,
    StorageProfileRetrieveStorageProfilesResponse,
)
```

Methods:

- <code title="get /iaas/api/storage-profiles/{id}">client.iaas.api.storage_profiles.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles/storage_profiles.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/storage_profile_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/storage_profile.py">StorageProfile</a></code>
- <code title="put /iaas/api/storage-profiles/{id}">client.iaas.api.storage_profiles.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles/storage_profiles.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/storage_profile_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/storage_profile.py">StorageProfile</a></code>
- <code title="delete /iaas/api/storage-profiles/{id}">client.iaas.api.storage_profiles.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles/storage_profiles.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/storage_profile_delete_params.py">params</a>) -> None</code>
- <code title="get /iaas/api/storage-profiles">client.iaas.api.storage_profiles.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles/storage_profiles.py">retrieve_storage_profiles</a>(\*\*<a href="src/vra_iaas/types/iaas/api/storage_profile_retrieve_storage_profiles_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/storage_profile_retrieve_storage_profiles_response.py">StorageProfileRetrieveStorageProfilesResponse</a></code>
- <code title="post /iaas/api/storage-profiles">client.iaas.api.storage_profiles.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles/storage_profiles.py">storage_profiles</a>(\*\*<a href="src/vra_iaas/types/iaas/api/storage_profile_storage_profiles_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/storage_profile.py">StorageProfile</a></code>

#### StorageProfileAssociations

Types:

```python
from vra_iaas.types.iaas.api.storage_profiles import (
    StorageProfileAssociationRetrieveStorageProfileAssociationsResponse,
    StorageProfileAssociationUpdateStorageProfileAssociationsResponse,
)
```

Methods:

- <code title="get /iaas/api/storage-profiles/{id}/storage-profile-associations">client.iaas.api.storage_profiles.storage_profile_associations.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles/storage_profile_associations.py">retrieve_storage_profile_associations</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles/storage_profile_association_retrieve_storage_profile_associations_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/storage_profiles/storage_profile_association_retrieve_storage_profile_associations_response.py">StorageProfileAssociationRetrieveStorageProfileAssociationsResponse</a></code>
- <code title="patch /iaas/api/storage-profiles/{id}/storage-profile-associations">client.iaas.api.storage_profiles.storage_profile_associations.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles/storage_profile_associations.py">update_storage_profile_associations</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles/storage_profile_association_update_storage_profile_associations_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/storage_profiles/storage_profile_association_update_storage_profile_associations_response.py">StorageProfileAssociationUpdateStorageProfileAssociationsResponse</a></code>

### Projects

Types:

```python
from vra_iaas.types.iaas.api import Project, ProjectSpecification, User, ProjectListResponse
```

Methods:

- <code title="post /iaas/api/projects">client.iaas.api.projects.<a href="./src/vra_iaas/resources/iaas/api/projects/projects.py">create</a>(\*\*<a href="src/vra_iaas/types/iaas/api/project_create_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/project.py">Project</a></code>
- <code title="get /iaas/api/projects/{id}">client.iaas.api.projects.<a href="./src/vra_iaas/resources/iaas/api/projects/projects.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/project_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/project.py">Project</a></code>
- <code title="patch /iaas/api/projects/{id}">client.iaas.api.projects.<a href="./src/vra_iaas/resources/iaas/api/projects/projects.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/project_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/project.py">Project</a></code>
- <code title="get /iaas/api/projects">client.iaas.api.projects.<a href="./src/vra_iaas/resources/iaas/api/projects/projects.py">list</a>(\*\*<a href="src/vra_iaas/types/iaas/api/project_list_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/project_list_response.py">ProjectListResponse</a></code>
- <code title="delete /iaas/api/projects/{id}">client.iaas.api.projects.<a href="./src/vra_iaas/resources/iaas/api/projects/projects.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/project_delete_params.py">params</a>) -> None</code>

#### Zones

Types:

```python
from vra_iaas.types.iaas.api.projects import (
    RequestTracker,
    ZoneAssignment,
    ZoneAssignmentSpecification,
    ZoneListResponse,
)
```

Methods:

- <code title="put /iaas/api/projects/{id}/zones">client.iaas.api.projects.zones.<a href="./src/vra_iaas/resources/iaas/api/projects/zones.py">create</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/projects/zone_create_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/projects/{id}/zones">client.iaas.api.projects.zones.<a href="./src/vra_iaas/resources/iaas/api/projects/zones.py">list</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/projects/zone_list_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/zone_list_response.py">ZoneListResponse</a></code>

#### ResourceMetadata

Types:

```python
from vra_iaas.types.iaas.api.projects import ResourceMetadataRetrieveResourceMetadataResponse
```

Methods:

- <code title="get /iaas/api/projects/{id}/resource-metadata">client.iaas.api.projects.resource_metadata.<a href="./src/vra_iaas/resources/iaas/api/projects/resource_metadata.py">retrieve_resource_metadata</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/projects/resource_metadata_retrieve_resource_metadata_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/resource_metadata_retrieve_resource_metadata_response.py">ResourceMetadataRetrieveResourceMetadataResponse</a></code>
- <code title="patch /iaas/api/projects/{id}/resource-metadata">client.iaas.api.projects.resource_metadata.<a href="./src/vra_iaas/resources/iaas/api/projects/resource_metadata.py">update_resource_metadata</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/projects/resource_metadata_update_resource_metadata_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/project.py">Project</a></code>

### Naming

Types:

```python
from vra_iaas.types.iaas.api import (
    CustomNaming,
    CustomNamingModel,
    CustomNamingProject,
    NamingListResponse,
)
```

Methods:

- <code title="post /iaas/api/naming">client.iaas.api.naming.<a href="./src/vra_iaas/resources/iaas/api/naming.py">create</a>(\*\*<a href="src/vra_iaas/types/iaas/api/naming_create_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/custom_naming.py">CustomNaming</a></code>
- <code title="get /iaas/api/naming/projectId/{id}">client.iaas.api.naming.<a href="./src/vra_iaas/resources/iaas/api/naming.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/naming_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/custom_naming.py">CustomNaming</a></code>
- <code title="get /iaas/api/naming">client.iaas.api.naming.<a href="./src/vra_iaas/resources/iaas/api/naming.py">list</a>(\*\*<a href="src/vra_iaas/types/iaas/api/naming_list_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/naming_list_response.py">NamingListResponse</a></code>
- <code title="delete /iaas/api/naming/{id}">client.iaas.api.naming.<a href="./src/vra_iaas/resources/iaas/api/naming.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/naming_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/custom_naming.py">CustomNaming</a></code>

### Zones

Types:

```python
from vra_iaas.types.iaas.api import FabricComputeResult, Zone, ZoneSpecification, ZoneListResponse
```

Methods:

- <code title="post /iaas/api/zones">client.iaas.api.zones.<a href="./src/vra_iaas/resources/iaas/api/zones.py">create</a>(\*\*<a href="src/vra_iaas/types/iaas/api/zone_create_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/zone.py">Zone</a></code>
- <code title="get /iaas/api/zones/{id}">client.iaas.api.zones.<a href="./src/vra_iaas/resources/iaas/api/zones.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/zone_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/zone.py">Zone</a></code>
- <code title="patch /iaas/api/zones/{id}">client.iaas.api.zones.<a href="./src/vra_iaas/resources/iaas/api/zones.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/zone_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/zone.py">Zone</a></code>
- <code title="get /iaas/api/zones">client.iaas.api.zones.<a href="./src/vra_iaas/resources/iaas/api/zones.py">list</a>(\*\*<a href="src/vra_iaas/types/iaas/api/zone_list_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/zone_list_response.py">ZoneListResponse</a></code>
- <code title="delete /iaas/api/zones/{id}">client.iaas.api.zones.<a href="./src/vra_iaas/resources/iaas/api/zones.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/zone_delete_params.py">params</a>) -> None</code>
- <code title="get /iaas/api/zones/{id}/computes">client.iaas.api.zones.<a href="./src/vra_iaas/resources/iaas/api/zones.py">retrieve_computes</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/zone_retrieve_computes_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_compute_result.py">FabricComputeResult</a></code>

### Tags

Types:

```python
from vra_iaas.types.iaas.api import Tag, TagListResponse
```

Methods:

- <code title="post /iaas/api/tags">client.iaas.api.tags.<a href="./src/vra_iaas/resources/iaas/api/tags.py">create</a>(\*\*<a href="src/vra_iaas/types/iaas/api/tag_create_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/tag.py">Tag</a></code>
- <code title="get /iaas/api/tags">client.iaas.api.tags.<a href="./src/vra_iaas/resources/iaas/api/tags.py">list</a>(\*\*<a href="src/vra_iaas/types/iaas/api/tag_list_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/tag_list_response.py">TagListResponse</a></code>
- <code title="delete /iaas/api/tags/{id}">client.iaas.api.tags.<a href="./src/vra_iaas/resources/iaas/api/tags.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/tag_delete_params.py">params</a>) -> None</code>
- <code title="post /iaas/api/tags/tags-usage">client.iaas.api.tags.<a href="./src/vra_iaas/resources/iaas/api/tags.py">tags_usage</a>(\*\*<a href="src/vra_iaas/types/iaas/api/tag_tags_usage_params.py">params</a>) -> None</code>

### StorageProfilesVsphere

Types:

```python
from vra_iaas.types.iaas.api import (
    StorageProfileVsphereSpecification,
    VsphereStorageProfile,
    StorageProfilesVsphereRetrieveStorageProfilesVsphereResponse,
)
```

Methods:

- <code title="get /iaas/api/storage-profiles-vsphere/{id}">client.iaas.api.storage_profiles_vsphere.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles_vsphere.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles_vsphere_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/vsphere_storage_profile.py">VsphereStorageProfile</a></code>
- <code title="patch /iaas/api/storage-profiles-vsphere/{id}">client.iaas.api.storage_profiles_vsphere.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles_vsphere.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles_vsphere_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/vsphere_storage_profile.py">VsphereStorageProfile</a></code>
- <code title="delete /iaas/api/storage-profiles-vsphere/{id}">client.iaas.api.storage_profiles_vsphere.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles_vsphere.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles_vsphere_delete_params.py">params</a>) -> None</code>
- <code title="get /iaas/api/storage-profiles-vsphere">client.iaas.api.storage_profiles_vsphere.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles_vsphere.py">retrieve_storage_profiles_vsphere</a>(\*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles_vsphere_retrieve_storage_profiles_vsphere_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/storage_profiles_vsphere_retrieve_storage_profiles_vsphere_response.py">StorageProfilesVsphereRetrieveStorageProfilesVsphereResponse</a></code>
- <code title="post /iaas/api/storage-profiles-vsphere">client.iaas.api.storage_profiles_vsphere.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles_vsphere.py">storage_profiles_vsphere</a>(\*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles_vsphere_storage_profiles_vsphere_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/vsphere_storage_profile.py">VsphereStorageProfile</a></code>

### StorageProfilesGcp

Types:

```python
from vra_iaas.types.iaas.api import (
    GcpStorageProfile,
    StorageProfileGcpSpecification,
    StorageProfilesGcpRetrieveStorageProfilesGcpResponse,
)
```

Methods:

- <code title="get /iaas/api/storage-profiles-gcp/{id}">client.iaas.api.storage_profiles_gcp.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles_gcp.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles_gcp_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/gcp_storage_profile.py">GcpStorageProfile</a></code>
- <code title="patch /iaas/api/storage-profiles-gcp/{id}">client.iaas.api.storage_profiles_gcp.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles_gcp.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles_gcp_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/gcp_storage_profile.py">GcpStorageProfile</a></code>
- <code title="delete /iaas/api/storage-profiles-gcp/{id}">client.iaas.api.storage_profiles_gcp.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles_gcp.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles_gcp_delete_params.py">params</a>) -> None</code>
- <code title="get /iaas/api/storage-profiles-gcp">client.iaas.api.storage_profiles_gcp.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles_gcp.py">retrieve_storage_profiles_gcp</a>(\*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles_gcp_retrieve_storage_profiles_gcp_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/storage_profiles_gcp_retrieve_storage_profiles_gcp_response.py">StorageProfilesGcpRetrieveStorageProfilesGcpResponse</a></code>
- <code title="post /iaas/api/storage-profiles-gcp">client.iaas.api.storage_profiles_gcp.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles_gcp.py">storage_profiles_gcp</a>(\*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles_gcp_storage_profiles_gcp_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/gcp_storage_profile.py">GcpStorageProfile</a></code>

### StorageProfilesAzure

Types:

```python
from vra_iaas.types.iaas.api import (
    AzureStorageProfile,
    StorageProfileAzureSpecification,
    StorageProfilesAzureRetrieveStorageProfilesAzureResponse,
)
```

Methods:

- <code title="get /iaas/api/storage-profiles-azure/{id}">client.iaas.api.storage_profiles_azure.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles_azure.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles_azure_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/azure_storage_profile.py">AzureStorageProfile</a></code>
- <code title="patch /iaas/api/storage-profiles-azure/{id}">client.iaas.api.storage_profiles_azure.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles_azure.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles_azure_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/azure_storage_profile.py">AzureStorageProfile</a></code>
- <code title="delete /iaas/api/storage-profiles-azure/{id}">client.iaas.api.storage_profiles_azure.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles_azure.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles_azure_delete_params.py">params</a>) -> None</code>
- <code title="get /iaas/api/storage-profiles-azure">client.iaas.api.storage_profiles_azure.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles_azure.py">retrieve_storage_profiles_azure</a>(\*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles_azure_retrieve_storage_profiles_azure_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/storage_profiles_azure_retrieve_storage_profiles_azure_response.py">StorageProfilesAzureRetrieveStorageProfilesAzureResponse</a></code>
- <code title="post /iaas/api/storage-profiles-azure">client.iaas.api.storage_profiles_azure.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles_azure.py">storage_profiles_azure</a>(\*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles_azure_storage_profiles_azure_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/azure_storage_profile.py">AzureStorageProfile</a></code>

### StorageProfilesAws

Types:

```python
from vra_iaas.types.iaas.api import (
    AwsStorageProfile,
    StorageProfileAwsSpecification,
    StorageProfilesAwRetrieveStorageProfilesAwsResponse,
)
```

Methods:

- <code title="get /iaas/api/storage-profiles-aws/{id}">client.iaas.api.storage_profiles_aws.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles_aws.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles_aw_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/aws_storage_profile.py">AwsStorageProfile</a></code>
- <code title="patch /iaas/api/storage-profiles-aws/{id}">client.iaas.api.storage_profiles_aws.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles_aws.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles_aw_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/aws_storage_profile.py">AwsStorageProfile</a></code>
- <code title="delete /iaas/api/storage-profiles-aws/{id}">client.iaas.api.storage_profiles_aws.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles_aws.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles_aw_delete_params.py">params</a>) -> None</code>
- <code title="get /iaas/api/storage-profiles-aws">client.iaas.api.storage_profiles_aws.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles_aws.py">retrieve_storage_profiles_aws</a>(\*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles_aw_retrieve_storage_profiles_aws_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/storage_profiles_aw_retrieve_storage_profiles_aws_response.py">StorageProfilesAwRetrieveStorageProfilesAwsResponse</a></code>
- <code title="post /iaas/api/storage-profiles-aws">client.iaas.api.storage_profiles_aws.<a href="./src/vra_iaas/resources/iaas/api/storage_profiles_aws.py">storage_profiles_aws</a>(\*\*<a href="src/vra_iaas/types/iaas/api/storage_profiles_aw_storage_profiles_aws_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/aws_storage_profile.py">AwsStorageProfile</a></code>

### SecurityGroups

Types:

```python
from vra_iaas.types.iaas.api import SecurityGroup, SecurityGroupRetrieveSecurityGroupsResponse
```

Methods:

- <code title="get /iaas/api/security-groups/{id}">client.iaas.api.security_groups.<a href="./src/vra_iaas/resources/iaas/api/security_groups/security_groups.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/security_group_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/security_group.py">SecurityGroup</a></code>
- <code title="patch /iaas/api/security-groups/{id}">client.iaas.api.security_groups.<a href="./src/vra_iaas/resources/iaas/api/security_groups/security_groups.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/security_group_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/security_group.py">SecurityGroup</a></code>
- <code title="delete /iaas/api/security-groups/{id}">client.iaas.api.security_groups.<a href="./src/vra_iaas/resources/iaas/api/security_groups/security_groups.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/security_group_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/security-groups">client.iaas.api.security_groups.<a href="./src/vra_iaas/resources/iaas/api/security_groups/security_groups.py">retrieve_security_groups</a>(\*\*<a href="src/vra_iaas/types/iaas/api/security_group_retrieve_security_groups_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/security_group_retrieve_security_groups_response.py">SecurityGroupRetrieveSecurityGroupsResponse</a></code>
- <code title="post /iaas/api/security-groups">client.iaas.api.security_groups.<a href="./src/vra_iaas/resources/iaas/api/security_groups/security_groups.py">security_groups</a>(\*\*<a href="src/vra_iaas/types/iaas/api/security_group_security_groups_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>

#### Operations

Types:

```python
from vra_iaas.types.iaas.api.security_groups import Rule, SecurityGroupSpecification
```

Methods:

- <code title="post /iaas/api/security-groups/{id}/operations/reconfigure">client.iaas.api.security_groups.operations.<a href="./src/vra_iaas/resources/iaas/api/security_groups/operations.py">reconfigure</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/security_groups/operation_reconfigure_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>

### Networks

Types:

```python
from vra_iaas.types.iaas.api import Network, PlacementConstraint, NetworkListResponse
```

Methods:

- <code title="post /iaas/api/networks">client.iaas.api.networks.<a href="./src/vra_iaas/resources/iaas/api/networks.py">create</a>(\*\*<a href="src/vra_iaas/types/iaas/api/network_create_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/networks/{id}">client.iaas.api.networks.<a href="./src/vra_iaas/resources/iaas/api/networks.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/network_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/network.py">Network</a></code>
- <code title="get /iaas/api/networks">client.iaas.api.networks.<a href="./src/vra_iaas/resources/iaas/api/networks.py">list</a>(\*\*<a href="src/vra_iaas/types/iaas/api/network_list_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/network_list_response.py">NetworkListResponse</a></code>
- <code title="delete /iaas/api/networks/{id}">client.iaas.api.networks.<a href="./src/vra_iaas/resources/iaas/api/networks.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/network_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/networks/{id}/network-ip-ranges">client.iaas.api.networks.<a href="./src/vra_iaas/resources/iaas/api/networks.py">retrieve_network_ip_ranges</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/network_retrieve_network_ip_ranges_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/network.py">Network</a></code>

### NetworkProfiles

Types:

```python
from vra_iaas.types.iaas.api import (
    NetworkProfile,
    NetworkProfileSpecification,
    NetworkProfileRetrieveNetworkProfilesResponse,
)
```

Methods:

- <code title="get /iaas/api/network-profiles/{id}">client.iaas.api.network_profiles.<a href="./src/vra_iaas/resources/iaas/api/network_profiles.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/network_profile_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/network_profile.py">NetworkProfile</a></code>
- <code title="patch /iaas/api/network-profiles/{id}">client.iaas.api.network_profiles.<a href="./src/vra_iaas/resources/iaas/api/network_profiles.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/network_profile_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/network_profile.py">NetworkProfile</a></code>
- <code title="delete /iaas/api/network-profiles/{id}">client.iaas.api.network_profiles.<a href="./src/vra_iaas/resources/iaas/api/network_profiles.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/network_profile_delete_params.py">params</a>) -> None</code>
- <code title="post /iaas/api/network-profiles">client.iaas.api.network_profiles.<a href="./src/vra_iaas/resources/iaas/api/network_profiles.py">network_profiles</a>(\*\*<a href="src/vra_iaas/types/iaas/api/network_profile_network_profiles_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/network_profile.py">NetworkProfile</a></code>
- <code title="get /iaas/api/network-profiles">client.iaas.api.network_profiles.<a href="./src/vra_iaas/resources/iaas/api/network_profiles.py">retrieve_network_profiles</a>(\*\*<a href="src/vra_iaas/types/iaas/api/network_profile_retrieve_network_profiles_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/network_profile_retrieve_network_profiles_response.py">NetworkProfileRetrieveNetworkProfilesResponse</a></code>

### NetworkIPRanges

Types:

```python
from vra_iaas.types.iaas.api import (
    NetworkIPRangeBase,
    NetworkIPRangeSpecification,
    NetworkIPRangeRetrieveResponse,
    NetworkIPRangeRetrieveNetworkIPRangesResponse,
)
```

Methods:

- <code title="get /iaas/api/network-ip-ranges/{id}">client.iaas.api.network_ip_ranges.<a href="./src/vra_iaas/resources/iaas/api/network_ip_ranges/network_ip_ranges.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/network_ip_range_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/network_ip_range_retrieve_response.py">NetworkIPRangeRetrieveResponse</a></code>
- <code title="patch /iaas/api/network-ip-ranges/{id}">client.iaas.api.network_ip_ranges.<a href="./src/vra_iaas/resources/iaas/api/network_ip_ranges/network_ip_ranges.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/network_ip_range_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/network_ip_range_base.py">NetworkIPRangeBase</a></code>
- <code title="delete /iaas/api/network-ip-ranges/{id}">client.iaas.api.network_ip_ranges.<a href="./src/vra_iaas/resources/iaas/api/network_ip_ranges/network_ip_ranges.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/network_ip_range_delete_params.py">params</a>) -> None</code>
- <code title="post /iaas/api/network-ip-ranges">client.iaas.api.network_ip_ranges.<a href="./src/vra_iaas/resources/iaas/api/network_ip_ranges/network_ip_ranges.py">network_ip_ranges</a>(\*\*<a href="src/vra_iaas/types/iaas/api/network_ip_range_network_ip_ranges_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/network_ip_range_base.py">NetworkIPRangeBase</a></code>
- <code title="get /iaas/api/network-ip-ranges">client.iaas.api.network_ip_ranges.<a href="./src/vra_iaas/resources/iaas/api/network_ip_ranges/network_ip_ranges.py">retrieve_network_ip_ranges</a>(\*\*<a href="src/vra_iaas/types/iaas/api/network_ip_range_retrieve_network_ip_ranges_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/network_ip_range_retrieve_network_ip_ranges_response.py">NetworkIPRangeRetrieveNetworkIPRangesResponse</a></code>

#### UnregisteredIPAddresses

Types:

```python
from vra_iaas.types.iaas.api.network_ip_ranges import IPAddressReleaseSpecification
```

Methods:

- <code title="post /iaas/api/network-ip-ranges/{id}/unregistered-ip-addresses/release">client.iaas.api.network_ip_ranges.unregistered_ip_addresses.<a href="./src/vra_iaas/resources/iaas/api/network_ip_ranges/unregistered_ip_addresses.py">release</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/network_ip_ranges/unregistered_ip_address_release_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>

#### IPAddresses

Types:

```python
from vra_iaas.types.iaas.api.network_ip_ranges import (
    NetworkIPAddress,
    IPAddressRetrieveIPAddressesResponse,
)
```

Methods:

- <code title="get /iaas/api/network-ip-ranges/{networkIPRangeId}/ip-addresses/{ipAddressId}">client.iaas.api.network_ip_ranges.ip_addresses.<a href="./src/vra_iaas/resources/iaas/api/network_ip_ranges/ip_addresses.py">retrieve</a>(ip_address_id, \*, network_ip_range_id, \*\*<a href="src/vra_iaas/types/iaas/api/network_ip_ranges/ip_address_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/network_ip_ranges/network_ip_address.py">NetworkIPAddress</a></code>
- <code title="post /iaas/api/network-ip-ranges/{id}/ip-addresses/allocate">client.iaas.api.network_ip_ranges.ip_addresses.<a href="./src/vra_iaas/resources/iaas/api/network_ip_ranges/ip_addresses.py">allocate</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/network_ip_ranges/ip_address_allocate_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/network-ip-ranges/{id}/ip-addresses/release">client.iaas.api.network_ip_ranges.ip_addresses.<a href="./src/vra_iaas/resources/iaas/api/network_ip_ranges/ip_addresses.py">release</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/network_ip_ranges/ip_address_release_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/network-ip-ranges/{id}/ip-addresses">client.iaas.api.network_ip_ranges.ip_addresses.<a href="./src/vra_iaas/resources/iaas/api/network_ip_ranges/ip_addresses.py">retrieve_ip_addresses</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/network_ip_ranges/ip_address_retrieve_ip_addresses_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/network_ip_ranges/ip_address_retrieve_ip_addresses_response.py">IPAddressRetrieveIPAddressesResponse</a></code>

### Machines

Types:

```python
from vra_iaas.types.iaas.api import (
    Machine,
    MachineBootConfig,
    SaltConfiguration,
    MachineListResponse,
)
```

Methods:

- <code title="post /iaas/api/machines">client.iaas.api.machines.<a href="./src/vra_iaas/resources/iaas/api/machines/machines.py">create</a>(\*\*<a href="src/vra_iaas/types/iaas/api/machine_create_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/machines/{id}">client.iaas.api.machines.<a href="./src/vra_iaas/resources/iaas/api/machines/machines.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/machine_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/machine.py">Machine</a></code>
- <code title="patch /iaas/api/machines/{id}">client.iaas.api.machines.<a href="./src/vra_iaas/resources/iaas/api/machines/machines.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/machine_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/machine.py">Machine</a></code>
- <code title="get /iaas/api/machines">client.iaas.api.machines.<a href="./src/vra_iaas/resources/iaas/api/machines/machines.py">list</a>(\*\*<a href="src/vra_iaas/types/iaas/api/machine_list_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/machine_list_response.py">MachineListResponse</a></code>
- <code title="delete /iaas/api/machines/{id}">client.iaas.api.machines.<a href="./src/vra_iaas/resources/iaas/api/machines/machines.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/machine_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>

#### Operations

Types:

```python
from vra_iaas.types.iaas.api.machines import NetworkInterfaceSpecification
```

Methods:

- <code title="post /iaas/api/machines/{id}/operations/revert/{snapshotId}">client.iaas.api.machines.operations.<a href="./src/vra_iaas/resources/iaas/api/machines/operations.py">update</a>(snapshot_id, \*, id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/operation_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/machines/{id}/operations/change-security-groups">client.iaas.api.machines.operations.<a href="./src/vra_iaas/resources/iaas/api/machines/operations.py">change_security_groups</a>(path_id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/operation_change_security_groups_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/machines/{id}/operations/power-off">client.iaas.api.machines.operations.<a href="./src/vra_iaas/resources/iaas/api/machines/operations.py">power_off</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/operation_power_off_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/machines/{id}/operations/power-on">client.iaas.api.machines.operations.<a href="./src/vra_iaas/resources/iaas/api/machines/operations.py">power_on</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/operation_power_on_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/machines/{id}/operations/reboot">client.iaas.api.machines.operations.<a href="./src/vra_iaas/resources/iaas/api/machines/operations.py">reboot</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/operation_reboot_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/machines/{id}/operations/reset">client.iaas.api.machines.operations.<a href="./src/vra_iaas/resources/iaas/api/machines/operations.py">reset</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/operation_reset_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/machines/{id}/operations/resize">client.iaas.api.machines.operations.<a href="./src/vra_iaas/resources/iaas/api/machines/operations.py">resize</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/operation_resize_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/machines/{id}/operations/restart">client.iaas.api.machines.operations.<a href="./src/vra_iaas/resources/iaas/api/machines/operations.py">restart</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/operation_restart_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/machines/{id}/operations/shutdown">client.iaas.api.machines.operations.<a href="./src/vra_iaas/resources/iaas/api/machines/operations.py">shutdown</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/operation_shutdown_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/machines/{id}/operations/snapshots">client.iaas.api.machines.operations.<a href="./src/vra_iaas/resources/iaas/api/machines/operations.py">snapshots</a>(path_id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/operation_snapshots_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/machines/{id}/operations/suspend">client.iaas.api.machines.operations.<a href="./src/vra_iaas/resources/iaas/api/machines/operations.py">suspend</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/operation_suspend_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/machines/{id}/operations/unregister">client.iaas.api.machines.operations.<a href="./src/vra_iaas/resources/iaas/api/machines/operations.py">unregister</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/operation_unregister_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>

#### Disks

Types:

```python
from vra_iaas.types.iaas.api.machines import BlockDeviceResult, DiskAttachmentSpecification
```

Methods:

- <code title="post /iaas/api/machines/{id}/disks">client.iaas.api.machines.disks.<a href="./src/vra_iaas/resources/iaas/api/machines/disks.py">create</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/disk_create_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/machines/{id}/disks/{diskId}">client.iaas.api.machines.disks.<a href="./src/vra_iaas/resources/iaas/api/machines/disks.py">retrieve</a>(disk_id, \*, id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/disk_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/block_device.py">BlockDevice</a></code>
- <code title="get /iaas/api/machines/{id}/disks">client.iaas.api.machines.disks.<a href="./src/vra_iaas/resources/iaas/api/machines/disks.py">list</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/disk_list_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/machines/block_device_result.py">BlockDeviceResult</a></code>
- <code title="delete /iaas/api/machines/{id}/disks/{diskId}">client.iaas.api.machines.disks.<a href="./src/vra_iaas/resources/iaas/api/machines/disks.py">delete</a>(disk_id, \*, id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/disk_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>

#### NetworkInterfaces

Types:

```python
from vra_iaas.types.iaas.api.machines import NetworkInterface
```

Methods:

- <code title="get /iaas/api/machines/{id}/network-interfaces/{networkId}">client.iaas.api.machines.network_interfaces.<a href="./src/vra_iaas/resources/iaas/api/machines/network_interfaces.py">retrieve</a>(network_id, \*, id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/network_interface_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/machines/network_interface.py">NetworkInterface</a></code>
- <code title="patch /iaas/api/machines/{id}/network-interfaces/{networkId}">client.iaas.api.machines.network_interfaces.<a href="./src/vra_iaas/resources/iaas/api/machines/network_interfaces.py">update</a>(network_id, \*, id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/network_interface_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/machines/network_interface.py">NetworkInterface</a></code>

#### Snapshots

Types:

```python
from vra_iaas.types.iaas.api.machines import Snapshot
```

Methods:

- <code title="get /iaas/api/machines/{id}/snapshots/{snapshotId}">client.iaas.api.machines.snapshots.<a href="./src/vra_iaas/resources/iaas/api/machines/snapshots.py">retrieve</a>(snapshot_id, \*, id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/snapshot_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/machines/snapshot.py">Snapshot</a></code>
- <code title="get /iaas/api/machines/{id}/snapshots">client.iaas.api.machines.snapshots.<a href="./src/vra_iaas/resources/iaas/api/machines/snapshots.py">list</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/snapshot_list_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/machines/snapshot.py">Snapshot</a></code>
- <code title="delete /iaas/api/machines/{id}/snapshots/{snapshotId}">client.iaas.api.machines.snapshots.<a href="./src/vra_iaas/resources/iaas/api/machines/snapshots.py">delete</a>(snapshot_id, \*, id, \*\*<a href="src/vra_iaas/types/iaas/api/machines/snapshot_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>

### LoadBalancers

Types:

```python
from vra_iaas.types.iaas.api import LoadBalancer, LoadBalancerRetrieveLoadBalancersResponse
```

Methods:

- <code title="get /iaas/api/load-balancers/{id}">client.iaas.api.load_balancers.<a href="./src/vra_iaas/resources/iaas/api/load_balancers/load_balancers.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/load_balancer_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/load_balancer.py">LoadBalancer</a></code>
- <code title="delete /iaas/api/load-balancers/{id}">client.iaas.api.load_balancers.<a href="./src/vra_iaas/resources/iaas/api/load_balancers/load_balancers.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/load_balancer_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/load-balancers">client.iaas.api.load_balancers.<a href="./src/vra_iaas/resources/iaas/api/load_balancers/load_balancers.py">load_balancers</a>(\*\*<a href="src/vra_iaas/types/iaas/api/load_balancer_load_balancers_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/load-balancers">client.iaas.api.load_balancers.<a href="./src/vra_iaas/resources/iaas/api/load_balancers/load_balancers.py">retrieve_load_balancers</a>(\*\*<a href="src/vra_iaas/types/iaas/api/load_balancer_retrieve_load_balancers_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/load_balancer_retrieve_load_balancers_response.py">LoadBalancerRetrieveLoadBalancersResponse</a></code>

#### Operations

Types:

```python
from vra_iaas.types.iaas.api.load_balancers import LoadBalancerSpecification, RouteConfiguration
```

Methods:

- <code title="post /iaas/api/load-balancers/{id}/operations/delete">client.iaas.api.load_balancers.operations.<a href="./src/vra_iaas/resources/iaas/api/load_balancers/operations.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/load_balancers/operation_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/load-balancers/{id}/operations/scale">client.iaas.api.load_balancers.operations.<a href="./src/vra_iaas/resources/iaas/api/load_balancers/operations.py">scale</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/load_balancers/operation_scale_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>

### IntegrationsIpam

#### PackageImport

Types:

```python
from vra_iaas.types.iaas.api.integrations_ipam import PackageImportPackageImportResponse
```

Methods:

- <code title="patch /iaas/api/integrations-ipam/package-import/{id}">client.iaas.api.integrations_ipam.package_import.<a href="./src/vra_iaas/resources/iaas/api/integrations_ipam/package_import.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/integrations_ipam/package_import_update_params.py">params</a>) -> None</code>
- <code title="post /iaas/api/integrations-ipam/package-import">client.iaas.api.integrations_ipam.package_import.<a href="./src/vra_iaas/resources/iaas/api/integrations_ipam/package_import.py">package_import</a>(\*\*<a href="src/vra_iaas/types/iaas/api/integrations_ipam/package_import_package_import_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/integrations_ipam/package_import_package_import_response.py">PackageImportPackageImportResponse</a></code>

### Integrations

Types:

```python
from vra_iaas.types.iaas.api import (
    CertificateInfoSpecification,
    Integration,
    IntegrationListResponse,
)
```

Methods:

- <code title="post /iaas/api/integrations">client.iaas.api.integrations.<a href="./src/vra_iaas/resources/iaas/api/integrations.py">create</a>(\*\*<a href="src/vra_iaas/types/iaas/api/integration_create_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/integrations/{id}">client.iaas.api.integrations.<a href="./src/vra_iaas/resources/iaas/api/integrations.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/integration_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/integration.py">Integration</a></code>
- <code title="patch /iaas/api/integrations/{id}">client.iaas.api.integrations.<a href="./src/vra_iaas/resources/iaas/api/integrations.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/integration_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/integrations">client.iaas.api.integrations.<a href="./src/vra_iaas/resources/iaas/api/integrations.py">list</a>(\*\*<a href="src/vra_iaas/types/iaas/api/integration_list_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/integration_list_response.py">IntegrationListResponse</a></code>
- <code title="delete /iaas/api/integrations/{id}">client.iaas.api.integrations.<a href="./src/vra_iaas/resources/iaas/api/integrations.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/integration_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>

### ImageProfiles

Types:

```python
from vra_iaas.types.iaas.api import (
    ImageMapping,
    ImageProfile,
    ImageProfileRetrieveImageProfilesResponse,
)
```

Methods:

- <code title="get /iaas/api/image-profiles/{id}">client.iaas.api.image_profiles.<a href="./src/vra_iaas/resources/iaas/api/image_profiles.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/image_profile_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/image_profile.py">ImageProfile</a></code>
- <code title="patch /iaas/api/image-profiles/{id}">client.iaas.api.image_profiles.<a href="./src/vra_iaas/resources/iaas/api/image_profiles.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/image_profile_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/image_profile.py">ImageProfile</a></code>
- <code title="delete /iaas/api/image-profiles/{id}">client.iaas.api.image_profiles.<a href="./src/vra_iaas/resources/iaas/api/image_profiles.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/image_profile_delete_params.py">params</a>) -> None</code>
- <code title="post /iaas/api/image-profiles">client.iaas.api.image_profiles.<a href="./src/vra_iaas/resources/iaas/api/image_profiles.py">image_profiles</a>(\*\*<a href="src/vra_iaas/types/iaas/api/image_profile_image_profiles_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/image_profile.py">ImageProfile</a></code>
- <code title="get /iaas/api/image-profiles">client.iaas.api.image_profiles.<a href="./src/vra_iaas/resources/iaas/api/image_profiles.py">retrieve_image_profiles</a>(\*\*<a href="src/vra_iaas/types/iaas/api/image_profile_retrieve_image_profiles_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/image_profile_retrieve_image_profiles_response.py">ImageProfileRetrieveImageProfilesResponse</a></code>

### FlavorProfiles

Types:

```python
from vra_iaas.types.iaas.api import (
    FlavorMapping,
    FlavorProfile,
    FlavorProfileRetrieveFlavorProfilesResponse,
)
```

Methods:

- <code title="get /iaas/api/flavor-profiles/{id}">client.iaas.api.flavor_profiles.<a href="./src/vra_iaas/resources/iaas/api/flavor_profiles.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/flavor_profile_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/flavor_profile.py">FlavorProfile</a></code>
- <code title="patch /iaas/api/flavor-profiles/{id}">client.iaas.api.flavor_profiles.<a href="./src/vra_iaas/resources/iaas/api/flavor_profiles.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/flavor_profile_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/flavor_profile.py">FlavorProfile</a></code>
- <code title="delete /iaas/api/flavor-profiles/{id}">client.iaas.api.flavor_profiles.<a href="./src/vra_iaas/resources/iaas/api/flavor_profiles.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/flavor_profile_delete_params.py">params</a>) -> None</code>
- <code title="post /iaas/api/flavor-profiles">client.iaas.api.flavor_profiles.<a href="./src/vra_iaas/resources/iaas/api/flavor_profiles.py">flavor_profiles</a>(\*\*<a href="src/vra_iaas/types/iaas/api/flavor_profile_flavor_profiles_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/flavor_profile.py">FlavorProfile</a></code>
- <code title="get /iaas/api/flavor-profiles">client.iaas.api.flavor_profiles.<a href="./src/vra_iaas/resources/iaas/api/flavor_profiles.py">retrieve_flavor_profiles</a>(\*\*<a href="src/vra_iaas/types/iaas/api/flavor_profile_retrieve_flavor_profiles_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/flavor_profile_retrieve_flavor_profiles_response.py">FlavorProfileRetrieveFlavorProfilesResponse</a></code>

### Deployments

Types:

```python
from vra_iaas.types.iaas.api import Deployment, DeploymentListResponse
```

Methods:

- <code title="post /iaas/api/deployments">client.iaas.api.deployments.<a href="./src/vra_iaas/resources/iaas/api/deployments.py">create</a>(\*\*<a href="src/vra_iaas/types/iaas/api/deployment_create_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/deployment.py">Deployment</a></code>
- <code title="get /iaas/api/deployments/{id}">client.iaas.api.deployments.<a href="./src/vra_iaas/resources/iaas/api/deployments.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/deployment_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/deployment.py">Deployment</a></code>
- <code title="get /iaas/api/deployments">client.iaas.api.deployments.<a href="./src/vra_iaas/resources/iaas/api/deployments.py">list</a>(\*\*<a href="src/vra_iaas/types/iaas/api/deployment_list_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/deployment_list_response.py">DeploymentListResponse</a></code>
- <code title="delete /iaas/api/deployments/{id}">client.iaas.api.deployments.<a href="./src/vra_iaas/resources/iaas/api/deployments.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/deployment_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>

### DataCollectors

Types:

```python
from vra_iaas.types.iaas.api import (
    DataCollector,
    DataCollectorDataCollectorsResponse,
    DataCollectorRetrieveDataCollectorsResponse,
)
```

Methods:

- <code title="get /iaas/api/data-collectors/{id}">client.iaas.api.data_collectors.<a href="./src/vra_iaas/resources/iaas/api/data_collectors.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/data_collector_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/data_collector.py">DataCollector</a></code>
- <code title="delete /iaas/api/data-collectors/{id}">client.iaas.api.data_collectors.<a href="./src/vra_iaas/resources/iaas/api/data_collectors.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/data_collector_delete_params.py">params</a>) -> None</code>
- <code title="post /iaas/api/data-collectors">client.iaas.api.data_collectors.<a href="./src/vra_iaas/resources/iaas/api/data_collectors.py">data_collectors</a>(\*\*<a href="src/vra_iaas/types/iaas/api/data_collector_data_collectors_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/data_collector_data_collectors_response.py">DataCollectorDataCollectorsResponse</a></code>
- <code title="get /iaas/api/data-collectors">client.iaas.api.data_collectors.<a href="./src/vra_iaas/resources/iaas/api/data_collectors.py">retrieve_data_collectors</a>(\*\*<a href="src/vra_iaas/types/iaas/api/data_collector_retrieve_data_collectors_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/data_collector_retrieve_data_collectors_response.py">DataCollectorRetrieveDataCollectorsResponse</a></code>

### ComputeNats

Types:

```python
from vra_iaas.types.iaas.api import ComputeNat, ComputeNatRetrieveComputeNatsResponse
```

Methods:

- <code title="get /iaas/api/compute-nats/{id}">client.iaas.api.compute_nats.<a href="./src/vra_iaas/resources/iaas/api/compute_nats/compute_nats.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/compute_nat_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/compute_nat.py">ComputeNat</a></code>
- <code title="delete /iaas/api/compute-nats/{id}">client.iaas.api.compute_nats.<a href="./src/vra_iaas/resources/iaas/api/compute_nats/compute_nats.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/compute_nat_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/compute-nats">client.iaas.api.compute_nats.<a href="./src/vra_iaas/resources/iaas/api/compute_nats/compute_nats.py">compute_nats</a>(\*\*<a href="src/vra_iaas/types/iaas/api/compute_nat_compute_nats_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/compute-nats">client.iaas.api.compute_nats.<a href="./src/vra_iaas/resources/iaas/api/compute_nats/compute_nats.py">retrieve_compute_nats</a>(\*\*<a href="src/vra_iaas/types/iaas/api/compute_nat_retrieve_compute_nats_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/compute_nat_retrieve_compute_nats_response.py">ComputeNatRetrieveComputeNatsResponse</a></code>

#### Operations

Types:

```python
from vra_iaas.types.iaas.api.compute_nats import NatRule
```

Methods:

- <code title="post /iaas/api/compute-nats/{id}/operations/reconfigure">client.iaas.api.compute_nats.operations.<a href="./src/vra_iaas/resources/iaas/api/compute_nats/operations.py">reconfigure</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/compute_nats/operation_reconfigure_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>

### ComputeGateways

Types:

```python
from vra_iaas.types.iaas.api import ComputeGateway, ComputeGatewayRetrieveComputeGatewaysResponse
```

Methods:

- <code title="get /iaas/api/compute-gateways/{id}">client.iaas.api.compute_gateways.<a href="./src/vra_iaas/resources/iaas/api/compute_gateways.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/compute_gateway_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/compute_gateway.py">ComputeGateway</a></code>
- <code title="delete /iaas/api/compute-gateways/{id}">client.iaas.api.compute_gateways.<a href="./src/vra_iaas/resources/iaas/api/compute_gateways.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/compute_gateway_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/compute-gateways">client.iaas.api.compute_gateways.<a href="./src/vra_iaas/resources/iaas/api/compute_gateways.py">compute_gateways</a>(\*\*<a href="src/vra_iaas/types/iaas/api/compute_gateway_compute_gateways_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/compute-gateways">client.iaas.api.compute_gateways.<a href="./src/vra_iaas/resources/iaas/api/compute_gateways.py">retrieve_compute_gateways</a>(\*\*<a href="src/vra_iaas/types/iaas/api/compute_gateway_retrieve_compute_gateways_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/compute_gateway_retrieve_compute_gateways_response.py">ComputeGatewayRetrieveComputeGatewaysResponse</a></code>

### CloudAccounts

Types:

```python
from vra_iaas.types.iaas.api import CloudAccount, CloudAccountRetrieveCloudAccountsResponse
```

Methods:

- <code title="get /iaas/api/cloud-accounts/{id}">client.iaas.api.cloud_accounts.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts/cloud_accounts.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_account_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_account.py">CloudAccount</a></code>
- <code title="patch /iaas/api/cloud-accounts/{id}">client.iaas.api.cloud_accounts.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts/cloud_accounts.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_account_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="delete /iaas/api/cloud-accounts/{id}">client.iaas.api.cloud_accounts.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts/cloud_accounts.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_account_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts">client.iaas.api.cloud_accounts.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts/cloud_accounts.py">cloud_accounts</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_account_cloud_accounts_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts/{id}/health-check">client.iaas.api.cloud_accounts.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts/cloud_accounts.py">health_check</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_account_health_check_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts/{id}/private-image-enumeration">client.iaas.api.cloud_accounts.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts/cloud_accounts.py">private_image_enumeration</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_account_private_image_enumeration_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/cloud-accounts">client.iaas.api.cloud_accounts.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts/cloud_accounts.py">retrieve_cloud_accounts</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_account_retrieve_cloud_accounts_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_account_retrieve_cloud_accounts_response.py">CloudAccountRetrieveCloudAccountsResponse</a></code>

#### RegionEnumeration

Types:

```python
from vra_iaas.types.iaas.api.cloud_accounts import RegionEnumerationRetrieveResponse
```

Methods:

- <code title="get /iaas/api/cloud-accounts/region-enumeration/{id}">client.iaas.api.cloud_accounts.region_enumeration.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts/region_enumeration.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts/region_enumeration_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_accounts/region_enumeration_retrieve_response.py">RegionEnumerationRetrieveResponse</a></code>
- <code title="post /iaas/api/cloud-accounts/region-enumeration">client.iaas.api.cloud_accounts.region_enumeration.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts/region_enumeration.py">region_enumeration</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts/region_enumeration_region_enumeration_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>

### CloudAccountsVsphere

Types:

```python
from vra_iaas.types.iaas.api import (
    CloudAccountVsphere,
    RegionSpecification,
    CloudAccountsVsphereRetrieveCloudAccountsVsphereResponse,
)
```

Methods:

- <code title="get /iaas/api/cloud-accounts-vsphere/{id}">client.iaas.api.cloud_accounts_vsphere.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vsphere.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vsphere_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_account_vsphere.py">CloudAccountVsphere</a></code>
- <code title="patch /iaas/api/cloud-accounts-vsphere/{id}">client.iaas.api.cloud_accounts_vsphere.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vsphere.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vsphere_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="delete /iaas/api/cloud-accounts-vsphere/{id}">client.iaas.api.cloud_accounts_vsphere.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vsphere.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vsphere_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-vsphere">client.iaas.api.cloud_accounts_vsphere.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vsphere.py">cloud_accounts_vsphere</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vsphere_cloud_accounts_vsphere_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-vsphere/{id}/private-image-enumeration">client.iaas.api.cloud_accounts_vsphere.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vsphere.py">private_image_enumeration</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vsphere_private_image_enumeration_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-vsphere/region-enumeration">client.iaas.api.cloud_accounts_vsphere.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vsphere.py">region_enumeration</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vsphere_region_enumeration_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/cloud-accounts-vsphere">client.iaas.api.cloud_accounts_vsphere.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vsphere.py">retrieve_cloud_accounts_vsphere</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vsphere_retrieve_cloud_accounts_vsphere_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_accounts_vsphere_retrieve_cloud_accounts_vsphere_response.py">CloudAccountsVsphereRetrieveCloudAccountsVsphereResponse</a></code>

### CloudAccountsVmc

Types:

```python
from vra_iaas.types.iaas.api import (
    CloudAccountVmc,
    CloudAccountsVmcRetrieveCloudAccountsVmcResponse,
)
```

Methods:

- <code title="get /iaas/api/cloud-accounts-vmc/{id}">client.iaas.api.cloud_accounts_vmc.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vmc.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vmc_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_account_vmc.py">CloudAccountVmc</a></code>
- <code title="patch /iaas/api/cloud-accounts-vmc/{id}">client.iaas.api.cloud_accounts_vmc.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vmc.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vmc_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="delete /iaas/api/cloud-accounts-vmc/{id}">client.iaas.api.cloud_accounts_vmc.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vmc.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vmc_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-vmc">client.iaas.api.cloud_accounts_vmc.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vmc.py">cloud_accounts_vmc</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vmc_cloud_accounts_vmc_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-vmc/{id}/private-image-enumeration">client.iaas.api.cloud_accounts_vmc.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vmc.py">private_image_enumeration</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vmc_private_image_enumeration_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-vmc/region-enumeration">client.iaas.api.cloud_accounts_vmc.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vmc.py">region_enumeration</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vmc_region_enumeration_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/cloud-accounts-vmc">client.iaas.api.cloud_accounts_vmc.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vmc.py">retrieve_cloud_accounts_vmc</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vmc_retrieve_cloud_accounts_vmc_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_accounts_vmc_retrieve_cloud_accounts_vmc_response.py">CloudAccountsVmcRetrieveCloudAccountsVmcResponse</a></code>

### CloudAccountsVcf

Types:

```python
from vra_iaas.types.iaas.api import (
    CloudAccountVcf,
    CloudAccountsVcfRetrieveCloudAccountsVcfResponse,
)
```

Methods:

- <code title="get /iaas/api/cloud-accounts-vcf/{id}">client.iaas.api.cloud_accounts_vcf.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vcf.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vcf_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_account_vcf.py">CloudAccountVcf</a></code>
- <code title="patch /iaas/api/cloud-accounts-vcf/{id}">client.iaas.api.cloud_accounts_vcf.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vcf.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vcf_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="delete /iaas/api/cloud-accounts-vcf/{id}">client.iaas.api.cloud_accounts_vcf.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vcf.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vcf_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-vcf">client.iaas.api.cloud_accounts_vcf.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vcf.py">cloud_accounts_vcf</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vcf_cloud_accounts_vcf_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-vcf/{id}/private-image-enumeration">client.iaas.api.cloud_accounts_vcf.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vcf.py">private_image_enumeration</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vcf_private_image_enumeration_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-vcf/region-enumeration">client.iaas.api.cloud_accounts_vcf.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vcf.py">region_enumeration</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vcf_region_enumeration_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/cloud-accounts-vcf">client.iaas.api.cloud_accounts_vcf.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_vcf.py">retrieve_cloud_accounts_vcf</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_vcf_retrieve_cloud_accounts_vcf_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_accounts_vcf_retrieve_cloud_accounts_vcf_response.py">CloudAccountsVcfRetrieveCloudAccountsVcfResponse</a></code>

### CloudAccountsNsxV

Types:

```python
from vra_iaas.types.iaas.api import (
    CloudAccountNsxV,
    CloudAccountsNsxVRetrieveCloudAccountsNsxVResponse,
)
```

Methods:

- <code title="get /iaas/api/cloud-accounts-nsx-v/{id}">client.iaas.api.cloud_accounts_nsx_v.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_nsx_v.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_nsx_v_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_account_nsx_v.py">CloudAccountNsxV</a></code>
- <code title="patch /iaas/api/cloud-accounts-nsx-v/{id}">client.iaas.api.cloud_accounts_nsx_v.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_nsx_v.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_nsx_v_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="delete /iaas/api/cloud-accounts-nsx-v/{id}">client.iaas.api.cloud_accounts_nsx_v.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_nsx_v.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_nsx_v_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-nsx-v">client.iaas.api.cloud_accounts_nsx_v.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_nsx_v.py">cloud_accounts_nsx_v</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_nsx_v_cloud_accounts_nsx_v_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/cloud-accounts-nsx-v">client.iaas.api.cloud_accounts_nsx_v.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_nsx_v.py">retrieve_cloud_accounts_nsx_v</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_nsx_v_retrieve_cloud_accounts_nsx_v_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_accounts_nsx_v_retrieve_cloud_accounts_nsx_v_response.py">CloudAccountsNsxVRetrieveCloudAccountsNsxVResponse</a></code>

### CloudAccountsNsxT

Types:

```python
from vra_iaas.types.iaas.api import (
    CloudAccountNsxT,
    CloudAccountsNsxTRetrieveCloudAccountsNsxTResponse,
)
```

Methods:

- <code title="get /iaas/api/cloud-accounts-nsx-t/{id}">client.iaas.api.cloud_accounts_nsx_t.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_nsx_t.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_nsx_t_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_account_nsx_t.py">CloudAccountNsxT</a></code>
- <code title="patch /iaas/api/cloud-accounts-nsx-t/{id}">client.iaas.api.cloud_accounts_nsx_t.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_nsx_t.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_nsx_t_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="delete /iaas/api/cloud-accounts-nsx-t/{id}">client.iaas.api.cloud_accounts_nsx_t.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_nsx_t.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_nsx_t_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-nsx-t">client.iaas.api.cloud_accounts_nsx_t.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_nsx_t.py">cloud_accounts_nsx_t</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_nsx_t_cloud_accounts_nsx_t_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/cloud-accounts-nsx-t">client.iaas.api.cloud_accounts_nsx_t.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_nsx_t.py">retrieve_cloud_accounts_nsx_t</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_nsx_t_retrieve_cloud_accounts_nsx_t_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_accounts_nsx_t_retrieve_cloud_accounts_nsx_t_response.py">CloudAccountsNsxTRetrieveCloudAccountsNsxTResponse</a></code>

### CloudAccountsGcp

Types:

```python
from vra_iaas.types.iaas.api import (
    CloudAccountGcp,
    CloudAccountsGcpRetrieveCloudAccountsGcpResponse,
)
```

Methods:

- <code title="get /iaas/api/cloud-accounts-gcp/{id}">client.iaas.api.cloud_accounts_gcp.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_gcp.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_gcp_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_account_gcp.py">CloudAccountGcp</a></code>
- <code title="patch /iaas/api/cloud-accounts-gcp/{id}">client.iaas.api.cloud_accounts_gcp.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_gcp.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_gcp_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="delete /iaas/api/cloud-accounts-gcp/{id}">client.iaas.api.cloud_accounts_gcp.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_gcp.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_gcp_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-gcp">client.iaas.api.cloud_accounts_gcp.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_gcp.py">cloud_accounts_gcp</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_gcp_cloud_accounts_gcp_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-gcp/{id}/private-image-enumeration">client.iaas.api.cloud_accounts_gcp.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_gcp.py">private_image_enumeration</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_gcp_private_image_enumeration_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-gcp/region-enumeration">client.iaas.api.cloud_accounts_gcp.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_gcp.py">region_enumeration</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_gcp_region_enumeration_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/cloud-accounts-gcp">client.iaas.api.cloud_accounts_gcp.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_gcp.py">retrieve_cloud_accounts_gcp</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_gcp_retrieve_cloud_accounts_gcp_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_accounts_gcp_retrieve_cloud_accounts_gcp_response.py">CloudAccountsGcpRetrieveCloudAccountsGcpResponse</a></code>

### CloudAccountsAzure

Types:

```python
from vra_iaas.types.iaas.api import (
    CloudAccountAzure,
    CloudAccountsAzureRetrieveCloudAccountsAzureResponse,
)
```

Methods:

- <code title="get /iaas/api/cloud-accounts-azure/{id}">client.iaas.api.cloud_accounts_azure.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_azure.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_azure_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_account_azure.py">CloudAccountAzure</a></code>
- <code title="patch /iaas/api/cloud-accounts-azure/{id}">client.iaas.api.cloud_accounts_azure.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_azure.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_azure_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="delete /iaas/api/cloud-accounts-azure/{id}">client.iaas.api.cloud_accounts_azure.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_azure.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_azure_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-azure">client.iaas.api.cloud_accounts_azure.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_azure.py">cloud_accounts_azure</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_azure_cloud_accounts_azure_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-azure/{id}/private-image-enumeration">client.iaas.api.cloud_accounts_azure.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_azure.py">private_image_enumeration</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_azure_private_image_enumeration_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-azure/region-enumeration">client.iaas.api.cloud_accounts_azure.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_azure.py">region_enumeration</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_azure_region_enumeration_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/cloud-accounts-azure">client.iaas.api.cloud_accounts_azure.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_azure.py">retrieve_cloud_accounts_azure</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_azure_retrieve_cloud_accounts_azure_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_accounts_azure_retrieve_cloud_accounts_azure_response.py">CloudAccountsAzureRetrieveCloudAccountsAzureResponse</a></code>

### CloudAccountsAws

Types:

```python
from vra_iaas.types.iaas.api import CloudAccountAws, CloudAccountsAwRetrieveCloudAccountsAwsResponse
```

Methods:

- <code title="get /iaas/api/cloud-accounts-aws/{id}">client.iaas.api.cloud_accounts_aws.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_aws.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_aw_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_account_aws.py">CloudAccountAws</a></code>
- <code title="patch /iaas/api/cloud-accounts-aws/{id}">client.iaas.api.cloud_accounts_aws.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_aws.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_aw_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="delete /iaas/api/cloud-accounts-aws/{id}">client.iaas.api.cloud_accounts_aws.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_aws.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_aw_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-aws">client.iaas.api.cloud_accounts_aws.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_aws.py">cloud_accounts_aws</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_aw_cloud_accounts_aws_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-aws/{id}/private-image-enumeration">client.iaas.api.cloud_accounts_aws.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_aws.py">private_image_enumeration</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_aw_private_image_enumeration_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-aws/region-enumeration">client.iaas.api.cloud_accounts_aws.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_aws.py">region_enumeration</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_aw_region_enumeration_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/cloud-accounts-aws">client.iaas.api.cloud_accounts_aws.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_aws.py">retrieve_cloud_accounts_aws</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_aw_retrieve_cloud_accounts_aws_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_accounts_aw_retrieve_cloud_accounts_aws_response.py">CloudAccountsAwRetrieveCloudAccountsAwsResponse</a></code>

### CloudAccountsAvilb

Types:

```python
from vra_iaas.types.iaas.api import (
    CloudAccountAviLb,
    CloudAccountsAvilbRetrieveCloudAccountsAvilbResponse,
)
```

Methods:

- <code title="get /iaas/api/cloud-accounts-avilb/{id}">client.iaas.api.cloud_accounts_avilb.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_avilb.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_avilb_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_account_avi_lb.py">CloudAccountAviLb</a></code>
- <code title="patch /iaas/api/cloud-accounts-avilb/{id}">client.iaas.api.cloud_accounts_avilb.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_avilb.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_avilb_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="delete /iaas/api/cloud-accounts-avilb/{id}">client.iaas.api.cloud_accounts_avilb.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_avilb.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_avilb_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/cloud-accounts-avilb">client.iaas.api.cloud_accounts_avilb.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_avilb.py">cloud_accounts_avilb</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_avilb_cloud_accounts_avilb_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/cloud-accounts-avilb">client.iaas.api.cloud_accounts_avilb.<a href="./src/vra_iaas/resources/iaas/api/cloud_accounts_avilb.py">retrieve_cloud_accounts_avilb</a>(\*\*<a href="src/vra_iaas/types/iaas/api/cloud_accounts_avilb_retrieve_cloud_accounts_avilb_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/cloud_accounts_avilb_retrieve_cloud_accounts_avilb_response.py">CloudAccountsAvilbRetrieveCloudAccountsAvilbResponse</a></code>

### BlockDevices

Types:

```python
from vra_iaas.types.iaas.api import BlockDevice
```

Methods:

- <code title="get /iaas/api/block-devices/{id}">client.iaas.api.block_devices.<a href="./src/vra_iaas/resources/iaas/api/block_devices/block_devices.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/block_device_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/block_device.py">BlockDevice</a></code>
- <code title="post /iaas/api/block-devices/{id}">client.iaas.api.block_devices.<a href="./src/vra_iaas/resources/iaas/api/block_devices/block_devices.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/block_device_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="delete /iaas/api/block-devices/{id}">client.iaas.api.block_devices.<a href="./src/vra_iaas/resources/iaas/api/block_devices/block_devices.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/block_device_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/block-devices">client.iaas.api.block_devices.<a href="./src/vra_iaas/resources/iaas/api/block_devices/block_devices.py">block_devices</a>(\*\*<a href="src/vra_iaas/types/iaas/api/block_device_block_devices_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="get /iaas/api/block-devices">client.iaas.api.block_devices.<a href="./src/vra_iaas/resources/iaas/api/block_devices/block_devices.py">retrieve_block_devices</a>(\*\*<a href="src/vra_iaas/types/iaas/api/block_device_retrieve_block_devices_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/machines/block_device_result.py">BlockDeviceResult</a></code>

#### Operations

Methods:

- <code title="post /iaas/api/block-devices/{id}/operations/promote">client.iaas.api.block_devices.operations.<a href="./src/vra_iaas/resources/iaas/api/block_devices/operations.py">promote</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/block_devices/operation_promote_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/block-devices/{diskId}/operations/revert">client.iaas.api.block_devices.operations.<a href="./src/vra_iaas/resources/iaas/api/block_devices/operations.py">revert</a>(disk_id, \*\*<a href="src/vra_iaas/types/iaas/api/block_devices/operation_revert_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="post /iaas/api/block-devices/{id}/operations/snapshots">client.iaas.api.block_devices.operations.<a href="./src/vra_iaas/resources/iaas/api/block_devices/operations.py">snapshots</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/block_devices/operation_snapshots_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>

#### Snapshots

Types:

```python
from vra_iaas.types.iaas.api.block_devices import DiskSnapshot
```

Methods:

- <code title="get /iaas/api/block-devices/{id}/snapshots/{id1}">client.iaas.api.block_devices.snapshots.<a href="./src/vra_iaas/resources/iaas/api/block_devices/snapshots.py">retrieve</a>(id1, \*, id, \*\*<a href="src/vra_iaas/types/iaas/api/block_devices/snapshot_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/block_devices/disk_snapshot.py">DiskSnapshot</a></code>
- <code title="get /iaas/api/block-devices/{id}/snapshots">client.iaas.api.block_devices.snapshots.<a href="./src/vra_iaas/resources/iaas/api/block_devices/snapshots.py">list</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/block_devices/snapshot_list_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/block_devices/disk_snapshot.py">DiskSnapshot</a></code>
- <code title="delete /iaas/api/block-devices/{id}/snapshots/{id1}">client.iaas.api.block_devices.snapshots.<a href="./src/vra_iaas/resources/iaas/api/block_devices/snapshots.py">delete</a>(id1, \*, id, \*\*<a href="src/vra_iaas/types/iaas/api/block_devices/snapshot_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>

### FabricVsphereDatastores

Types:

```python
from vra_iaas.types.iaas.api import (
    FabricVsphereDatastore,
    FabricVsphereDatastoreRetrieveFabricVsphereDatastoresResponse,
)
```

Methods:

- <code title="get /iaas/api/fabric-vsphere-datastores/{id}">client.iaas.api.fabric_vsphere_datastores.<a href="./src/vra_iaas/resources/iaas/api/fabric_vsphere_datastores.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/fabric_vsphere_datastore_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_vsphere_datastore.py">FabricVsphereDatastore</a></code>
- <code title="patch /iaas/api/fabric-vsphere-datastores/{id}">client.iaas.api.fabric_vsphere_datastores.<a href="./src/vra_iaas/resources/iaas/api/fabric_vsphere_datastores.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/fabric_vsphere_datastore_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_vsphere_datastore.py">FabricVsphereDatastore</a></code>
- <code title="get /iaas/api/fabric-vsphere-datastores">client.iaas.api.fabric_vsphere_datastores.<a href="./src/vra_iaas/resources/iaas/api/fabric_vsphere_datastores.py">retrieve_fabric_vsphere_datastores</a>(\*\*<a href="src/vra_iaas/types/iaas/api/fabric_vsphere_datastore_retrieve_fabric_vsphere_datastores_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_vsphere_datastore_retrieve_fabric_vsphere_datastores_response.py">FabricVsphereDatastoreRetrieveFabricVsphereDatastoresResponse</a></code>

### FabricNetworks

Types:

```python
from vra_iaas.types.iaas.api import FabricNetwork, FabricNetworkResult
```

Methods:

- <code title="get /iaas/api/fabric-networks/{id}">client.iaas.api.fabric_networks.<a href="./src/vra_iaas/resources/iaas/api/fabric_networks.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/fabric_network_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_network.py">FabricNetwork</a></code>
- <code title="patch /iaas/api/fabric-networks/{id}">client.iaas.api.fabric_networks.<a href="./src/vra_iaas/resources/iaas/api/fabric_networks.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/fabric_network_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_network.py">FabricNetwork</a></code>
- <code title="get /iaas/api/fabric-networks">client.iaas.api.fabric_networks.<a href="./src/vra_iaas/resources/iaas/api/fabric_networks.py">retrieve_fabric_networks</a>(\*\*<a href="src/vra_iaas/types/iaas/api/fabric_network_retrieve_fabric_networks_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_network_result.py">FabricNetworkResult</a></code>
- <code title="get /iaas/api/fabric-networks/{id}/network-ip-ranges">client.iaas.api.fabric_networks.<a href="./src/vra_iaas/resources/iaas/api/fabric_networks.py">retrieve_network_ip_ranges</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/fabric_network_retrieve_network_ip_ranges_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_network.py">FabricNetwork</a></code>

### FabricNetworksVsphere

Types:

```python
from vra_iaas.types.iaas.api import (
    FabricNetworkVsphere,
    FabricNetworksVsphereRetrieveFabricNetworksVsphereResponse,
)
```

Methods:

- <code title="get /iaas/api/fabric-networks-vsphere/{id}">client.iaas.api.fabric_networks_vsphere.<a href="./src/vra_iaas/resources/iaas/api/fabric_networks_vsphere.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/fabric_networks_vsphere_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_network_vsphere.py">FabricNetworkVsphere</a></code>
- <code title="patch /iaas/api/fabric-networks-vsphere/{id}">client.iaas.api.fabric_networks_vsphere.<a href="./src/vra_iaas/resources/iaas/api/fabric_networks_vsphere.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/fabric_networks_vsphere_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_network_vsphere.py">FabricNetworkVsphere</a></code>
- <code title="get /iaas/api/fabric-networks-vsphere">client.iaas.api.fabric_networks_vsphere.<a href="./src/vra_iaas/resources/iaas/api/fabric_networks_vsphere.py">retrieve_fabric_networks_vsphere</a>(\*\*<a href="src/vra_iaas/types/iaas/api/fabric_networks_vsphere_retrieve_fabric_networks_vsphere_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_networks_vsphere_retrieve_fabric_networks_vsphere_response.py">FabricNetworksVsphereRetrieveFabricNetworksVsphereResponse</a></code>
- <code title="get /iaas/api/fabric-networks-vsphere/{id}/network-ip-ranges">client.iaas.api.fabric_networks_vsphere.<a href="./src/vra_iaas/resources/iaas/api/fabric_networks_vsphere.py">retrieve_network_ip_ranges</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/fabric_networks_vsphere_retrieve_network_ip_ranges_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_network_vsphere.py">FabricNetworkVsphere</a></code>

### FabricComputes

Types:

```python
from vra_iaas.types.iaas.api import FabricCompute
```

Methods:

- <code title="get /iaas/api/fabric-computes/{id}">client.iaas.api.fabric_computes.<a href="./src/vra_iaas/resources/iaas/api/fabric_computes.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/fabric_compute_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_compute.py">FabricCompute</a></code>
- <code title="patch /iaas/api/fabric-computes/{id}">client.iaas.api.fabric_computes.<a href="./src/vra_iaas/resources/iaas/api/fabric_computes.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/fabric_compute_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_compute.py">FabricCompute</a></code>
- <code title="get /iaas/api/fabric-computes">client.iaas.api.fabric_computes.<a href="./src/vra_iaas/resources/iaas/api/fabric_computes.py">retrieve_fabric_computes</a>(\*\*<a href="src/vra_iaas/types/iaas/api/fabric_compute_retrieve_fabric_computes_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_compute_result.py">FabricComputeResult</a></code>

### ExternalNetworkIPRanges

Types:

```python
from vra_iaas.types.iaas.api import (
    ExternalNetworkIPRange,
    ExternalNetworkIPRangeRetrieveExternalNetworkIPRangesResponse,
)
```

Methods:

- <code title="get /iaas/api/external-network-ip-ranges/{id}">client.iaas.api.external_network_ip_ranges.<a href="./src/vra_iaas/resources/iaas/api/external_network_ip_ranges.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/external_network_ip_range_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/external_network_ip_range.py">ExternalNetworkIPRange</a></code>
- <code title="patch /iaas/api/external-network-ip-ranges/{id}">client.iaas.api.external_network_ip_ranges.<a href="./src/vra_iaas/resources/iaas/api/external_network_ip_ranges.py">update</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/external_network_ip_range_update_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/external_network_ip_range.py">ExternalNetworkIPRange</a></code>
- <code title="get /iaas/api/external-network-ip-ranges">client.iaas.api.external_network_ip_ranges.<a href="./src/vra_iaas/resources/iaas/api/external_network_ip_ranges.py">retrieve_external_network_ip_ranges</a>(\*\*<a href="src/vra_iaas/types/iaas/api/external_network_ip_range_retrieve_external_network_ip_ranges_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/external_network_ip_range_retrieve_external_network_ip_ranges_response.py">ExternalNetworkIPRangeRetrieveExternalNetworkIPRangesResponse</a></code>

### ConfigurationProperties

Types:

```python
from vra_iaas.types.iaas.api import ConfigurationProperty, ConfigurationPropertyResult
```

Methods:

- <code title="get /iaas/api/configuration-properties/{id}">client.iaas.api.configuration_properties.<a href="./src/vra_iaas/resources/iaas/api/configuration_properties.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/configuration_property_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/configuration_property_result.py">ConfigurationPropertyResult</a></code>
- <code title="delete /iaas/api/configuration-properties/{id}">client.iaas.api.configuration_properties.<a href="./src/vra_iaas/resources/iaas/api/configuration_properties.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/configuration_property_delete_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/configuration_property.py">ConfigurationProperty</a></code>
- <code title="get /iaas/api/configuration-properties">client.iaas.api.configuration_properties.<a href="./src/vra_iaas/resources/iaas/api/configuration_properties.py">retrieve_configuration_properties</a>(\*\*<a href="src/vra_iaas/types/iaas/api/configuration_property_retrieve_configuration_properties_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/configuration_property_result.py">ConfigurationPropertyResult</a></code>
- <code title="patch /iaas/api/configuration-properties">client.iaas.api.configuration_properties.<a href="./src/vra_iaas/resources/iaas/api/configuration_properties.py">update_configuration_properties</a>(\*\*<a href="src/vra_iaas/types/iaas/api/configuration_property_update_configuration_properties_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/configuration_property.py">ConfigurationProperty</a></code>

### RequestTracker

Types:

```python
from vra_iaas.types.iaas.api import RequestTrackerRetrieveRequestTrackerResponse
```

Methods:

- <code title="get /iaas/api/request-tracker/{id}">client.iaas.api.request_tracker.<a href="./src/vra_iaas/resources/iaas/api/request_tracker.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/request_tracker_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/projects/request_tracker.py">RequestTracker</a></code>
- <code title="delete /iaas/api/request-tracker/{id}">client.iaas.api.request_tracker.<a href="./src/vra_iaas/resources/iaas/api/request_tracker.py">delete</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/request_tracker_delete_params.py">params</a>) -> None</code>
- <code title="get /iaas/api/request-tracker">client.iaas.api.request_tracker.<a href="./src/vra_iaas/resources/iaas/api/request_tracker.py">retrieve_request_tracker</a>(\*\*<a href="src/vra_iaas/types/iaas/api/request_tracker_retrieve_request_tracker_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/request_tracker_retrieve_request_tracker_response.py">RequestTrackerRetrieveRequestTrackerResponse</a></code>

### Regions

Types:

```python
from vra_iaas.types.iaas.api import Region, RegionListResponse
```

Methods:

- <code title="get /iaas/api/regions/{id}">client.iaas.api.regions.<a href="./src/vra_iaas/resources/iaas/api/regions.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/region_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/region.py">Region</a></code>
- <code title="get /iaas/api/regions">client.iaas.api.regions.<a href="./src/vra_iaas/resources/iaas/api/regions.py">list</a>(\*\*<a href="src/vra_iaas/types/iaas/api/region_list_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/region_list_response.py">RegionListResponse</a></code>

### NetworkDomains

Types:

```python
from vra_iaas.types.iaas.api import NetworkDomain, NetworkDomainRetrieveNetworkDomainsResponse
```

Methods:

- <code title="get /iaas/api/network-domains/{id}">client.iaas.api.network_domains.<a href="./src/vra_iaas/resources/iaas/api/network_domains.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/network_domain_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/network_domain.py">NetworkDomain</a></code>
- <code title="get /iaas/api/network-domains">client.iaas.api.network_domains.<a href="./src/vra_iaas/resources/iaas/api/network_domains.py">retrieve_network_domains</a>(\*\*<a href="src/vra_iaas/types/iaas/api/network_domain_retrieve_network_domains_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/network_domain_retrieve_network_domains_response.py">NetworkDomainRetrieveNetworkDomainsResponse</a></code>

### FabricVsphereStoragePolicies

Types:

```python
from vra_iaas.types.iaas.api import (
    FabricVsphereStoragePolicy,
    FabricVsphereStoragePolicyRetrieveFabricVsphereStoragePoliciesResponse,
)
```

Methods:

- <code title="get /iaas/api/fabric-vsphere-storage-policies/{id}">client.iaas.api.fabric_vsphere_storage_policies.<a href="./src/vra_iaas/resources/iaas/api/fabric_vsphere_storage_policies.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/fabric_vsphere_storage_policy_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_vsphere_storage_policy.py">FabricVsphereStoragePolicy</a></code>
- <code title="get /iaas/api/fabric-vsphere-storage-policies">client.iaas.api.fabric_vsphere_storage_policies.<a href="./src/vra_iaas/resources/iaas/api/fabric_vsphere_storage_policies.py">retrieve_fabric_vsphere_storage_policies</a>(\*\*<a href="src/vra_iaas/types/iaas/api/fabric_vsphere_storage_policy_retrieve_fabric_vsphere_storage_policies_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_vsphere_storage_policy_retrieve_fabric_vsphere_storage_policies_response.py">FabricVsphereStoragePolicyRetrieveFabricVsphereStoragePoliciesResponse</a></code>

### FabricImages

Types:

```python
from vra_iaas.types.iaas.api import FabricImage, FabricImageRetrieveFabricImagesResponse
```

Methods:

- <code title="get /iaas/api/fabric-images/{id}">client.iaas.api.fabric_images.<a href="./src/vra_iaas/resources/iaas/api/fabric_images.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/fabric_image_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_image.py">FabricImage</a></code>
- <code title="get /iaas/api/fabric-images">client.iaas.api.fabric_images.<a href="./src/vra_iaas/resources/iaas/api/fabric_images.py">retrieve_fabric_images</a>(\*\*<a href="src/vra_iaas/types/iaas/api/fabric_image_retrieve_fabric_images_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_image_retrieve_fabric_images_response.py">FabricImageRetrieveFabricImagesResponse</a></code>

### FabricAzureStorageAccounts

Types:

```python
from vra_iaas.types.iaas.api import (
    FabricAzureStorageAccount,
    FabricAzureStorageAccountRetrieveFabricAzureStorageAccountsResponse,
)
```

Methods:

- <code title="get /iaas/api/fabric-azure-storage-accounts/{id}">client.iaas.api.fabric_azure_storage_accounts.<a href="./src/vra_iaas/resources/iaas/api/fabric_azure_storage_accounts.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/fabric_azure_storage_account_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_azure_storage_account.py">FabricAzureStorageAccount</a></code>
- <code title="get /iaas/api/fabric-azure-storage-accounts">client.iaas.api.fabric_azure_storage_accounts.<a href="./src/vra_iaas/resources/iaas/api/fabric_azure_storage_accounts.py">retrieve_fabric_azure_storage_accounts</a>(\*\*<a href="src/vra_iaas/types/iaas/api/fabric_azure_storage_account_retrieve_fabric_azure_storage_accounts_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_azure_storage_account_retrieve_fabric_azure_storage_accounts_response.py">FabricAzureStorageAccountRetrieveFabricAzureStorageAccountsResponse</a></code>

### ExternalIPBlocks

Methods:

- <code title="get /iaas/api/external-ip-blocks/{id}">client.iaas.api.external_ip_blocks.<a href="./src/vra_iaas/resources/iaas/api/external_ip_blocks.py">retrieve</a>(id, \*\*<a href="src/vra_iaas/types/iaas/api/external_ip_block_retrieve_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_network.py">FabricNetwork</a></code>
- <code title="get /iaas/api/external-ip-blocks">client.iaas.api.external_ip_blocks.<a href="./src/vra_iaas/resources/iaas/api/external_ip_blocks.py">retrieve_external_ip_blocks</a>(\*\*<a href="src/vra_iaas/types/iaas/api/external_ip_block_retrieve_external_ip_blocks_params.py">params</a>) -> <a href="./src/vra_iaas/types/iaas/api/fabric_network_result.py">FabricNetworkResult</a></code>
