from typing import Optional
import requests
from e2enetworks.cloud.tir import client
from e2enetworks.constants import CLIENT_NOT_READY_MESSAGE
from e2enetworks.cloud.tir.integrations.constants import (
    INTEGRATION_TYPES, INTEGRATION_TYPE_ERROR,
    WEIGHTS_BIASES, WANDB_USERNAME_ERROR,
    WANDB_PROJECT_ERROR, INTEGRATION_LIST_ERROR,
    SHOW_DETAILS_ERROR,
)
from e2enetworks.cloud.tir.utils import prepare_object
from e2enetworks.cloud.tir.integrations.helpers import (
    prepare_payload, get_integrations_table,
    get_details_table,
)


class Integration:
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

    def create_integration(
        self,
        name: str,
        token: str,
        integration_type: str,
        wandb_username: Optional[str] = None,
        wandb_project: Optional[str] = None,
        _get_raw: Optional[bool] = False
    ):
        if integration_type not in INTEGRATION_TYPES:
            raise ValueError(INTEGRATION_TYPE_ERROR.format(
                given_type=integration_type, integration_types=INTEGRATION_TYPES
            ))

        if integration_type == WEIGHTS_BIASES:
            if not wandb_username:
                raise ValueError(WANDB_USERNAME_ERROR)
            if not wandb_project:
                raise ValueError(WANDB_PROJECT_ERROR)
            payload = prepare_payload(
                name, token, integration_type, wandb_username=wandb_username, wandb_project=wandb_project
            )
        else:
            payload = prepare_payload(name, token, integration_type)

        url = f"{client.Default.gpu_team_projects_path()}/integrations/?"
        req = requests.Request('POST', url, json=payload)
        response = client.Default.make_request(req)
        return prepare_object(response, _get_raw)

    def list_integrations(
        self,
        integration_type: str,
        _get_raw: Optional[bool] = False
    ):
        if integration_type not in INTEGRATION_TYPES:
            raise ValueError(INTEGRATION_TYPE_ERROR.format(
                given_type=integration_type, integration_types=INTEGRATION_TYPES
            ))

        url = f"{client.Default.gpu_team_projects_path()}/integrations/?integration_type={integration_type}&"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response, _get_raw)

    def get_integration_details(
        self,
        integration_id: int,
        _get_raw: Optional[bool] = False
    ):
        url = f"{client.Default.gpu_team_projects_path()}/integrations/{integration_id}/?"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response, _get_raw)

    def delete_integration(
        self,
        integration_id: int,
        _get_raw: Optional[bool] = False
    ):
        url = f"{client.Default.gpu_team_projects_path()}/integrations/{integration_id}/?"
        req = requests.Request('DELETE', url)
        response = client.Default.make_request(req)
        return prepare_object(response, _get_raw)

    def show_integrations(
        self,
        integration_type: str,
    ):
        is_success, response = self.list_integrations(integration_type)
        if not is_success:
            print(INTEGRATION_LIST_ERROR)
            return
        integrations_table = get_integrations_table(response)

        if not integrations_table:
            print(INTEGRATION_LIST_ERROR)
            return
        print(integrations_table)

    def show_integration_details(
        self,
        integration_id: int
    ):
        is_success, response = self.get_integration_details(integration_id)
        if not is_success:
            print(SHOW_DETAILS_ERROR)
            return

        integration_details_table = get_details_table(response)
        if not integration_details_table:
            print(SHOW_DETAILS_ERROR)
            return
        print(integration_details_table)

    @staticmethod
    def help():
        help_text = f"""
        Integration Class Help:

        Available Methods:

        1. create_integration(name, token, integration_type={INTEGRATION_TYPES}, wandb_username=None, wandb_project=None)
           - Creates a new integration (Hugging Face or Weights & Biases).

        2. list_integrations(integration_type)
           - Lists all integrations of a specified type.

        3. get_integration_details(integration_id)
           - Retrieves details for a specific integration.

        4. delete_integration(integration_id)
           - Deletes a specific integration.

        5. show_integrations(integration_type)
           - Displays a table of all integrations.

        6. show_integration_details(integration_id)
           - Displays a table of detailed information about a specific integration.
        """
        print(help_text)
