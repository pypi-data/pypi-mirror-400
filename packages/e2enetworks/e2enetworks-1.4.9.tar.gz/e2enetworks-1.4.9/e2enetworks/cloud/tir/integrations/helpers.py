from typing import Optional, Dict
from prettytable import PrettyTable
from e2enetworks.cloud.tir.integrations.constants import (
    WANDB_USERNAME, WANDB_KEY, INTEGRATION_TYPE,
    WANDB_PROJECT, INTEGRATION_DETAILS, NAME,
    HUGGINGFACE_TOKEN, WEIGHTS_BIASES,
)


def prepare_payload(
    name: str,
    token: str,
    integration_type: str,
    wandb_username: Optional[str] = None,
    wandb_project: Optional[str] = None
) -> Dict:
    """
    Prepares the payload for creating Hugging Face or Weights & Biases integration.

    Returns:
        Dict: A dictionary containing the prepared payload.
    """
    integration_details = {HUGGINGFACE_TOKEN: token}

    # Add additional details if it's Weights & Biases integration
    if integration_type == WEIGHTS_BIASES:
        integration_details = {
            WANDB_USERNAME: wandb_username,
            WANDB_KEY: token,
            WANDB_PROJECT: wandb_project
        }
    payload = {
        NAME: name,
        INTEGRATION_TYPE: integration_type,
        INTEGRATION_DETAILS: integration_details,
    }
    return payload


def get_integrations_table(response):
    """
    Prepares the table from the response of get_integrations function

    Returns:
        Dict: A table containing the details of all integrations
    """
    integrations_table = PrettyTable()
    integrations_table.field_names = ['ID', 'Name', 'Integration Type']
    for integration in response:
        integrations_table.add_row([
            integration.id,
            integration.name,
            integration.integration_type,
        ])
    return integrations_table


def get_details_table(response):
    """
    Prepares the table from the response of get_integration_details function

    Returns:
        Dict: A table containing the details of the integration id
    """
    details_table = PrettyTable()
    details_table.field_names = ['ID', 'Name', 'Integration Type', 'Created By', 'Created At', 'Integration Details']
    details_table.add_row([
        response.id,
        response.name,
        response.integration_type,
        response.created_by.email,
        response.created_at,
        response.integration_details
    ])
    return details_table
