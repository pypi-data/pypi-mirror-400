from typing import Dict, Optional

import requests
import json

from e2enetworks.constants import headers
from e2enetworks.constants import BASE_GPU_URL
from e2enetworks.cloud.tir.constants import ARGUMENT_IS_MANDATORY
from e2enetworks.cloud.tir.helpers import plan_name_to_sku_item_price_id
from e2enetworks.cloud.tir.skus import Plans, client
from e2enetworks.constants import PIPELINE
from e2enetworks.cloud.tir.utils import prepare_object


class PipelineClient:
    def __init__(
        self,
        project: Optional[str] = None,
        location: Optional[str] = None,
    ):  
        client_not_ready = (
            "Client is not ready. Please initiate client by:"
            "\n- Using e2enetworks.cloud.tir.init(...)"
        )
        if not client.Default.ready():
            raise ValueError(client_not_ready)
        
        if project:
            client.Default.set_project(project)

        if location:
            client.Default.set_location(location)

    def create_pipeline(
        self,
        name,
        file_path,
        description=''
    ):
        if not name or not file_path:
            raise ValueError(f"name and file {ARGUMENT_IS_MANDATORY}")
        file = open(file_path, 'rb')
        files = [
            ('uploadfile',
             (file.name, file, 'application/octet-stream'))
        ]
        url = f"{client.Default.gpu_projects_path()}/pipelines/upload/?name={name}&description={description}&"
        req = requests.Request('POST', url, files=files)
        response = client.Default.make_request(req)
        return prepare_object(response)
    
    def list_pipelines(self):
        url = f"{client.Default.gpu_projects_path()}/pipelines/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def get_pipeline(
        self,
        pipeline_id: str = ''
    ):
        if not pipeline_id:
            raise ValueError(f"PIPELINE_ID {ARGUMENT_IS_MANDATORY}")
        url = f"{client.Default.gpu_projects_path()}/pipelines/{pipeline_id}/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def delete_pipeline(
        self,
        pipeline_id: str = ''
    ):
        if not pipeline_id:
            raise ValueError(f"PIPELINE_ID {ARGUMENT_IS_MANDATORY}")
        url = f"{client.Default.gpu_projects_path()}/pipelines/{pipeline_id}/"
        req = requests.Request('DELETE', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    # APIS for Pipeline Versions

    def create_pipeline_version(
        self,
        name,
        file_path,
        pipeline_id: str = '',
        description=''
    ):
        if not name:
            raise ValueError(f"name {ARGUMENT_IS_MANDATORY}")
        if not file_path:
            raise ValueError(f"yaml file {ARGUMENT_IS_MANDATORY}")
        if not pipeline_id:
            raise ValueError(f"pipeline_id {ARGUMENT_IS_MANDATORY}")

        file = open(file_path, 'rb')
        files = [
            ('uploadfile',
             (file.name, file, 'application/octet-stream'))
        ]
        url = f"{client.Default.gpu_projects_path()}/pipelines/upload/?name={name}&description={description}&" \
              f"pipeline_id={pipeline_id}&"
        req = requests.Request('POST', url, files=files)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def list_pipeline_version(
            self,
            pipeline_id: str = ''
    ):
        if not pipeline_id:
            raise ValueError(f"PIPELINE_ID {ARGUMENT_IS_MANDATORY}")
        url = f"{client.Default.gpu_projects_path()}/pipelines/{pipeline_id}/versions/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def get_pipeline_version(
        self,
        pipeline_id: str = '',
        version_id: str = ''
    ):
        if not pipeline_id:
            raise ValueError(f"PIPELINE_ID {ARGUMENT_IS_MANDATORY}")
        url = f"{client.Default.gpu_projects_path()}/pipelines/{pipeline_id}/versions/{version_id}/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def delete_pipeline_version(
        self,
        pipeline_id: str = '',
        version_id: str = ''
    ):
        if not pipeline_id:
            raise ValueError(f"PIPELINE_ID {ARGUMENT_IS_MANDATORY}")
        url = f"{client.Default.gpu_projects_path()}/pipelines/{pipeline_id}/versions/{version_id}/"
        req = requests.Request('DELETE', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def create_experiment(
        self,
        name: str,
        description: Optional[str] = None,
    ):
        request_params = {
            'name': name,
            'description': description,
        }
        url = f"{client.Default.gpu_projects_path()}/pipelines/experiments/"
        req = requests.Request('POST', url, data=request_params)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def list_experiments(
        self
    ):
        url = f"{client.Default.gpu_projects_path()}/pipelines/experiments/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def get_experiment(
        self,
        experiment_id: str = '',
    ):
        if not experiment_id:
            raise ValueError(f"EXPERIMENT_ID {ARGUMENT_IS_MANDATORY}")
        url = f"{client.Default.gpu_projects_path()}/pipelines/experiments/{experiment_id}/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def delete_experiment(
        self,
        experiment_id: str = '',
    ):

        if not experiment_id:
            raise ValueError(f"EXPERIMENT_ID {ARGUMENT_IS_MANDATORY}")

        url = f"{client.Default.gpu_projects_path()}/pipelines/experiments/{experiment_id}/"
        req = requests.Request('DELETE', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def create_run(
        self,
        name: str,
        plan_name=None,
        description: str = '',
        experiment_id: str = '',
        pipeline_version_id: str = '',
    ):
        if not plan_name:
            return ValueError(f"plan_name is necessary")
        if not name or not experiment_id or not pipeline_version_id:
            raise ValueError(f"name, experiment_id, pipeline_version_id {ARGUMENT_IS_MANDATORY}")
        skus, skus_table = Plans().get_plans_list(PIPELINE)
        payloads = json.dumps({"name": name,
                    "description": description,
                    "experiment_id": experiment_id,
                    "sku_item_price_id": plan_name_to_sku_item_price_id(skus, plan_name),
                    "pipeline_version_id": pipeline_version_id})
        headers['Authorization'] = f'Bearer {client.Default.access_token()}'
        url = f"{client.Default.gpu_projects_path()}/pipelines/runs/?apikey={client.Default.api_key()}&location={client.Default.location()}"
        response = requests.post(url=url, headers=headers, data=payloads)
        return response

    def list_runs(self):
        url = f"{client.Default.gpu_projects_path()}/pipelines/runs/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def get_run(self, run_id):
        if not run_id:
            raise ValueError(f"RUN_ID {ARGUMENT_IS_MANDATORY}")
        url = f"{client.Default.gpu_projects_path()}/pipelines/runs/{run_id}/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def delete_run(self, run_id):
        if not run_id:
            raise ValueError(f"RUN_ID {ARGUMENT_IS_MANDATORY}")

        url = f"{client.Default.gpu_projects_path()}/pipelines/runs/{run_id}/"
        req = requests.Request('DELETE', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    @staticmethod
    def help():
        help_text = """
        PipelineClient Class Help:

        This class provides methods for interacting with pipeline-related operations.
        Before using these methods, make sure to initialize the client using:
        - Using e2enetworks.cloud.tir.init(...)

        Available Methods:
        1. create_pipeline(name, description, file_path)
           - Create a new pipeline.
        2. list_pipelines()
           - List existing pipelines.
        3. get_pipeline(pipeline_id)
           - Get details of a specific pipeline.
        4. delete_pipeline(pipeline_id)
           - Delete a specific pipeline.
        5. create_pipeline_version(name, description, file_path, pipeline_id)
           - Create a new pipeline version.
        6. list_pipeline_version(pipeline_id)
           - List all versions of a pipeline.
        7. get_pipeline_version(pipeline_id, version_id)
           - Get details of a specific pipeline version.
        8. delete_pipeline_version(pipeline_id, version_id)
           - Delete a specific pipeline version.
        9. create_experiment(name, description=None)
           - Create a new experiment.
        10. list_experiments()
           - List existing experiments.
        11. get_experiment(experiment_id='')
           - Get details of a specific experiment.
        12. delete_experiment(experiment_id='')
           - Delete a specific experiment.
        13. create_run(name='', description='', experiment_id='', pipeline_version_id='', service_account='')
           - Create a new run.
        14. list_runs()
            - List existing runs.
        15. get_run(run_id='')
            - Get details of a specific run.
        16. delete_run(run_id='')
            - Delete a specific run.

        Note: Certain methods require specific arguments. Refer to the method signatures for details.
        """
        print(help_text)
