from typing import Optional
import requests
from prettytable import PrettyTable

from e2enetworks.cloud.tir.finetuning.constants import (
    TEXT_MODELS_LIST, PLAN_NAME_ERROR,
    DEFAULT_TEXT_TRAINING_ARGS, DATASET_TYPES_LIST,
    DATASET_TYPE_ERROR, DEFAULT_IMAGE_TRAINING_ARGS,
    IMAGE_MODELS_LIST, INVALID_MODEL_NAME,
    SUPPORTED_MODELS_NOT_FOUND, FINETUNED,
    FAILED_TO_SHOW_FINETUNINGS, POD_NOT_FOUND,
    DETAILED_INFO, DEFAULT_FINETUNING_MODEL,
    SUCCEEDED, FINETUNING_NOT_SUCCEEDED,
    FINETUNING_MODEL_PATH, MODEL_ID_NOT_FOUND,
    )
from e2enetworks.constants import (
    INFERENCE, PIPELINE, CLIENT_NOT_READY_MESSAGE
    )
from e2enetworks.cloud.tir.skus import Plans, client
from e2enetworks.cloud.tir.utils import prepare_object
from e2enetworks.cloud.tir.finetuning.helpers import (
    get_supported_models_table, get_finetunings_table,
    get_sku_item_price_from_plan_name,
    get_model_training_inputs, get_finetuning_details,
    prepare_custom_endpoint_details,
    )


