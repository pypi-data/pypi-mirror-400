import json
from typing import Optional, List
import requests

from e2enetworks.cloud.tir.skus import Plans, client
from e2enetworks.cloud.tir.utils import prepare_object
from e2enetworks.cloud.tir.helpers import plan_name_to_sku_item_price_id, plan_name_to_sku_id
from e2enetworks.constants import (
    CLIENT_NOT_READY_MESSAGE, NOTEBOOK,
    CUSTOM, headers,
)
from e2enetworks.cloud.tir.notebooks.constants import (
    COMMITTED_POLICY_REQUIRED_ERROR,
    INVALID_COMMITTED_POLICY_ERROR,
    NEXT_SKU_ITEM_PRICE_ID_REQUIRED_ERROR,
    IMAGE_VERSION_ID_REQUIRED_ERROR,
    CUSTOM_IMAGE_DETAILS_REQUIRED_ERROR,
    NOTEBOOK_ID_TYPE_ERROR, AUTO_RENEW_STATUS,
    AUTO_TERMINATE_STATUS, CONVERT_TO_HOURLY_BILLING,
    INVALID_NOTEBOOK_ID_TYPE_ERROR,
    INVALID_PLAN_NAME_TYPE_ERROR,
    INVALID_SKU_ITEM_PRICE_ID_TYPE_ERROR,
    INVALID_COMMITTED_POLICY_TYPE_ERROR,
    COMMITTED_POLICIES, SSH_ENABLE,
    SSH_DISABLE, SSH_UPDATE, PAID_USAGE,
    INSTANCE_TYPE, AVAILABLE_ACTIONS,
    INVALID_ACTION, UPDATE_ACTION_ERROR,
    ENABLE_ACTION_ERROR,
)


