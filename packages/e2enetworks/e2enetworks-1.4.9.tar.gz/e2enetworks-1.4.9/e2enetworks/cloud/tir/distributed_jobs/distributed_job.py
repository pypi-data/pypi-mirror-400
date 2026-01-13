from typing import Optional

from prettytable import PrettyTable
import requests

from e2enetworks.cloud.tir import client
from e2enetworks.cloud.tir.distributed_jobs.helpers import (convert_to_base64,
                                                            decode_base64)
from e2enetworks.constants import CLIENT_NOT_READY_MESSAGE
from e2enetworks.cloud.tir.utils import prepare_object


class DistributedJobClient:
    def __init__(self,
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

    def submit_pytorch_job(
        self,
        name: str,
        image: str,
        job_cpu: int,
        job_gpu: int,
        job_memory: int,
        cluster_id: int,
        master_replica: int,
        master_commands: list[str],
        worker_replica: int,
        worker_commands: list[str],
        sfs_id: int = None,
        sfs_mount_path: str = "/mnt/data",
        image_type: str = "public",
        image_pull_policy: str = "IfNotPresent",
        env: list = [],
        _get_raw: bool = False,
        **kwargs
    ):
        url = f"{client.Default.gpu_team_projects_path()}/distributed_jobs/jobs/?"
        payload = {"name": name,
                   "job_type": "PytorchJob",
                   "job_cpu": job_cpu,
                   "job_gpu": job_gpu,
                   "job_memory": job_memory,
                   "cluster_id": cluster_id,
                   "sfs_id": sfs_id,
                   "sfs_mount_path": sfs_mount_path,
                   "master_replica": master_replica,
                   "master_commands": convert_to_base64(str(master_commands)),
                   "worker_replica": worker_replica,
                   "worker_commands": convert_to_base64(str(worker_commands)),
                   "image_url": image,
                   "image_type": image_type,
                   "image_pull_policy": image_pull_policy,
                   "environmentVariable": env}
        if not sfs_id:
            payload.pop("sfs_id", "")
        req = requests.Request('POST', url, json=payload)
        response = client.Default.make_request(req)
        return prepare_object(response, _get_raw)

    def list_jobs(self,
                  _get_raw: bool = False):
        url = f"{client.Default.gpu_team_projects_path()}/distributed_jobs/jobs/?"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response, _get_raw)

    def list_clusters(self,
                      _get_raw: bool = False):
        url = f"{client.Default.gpu_team_projects_path()}/distributed_jobs/cluster/?"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response, _get_raw)

    def describe_cluster(self,
                         cluster_id: int,
                         _get_raw: bool = False):
        url = f"{client.Default.gpu_team_projects_path()}/distributed_jobs/cluster/{cluster_id}/?"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response, _get_raw)

    def list_sfs(self,
                 _get_raw: bool = False):
        url = f"{client.Default.gpu_team_projects_path()}/distributed_jobs/sfs/?"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response, _get_raw)

    def describe_job(self,
                     job_id: int,
                     _get_raw: bool = False):
        url = f"{client.Default.gpu_team_projects_path()}/distributed_jobs/jobs/{job_id}/?"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response, _get_raw)

    def delete_job(self,
                   job_id: int,
                   _get_raw: bool = False):
        url = f"{client.Default.gpu_team_projects_path()}/distributed_jobs/jobs/{job_id}/?"
        req = requests.Request('DELETE', url)
        response = client.Default.make_request(req)
        return prepare_object(response, _get_raw)

    def terminate_job(self,
                      job_id: int,
                      _get_raw: bool = False):
        url = f"{client.Default.gpu_team_projects_path()}/distributed_jobs/jobs/{job_id}/?&action=terminate&"
        req = requests.Request('PUT', url)
        response = client.Default.make_request(req)
        return prepare_object(response, _get_raw)

    def get_job_pods(self,
                     job_id: int,
                     _get_raw: bool = False):
        url = f"{client.Default.gpu_team_projects_path()}/distributed_jobs/jobs/{job_id}/pods/?"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response, _get_raw)

    def get_job_events(self,
                       job_id: int,
                       _get_raw: bool = False):
        url = f"{client.Default.gpu_team_projects_path()}/distributed_jobs/jobs/{job_id}/events/?"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response, _get_raw)

    def get_job_logs(self,
                     job_id: int,
                     pod_name: str,
                     _get_raw: bool = False):
        url = f"{client.Default.gpu_team_projects_path()}/distributed_jobs/jobs/{job_id}/logs/{pod_name}/?"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response, _get_raw)

    def show_job_logs(self,
                      job_id: int,
                      pod_name: str):
        is_success, data = self.get_job_logs(job_id, pod_name)
        if is_success:
            print(data.logs)

    def show_job_collective_details(self,
                                    job_id: int):
        is_detail_success, details_resp = self.describe_job(job_id)
        is_pod_success, pods_resp = self.get_job_pods(job_id)
        if is_pod_success == is_detail_success == True:
            main_table = PrettyTable()
            main_table.field_names = ["Field", "value"]
            # Add nested tables to the main table
            for key, value in details_resp.__dict__.items():
                if key not in ['id', 'name', 'job_type', 'status']:
                    continue
                main_table.add_row([key, value])
            main_table.add_row(['', ''])
            nested_table = self._create_pods_sub_table(pods_resp)
            main_table.add_row(['pods', nested_table.get_string()])
            print(main_table)
            print(f"for more info visit : https://gpu-notebooks.e2enetworks.com/teams/{client.Default.team()}/projects/{client.Default.project()}/distributedtraining/?section=training&job_id=1&tab=pod_logs")

    def _create_pods_sub_table(self, pods_array):
        table = PrettyTable()
        table.field_names = ["name", "last_state"]
        for pod in pods_array:
            table.add_row([pod.pod_name, pod.status])
        return table

    @staticmethod
    def help():
        help_text = """
        jobClient Class Help:

        This class provides methods for interacting with job-related operations.
        Before using these methods, make sure to initialize the client using:
        - Using e2enetworks.cloud.tir.init(...)

        Available Methods:
        1. submit_pytorch_job(
            self,
            name: str,
            image: str,
            job_cpu: int,
            job_gpu: int,
            job_memory: int,
            cluster_id: int,
            sfs_id: int,
            sfs_mount_path: str,
            master_replica: int,
            master_commands: list[str],
            worker_replica: int,
            worker_commands: list[str],
            image_type="public",
            image_pull_policy="public",
            environmentVariable: list = [],
            **kwargs
        ):
            - Create a new job.

        2. list_jobs()
            - List existing jobs.

        3. describe_job(job_id)
            - Get details of a specific job.

        4. delete_job(job_id)
            - Delete a specific job.

        5. terminate_job(job_id)
            - Stop a specific job.

        6. list_clusters()
            - List currently available clusters for job.

        7. list_sfs()
            - List available sfs for job.

        Note: Certain methods require specific arguments. Refer to the method signatures for details.
        """
        print(help_text)
