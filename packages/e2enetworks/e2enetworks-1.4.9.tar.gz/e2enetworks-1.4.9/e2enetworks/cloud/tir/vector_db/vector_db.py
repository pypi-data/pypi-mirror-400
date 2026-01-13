import requests

from e2enetworks.constants import BASE_GPU_URL, VECTOR_DB
from e2enetworks.cloud.tir.helpers import plan_name_to_sku_item_price_id
from e2enetworks.cloud.tir.skus import client, Plans
from e2enetworks.cloud.tir.utils import prepare_object


class VectorDB:

    def __init__(self, team=None, project=None, location=None):
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

    def create(
        self,
        name,
        plan_name,
        replicas=3,
    ):
        skus_list, _ = Plans().get_plans_list(VECTOR_DB)
        sku_item_price_id = plan_name_to_sku_item_price_id(skus_list, plan_name)
        if not sku_item_price_id:
            raise ValueError("Enter a valid plan_name.")

        req = requests.Request(
            method='POST',
            url=f"{BASE_GPU_URL}/teams/{client.Default.team()}/projects/{client.Default.project()}/vector_db/",
            json={
                "disk_size": 30,
                "name": name,
                "replicas": replicas,
                "sku_item_price_id": sku_item_price_id
            }
        )
        return prepare_object(client.Default.make_request(req))

    def list(self):
        response = client.Default.make_request(
            requests.Request(
                method='GET',
                url=f"{BASE_GPU_URL}/teams/{client.Default.team()}/projects/{client.Default.project()}/vector_db/"
            )
        )
        return prepare_object(response)

    def details(self, vectordb_id):
        response = client.Default.make_request(
            requests.Request(
                method='GET',
                url=f"{BASE_GPU_URL}/teams/{client.Default.team()}/projects/{client.Default.project()}/vector_db/{vectordb_id}/"
            )
        )
        if response.status_code == 200:
            return response.json()["data"]
        return prepare_object(response)

    def delete(self, vectordb_id):
        response = client.Default.make_request(
            requests.Request(
                method='DELETE',
                url=f"{BASE_GPU_URL}/teams/{client.Default.team()}/projects/{client.Default.project()}/vector_db/{vectordb_id}/"
            )
        )
        return prepare_object(response)

    def upgrade_nodes(self, vectordb_id, replicas):
        response = client.Default.make_request(
            requests.Request(
                method='PUT',
                url=f"{BASE_GPU_URL}/teams/{client.Default.team()}/projects/{client.Default.project()}/vector_db/{vectordb_id}/",
                json={"replicas": replicas}
            )
        )
        return prepare_object(response)

    def upgrade_disk_size(self, vectordb_id, disk_size):
        response = client.Default.make_request(
            requests.Request(
                method='PUT',
                url=f"{BASE_GPU_URL}/teams/{client.Default.team()}/projects/{client.Default.project()}/vector_db/{vectordb_id}/pvcs/",
                json={"disk_size": disk_size}
            )
        )
        return prepare_object(response)

    def create_snapshot(self, vectordb_id):
        response = client.Default.make_request(
            requests.Request(
                method='POST',
                url=f"{BASE_GPU_URL}/teams/{client.Default.team()}/projects/{client.Default.project()}/vector_db/{vectordb_id}/snapshot/",
                json={}
            )
        )
        return prepare_object(response)

    def list_snapshots(self, vectordb_id):
        response = client.Default.make_request(
            requests.Request(
                method='GET',
                url=f"{BASE_GPU_URL}/teams/{client.Default.team()}/projects/{client.Default.project()}/vector_db/{vectordb_id}/snapshot/",
            )
        )
        return prepare_object(response)

    def restore_snapshot(self, vectordb_id, snapshot_id):
        response = client.Default.make_request(
            requests.Request(
                method='PUT',
                url=f"{BASE_GPU_URL}/teams/{client.Default.team()}/projects/{client.Default.project()}/vector_db/{vectordb_id}/snapshot/{snapshot_id}/restore/",
            )
        )
        return prepare_object(response)

    def delete_snapshot(self, vectordb_id, snapshot_id):
        response = client.Default.make_request(
            requests.Request(
                method='DELETE',
                url=f"{BASE_GPU_URL}/teams/{client.Default.team()}/projects/{client.Default.project()}/vector_db/{vectordb_id}/snapshot/{snapshot_id}/",
            )
        )
        return prepare_object(response)

    @staticmethod
    def help():
        print("\t\tVectorDB Class Help")
        print("\t\t===================")
        help_text = """
                A class to manage operations on Vector Databases (VectorDB).

                This class provides methods to create, list, and manage vector databases,
                including details about the database, upgrading resources, and snapshot management.

                Methods:
                --------
                1. create(name: str, plan_name: str, replicas(optional): int)
                    Creates a new vector database with the specified name, size, and replicas.

                2. list()
                    Lists all existing vector databases.

                3. details(vectordb_id: int)
                    Retrieves details of a specific vector database given its ID.

                4. delete(vectordb_id: int)
                    Deletes a vector database specified by its ID.

                5. upgrade_nodes(vectordb_id: int, replicas: int)
                    Upgrades the number of replicas for the specified vector database.

                6. upgrade_disk_size(vectordb_id: int, disk_size: int)
                    Upgrades the disk size for the specified vector database.

                7. create_snapshot(vectordb_id: int)
                    Creates a snapshot for the specified vector database.

                8. list_snapshots(vectordb_id: int)
                    Lists all snapshots for the specified vector database.

                9. restore_snapshot(vectordb_id: int, snapshot_id: int)
                    Restores a vector database to a specific snapshot state.

                10. delete_snapshot(vectordb_id: int, snapshot_id: int)
                    Deletes a specific snapshot for the vector database.

                Examples:
                ---------

                # Create a new VectorDB
                vdb = VectorDB()
                vdb.create("my_db", "CPU-C3-4-8GB-0", 5)

                # List all VectorDBs
                vdb.list()

                # Get details of a specific VectorDB
                details = vdb.details(vectordb_id)

                # Delete a VectorDB
                vdb.delete(vectordb_id)

                # Upgrade the number of replicas
                vdb.upgrade_nodes(vectordb_id, 5)

                # Upgrade the disk size
                vdb.upgrade_disk_size(vectordb_id, 200)

                # Create a snapshot
                vdb.create_snapshot(vectordb_id)

                # List all snapshots
                vdb.list_snapshts(vectordb_id)

                # Restore a snapshot
                vdb.restore_snapshot(vectordb_id, snapshot_id)

                # Delete a snapshot
                vdb.delete_snapshot(vectordb_id, snapshot_id)
                """
        print(help_text)
