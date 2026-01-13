import json
from typing import Optional
from datasets import load_dataset

import requests
import os

from e2enetworks.cloud.tir import client
from e2enetworks.cloud.tir.minio_service import MinioService
from e2enetworks.cloud.tir.utils import prepare_object
from e2enetworks.cloud.tir.datasets.helpers import (
    prepare_datasets_table
)
from e2enetworks.cloud.tir.helpers import get_file_extension
from e2enetworks.constants import (
    BASE_GPU_URL, headers,
)
from e2enetworks.cloud.tir.datasets.constants import (
    ALLOWED_FILE_FORMATS, ALLOWED_FILES_ERROR,
    DATASET_LOAD_ERROR, INVALID_DATASET_ID_ERROR,
    DATASET_LISTING_ERROR, NO_DATASETS_AVAILABLE,
    MANAGED_STORAGE, BUCKET_NAME_ERROR, ENCRYPTION_TYPES,
    BUCKET_TYPE_ERROR, ENCRYPTION_TYPE_ERROR,
    ENCRYPTION_TYPES_MAPPING, ENCRYPTION_ENABLE_TYPE_ERROR,
    BUCKET_TYPES, E2E_OBJECT_STORAGE, UPLOAD_FILE_DIR_ERROR,
    UPLOAD_PATH_ERROR,
)
from e2enetworks.constants import CLIENT_NOT_READY_MESSAGE


