from minio import Minio
from minio.error import S3Error
from e2enetworks.constants import S3_ENDPOINT
from e2enetworks.cloud.tir.constants import WRONG_PATH_ERROR
import os
import time
import io
import tempfile
import json


class MinioService:

    def __init__(self, access_key, secret_key, endpoint=S3_ENDPOINT):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.client = Minio(endpoint, access_key, secret_key)

    def upload_directory_recursive(self, bucket_name, source_directory, prefix=""):
        logs = []
        success = True

        for root, dirs, files in os.walk(source_directory):
            for file in files:
                file_path = os.path.join(root, file)
                object_name = os.path.join(prefix, os.path.relpath(file_path, source_directory))

                try:
                    self.client.fput_object(bucket_name, object_name, file_path)
                    log_msg = f"Uploaded {object_name}"
                    logs.append(log_msg)
                except S3Error as e:
                    log_msg = f"Error uploading {object_name}: {e}"
                    logs.append(log_msg)
                    success = False

        return success, logs

    def upload_file(self, bucket_name, file_path, prefix=""):
        object_name = f"{prefix}{os.path.basename(file_path)}" if prefix.endswith('/') else f"{prefix}/{os.path.basename(file_path)}"

        try:
            self.client.fput_object(bucket_name, object_name, file_path)
            return True, f"Uploaded {object_name}"
        except Exception as err:
            return False, f"Error uploading {object_name}: {err}"

    def download_directory_recursive(self, bucket_name, local_path, prefix=""):
        logs = []
        success = True
        objects = self.client.list_objects(bucket_name=bucket_name, prefix=prefix, recursive=True)
        if not objects:
            raise ValueError(WRONG_PATH_ERROR)

        for obj in objects:
            object_name = obj.object_name
            try:
                local_file_path = f"{local_path}/{object_name}"
                self.client.fget_object(bucket_name, object_name, local_file_path)
                logs.append(f"Downloaded: {object_name} to {local_file_path}")
            except Exception as err:
                logs.append(f"Error downloading {object_name}: {err}")
                success = False
        return success, logs

    def update_cache_file(self, bucket_name):
        print("Updating Cache info file")
        object_name = ".tir-cache"
        try:
            current_timestamp = str(int(time.time())).encode()
            current_timestamp_as_a_stream = io.BytesIO(current_timestamp)
            self.client.put_object(bucket_name, object_name, current_timestamp_as_a_stream, len(current_timestamp))
            print("Cache Info Updated")
        except S3Error as err:
            print("Error Occured while updating cache file")
            print(f"Error: {err}")

    def download_load_json_file(
        self, bucket_name: str, object_path: str
    ):
        try:
            with tempfile.NamedTemporaryFile(mode="r+", delete=True, suffix=".json") as temp_file:
                self.client.fget_object(bucket_name, object_path, temp_file.name)
                temp_file.seek(0)
                with open(temp_file.name, "r") as file:
                    content = file.read()
                    json_content = json.loads(content)
                return True, json_content
        except Exception as e:
            return False, str(e)
