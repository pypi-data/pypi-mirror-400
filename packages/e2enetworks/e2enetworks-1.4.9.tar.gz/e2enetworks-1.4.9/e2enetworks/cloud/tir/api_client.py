import json
import os
from typing import Optional
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper
import requests

from e2enetworks.cloud.tir import client
from e2enetworks.cloud.tir.constants import MODEL_NAME_TO_URL_PATH_MAPPING, LANGUAGES_SUPPORTED_BY_WHISPER,REQUIRED_PARAMETERS_WHISPER,ALLOWED_TIMESTAMPS_VALUE_WHISPER
from e2enetworks.cloud.tir.helpers import (get_formated_data_for_model,
                                           get_model_url, get_random_string)
from e2enetworks.cloud.tir.minio_service import MinioService
from e2enetworks.cloud.tir.utils import prepare_object
from e2enetworks.constants import (BASE_GPU_URL, BUCKET_TYPES, MANAGED_STORAGE,
                                   MODEL_TYPES, headers,WHISPER_LARGE_V3,STABLE_DIFFUSION_2_1,WHISPER_DATA_LIMIT_BYTES, PARAKEET_CTC_ASR, NAMESPACE_PREFIX, PARAKEET_PATH)


class ModelAPIClient:
    def __init__(self, team: Optional[str] = "", project: Optional[str] = "", location: Optional[str] = "",):
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

    def infer(self, model_name, data):
        
        if model_name == WHISPER_LARGE_V3 :
            return self.__whisper_infer(data)
        
        if model_name == PARAKEET_CTC_ASR:
            return self.__parakeet_infer(data)
        
        if model_name == STABLE_DIFFUSION_2_1 and (not data.get('generator') or data.get('generator')=='null') :
            raise ValueError('generator should not be null')
        
        namespace = NAMESPACE_PREFIX + str(client.Default.project())
        try:
            url_status, url = get_model_url(model_name, namespace)
            if not url_status:
                raise Exception(f"Invalid input Error {url} model not present")
            data_status, payload = get_formated_data_for_model(model_name, data)
            if not data_status:
                raise Exception(f"Invalid data key Error {str(payload)}")

        except Exception as e:
            raise Exception(f"Input Error {e}")
        headers["Authorization"] = f"Bearer {client.Default.access_token()}"
        response = requests.post(url=url, headers=headers, data=json.dumps(payload))
        response = prepare_object(response)
        return response

    
    def __whisper_infer(self, data : dict):
        namespace = NAMESPACE_PREFIX + str(client.Default.project())
        try:
            is_valid_input, error = self.__validate_whisper_data(data)

            if not is_valid_input :
                raise Exception(error)
            
            url_status, url = get_model_url(WHISPER_LARGE_V3, namespace)
            if not url_status:
                raise Exception({
                    "error_type" : "Input Error",
                    "message" : f"Invalid input Error {url} model not present"
                })
            data_status, api_payload = get_formated_data_for_model(WHISPER_LARGE_V3, data)
            if not data_status:
                raise Exception({
                    "error_type" : "Input Error",
                    "message" : f"Invalid data key Error {str(data)}"
                })
            
            upload_response = self.__upload_data_genai(data["input"])
            if upload_response and upload_response.get("code") == 200:
                uploaded_file_path = upload_response["data"]["uploaded_file_url"]
                api_payload["inputs"][0]['data'] = [uploaded_file_path]
            else :
                return {
                     "code": upload_response.get("code"),
                     "message" : upload_response.get("message")
                }
                
        except Exception as e:

            return {
                "status": "error",
                "message" : "Error Occured",
                "data" : {},
                "error" : e,
            }
        
        
        headers["Authorization"] = f"Bearer {client.Default.access_token()}"
        infer_response = requests.post(url=url, headers=headers, data=json.dumps(api_payload))
        infer_response = prepare_object(infer_response)
        return infer_response
    
    def __parakeet_infer(self, data: dict):
        namespace = NAMESPACE_PREFIX + str(client.Default.project())
        try:
            is_valid_input, error = self.__validate_parakeet_data(data)
            
            if not is_valid_input:
                raise Exception(error)
            
            url_status, url = get_model_url(PARAKEET_CTC_ASR, namespace)

            if not url_status:
                raise Exception({
                    "error_type" : "Input Error",
                    "message" : f"Invalid input Error {url} model not present"
                })
            api_payload = data
            
            upload_response = self.__upload_data_genai(data["path"])
            if upload_response and upload_response.get("code") == 200:
                uploaded_file_path = upload_response["data"]["uploaded_file_url"]
                api_payload["path"] = [uploaded_file_path]
            else :
                return {
                     "code": upload_response.get("code"),
                     "message" : upload_response.get("message")
                }

        except Exception as e:
            return {
                "status": "error",
                "message" : "Error Occured",
                "data" : {},
                "error" : e,
            }
        
        headers["Authorization"] = f"Bearer {client.Default.access_token()}"
        infer_response = requests.post(url=url, headers=headers, data=json.dumps(api_payload))
        infer_response = prepare_object(infer_response)
        return infer_response
        
    def __upload_data_genai(self,file_path):

        if os.path.exists(file_path) and os.path.isfile(file_path) :
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            if file_size <= WHISPER_DATA_LIMIT_BYTES :
                headers['Authorization'] = f'Bearer {client.Default.access_token()}'
                url_to_get_upload_url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/datasets/genai/objects/urls/?"\
                                        f"apikey={client.Default.api_key()}&file_name={file_name}&action=upload&location={client.Default.location()}" 
                response_get_upload_url = requests.get(url_to_get_upload_url,headers=headers)
                response_get_upload_url = response_get_upload_url.json()
                
                if response_get_upload_url.get("code") != 200:
                    return response_get_upload_url
                
                uploaded_file_url = response_get_upload_url["data"].get("model_input_url")
                file_upload_url = response_get_upload_url["data"].get("upload_url")
                
                put_instance = requests.Session()
                put_instance.headers.update({'content-type': 'multipart/form-data'})
                put_instance.timeout = 600 

                with open(file_path, "rb") as fd:
                    with tqdm(desc=f"Uploading Audio File '{file_name}' ", total=file_size, unit="B", unit_scale=True, unit_divisor=1024) as t:
                        reader_wrapper = CallbackIOWrapper(t.update, fd, "read")
                        file_upload_response = requests.put(file_upload_url, data=reader_wrapper)
                        file_upload_response.raise_for_status()
                        
                file_upload_status_code = file_upload_response.status_code
                if file_upload_status_code == 200:

                    return {
                        "code": file_upload_status_code,
                        "message": "Audio File Uploaded Successfully",
                        "data": {
                            "uploaded_file_url" : uploaded_file_url
                        }
                    }
                else : 
                    raise Exception({
                        "error_type" : "Audio File Upload Error",
                        "message" : f"Internal Error. Failed to upload file."
                    })
                
            else :
                 raise Exception({
                    "error_type" : "Audio File Error",
                    "message" : f"The audio file size exceeds the maximum limit of 50 Megabytes. The current file size is {round(file_size/(pow(1024,2)), 2)} Megabytes."
                })
        else :
            raise Exception({
                "error_type" : "Audio File Error",
                "message" : "File not found or file does not exist on the 'input' "
            })
    
    def __validate_whisper_data(self, data : dict):

        for parameter in REQUIRED_PARAMETERS_WHISPER :
            if parameter not in data.keys():
                return False, {
                    "error_type" : "Input Error",
                    "message" : f"The necessary parameter '{parameter}' is missing."
                    }
        
        if data["language"].lower() not in LANGUAGES_SUPPORTED_BY_WHISPER :
            return False, {
                "error_type" : "Input Error",
                "message" :  f"Invalid 'language', Following are the allowed values {LANGUAGES_SUPPORTED_BY_WHISPER}"
            }
        
        if  data.get("max_new_tokens")  and (data["max_new_tokens"] < 0 or data["max_new_tokens"] > 445 ) :
            return False, {
                "error_type" : "Input Error",
                "message" :  f"'max_new_tokens' should be in the range [1,445]."
            }
        
        if data.get("return_timestamps") and data['return_timestamps'] not in ALLOWED_TIMESTAMPS_VALUE_WHISPER :
            return False,{
                "error_type" : "Input Error",
                "message" :  f"Invalid 'return_timestamps', Following are the allowed values {ALLOWED_TIMESTAMPS_VALUE_WHISPER}"
            }

        return True, {}
    
    def __validate_parakeet_data(self, data: dict):
        if PARAKEET_PATH not in data or not isinstance(data["path"], str) or not data["path"].strip():
            return False, {
                "error_type": "Input Error",
                "message": "The 'path' parameter is required and must be a non-empty string."
            }

        return True, {}
   
    def list(self):
        response = MODEL_NAME_TO_URL_PATH_MAPPING.keys()
        return list(response)

    @staticmethod
    def help():
        print("ModelAPIClient Class Help")
        print("\t\t=================")
        print("\t\tThis class provides functionalities to infer with models.")
        print("\t\tAvailable methods:")
        print(
            "\t\t1. __init__(team, project): Initializes a Models instance with the specified team and project "
            "IDs."
        )
        print("\t\t2. list(): List all available models" "details.")
        print(
            "\t\t3. infer(model_name, data): Infer model with the provided "
            "details."
        )
        print("\t\t4. help(): Displays this help message.")

        # Example usages
        print("\t\tExample usages:")
        print("\t\tmodelclient = ModelAPIClient(123, 456)")
        print(f"\t\tmodelclient.list()")
        print(f"\t\tmodelclient.infer(model_name, data)")
