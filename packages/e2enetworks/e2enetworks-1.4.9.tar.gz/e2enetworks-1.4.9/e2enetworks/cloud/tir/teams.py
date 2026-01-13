import requests

from typing import Optional
from e2enetworks.constants import BASE_GPU_URL
from e2enetworks.cloud.tir import client
from e2enetworks.cloud.tir.utils import prepare_object


class Teams:
    def __init__(self):
        client_not_ready = (
            "Client is not ready. Please initiate client by:"
            "\n- Using e2enetworks.cloud.tir.init(...)"
        )
        if not client.Default.ready():
            raise ValueError(client_not_ready)

    def create(self, team_name):
        payload = {
            "team_name": team_name,
        }
        url = f"{BASE_GPU_URL}teams/"
        req = requests.Request('POST', url, data=payload)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def get(self, team_id):

        if type(team_id) != int:
            raise ValueError(team_id)

        url = f"{BASE_GPU_URL}teams/{team_id}/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def list(self):

        url = f"{BASE_GPU_URL}teams/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def delete(self, team_id):
        if type(team_id) != int:
            raise ValueError(team_id)

        url = f"{BASE_GPU_URL}teams/{team_id}/"
        req = requests.Request('DELETE', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    @staticmethod
    def help():
        print("Teams Class Help")
        print("\t\t================")
        print("\t\tThis class provides functionalities to interact with teams.")
        print("\t\tAvailable methods:")
        print("\t\t1. create(team_name): Creates a new team with the provided team name.")
        print("\t\t2. get(team_id): Retrieves information about a specific team using its ID.")
        print("\t\t3. list(): Lists all teams.")
        print("\t\t4. delete(team_id): Deletes a team with the given ID.")
        print("\t\t5. help(): Displays this help message.")

        # Example usages
        print("\t\tExample usages:")
        print("\t\tteams = Teams()")
        print("\t\tteams.create('Team Name')")
        print("\t\tteams.get(123)")
        print("\t\tteams.list()")
        print("\t\tteams.delete(123)")
        