class Datasets:
    def __init__(
            self,
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

    def create(
        self,
        name: str,
        bucket_name: Optional[str] = None,
        bucket_type: Optional[str] = MANAGED_STORAGE,
        encryption_enable: Optional[bool] = False,
        encryption_type: Optional[str] = None,
        description: Optional[str] = ""
    ):
        if bucket_type not in BUCKET_TYPES:
            raise ValueError(BUCKET_TYPE_ERROR.format(BUCKET_TYPES))
        if bucket_type == E2E_OBJECT_STORAGE:
            if not bucket_name:
                raise ValueError(BUCKET_NAME_ERROR)
        if not isinstance(encryption_enable, bool):
            raise TypeError(ENCRYPTION_ENABLE_TYPE_ERROR)
        if encryption_enable and encryption_type not in ENCRYPTION_TYPES:
            raise ValueError(ENCRYPTION_TYPE_ERROR)

        payload = json.dumps({
            "storage_type": bucket_type,
            "name": name,
            "bucket_name": bucket_name,
            "encryption_enable": encryption_enable,
            "encryption_type": ENCRYPTION_TYPES_MAPPING.get(encryption_type),
            "description": description,
        })
        headers['Authorization'] = f'Bearer {client.Default.access_token()}'
        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/datasets/?" \
              f"apikey={client.Default.api_key()}&location={client.Default.location()}"
        response = requests.post(url=url, headers=headers, data=payload)
        return prepare_object(response)

    def get(self, dataset_id: int):
        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/datasets/" \
              f"{dataset_id}/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def list(self):
        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/datasets/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def delete(self, dataset_id: int):
        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/datasets/" \
              f"{dataset_id}/"
        req = requests.Request('DELETE', url)
        response = client.Default.make_request(req)
        return prepare_object(response)

    def upload_dataset(
        self,
        dataset_id: int,
        upload_dataset_path: str,
        prefix: Optional[str] = ""
    ):
        if not os.path.exists(upload_dataset_path):
            raise FileNotFoundError(UPLOAD_PATH_ERROR.format(dataset_path=upload_dataset_path))
        if not os.path.isfile(upload_dataset_path) and not os.path.isdir(upload_dataset_path):
            raise ValueError(UPLOAD_FILE_DIR_ERROR.format(dataset_path=upload_dataset_path))

        is_success, dataset = self.get(dataset_id)
        if not is_success:
            raise ValueError(INVALID_DATASET_ID_ERROR.format(dataset_id=dataset_id))

        access_key = dataset.access_key.access_key
        secret_key = dataset.access_key.secret_key
        minio_service = MinioService(access_key=access_key, secret_key=secret_key)

        if os.path.isdir(upload_dataset_path):
            return minio_service.upload_directory_recursive(
                bucket_name=dataset.bucket.bucket_name,
                source_directory=upload_dataset_path,
                prefix=prefix
            )
        else:
            return minio_service.upload_file(
                bucket_name=dataset.bucket.bucket_name,
                file_path=upload_dataset_path,
                prefix=prefix
            )

    def download_dataset(
        self,
        dataset_id: int,
        local_path: str,
        prefix: Optional[str] = ""
    ):
        is_success, dataset = self.get(dataset_id)
        if not is_success:
            raise ValueError(INVALID_DATASET_ID_ERROR.format(dataset_id=dataset_id))
        access_key = dataset.access_key.access_key
        secret_key = dataset.access_key.secret_key
        try:
            minio_service = MinioService(access_key=access_key, secret_key=secret_key)
            return minio_service.download_directory_recursive(
                bucket_name=dataset.bucket.bucket_name,
                local_path=local_path, prefix=prefix
            )
        except Exception as e:
            return False, str(e)

    def download_load_json_file(
        self, dataset_id, file_path: str
    ):
        is_success, dataset = self.get(dataset_id)
        if not is_success:
            raise ValueError(INVALID_DATASET_ID_ERROR.format(dataset_id=dataset_id))
        access_key = dataset.access_key.access_key
        secret_key = dataset.access_key.secret_key
        try:
            minio_service = MinioService(access_key=access_key, secret_key=secret_key)
            return minio_service.download_load_json_file(
                dataset.bucket.bucket_name,
                file_path
            )
        except Exception as e:
            return False, str(e)

    def list_datasets(self):
        """
        Lists and displays datasets in a formatted table.
        """
        is_success, dataset_response = self.list()

        if not is_success:
            print(DATASET_LISTING_ERROR)
            return

        datasets_table = prepare_datasets_table(dataset_response)
        if datasets_table:
            print(datasets_table)
        else:
            print(NO_DATASETS_AVAILABLE)

    def load_dataset_file(
        self,
        dataset_id: int,
        file_path: str,
        streaming: Optional[bool] = True,
    ):
        """
        Load/Stream a dataset from an EOS bucket using dataset ID and file path.

        Args:
            dataset_id (int): The ID of the dataset to load.
            file_path (str): The file path within the S3 bucket to load.
            streaming (bool): Whether to load the dataset in streaming mode. Defaults to True.

        Returns:
            Union[Dataset, DatasetDict, IterableDataset, IterableDatasetDict]:
            A dataset object depending on the file and whether streaming is enabled.
        """
        is_success, dataset = self.get(dataset_id)
        if not is_success:
            raise ValueError(INVALID_DATASET_ID_ERROR.format(dataset_id=dataset_id))

        file_extension = get_file_extension(file_path)
        if file_extension not in ALLOWED_FILE_FORMATS:
            raise ValueError(ALLOWED_FILES_ERROR.format(file_formats=ALLOWED_FILE_FORMATS))

        try:
            # EOS bucket credentials
            access_key = dataset.access_key.access_key
            secret_key = dataset.access_key.secret_key
            s3_path = f"{dataset.bucket.bucket_url}{file_path}"
            endpoint_url = dataset.bucket.endpoint

            # Load the dataset using the load_dataset
            # This implementation of load_dataset is in experimental stage
            return load_dataset(
                file_extension,
                data_files=s3_path,
                streaming=streaming,
                storage_options={
                    'key': access_key,
                    'secret': secret_key,
                    'client_kwargs': {
                        'endpoint_url': endpoint_url,
                    }
                }
            )
        except Exception as e:
            raise ValueError(DATASET_LOAD_ERROR.format(error_message=str(e)))
        
    def list_bucket_names(self):
        url = f"{BASE_GPU_URL}teams/{client.Default.team()}/projects/{client.Default.project()}/datasets/eos-bucket-selection-list/"
        req = requests.Request('GET', url)
        response = client.Default.make_request(req)
        return prepare_object(response)
    
    def list_bucket_types(self):
        return BUCKET_TYPES

    @staticmethod
    def help():
        """
        Provides help information about the Datasets class, its methods, and usage examples.
        """
        help_text = """
    Datasets Class Help
    ===================
    This class provides functionalities to interact with datasets.
    Available methods:
        1. create(name, bucket_name=None, encryption_enable=False, encryption_type=None, bucket_type, description): Creates a new dataset with the provided
        name, bucket name, bucket type, and description. Bucket name is not required if bucket_type='managed'.
        2. get(bucket_name): Retrieves information about a specific dataset using its bucket name.
        3. list(): Retrieves raw dataset information from the API. Returns a response object containing dataset details.
        4. list_datasets(): Fetches dataset information using the `list` method and prints a formatted table of datasets.
        5. delete(dataset_id): Deletes a dataset with the given dataset_id.
        6. upload_dataset(dataset_path, prefix, dataset_id=None): Uploads the dataset to the bucket.
        7. download_dataset(dataset_id, local_path, prefix=""): Downloads the dataset to a local path.
        8. load_dataset_file(dataset_id, file_path, streaming=True): Streams a dataset from an EOS bucket using dataset ID
        and file path. Can optionally stream the dataset.
        9. help(): Displays this help message.

    Example Usages:
        datasets = Datasets(team=123, project=456)
        datasets.create(name='test-dataset', bucket_name='dataset-bucket', bucket_type='managed', description='Test Dataset')
        datasets.get('dataset-bucket')
        datasets.list()
        datasets.list_datasets()
        datasets.delete(dataset_id=236)
        datasets.push_dataset(dataset_path='path/to/dataset', prefix='', dataset_id=None)
        datasets.download_dataset(dataset_id=123, local_path='path/to/local/dir', prefix='')
        datasets.load_dataset_file(dataset_id=123, file_path='path/to/file', streaming=True)
        """
        print(help_text)