class Notebooks:
    def __init__(
            self,
            team: Optional[str] = "",
            project: Optional[str] = "",
            location: Optional[str] = "",
    ):
        if not client.Default.ready():
            raise ValueError(CLIENT_NOT_READY_MESSAGE)
        if project:
            client.Default.set_project(project)
        if team:
            client.Default.set_team(team)
        if location:
            client.Default.set_location(location)

    def create(
        self,
        name: str,
        plan_name: str,
        image_type: str,
        image_version_id: Optional[int] = None,
        dataset_id_list: Optional[List[int]] = None,
        disk_size_in_gb: int = 30,
        is_jupyterlab_enabled: bool = True,
        public_key: Optional[List[str]] = None,
        notebook_type: str = "new",
        notebook_url: str = "",
        registry_namespace_id: Optional[int] = None,
        e2e_registry_image_url: Optional[str] = None,
        sku_item_price_id: Optional[int] = None,
        commited_policy: Optional[str] = None,
        next_sku_item_price_id: Optional[int] = None,
    ):
        # Avoid mutable defaults
        dataset_id_list = dataset_id_list or []
        public_key = public_key or []

        # Fetch SKU items based on the plan
        skus, skus_table = Plans().get_plans_list(NOTEBOOK, image_version_id)
        hourly_sku_item_price_id = plan_name_to_sku_item_price_id(skus, plan_name)
        sku_item_price_id = sku_item_price_id or hourly_sku_item_price_id

        # Validation for commited_policy and related fields
        if sku_item_price_id != hourly_sku_item_price_id and not commited_policy:
            raise ValueError(COMMITTED_POLICY_REQUIRED_ERROR)

        if commited_policy and commited_policy not in COMMITTED_POLICIES:
            raise ValueError(INVALID_COMMITTED_POLICY_ERROR.format(COMMITTED_POLICIES))

        if commited_policy in [AUTO_RENEW_STATUS, CONVERT_TO_HOURLY_BILLING] and not next_sku_item_price_id:
            raise ValueError(NEXT_SKU_ITEM_PRICE_ID_REQUIRED_ERROR)

        if commited_policy == AUTO_TERMINATE_STATUS:
            next_sku_item_price_id = None
        elif commited_policy == CONVERT_TO_HOURLY_BILLING:
            next_sku_item_price_id = hourly_sku_item_price_id

        # Validate image parameters
        if image_type != CUSTOM and not image_version_id:
            raise ValueError(IMAGE_VERSION_ID_REQUIRED_ERROR)

        if image_type == CUSTOM and (not registry_namespace_id or not e2e_registry_image_url):
            raise ValueError(CUSTOM_IMAGE_DETAILS_REQUIRED_ERROR)

        payload = {
            "name": name,
            "dataset_id_list": dataset_id_list,
            "image_type": image_type,
            "is_jupyterlab_enabled": is_jupyterlab_enabled,
            "public_key": public_key,
            "sku_item_price_id": sku_item_price_id,
            "auto_shutdown_timeout": None,
            "instance_type": PAID_USAGE,
            "disk_size_in_gb": disk_size_in_gb,
            "notebook_type": notebook_type,
            "notebook_url": notebook_url,
        }

        if image_type == CUSTOM:
            payload["registry_namespace_id"] = registry_namespace_id
            payload["e2e_registry_image_url"] = e2e_registry_image_url
        else:
            payload["image_version_id"] = image_version_id

        if commited_policy:
            payload["committed_instance_policy"] = commited_policy
            payload["next_sku_item_price_id"] = next_sku_item_price_id

        url = f"{client.Default.gpu_team_projects_path()}/notebooks/?"
        req = requests.Request('POST', url, json=payload)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def get(self, notebook_id: int):
        if not isinstance(notebook_id, int):
            raise TypeError(NOTEBOOK_ID_TYPE_ERROR)
        url = f"{client.Default.gpu_team_projects_path()}/notebooks/{notebook_id}/?"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def list(self):
        url = f"{client.Default.gpu_team_projects_path()}/notebooks/?"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def delete(self, notebook_id: int):
        if not isinstance(notebook_id, int):
            raise TypeError(NOTEBOOK_ID_TYPE_ERROR)
        url = f"{client.Default.gpu_team_projects_path()}/notebooks/{notebook_id}/?"
        req = requests.Request('DELETE', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def start(self, notebook_id: int):
        if not isinstance(notebook_id, int):
            raise TypeError(NOTEBOOK_ID_TYPE_ERROR)
        url = f"{client.Default.gpu_team_projects_path()}/notebooks/{notebook_id}/actions/?action=start&"
        req = requests.Request('PUT', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def stop(self, notebook_id: int):
        if not isinstance(notebook_id, int):
            raise TypeError(NOTEBOOK_ID_TYPE_ERROR)
        url = f"{client.Default.gpu_team_projects_path()}/notebooks/{notebook_id}/actions/?action=stop&"
        req = requests.Request('PUT', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def configure_ssh(self, notebook_id: int, action: str, ssh_keys_to_add=[], ssh_keys_to_remove=[]):
        if not isinstance(notebook_id, int):
            raise TypeError(NOTEBOOK_ID_TYPE_ERROR)
        if isinstance(ssh_keys_to_add, str):
            ssh_keys_to_add = [ssh_keys_to_add]
        if isinstance(ssh_keys_to_remove, str):
            ssh_keys_to_remove = [ssh_keys_to_remove]

        if action not in AVAILABLE_ACTIONS:
            raise ValueError(INVALID_ACTION.format(actions=AVAILABLE_ACTIONS))
        if action == SSH_UPDATE and not ssh_keys_to_add and not ssh_keys_to_remove:
            raise ValueError(UPDATE_ACTION_ERROR)
        if action == SSH_ENABLE and not ssh_keys_to_add:
            raise ValueError(ENABLE_ACTION_ERROR)

        if action == SSH_DISABLE:
            disable_url = f"{client.Default.gpu_team_projects_path()}/notebooks/{notebook_id}/ssh-keys/"
            req = requests.Request('PUT', disable_url, json={"ssh_keys_to_remove": "all"})
        elif action == SSH_ENABLE:
            enable_url = f"{client.Default.gpu_team_projects_path()}/notebooks/{notebook_id}/ssh-keys/"
            req = requests.Request('PUT', enable_url, json={"ssh_keys_to_add": ssh_keys_to_add})
        elif action == SSH_UPDATE:
            update_url = f"{client.Default.gpu_team_projects_path()}/notebooks/{notebook_id}/ssh-keys/"
            req = requests.Request('PUT', update_url, json={"ssh_keys_to_add": ssh_keys_to_add, "ssh_keys_to_remove": ssh_keys_to_remove})
        else:
            raise ValueError(INVALID_ACTION)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def list_attached_ssh_keys(self, notebook_id: int):
        if not isinstance(notebook_id, int):
            raise TypeError(NOTEBOOK_ID_TYPE_ERROR)
        url = f"{client.Default.gpu_team_projects_path()}/notebooks/{notebook_id}/ssh-keys/"
        req = requests.Request('GET', url)
        return prepare_object(client.Default.make_request(req))

    def upgrade(
        self,
        notebook_id: int,
        plan_name: str,
        sku_item_price_id: int,
        commited_policy: str,
        next_sku_item_price_id: Optional[int] = None
    ):
        if not isinstance(notebook_id, int):
            raise TypeError(INVALID_NOTEBOOK_ID_TYPE_ERROR)

        if not isinstance(plan_name, str):
            raise TypeError(INVALID_PLAN_NAME_TYPE_ERROR)

        if not isinstance(sku_item_price_id, (int, type(None))):
            raise TypeError(INVALID_SKU_ITEM_PRICE_ID_TYPE_ERROR)

        if not isinstance(commited_policy, str):
            raise TypeError(INVALID_COMMITTED_POLICY_TYPE_ERROR)

        skus, skus_table = Plans().get_plans_list(NOTEBOOK)
        hourly_sku_item_price_id = plan_name_to_sku_item_price_id(skus, plan_name)
        sku_id = plan_name_to_sku_id(skus, plan_name)
        sku_item_price_id = sku_item_price_id if sku_item_price_id else hourly_sku_item_price_id

        if sku_item_price_id != hourly_sku_item_price_id and not commited_policy:
            raise ValueError(COMMITTED_POLICY_REQUIRED_ERROR)

        if commited_policy not in COMMITTED_POLICIES:
            raise ValueError(INVALID_COMMITTED_POLICY_ERROR.format(COMMITTED_POLICIES))

        if commited_policy in [AUTO_RENEW_STATUS, CONVERT_TO_HOURLY_BILLING] and not next_sku_item_price_id:
            raise ValueError(NEXT_SKU_ITEM_PRICE_ID_REQUIRED_ERROR)

        if commited_policy == AUTO_TERMINATE_STATUS:
            next_sku_item_price_id = None
        elif commited_policy == CONVERT_TO_HOURLY_BILLING:
            next_sku_item_price_id = hourly_sku_item_price_id

        payload = {
            "sku_id": sku_id,
            "sku_item_price_id": sku_item_price_id,
            "committed_instance_policy": commited_policy,
            "next_sku_item_price_id": next_sku_item_price_id
        }
        headers['Authorization'] = f'Bearer {client.Default.access_token()}'
        url = f"{client.Default.gpu_team_projects_path()}/notebooks/{notebook_id}/?apikey={client.Default.api_key()}&location={client.Default.location()}"
        response = requests.put(url=url, headers=headers, json=payload)
        return prepare_object(response)

    def upgrade_pvc(self, notebook_id: int, size: int):
        if not isinstance(notebook_id, int):
            raise TypeError(INVALID_NOTEBOOK_ID_TYPE_ERROR)
        if not isinstance(size, int):
            raise TypeError(size)

        payload = json.dumps({
            "size": size})
        headers['Authorization'] = f'Bearer {client.Default.access_token()}'
        url = url = f"{client.Default.gpu_team_projects_path()}/notebooks/{notebook_id}/pvc/upgrade/?apikey={client.Default.api_key()}&location={client.Default.location()}"
        response = requests.put(url=url, headers=headers, data=payload)
        return prepare_object(response)

    def registry_namespace_list(self):
        url = f"{client.Default.gpu_team_projects_path()}/container_registry/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def registry_detail(self, registry_namespace_id: int):
        url = f"{client.Default.gpu_team_projects_path()}/container_registry/{registry_namespace_id}/namespace-repository/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def commited_policy(self):
        print(COMMITTED_POLICIES)

    @staticmethod
    def help():
        help_text = """
    "Notebook Class Help"
    "================="
    The `Notebooks` class provides methods to interact with notebooks in a project.

    Available methods:
    1. create(
        name (required): str,
        plan_name (required): str - The name of the plan. You can list plans using the Plans API,
        image_type (required): str - The type of image ('custom' or predefined),
        image_version_id (optional): int - The version ID of the image,
        dataset_id_list (optional): list[int] - List of dataset IDs to attach to the notebook,
        disk_size_in_gb: int - Size of the disk in GB (default: 30),
        is_jupyterlab_enabled: bool - Enable/disable JupyterLab (default: True),
        public_key (optional): list[str] - List of SSH public keys,
        notebook_type: str - The type of notebook ('new' or 'existing') (default: 'new'),
        notebook_url: str - URL of an existing notebook (if notebook_type is 'existing'),
        registry_namespace_id (optional): int - Namespace ID for custom images,
        e2e_registry_image_url (optional): str - URL for the custom image in the registry,
        sku_item_price_id (optional): int - SKU item price ID for the notebook,
        commited_policy (optional): str - Committed policy type (required if SKU differs from hourly pricing),
        next_sku_item_price_id (optional): int - SKU item price ID for the next committed instance
    ): Create a new notebook with the specified parameters.

    2. get(notebook_id: int): Retrieve details about a specific notebook by its ID.

    3. list(): List all notebooks available in the current project.

    4. delete(notebook_id: int): Delete a notebook by its ID.

    5. start(notebook_id: int): Start a stopped notebook by its ID.

    6. stop(notebook_id: int): Stop a running notebook by its ID.

    7. configure_ssh(
        notebook_id: int,
        action: str - Action to perform ('enable', 'disable', 'update'),
        ssh_keys_to_add (optional): list[str] - List of SSH keys to add,
        ssh_keys_to_remove (optional): list[str] - List of SSH keys to remove
    ): Manage SSH keys for a notebook by enabling, disabling, or updating them.

    8. list_attached_ssh_keys(notebook_id: int): List all SSH keys attached to a notebook.

    9. upgrade(
        notebook_id: int,
        plan_name: str - The name of the new plan for upgrading,
        sku_item_price_id: int - The SKU item price ID for the upgrade,
        commited_policy: str - The committed policy type for the upgrade,
        next_sku_item_price_id (optional): int - The SKU item price ID for the next committed instance
    ): Upgrade the plan of an existing notebook.

    10. upgrade_pvc(notebook_id: int, size: int): Upgrade the PVC (Persistent Volume Claim) for a notebook.

    11. registry_namespace_list(): List all available container registry namespaces.

    12. registry_detail(registry_namespace_id: int): Retrieve details about a specific registry namespace by its ID.

    13. commited_policy(): Print all available committed policies.

    """
        print(help_text)
