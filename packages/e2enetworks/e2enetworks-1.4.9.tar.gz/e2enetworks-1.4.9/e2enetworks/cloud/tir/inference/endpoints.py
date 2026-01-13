import json
from typing import Optional

import requests

from e2enetworks.cloud.tir.datasets.datasets import Datasets
from e2enetworks.cloud.tir.skus import Plans, client
from e2enetworks.cloud.tir.helpers import plan_to_sku_id, convert_to_base64
from e2enetworks.cloud.tir.utils import prepare_object
from e2enetworks.constants import (BASE_GPU_URL, INFERENCE, PYTORCH, TRITON,TENSORRT,PRIVATE,REGISTRY,
                                   headers, TIR_CUSTOM_FRAMEWORKS, ALLOWED_CONTAINER_IMAGES, STABLE_DIFFUSION,
                                   STABLE_DIFFUSION_XL, STABLE_VIDEO_DIFFUSION_XT, ASYNC_DATASET_RESPONSE_PATH,
                                   ASYNC_STATUS_FETCH_URL, DATE_FILTER_TYPES, DateFilterType)

containers = {
    "stable-video-diffusion-img2vid-xt_eos": "aimle2e/stable-video-diffusion:v1_eos",
    "stable_diffusion_eos": "registry.e2enetworks.net/aimle2e/stable-diffusion-2-1:eos-v1",
    "stable_diffusion_xl_eos": "registry.e2enetworks.net/aimle2e/stable-diffusion-xl-base-1.0:eos-v1",
}
eos_framework = [STABLE_VIDEO_DIFFUSION_XT, STABLE_DIFFUSION, STABLE_DIFFUSION_XL]


