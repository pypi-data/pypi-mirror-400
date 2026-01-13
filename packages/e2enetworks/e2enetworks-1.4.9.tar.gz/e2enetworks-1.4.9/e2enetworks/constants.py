import os
from enum import Enum

BASE_URL_MODEL_API_CLIENT = os.environ.get("MODEL_API_CLIENT_HOST", "https://infer.e2enetworks.net/")
MY_ACCOUNT_LB_URL = os.environ.get("E2E_TIR_API_HOST", "https://api.e2enetworks.com/myaccount/")

GPU_URL = "api/v1/gpu/"
BASE_GPU_URL = f"{MY_ACCOUNT_LB_URL}{GPU_URL}"
VALIDATED_SUCCESSFULLY = "Validated Successfully"
INVALID_CREDENTIALS = "Validation Failed, Invalid APIkey or Token"
headers = {
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://thor-gpu.e2enetworks.net',
    'Referer': 'https://thor-gpu.e2enetworks.net/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
}
MANAGED_STORAGE = "managed"
E2E_OBJECT_STORAGE = "e2e_s3"
BUCKET_TYPES = [MANAGED_STORAGE, E2E_OBJECT_STORAGE]
BUCKET_TYPES_HELP = {
    MANAGED_STORAGE: "To Create New Bucket",
    E2E_OBJECT_STORAGE: " To Use Existing Bucket"
}
NAMESPACE_PREFIX = "p-"
PARAKEET_PATH = "path"
NOTEBOOK = "notebook"
INFERENCE = "inference_service"
PIPELINE = "pipeline"
VECTOR_DB = "vector_db"

PRIVATE = "private"
CUSTOM = "custom"
REGISTRY = os.environ.get("E2E_TIR_REGISTRY", "registry.e2enetworks.net")
TRITON = "triton"
TENSORRT = "tensorrt"
PYTORCH = "pytorch"
MODEL_TYPES = ['pytorch', 'triton', 'custom']
S3_ENDPOINT = os.environ.get("E2E_TIR_S3_ENDPOINT", "objectstore.e2enetworks.net")