class FinetuningClient:
    def __init__(self, project: Optional[str] = None, location: Optional[str] = ""):
        if not client.Default.ready():
            raise ValueError(CLIENT_NOT_READY_MESSAGE)
        if project:
            client.Default.set_project(project)
        if location:
            client.Default.set_location(location)

    def create_finetuning(
        self,
        name: str,
        model_name: str,
        plan_name: str,
        huggingface_integration_id: str | int,
        dataset: str,
        dataset_type: str = "huggingface",
        wandb_integration_id: int = None,
        wandb_integration_run_name: str = "",
        description: str = None,
        training_type: str = "Peft",
        **training_args: dict
    ):
        if not isinstance(plan_name, str):
            return ValueError(PLAN_NAME_ERROR)
        if dataset_type not in DATASET_TYPES_LIST:
            raise ValueError(DATASET_TYPE_ERROR)

        if model_name in TEXT_MODELS_LIST:
            training_inputs = get_model_training_inputs(
                dataset,
                dataset_type,
                DEFAULT_TEXT_TRAINING_ARGS,
                **training_args)
        elif model_name in IMAGE_MODELS_LIST:
            training_inputs = get_model_training_inputs(
                dataset,
                dataset_type,
                DEFAULT_IMAGE_TRAINING_ARGS,
                **training_args)
        else:
            raise Exception(INVALID_MODEL_NAME)

        payload = {
            "name": name,
            "model_name": model_name,
            "huggingface_integration_id": huggingface_integration_id,
            "sku_item_price_id": get_sku_item_price_from_plan_name(plan_name=plan_name, service=PIPELINE, framework=None),
            "training_inputs": training_inputs,
            "training_type": training_type,
            "wandb_integration_id": wandb_integration_id if wandb_integration_id else None,
            "wandb_integration_run_name": wandb_integration_run_name,
            "description": description,
        }
        url = f"{client.Default.gpu_projects_path()}/finetuning/?"
        req = requests.Request('POST', url, json=payload)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def delete_finetuning(self, finetuning_id: str | int):
        url = f"{client.Default.gpu_projects_path()}/finetuning/{finetuning_id}/?"
        req = requests.Request('DELETE', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def stop_finetuning(self, finetuning_id: str | int):
        url = f"{client.Default.gpu_projects_path()}/finetuning/{finetuning_id}/?&action=terminate&"
        req = requests.Request('PUT', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def retry_finetuning(self, finetuning_id: str | int):
        url = f"{client.Default.gpu_projects_path()}/finetuning/{finetuning_id}/?&action=retry&"
        req = requests.Request('PUT', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def create_finetuning_inference(
        self,
        inference_name: str,
        finetuning_id: str | int,
        huggingface_integration_id: int,
        plan_name: str,
        disk_size: int = 120,
    ):
        is_success, data = self.get_finetuning_details(finetuning_id)
        if not is_success:
            raise Exception(FAILED_TO_SHOW_FINETUNINGS)
        if data.status != SUCCEEDED:
            raise Exception(FINETUNING_NOT_SUCCEEDED.format(status=data.status))
        if not data.model_details:
            raise Exception(MODEL_ID_NOT_FOUND.format(finetuning_id=finetuning_id))

        DETAILED_INFO["hugging_face_id"] = data.model_name if data.model_name else DEFAULT_FINETUNING_MODEL
        custom_endpoint_details = prepare_custom_endpoint_details(data, disk_size)

        payload = {
            "name": inference_name,
            "custom_endpoint_details": custom_endpoint_details,
            "model_id": data.model_details.id,
            "sku_item_price_id": get_sku_item_price_from_plan_name(plan_name, INFERENCE, FINETUNED),
            "committed_instance_policy": "",
            "replica": 1,
            "committed_replicas": 0,
            "path": FINETUNING_MODEL_PATH,
            "framework": FINETUNED,
            "is_auto_scale_enabled": False,
            "detailed_info": DETAILED_INFO,
            "model_load_integration_id": huggingface_integration_id,
        }
        url = f"{client.Default.gpu_team_projects_path()}/serving/inference/?"
        req = requests.Request('POST', url, json=payload)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def show_all_finetunings(self):
        is_success, data = self.get_all_finetunings()
        if not is_success:
            print(FAILED_TO_SHOW_FINETUNINGS)
            return
        finetunings_table = get_finetunings_table(data)
        print(finetunings_table)

    def show_finetuning_details(self, finetuning_id: str | int):
        is_success, data = self.get_finetuning_details(finetuning_id)
        if not is_success:
            print(FAILED_TO_SHOW_FINETUNINGS)
            return
        finetuning_details = get_finetuning_details(data)
        print(finetuning_details)

    def show_finetuning_logs(self, finetuning_id: str | int):
        is_success, data = self.get_finetuning_logs(finetuning_id)
        if not is_success:
            print(FAILED_TO_SHOW_FINETUNINGS)
            return
        print(data)

    def show_supported_models(self):
        is_success, data = self.get_supported_models()
        if not is_success:
            print(SUPPORTED_MODELS_NOT_FOUND)
            return
        supported_models_table = get_supported_models_table(data)
        print(supported_models_table)

    def show_plan_names(self):
        plans = Plans()
        plans_list = plans.list(PIPELINE)
        gpu_skus = plans_list["GPU"]
        plans_table = PrettyTable()
        plans_table.field_names = ['name', 'series', 'cpu', 'gpu', 'memory',
                                   'sku_item_price_id', 'sku_type', 'committed_days', 'unit_price']
        plans.insert_plans_in_table(gpu_skus, plans_table)
        print(plans_table)

    def show_text_model_training_inputs(self):
        """
        Prints the training inputs for text models with their default values.
        """
        print("Text Model Training Inputs:")
        for key, (type_, default, _) in DEFAULT_TEXT_TRAINING_ARGS.items():
            print(f"- {key}: {type_.__name__} (default: {default})")

    def show_image_model_training_inputs(self):
        """
        Prints the training inputs for image models with their default values.
        """
        print("Image Model Training Inputs:")
        for key, (type_, default, _) in DEFAULT_IMAGE_TRAINING_ARGS.items():
            print(f"- {key}: {type_.__name__} (default: {default})")

    def get_all_finetunings(self):
        url = f"{client.Default.gpu_projects_path()}/finetuning/?"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def get_finetuning_details(self, finetuning_id: str | int):
        url = f"{client.Default.gpu_projects_path()}/finetuning/{finetuning_id}/?"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def get_finetuning_logs(self, finetuning_id: str | int):
        is_success, data = self.get_finetuning_details(finetuning_id)
        if not is_success:
            raise Exception(FAILED_TO_SHOW_FINETUNINGS)
        run_pods = data.run_pods
        if not run_pods:
            raise Exception(POD_NOT_FOUND.format(finetuning_id=finetuning_id))
        url = f"{client.Default.gpu_projects_path()}/finetuning/{finetuning_id}/logs/?podname={run_pods[0].id}&"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def get_supported_models(self):
        url = f"{client.Default.gpu_projects_path()}/finetuning/model_types/?"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    @staticmethod
    def help():
        help_text = """
        FinetuningClient Class Help:

        This class provides methods for interacting with finetuning-related operations.
        Before using these methods, make sure to initialize the client using:
        - Using e2enetworks.cloud.tir.init(...)

        Available Methods:
        1. create_finetuning(
            self,
            name,
            model_name,
            plan_name,
            huggingface_integration_id,
            dataset,
            dataset_type,
            wandb_integration_id=None,
            wandb_integration_run_name="",
            description=None,
            training_type="Peft",
            **training_args
        )
            - Create a new finetuning.
            Note: Training inputs should be passed in **training_args as a dictionary.

        2. delete_finetuning(finetuning_id)
            - Delete a specific finetuning.

        3. stop_finetuning(finetuning_id)
            - Stop a specific finetuning.

        4. retry_finetuning(finetuning_id)
            - Retry a failed/terminated finetuning.

        5. create_finetuning_inference(
            self,
            inference_name,
            finetuning_id,
            huggingface_integration_id,
            plan_name,
            disk_size=120
        )
            - Create a new inference endpoint from a finetuning.

        6. show_all_finetunings()
            - Display a table of all finetunings.

        7. show_finetuning_details(finetuning_id)
            - Display detailed information about a specific finetuning.

        8. show_finetuning_logs(finetuning_id)
            - Show the finetuning logs.

        9. show_supported_models()
            - List currently supported models for finetuning.

        10. show_plan_names()
            - List currently supported SKUs for finetuning.

        11. show_text_model_training_inputs()
            - Print text model training inputs and defaults.

        12. show_image_model_training_inputs()
            - Print image model training inputs and defaults.

        13. get_all_finetunings()
            - Get details of all existing finetunings.

        14. get_finetuning_details(finetuning_id)
            - Get details of a specific finetuning.

        15. get_finetuning_logs(finetuning_id)
            - Get details of finetuning logs.

        16. get_supported_models()
            - Get currently supported models for finetuning.

        Note: Certain methods require specific arguments. Refer to the method signatures for details.
        """
        print(help_text)