class EndPoints:
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

    def list_plans(self,framework):
        if framework not in TIR_CUSTOM_FRAMEWORKS:
            raise ValueError(f"framework {framework} is not supported. framework should be one of: %s" % TIR_CUSTOM_FRAMEWORKS)
        return Plans().list_endpoint_plans(framework=framework)
    
    def list_frameworks(self):
        print(TIR_CUSTOM_FRAMEWORKS)
        return TIR_CUSTOM_FRAMEWORKS

    def get_container_name(self, framework, container_name=None, model_id=None):
        if framework not in TIR_CUSTOM_FRAMEWORKS:
            raise ValueError(f"framework {framework} is not supported. framework should be one of: %s" % TIR_CUSTOM_FRAMEWORKS)
        if framework == "custom":
            return container_name
        if model_id and framework in eos_framework:
            return containers[framework+'_eos'] if framework+'_eos' in containers else None
        else:
            return ALLOWED_CONTAINER_IMAGES[framework] if framework in TIR_CUSTOM_FRAMEWORKS else None
        
    def get_container_type(self, framework):
        if framework in TIR_CUSTOM_FRAMEWORKS:
            return 'public'
        else:
            return 'private'

    def create_triton(self, endpoint_name, plan, model_id, container_name=None,
                                        model_path='', is_auto_scale_enabled=False, metric="cpu",
                                        replicas=1, commands=[], value=12, disk_size=30, env_variables=[],
                                        world_size=1, mount_path='', min_replicas=1, max_replicas=2):
        if not endpoint_name:
            raise ValueError(endpoint_name)
        if not plan:
            raise ValueError(plan)
        if not model_id:
            raise ValueError(model_id)

        args = "['mpirun','--allow-run-as-root','-n', '1','tritonserver','--exit-on-error=false','--model-store=/mnt/models','--grpc-port=9000','--http-port=8080','--metrics-port=8082','--allow-grpc=true','--allow-http=true']"
        args = convert_to_base64(args)
        commands = convert_to_base64(str(commands))
        return self.create_inference_for_framework(endpoint_name=endpoint_name,
                                                   plan=plan,
                                                   model_path=model_path,
                                                   model_id=model_id,
                                                   commands=commands,
                                                   value=value,
                                                   disk_size=disk_size,
                                                   env_variables=env_variables,
                                                   world_size=world_size,
                                                   mount_path=mount_path,
                                                   min_replicas=min_replicas,
                                                   max_replicas=max_replicas,
                                                   replicas=replicas,
                                                   framework=TRITON,
                                                   container_name=container_name,
                                                   metric=metric,
                                                   args=args,
                                                   is_auto_scale_enabled=is_auto_scale_enabled)

    def create_tensorrt(self, endpoint_name, plan, model_id, container_name,
                                        model_path='', is_auto_scale_enabled=False, metric="cpu",
                                        replicas=1, commands=[], value=12, disk_size=30, env_variables=[],
                                        world_size=1, mount_path='', min_replicas=1, max_replicas=2):
        if not endpoint_name:
            raise ValueError(endpoint_name)
        if not plan:
            raise ValueError(plan)
        if not model_id:
            raise ValueError(model_id)

        args = "['mpirun','--allow-run-as-root','-n', '1','tritonserver','--exit-on-error=false','--model-store=/mnt/models','--grpc-port=9000','--http-port=8080','--metrics-port=8082','--allow-grpc=true','--allow-http=true']"
        args = convert_to_base64(args)
        commands = convert_to_base64(str(commands))
        return self.create_inference_for_framework(endpoint_name=endpoint_name,
                                                   plan=plan,
                                                   model_path=model_path,
                                                   model_id=model_id,
                                                   commands=commands,
                                                   value=value,
                                                   disk_size=disk_size,
                                                   env_variables=env_variables,
                                                   world_size=world_size,
                                                   mount_path=mount_path,
                                                   min_replicas=min_replicas,
                                                   max_replicas=max_replicas,
                                                   replicas=replicas,
                                                   framework=TENSORRT,
                                                   container_name=container_name,
                                                   metric=metric,
                                                   args=args,
                                                   is_auto_scale_enabled=is_auto_scale_enabled)

    def create_pytorch(self, endpoint_name, plan, model_id, container_name,
                                        model_path='', is_auto_scale_enabled=False,
                                        metric="cpu", replicas=1, commands=[], value=12, disk_size=30, env_variables=[], 
                                        world_size=1, mount_path='', min_replicas=1, max_replicas=2):
        if not endpoint_name:
            raise ValueError(endpoint_name)
        if not plan:
            raise ValueError(plan)
        if not model_id:
            raise ValueError(model_id)
        
        args = "['torchserve','--start', '--model-store=/mnt/models/model-store','--ts-config=/mnt/models/config/config.properties']"
        args = convert_to_base64(args)
        commands = convert_to_base64(str(commands))
        return self.create_inference_for_framework(endpoint_name=endpoint_name,
                                                   container_name=container_name,
                                                   metric=metric,
                                                   args=args,
                                                   commands=commands,
                                                   value=value,
                                                   disk_size=disk_size,
                                                   env_variables=env_variables,
                                                   world_size=world_size,
                                                   mount_path=mount_path,
                                                   min_replicas=min_replicas,
                                                   max_replicas=max_replicas,
                                                   plan=plan,
                                                   model_path=model_path,
                                                   model_id=model_id,
                                                   replicas=replicas,
                                                   framework=PYTORCH,
                                                   is_auto_scale_enabled=is_auto_scale_enabled)

    def create_inference_for_framework(self, endpoint_name, container_name, plan,
                                        model_path, model_id, framework, is_auto_scale_enabled,
                                        args, metric="cpu", replicas=1, commands=[], value=12, disk_size=50, env_variables=[],
                                        world_size=1, mount_path='', min_replicas=1, max_replicas=2):
        skus = Plans().get_skus_list(INFERENCE, framework=framework)
        sku_id = plan_to_sku_id(skus=skus, plan=plan)

        if not sku_id:
            raise ValueError(plan)

        payload = {
            "name": endpoint_name,
            "world_size": world_size,
            "custom_endpoint_details": {
                "container": {
                    "container_name": container_name,
                    "container_type": "public",
                    "advance_config": {
                        "image_pull_policy": "Always",
                    }
                },
                "resource_details": {
                    "disk_size": disk_size,
                    "mount_path": mount_path,
                    "env_variables": env_variables
                },
            },
            "model_id": model_id,
            "sku_id": sku_id,
            "replica": replicas,
            "path": model_path,
            "framework": framework,
            "is_auto_scale_enabled": is_auto_scale_enabled,
            "detailed_info": {
                "commands": commands,
                "args": args,
            },
        }

        if is_auto_scale_enabled:
            rules = [
                {
                    "metric": metric,
                    "condition_type": "limit",
                    "value": value,
                    "watch_period": "60"
                }
            ]
            
            auto_scale_policy = {
                "min_replicas": min_replicas,
                "max_replicas": max_replicas,
                "rules": rules,
                "stability_period": "300"
            }
            payload["auto_scale_policy"] = auto_scale_policy

        payload = json.dumps(payload)
        headers['Authorization'] = f'Bearer {client.Default.access_token()}'
        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/serving/inference/"
        req = requests.Request('POST', url=url, data=payload, headers=headers)
        response = client.Default.make_request(req)
        if response.ok:
            print(f"To check the Inference Status and logs, PLease visit "
                f"https://gpu-notebooks.e2enetworks.com/projects/{client.Default.project()}/model-endpoints")
        return prepare_object(response)
    
    def registry_namespace_list(self):
        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/container_registry/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)
    
    def registry_detail(self, registry_namespace_id):
        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/container_registry/{registry_namespace_id}/namespace-repository/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def create(self, endpoint_name, framework, plan, is_auto_scale_enabled=False, 
               registry_namespace_id=None, model_id=None, container_name=None, container_type="public",commands=[],args=[],
               replicas=1, disc_size=50, world_size=1, model_path="", env_variables=[], mount_path="", metric="cpu", value=12, min_replicas=1, max_replicas=2,
               hugging_face_id=None, hf_token_ingration_id=None, dataset_id=None, dataset_path=None, initial_delay_seconds=10, period_seconds=10, timeout_seconds=10,
               failure_threshold=3, success_threshold=1, liveness_probe_protocol='http', readiness_probe_protocol='http', probe_url="/metrics", liveness_commands='', readiness_commands=''):
        if not endpoint_name:
            raise ValueError(endpoint_name)
        if not framework:
            raise ValueError(framework)
        if not plan:
            raise ValueError(plan)

        skus = Plans().get_skus_list(INFERENCE, framework=framework)
        sku_id = plan_to_sku_id(skus=skus, plan=plan)
        if not sku_id:
            raise ValueError(plan)

        container_name = self.get_container_name(container_name=container_name, model_id=model_id, framework=framework)
        if not container_name:
            raise ValueError(container_name)
        if container_name == 'vllm/vllm-openai:latest' and not ((hugging_face_id == None) ^ (model_id == None)):
            raise ValueError("Hugging Face ID is required.")

        private_image_details = {}
        if container_type == PRIVATE:
            private_image_details = {"registry_namespace_id": registry_namespace_id}
            container_name = REGISTRY+"/"+container_name

        args = convert_to_base64(str(args))
        commands = convert_to_base64(str(commands))
        payload = {
                "name": endpoint_name,
                "world_size": world_size,
                "custom_endpoint_details": {
                    "container": {
                        "container_name": container_name,
                        "container_type": container_type,
                        "private_image_details": private_image_details,
                        "advance_config": {
                            "image_pull_policy": "Always",
                            "is_readiness_probe_enabled": "false",
                            "is_liveness_probe_enabled": "false",
                        }
                    },
                    "resource_details": {
                        "disk_size": disc_size,
                        "mount_path": mount_path,
                        "env_variables": env_variables
                    },
                },
                "model_id": model_id,
                "sku_id": sku_id,
                "replica": replicas,
                "path": model_path,
                "framework": framework,
                "is_auto_scale_enabled": is_auto_scale_enabled,
                "detailed_info": {
                    "commands": commands,
                    "args": args,
                    "hugging_face_id": hugging_face_id,
                    "tokenizer": ""
                },
                "model_load_integration_id": hf_token_ingration_id,
                "dataset_id": dataset_id,
                "dataset_path": dataset_path
            }

        if is_auto_scale_enabled:
            rules = [
                {
                    "metric": metric,
                    "condition_type": "limit",
                    "value": value,
                    "watch_period": "60"
                }
            ]

            auto_scale_policy = {
                "min_replicas": min_replicas,
                "max_replicas": max_replicas,
                "rules": rules,
                "stability_period": "300"
            }
            payload["auto_scale_policy"] = auto_scale_policy

        if framework == 'custom':
            payload["custom_endpoint_details"]["container"]["advance_config"].update({
                "readiness_probe": {
                                        "protocol": readiness_probe_protocol,
                                        "initial_delay_seconds": initial_delay_seconds,
                                        "success_threshold": success_threshold,
                                        "failure_threshold": failure_threshold,
                                        "port": 8080,
                                        "period_seconds": period_seconds,
                                        "timeout_seconds": timeout_seconds,
                                        "path": probe_url,
                                        "grpc_service": "",
                                        "commands": readiness_commands
                                    },
                "liveness_probe": {
                                        "protocol": liveness_probe_protocol,
                                        "initial_delay_seconds": initial_delay_seconds,
                                        "success_threshold": success_threshold,
                                        "failure_threshold": failure_threshold,
                                        "port": 8080,
                                        "period_seconds": period_seconds,
                                        "timeout_seconds": timeout_seconds,
                                        "path": probe_url,
                                        "grpc_service": "",
                                        "commands": liveness_commands
                                    }
            })

        payload = json.dumps(payload)
        headers['Authorization'] = f'Bearer {client.Default.access_token()}'
        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/serving/inference/?" \
              f"apikey={client.Default.api_key()}&location={client.Default.location()}"
        response = requests.post(url=url, headers=headers, data=payload)
        print(f"To check the Inference Status and logs, PLease visit "
              f"https://gpu-notebooks.e2enetworks.com/projects/{client.Default.project()}/model-endpoints")
        return prepare_object(response)

    def get(self, endpoint_id):
        if type(endpoint_id) != int:
            raise ValueError(endpoint_id)

        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/serving/inference/" \
              f"{endpoint_id}/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def logs(self, endpoint_id):
        if type(endpoint_id) != int:
            raise ValueError(endpoint_id)

        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/serving/inference/" \
              f"{endpoint_id}/logs/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def start(self, endpoint_id):
        payload = json.dumps({
            "action": "start"
        })
        if type(endpoint_id) != int:
            raise ValueError(endpoint_id)
        headers['Authorization'] = f'Bearer {client.Default.access_token()}'
        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/serving/inference/" \
              f"{endpoint_id}/"
        req = requests.Request('PUT', url=url, data=payload, headers=headers)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def stop(self, endpoint_id):
        payload = json.dumps({
            "action": "stop"
        })
        if type(endpoint_id) != int:
            raise ValueError(endpoint_id)
        headers['Authorization'] = f'Bearer {client.Default.access_token()}'
        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/serving/inference/" \
              f"{endpoint_id}/"
        req = requests.Request('PUT', url=url, data=payload, headers=headers)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def restart(self, endpoint_id):
        payload = json.dumps({
            "action": "restart"
        })
        if type(endpoint_id) != int:
            raise ValueError(endpoint_id)
        headers['Authorization'] = f'Bearer {client.Default.access_token()}'
        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/serving/inference/" \
              f"{endpoint_id}/"
        req = requests.Request('PUT', url=url, data=payload, headers=headers)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def list(self):
        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/serving/inference/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def delete(self, endpoint_id):
        if type(endpoint_id) != int:
            raise ValueError(endpoint_id)

        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/serving/inference/" \
              f"{endpoint_id}/"
        req = requests.Request('DELETE', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def list_replicas(self, endpoint_id):
        if type(endpoint_id) != int:
            raise ValueError(endpoint_id)
        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/serving/inference/" \
              f"{endpoint_id}/replicas/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def manage_replica_count(self, replica_count, endpoint_id):
        if type(endpoint_id) != int:
            raise ValueError(endpoint_id)
        if replica_count < 1 or replica_count > 5:
            raise ValueError(f"Invalid replica count. Expected between 1 and 5, got {replica_count}")
        payload = json.dumps({
                              "action": "disable_auto_scale",
                              "replicas": replica_count,
                              })
        headers['Authorization'] = f'Bearer {client.Default.access_token()}'
        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/serving/inference/" \
              f"{endpoint_id}/"
        req = requests.Request('PUT', url=url, data=payload, headers=headers)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def restart_replica(self, replica_name, endpoint_id):
        if type(endpoint_id) != int:
            raise ValueError(endpoint_id)
        if type(replica_name)!=str:
            raise ValueError(f"Invalid replica name. Expected a string, got {replica_name}")

        headers['Authorization'] = f'Bearer {client.Default.access_token()}'
        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/serving/inference/" \
              f"{endpoint_id}/replicas/{replica_name}/"
        req = requests.Request('DELETE', url=url, headers=headers)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def get_integration(self):
        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/integrations/?integration_type=hugging_face&"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def get_async_invocation_request_response(self, endpoint_id: int, request_id: str):
        """
        Retrieve the response of a completed asynchronous invocation request.

        Args:
            endpoint_id (int): The unique identifier of the inference endpoint.
            request_id (str): The request ID associated with the asynchronous invocation.

        Returns:
            tuple: (bool, dict) where the first value indicates success, and the second contains
                the invocation response data or an error message.
        """

        success, endpoint_data = self.get(endpoint_id)
        if not success:
            return success, endpoint_data
        if not endpoint_data.async_enabled:
            raise ValueError(f"Async invocation not enable for the Model Endpoint ID: {endpoint_id}, Name: {endpoint_data.name}")
        success, request_status = self.get_async_invocation_request_status(endpoint_id, request_id, endpoint_data)
        if not success:
            return False, request_status
        if request_status[0].status not in ['completed', 'failed']:
            return False, "Async invocation request is not yet completed"
        dataset_id = endpoint_data.async_dataset_id
        response_file_path = ASYNC_DATASET_RESPONSE_PATH.format(inf_id=endpoint_id) + f"{request_id}.json"
        success, response = Datasets().download_load_json_file(dataset_id, response_file_path)
        if not success:
            return False, f"Failed get response for the Request ID: {request_id}"
        return success, response

    def get_async_invocation_request_status(self, endpoint_id: int, request_id: str, endpoint_data=None):
        """
        Retrieve the status of an asynchronous invocation request.

        Args:
            endpoint_id (int): The unique identifier of the inference endpoint.
            request_id (str): The request ID associated with the asynchronous invocation.
            endpoint_data (optional): Pre-fetched endpoint data to avoid redundant API calls. Defaults to None.

        Returns:
            tuple: (bool, list) where the first value indicates success, and the second contains
                the request status details or an error message.
        """
        if not endpoint_data:
            success, endpoint_data = self.get(endpoint_id)
            if not success:
                return success, endpoint_data
        if not endpoint_data.async_enabled:
            raise ValueError(f"Async invocation not enable for the Model Endpoint ID: {endpoint_id}, Name: {endpoint_data.name}")
        url = ASYNC_STATUS_FETCH_URL.format(
            team_id=client.Default.team(),
            project_id=client.Default.project(),
            endpoint_id=endpoint_id
        ) + f"?request_id={request_id}&"
        headers['Authorization'] = f'Bearer {client.Default.access_token()}'
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        success, response = prepare_object(response)
        if not success:
            return False, response
        if isinstance(response, list) and len(response) == 0:
            return False, f"Async invocation request ID: {request_id} not found"
        return success, response

    def get_async_invocation_requests_list(
        self, endpoint_id: int, fetch_requests_num: int,
        queue_name=None, date_filter=DateFilterType.LAST_HOUR.value
    ):
        """
        Retrieve a paginated list of asynchronous invocation requests for a given model endpoint.

        Args:
            endpoint_id (int): The unique identifier of the inference model endpoint.
            fetch_requests_num (int): Number of requests to list
            queue_name (str, optional): The name of the queue to filter requests. Defaults to None.
            date_filter (str, optional): The time range filter for requests (e.g., "last_hour", "last_day")
                                        Defaults to DateFilterType.LAST_HOUR.value.

        Returns:
            tuple: (bool, list) where the first value indicates success, and the second contains the
                list of invocation requests or an error message.

        """
        page_no = 1
        per_page = fetch_requests_num
        if not isinstance(fetch_requests_num, int) or fetch_requests_num <= 0:
            raise ValueError("Invalid fetch_requests_num should be integer and >= 1 ")
        if date_filter not in DATE_FILTER_TYPES:
            raise ValueError("Invalid date filter passed")
        success, endpoint_data = self.get(endpoint_id)
        if not success:
            return success, endpoint_data
        url = ASYNC_STATUS_FETCH_URL.format(
            team_id=client.Default.team(),
            project_id=client.Default.project(),
            endpoint_id=endpoint_id
        ) + f"?date_filter={date_filter}&page_no={page_no}&per_page={per_page}&"
        if queue_name:
            url + f"queue_name={queue_name}&"
        headers['Authorization'] = f'Bearer {client.Default.access_token()}'
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        success, response = prepare_object(response)
        if not success:
            return False, response
        return success, response

    def upscale_replica(self, endpoint_id: int):
        """
            This function upscales the replica/replicas by the count of 1.
        """
        if not isinstance(endpoint_id, int):
            raise ValueError(f"endpoint_id must be int, got {type(endpoint_id).__name__}")

        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/serving/inference/" \
            f"{endpoint_id}/?"

        _, obj = self.get(endpoint_id=endpoint_id)

        if not obj.is_auto_scale_enabled:
            raise ValueError("Auto scale policy is not enabled")

        update_min_replicas_by_one = obj.auto_scale_policy.min_replicas + 1
        update_max_replica = obj.auto_scale_policy.max_replicas

        if update_min_replicas_by_one == update_max_replica:
            update_max_replica += 1

        payload = json.dumps({
            "action": "update_auto_scale",
            "auto_scale_policy": {
                "min_replicas": update_min_replicas_by_one,
                "max_replicas": update_max_replica,
                "rules": [obj.auto_scale_policy.rules[0].__dict__],
                "stability_period": obj.auto_scale_policy.stability_period,
                "initial_cooldown_period": obj.auto_scale_policy.initial_cooldown_period
            }
        })
        if obj.is_auto_scale_enabled and obj.auto_scale_policy.max_replicas > obj.auto_scale_policy.min_replicas:
            headers['Authorization'] = f'Bearer {client.Default.access_token()}'
            req = requests.Request("PUT", url=url, data=payload, headers=headers)
            response = client.Default.make_request(req)
            if response.status_code == 200:
                return "Replica upscaled successfully"
            else:
                raise RuntimeError(f"Failed to update replica, status={response.status_code}")

            # return prepare_object(response)

    def downscale_replica(self, endpoint_id: int):
        """
            This function downscales the replicas/replicas by count of 1.
        """
        if not isinstance(endpoint_id, int):
            raise ValueError(f"endpoint_id must be int, got {type(endpoint_id).__name__}")

        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/serving/inference/" \
              f"{endpoint_id}/?"

        _, obj = self.get(endpoint_id=endpoint_id)

        if not obj.is_auto_scale_enabled:
            raise ValueError("Auto scale policy is not enabled")

        if "committed" == obj.sku_details.plan.sku_type:
            raise ValueError("Downscaling is not allowed for committed plans.")

        update_min_replicas_by_one = obj.auto_scale_policy.min_replicas - 1

        if update_min_replicas_by_one < 0:
            raise ValueError(f"min_replicas cannot be negative, got {obj.auto_scale_policy.min_replicas}")

        payload = json.dumps({
            "action": "update_auto_scale",
            "auto_scale_policy": {
                "min_replicas": update_min_replicas_by_one,
                "max_replicas": obj.auto_scale_policy.max_replicas,
                "rules": [obj.auto_scale_policy.rules[0].__dict__],
                "stability_period": obj.auto_scale_policy.stability_period,
                "initial_cooldown_period": obj.auto_scale_policy.initial_cooldown_period
            }
        })
        if obj.is_auto_scale_enabled and obj.auto_scale_policy.min_replicas > 1:
            headers['Authorization'] = f'Bearer {client.Default.access_token()}'
            req = requests.Request('PUT', url=url, data=payload, headers=headers)
            response = client.Default.make_request(req)
            if response.status_code == 200:
                return "Replica downscaled successfully"
            else:
                raise RuntimeError(f"Failed to update replica, status={response.status_code}")

    @staticmethod
    def help():
        print("EndPoint Class Help")
        print("\t\t=================")
        print("\t\tThis class provides functionalities to interact with EndPoint.")
        print("\t\tAvailable methods:")
        print("\t\t1. __init__(team, project): Initializes an EndPoints instance with the specified team and "
              "project IDs.")
        print("\t\t2. list_plans(): List the plans details")
        print("\t\t3. list_frameworks(): List the all available framework")
        print("\t\t4. get_container_name(): Get the name of the container associated with a framework")
        print("\t\t5. get_container_type(): Get the container type")
        print("\t\t6. create_triton(endpoint_name, plan, model_id, model_path='', replicas=1)")
        print("\t\t7. create_tensorrt(endpoint_name, plan, model_id, model_path='', replicas=1)")
        print("\t\t8. create_pytorch(endpoint_name, plan, model_id, model_path='', replicas=1)")
        print("\t\t9. create(endpoint_name, framework, plan, container_name, container_type, model_id, replicas=1, "
              "disc_size=10, model_path="", env_variables=[], mount_path="", registry_endpoint="", "
              "auth_type='pass', username="", password="", docker_config=""): "
              "Creates an endpoint with the provided details.")
        print("\t\t10. registry_namespace_list(): Get the list of all registry on e2enetworks")
        print("\t\t11. registry_detail(registry_namespace_id): Get details of registry")
        print("\t\t12. get(endpoint_id): Retrieves information about a specific endpoint using its ID.")
        print("\t\t13. logs(endpoint_id): Retrieves logs of a specific endpoint using its ID.")
        print("\t\t14. stop(endpoint_id): Stops a specific endpoint using its ID.")
        print("\t\t15. start(endpoint_id): Starts a specific endpoint using its ID.")
        print("\t\t16. list(): Lists all endpoints associated with the team and project.")
        print("\t\t17. restart(endpoint_id): Restart a inference")
        print("\t\t18. delete(endpoint_id): Deletes an endpoint with the given ID.")
        print("\t\t19. list_replicas(endpoint_id): List all endpoints associated replicas")
        print("\t\t20. manage_replica_count(endpoint_id): Manage replica count either increase or decrease")
        print("\t\t21. restart_replica(replica_name,endpoint_id): Restart a specific replica")
        print("\t\t22. get_integration(): Get all integration details")
        print("\t\t23. get_async_invocation_request_response(endpoint_id: int, request_id: str): Fetch the response of an asynchronous invocation request")
        print("\t\t24. get_async_invocation_request_status(endpoint_id: int, request_id: str): Get the status of an asynchronous invocation request")
        print("\t\t25. get_async_invocation_requests_list(endpoint_id: int, fetch_requests_num: int, queue_name=None, date_filter=DateFilterType.LAST_HOUR.value): Get a paginated list of asynchronous invocation requests")
        print("\t\t26. upscale_replica(endpoint_id: int): Increase the replica by the count of 1")
        print("\t\t27. downscale_replica(endpoint_id: int): Decrease the replica by the count of 1")
        print("\t\t28. help(): Displays this help message.")

        # Example usages
        print("\t\tExample usages:")
        print("\t\tendpoints = EndPoints(123, 456)")
        print("\t\tendpoints.create("
              "\n\t\t\t\tendpoint_name(required):String => 'Name of Endpoint'",
              "\n\t\t\t\tframework(required):String => '['triton', 'pytorch', 'llma', 'stable_diffusion', 'mpt,"
              "\n\t\t\t\t\t'codellama', 'custom']'",
              "\n\t\t\t\tplan(required):String=> Plans Can be listed using tir.Plans Apis",
              "\n\t\t\t\tcontainer_type(optional):String=> Default value is public and "
              "\n\t\t\t\t\tallowed values are [public, private]",
              "\n\t\t\t\tmodel_id:Integer=> Required in case of Framework type=[triton, pytorch] and "
              "\n\t\t\t\t\tif model is stored in EOS",
              "\n\t\t\t\tcontainer_name(optional):String=> Docker Container Image Name required in case of Custom "
              "\n\t\t\t\tContainer Only",
              "\n\t\t\t\treplicas(optional):Integer=> Default value id 1",
              "\n\t\t\t\tdisc_size(optional):Integer=> Default value id 10Gb",
              "\n\t\t\t\tmodel_path(optional):String=> Path of EOS bucket where the model is stored",
              "\n\t\t\t\tenv_variables(optional):List=> Env variables can be passed as "
              "\n\t\t\t\t\t[{ 'key': '', 'value': '/mnt/models'}]"
              "\n\t\t\t\tmount_path(optional):String=> Default value is '/mnt/models'"
              "\n\t\t\t\tregistry_endpoint(optional):String=> Required in Case of container_type=private"
              "\n\t\t\t\tauth_type(optional):String=> Required in case of container_type=private, "
              "\n\t\t\t\t\tAllowed Values are ['pass', 'docker'] "
              "\n\t\t\t\t\tDefault Value is pass'"
              "\n\t\t\t\tusername(optional):String=> Required in case of container_type=private and auth_type=pass"
              "\n\t\t\t\tusername(optional):String=> Required in case of container_type=private and auth_type=pass"
              "\n\t\t\t\tdocker_config(optional):String=> Required in case of container_type=private and "
              "auth_type=docker")
        print("\t\tendpoints.get(789)")
        print("\t\tendpoints.logs(789)")
        print("\t\tendpoints.stop(789)")
        print("\t\tendpoints.start(789)")
        print("\t\tendpoints.list()")
        print("\t\tendpoints.delete(789)")
