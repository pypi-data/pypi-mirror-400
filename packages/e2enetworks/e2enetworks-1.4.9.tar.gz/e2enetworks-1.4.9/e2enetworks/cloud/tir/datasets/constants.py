# Error constants
ALLOWED_FILES_ERROR = "Given file format must be in {file_formats}"
DATASET_LOAD_ERROR = "Unable to load dataset: {error_message}"
INVALID_DATASET_ID_ERROR = "Invalid dataset Id: {dataset_id}"
DATASET_LISTING_ERROR = "Unable to list datasets"
NO_DATASETS_AVAILABLE = "No datasets available"
BUCKET_NAME_ERROR = "Please specify a valid bucket name"
DATASET_ID_ERROR = "Invalid dataset_id parameter"
BUCKET_TYPE_ERROR = "Bucket type must be in {bucket_types}"
UPLOAD_PATH_ERROR = "The provided path '{dataset_path}' does not exist."
UPLOAD_FILE_DIR_ERROR = "The provided path '{dataset_path}' is neither a file nor a directory."

# Dataset constraints
ALLOWED_FILE_FORMATS = ['csv', 'json', 'jsonl', 'txt', 'parquet']

# Storage
MANAGED_STORAGE = "managed"
E2E_OBJECT_STORAGE = "e2e_s3"
BUCKET_TYPES = [MANAGED_STORAGE, E2E_OBJECT_STORAGE]

# Encryption constants
E2E_MANAGED = "e2e-managed"
USER_MANAGED = "user-managed"
E2E_MANAGED_KEY = "sse-kms"
USER_MANAGED_KEY = "sse-c"
ENCRYPTION_TYPES = [E2E_MANAGED, USER_MANAGED]
ENCRYPTION_TYPES_MAPPING = {
    E2E_MANAGED: E2E_MANAGED_KEY,
    USER_MANAGED: USER_MANAGED_KEY,
}
ENCRYPTION_TYPE_ERROR = f"Encryption type must be in {ENCRYPTION_TYPES}"
ENCRYPTION_ENABLE_TYPE_ERROR = "encryption_enable must be of type 'bool'"
