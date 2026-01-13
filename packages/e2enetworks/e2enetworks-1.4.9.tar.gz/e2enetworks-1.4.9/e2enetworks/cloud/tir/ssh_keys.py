import requests

from e2enetworks.cloud.tir import client
from e2enetworks.cloud.tir.utils import prepare_object
from e2enetworks.constants import BASE_GPU_URL


class SSHKeys:

    def __init__(self):
        client_not_ready = (
            "Client is not ready. Please initiate client by:"
            "\n- Using e2enetworks.cloud.tir.init(...)"
        )
        if not client.Default.ready():
            raise ValueError(client_not_ready)

    def add(self, label, ssh_key):
        url = f"{BASE_GPU_URL}ssh_keys/"
        req = requests.Request('POST', url, json={"label": label, "ssh_key": ssh_key})
        response = client.Default.make_request(req)
        if response.status_code == 200:
            print("Successfully added SSH key.")
        return prepare_object(response)

    def list(self):
        url = f"{BASE_GPU_URL}ssh_keys/"
        req = requests.Request('GET', url)
        return prepare_object(client.Default.make_request(req))

    def sync(self):
        url = f"{BASE_GPU_URL}ssh_keys/sync/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        if response.status_code == 200:
            print("Successfully synced.")
        return prepare_object(response)

    def delete(self, id):
        url = f"{BASE_GPU_URL}ssh_keys/{id}/"
        req = requests.Request('DELETE', url)
        response = client.Default.make_request(req)
        if response.status_code == 200:
            print("Successfully deleted SSH key.")
        return prepare_object(response)

    @staticmethod
    def help():
        print("\t\tSSHKeys Class Help")
        print("\t\t===================")
        help_text = """
                SSHKeys class provides methods for ssh-keys related operations.

                Available methods:
                1. Add a new ssh-key.
                    add(
                        label(required): String,
                        ssh_key(required): String
                    )
                2. List all ssh-keys.
                    list()
                3. Sync ssh-keys with my-account.
                    sync()
                4. Delete a ssh-key.
                    delete(
                        id(required): integer => obtain from list() method
                    )

                Usage:
                ssh_key = SSHKeys()
                ssh_key.add(label, ssh_key)
                ssh_key.list()
                ssh_key.sync()
                ssh_key.delete(id)
                """
        print(help_text)
