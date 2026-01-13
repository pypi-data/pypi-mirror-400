import requests

from e2enetworks.constants import BASE_GPU_URL
from typing import Optional
from e2enetworks.cloud.tir import client
from e2enetworks.cloud.tir.utils import prepare_object


class APITokens:
    def __init__(
            self,
            team: Optional[str] = "",
            project: Optional[str] = "",
            location: Optional[str] = "",
    ):
        client_not_ready = (
            "Client is not ready. Please initiate client by:"
            "\n- Using e2enetworks.cloud.tir.init(...)"
        )
        if not client.Default.ready():
            raise ValueError(client_not_ready)

        if project:
            client.Default.set_project(project)

        if team:
            client.Default.set_team(team)

        if location:
            client.Default.set_location(location)

    def create(self, token_name):

        if not token_name:
            raise ValueError(token_name)

        payload = {
            "token_name": token_name,
        }
        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/auth-token/?project_id=" \
              f"{client.Default.project()}&"

        req = requests.Request('POST', url, data=payload)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def list(self):

        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/auth-token/?project_id={client.Default.project()}&"

        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def delete(self, token_id):
        if not token_id:
            raise ValueError(token_id)

        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/auth-token/{token_id}/?project_id=" \
              f"{client.Default.project()}&"

        req = requests.Request('DELETE', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    @staticmethod
    def help():
        print("APITokens Class Help")
        print("\t\t====================")
        print("\t\tThis class provides functionalities to manage API tokens.")
        print("\t\tAvailable methods:")
        print(
            "\t\t1. __init__(team, project): Initializes an APITokens instance with the specified team ID and "
            "project ID.")
        print("\t\t2. create(token_name): Creates a new API token with the provided authentication token.")
        print("\t\t3. list(): Lists all API tokens associated with the team and project.")
        print("\t\t4. delete(token_id): Deletes an API token with the given token ID.")
        print("\t\t7. help(): Displays this help message.")

        # Example usages
        print("\t\tExample usages:")
        print("\t\tapi_tokens = APITokens(123, 456)")
        print("\t\tapi_tokens.create('token_name')")
        print("\t\tapi_tokens.list()")
        print("\t\tapi_tokens.delete(789)")