WHISPER_DATA_LIMIT_BYTES = 50000000
WHISPER_LARGE_V3 = "whisper-large-v3"
PARAKEET_CTC_ASR = "parakeet-ctc-asr"
LLAMA_2_13B_CHAT = "llama-2-13b-chat"
STABLE_DIFFUSION_2_1 = "stable-diffusion-2-1"
MIXTRAL_8X7B_INSTRUCT = "mixtral-8x7b-instruct"
CODELLAMA_13B_INSTRUCT = "codellama-13b-instruct"
E5_MISTRAL_7B_INSTRUCT = "e5-mistral-7b-instruct"
LLAMA_3_8B_INSTRUCT = "llama-3-8b-instruct"
LLMA = "llma"
STABLE_DIFFUSION = "stable_diffusion"
MPT = "mpt"
CODE_LLAMA = "codellama"
FINETUNED = "finetuned"
MIXTRAL8X7B = 'mixtral8x7b'
MIXTRAL7B = 'mixtral7b'
MIXTRAL7B_INSTRUCT = "mistral-7b-instruct"
MIXTRAL8X7B_INSTRUCT = "mixtral-8x7b-instruct"
GEMMA_7B_IT = "gemma-7b-it"
GEMMA_7B = "gemma-7b"
GEMMA_2B = "gemma-2b"
GEMMA_2B_IT = "gemma-2b-it"
PHI_3_MINI_128K_INSTRUCT = "Phi-3-mini-128k-instruct"
STARCODER2_7B = "starcoder2-7b"
VLLM = "vllm"
NEMO_RAG_SERVICE = 'nemo-rag'
STABLE_VIDEO_DIFFUSION_XT = "stable-video-diffusion-img2vid-xt"
STABLE_DIFFUSION_XL = "stable_diffusion_xl"
YOLO = 'yolov8'
CUSTOM = 'custom'
TIR_CUSTOM_FRAMEWORKS = [LLMA, STABLE_DIFFUSION, STABLE_DIFFUSION_XL, YOLO, MPT, CODE_LLAMA, MIXTRAL7B, MIXTRAL8X7B, MIXTRAL7B_INSTRUCT, MIXTRAL8X7B_INSTRUCT, GEMMA_7B_IT, GEMMA_7B, GEMMA_2B, GEMMA_2B_IT, TENSORRT, PYTORCH, TRITON, LLAMA_3_8B_INSTRUCT, VLLM, STARCODER2_7B, PHI_3_MINI_128K_INSTRUCT, NEMO_RAG_SERVICE, STABLE_VIDEO_DIFFUSION_XT, CUSTOM]  # custom model inferences provided by E2E
ALLOWED_CONTAINER_IMAGES = {
    STARCODER2_7B: 'vllm/vllm-openai:latest',
    GEMMA_7B_IT: 'vllm/vllm-openai:latest',
    GEMMA_2B_IT: 'vllm/vllm-openai:latest',
    LLMA: 'vllm/vllm-openai:latest',
    STABLE_DIFFUSION: 'registry.e2enetworks.net/aimle2e/stable-diffusion-2-1:hf-v1',
    MPT: 'vllm/vllm-openai:latest',
    CODE_LLAMA: 'vllm/vllm-openai:latest',
    STABLE_DIFFUSION_XL: 'registry.e2enetworks.net/aimle2e/stable-diffusion-xl-base-1.0:hf-v1',
    MIXTRAL7B_INSTRUCT: 'vllm/vllm-openai:latest',
    MIXTRAL8X7B_INSTRUCT: 'vllm/vllm-openai:latest',
    TENSORRT: ['aimle2e/tritonserver:24.02-trtllm-python-py3-01', 'aimle2e/tritonserver:24.01-trtllm-python-py3-01', 'aimle2e/tritonserver:23.12-trtllm-python-py3-01', 'aimle2e/tritonserver:23.11-trtllm-python-py3-01', 'aimle2e/tritonserver:23.10-trtllm-python-py3-01',],
    PYTORCH: ['pytorch/torchserve:0.9.0', 'pytorch/torchserve:0.8.1', 'pytorch/torchserve:0.8.2',],
    TRITON: ['aimle2e/tritonserver:24.02-py3-01', 'aimle2e/tritonserver:24.01-py3-01', 'aimle2e/tritonserver:23.12-py3-01', 'aimle2e/tritonserver:23.01-py3-01', 'aimle2e/tritonserver:23.10-py3-01',],
    LLAMA_3_8B_INSTRUCT: 'vllm/vllm-openai:latest',
    VLLM: 'vllm/vllm-openai:latest',
    PHI_3_MINI_128K_INSTRUCT: 'vllm/vllm-openai:latest',
    STABLE_VIDEO_DIFFUSION_XT: 'aimle2e/stable-video-diffusion:v1',
    YOLO: 'registry.e2enetworks.net/aimle2e/yolov8:v1',
}

CLIENT_NOT_READY_MESSAGE = "Client is not ready. Please initiate client by using: \ne2enetworks.cloud.tir.init(...)"

ASYNC_DATASET_RESPONSE_PATH = "api/is-{inf_id}/response/"
ASYNC_STATUS_FETCH_URL = BASE_GPU_URL + "teams/{team_id}/projects/{project_id}/serving/inference/{endpoint_id}/async_status/"
LAST_HOUR = "last_hour"
LAST_24_HOURS = "last_24_hours"
LAST_7_DAYS = "last_7_days"
CURRENT_MONTH = "current_month"
PREVIOUS_MONTH = "previous_month"

DELHI_LOCATION = "Delhi"
CHENNAI_LOCATION = "Chennai"


class DateFilterType(Enum):
    LAST_HOUR = LAST_HOUR
    LAST_24_HOURS = LAST_24_HOURS
    LAST_7_DAYS = LAST_7_DAYS
    CURRENT_MONTH = CURRENT_MONTH
    PREVIOUS_MONTH = PREVIOUS_MONTH


DATE_FILTER_TYPES = [
    LAST_HOUR, LAST_24_HOURS, LAST_7_DAYS, CURRENT_MONTH, PREVIOUS_MONTH
]
