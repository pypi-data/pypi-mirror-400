
from e2enetworks.constants import WHISPER_LARGE_V3, LLAMA_2_13B_CHAT, STABLE_DIFFUSION_2_1, MIXTRAL_8X7B_INSTRUCT, \
    CODELLAMA_13B_INSTRUCT, E5_MISTRAL_7B_INSTRUCT, LLAMA_3_8B_INSTRUCT, PARAKEET_CTC_ASR

ARGUMENT_IS_MANDATORY = "IS MANDATORY"
    
MODEL_NAME_TO_URL_PATH_MAPPING = {
    LLAMA_2_13B_CHAT : "project/{namespace}/v1/llama-2-13b-chat/infer",
    STABLE_DIFFUSION_2_1 : "project/{namespace}/v1/stable-diffusion-2-1/infer",
    MIXTRAL_8X7B_INSTRUCT: "project/{namespace}/v1/mixtral-8x7b-instruct/infer",
    CODELLAMA_13B_INSTRUCT : "project/{namespace}/v1/codellama-13b-instruct/infer",
    WHISPER_LARGE_V3 : "project/{namespace}/v1/whisper-large-v3/infer",
    E5_MISTRAL_7B_INSTRUCT: "project/{namespace}/v1/e5-mistral-7b-instruct/infer",
    LLAMA_3_8B_INSTRUCT: "project/{namespace}/v1/llama-3-8b-instruct/infer",
    PARAKEET_CTC_ASR: "project/{namespace}/v1/parakeet-ctc-asr/infer"
}
MODEL_API_DEFAULT_DATA = {"inputs": []}

MODELS_API_DATA_FORMATS = {
    LLAMA_2_13B_CHAT: {
        "prompt": {
            "name": "prompt",
            "shape": [1],
            "datatype": "BYTES",
            "data": [],
        },
        "system_prompt": {
            "name": "system_prompt",
            "shape": [1],
            "datatype": "BYTES",
            "data": [],
        },
        "max_new_tokens": {
            "name": "max_new_tokens",
            "shape": [1],
            "datatype": "INT32",
            "data": [],
        },
        "top_k": {
            "name": "top_k",
            "shape": [1],
            "datatype": "INT32",
            "data": [],
        },
        "top_p": {
            "name": "top_p",
            "shape": [1],
            "datatype": "FP32",
            "data": [],
        },
        "temperature": {
            "name": "temperature",
            "shape": [1],
            "datatype": "FP32",
            "data": [],
        },
        "num_return_sequences": {
            "name": "num_return_sequences",
            "shape": [1],
            "datatype": "INT32",
            "data": [],
        },
        "repetition_penalty": {
            "name": "repetition_penalty",
            "shape": [1],
            "datatype": "FP32",
            "data": [],
        },
    },
    LLAMA_3_8B_INSTRUCT: {
        "prompt": {
            "name": "prompt",
            "shape": [1],
            "datatype": "BYTES",
            "data": [],
        },
        "system_prompt": {
            "name": "system_prompt",
            "shape": [1],
            "datatype": "BYTES",
            "data": [],
        },
        "max_new_tokens": {
            "name": "max_new_tokens",
            "shape": [1],
            "datatype": "INT32",
            "data": [],
        },
        "top_k": {
            "name": "top_k",
            "shape": [1],
            "datatype": "INT32",
            "data": [],
        },
        "top_p": {
            "name": "top_p",
            "shape": [1],
            "datatype": "FP32",
            "data": [],
        },
        "temperature": {
            "name": "temperature",
            "shape": [1],
            "datatype": "FP32",
            "data": [],
        },
        "num_return_sequences": {
            "name": "num_return_sequences",
            "shape": [1],
            "datatype": "INT32",
            "data": [],
        },
        "repetition_penalty": {
            "name": "repetition_penalty",
            "shape": [1],
            "datatype": "FP32",
            "data": [],
        },
    },
    MIXTRAL_8X7B_INSTRUCT: {
        "prompt": {
            "name": "prompt",
            "shape": [1],
            "datatype": "BYTES",
            "data": [],
        },
        "system_prompt": {
            "name": "system_prompt",
            "shape": [1],
            "datatype": "BYTES",
            "data": [],
        },
        "max_new_tokens": {
            "name": "max_new_tokens",
            "shape": [1],
            "datatype": "INT32",
            "data": [],
        },
        "top_k": {
            "name": "top_k",
            "shape": [1],
            "datatype": "INT32",
            "data": [],
        },
        "top_p": {
            "name": "top_p",
            "shape": [1],
            "datatype": "FP32",
            "data": [],
        },
        "temperature": {
            "name": "temperature",
            "shape": [1],
            "datatype": "FP32",
            "data": [],
        },
        "num_return_sequences": {
            "name": "num_return_sequences",
            "shape": [1],
            "datatype": "INT32",
            "data": [],
        },
        "repetition_penalty": {
            "name": "repetition_penalty",
            "shape": [1],
            "datatype": "FP32",
            "data": [],
        },
    },
    CODELLAMA_13B_INSTRUCT : {
        "prompt": {
            "name": "prompt",
            "shape": [1],
            "datatype": "BYTES",
            "data": [],
        },
        "system_prompt": {
            "name": "system_prompt",
            "shape": [1],
            "datatype": "BYTES",
            "data": [],
        },
        "max_new_tokens": {
            "name": "max_new_tokens",
            "shape": [1],
            "datatype": "INT32",
            "data": [],
        },
        "top_k": {
            "name": "top_k",
            "shape": [1],
            "datatype": "INT32",
            "data": [],
        },
        "top_p": {
            "name": "top_p",
            "shape": [1],
            "datatype": "FP32",
            "data": [],
        },
        "temperature": {
            "name": "temperature",
            "shape": [1],
            "datatype": "FP32",
            "data": [],
        },
        "action": {
            "name": "action",
            "shape": [1],
            "datatype": "BYTES",
            "data": [],
        },
        "repetition_penalty": {
            "name": "repetition_penalty",
            "shape": [1],
            "datatype": "FP32",
            "data": [],
        },
    },
    STABLE_DIFFUSION_2_1: {
        "prompt": {
            "name": "prompt",
            "shape": [1, 1],
            "datatype": "BYTES",
            "data": [],
        },
        "negative_prompt": {
            "name": "negative_prompt",
            "shape": [1, 1],
            "datatype": "BYTES",
            "data": [],
        },
        "height": {
            "name": "height",
            "shape": [1, 1],
            "datatype": "UINT16",
            "data": [],
        },
        "width": {
            "name": "width",
            "shape": [1, 1],
            "datatype": "UINT16",
            "data": [],
        },
        "generator": {
            "name": "generator",
            "shape": [1, 1],
            "datatype": "UINT16",
            "data": [],
        },
        "num_inference_steps": {
            "name": "num_inference_steps",
            "shape": [1, 1],
            "datatype": "UINT16",
            "data": [],
        },
        "guidance_scale": {
            "name": "guidance_scale",
            "shape": [1, 1],
            "datatype": "FP32",
            "data": [],
        },
        "guidance_rescale": {
            "name": "guidance_rescale",
            "shape": [1, 1],
            "datatype": "FP32",
            "data": [],
        },
    },
    WHISPER_LARGE_V3 : {
        "input": {
            "name": "input",
            "shape": [1],
            "datatype": "BYTES",
            "data": []
        },
        "language": {
            "name": "language",
            "shape": [1],
            "datatype": "BYTES",
            "data": []
        },
        "task" : {
            "name": "task",
            "shape": [1],
            "datatype": "BYTES",
            "data": []
        },
        "return_timestamps" : {
            "name": "return_timestamps",
            "shape": [1],
            "datatype": "BYTES",
            "data": []
        },
        "max_new_tokens": {
            "name": "max_new_tokens",
            "shape": [1],
            "datatype": "INT32",
            "data": []
        }
    },
    E5_MISTRAL_7B_INSTRUCT : {
        "prompt": {
            "name": "prompt",
            "shape": [1],
            "datatype": "BYTES",
            "data": []
        }
    },
    PARAKEET_CTC_ASR:{
        "path":""
    }
}

ALLOWED_TIMESTAMPS_VALUE_WHISPER = ['none', 'sentence','word']
REQUIRED_PARAMETERS_WHISPER = [ 'input', 'task',  'language']
LANGUAGES_SUPPORTED_BY_WHISPER = [
    "english",
    "hindi",
    "bengali",
    "telugu",
    "marathi",
    "tamil",
    "urdu",
    "gujarati",
    "kannada",
    "punjabi",
    "malayalam",
    "assamese",
    "sanskrit",
    "chinese",
    "spanish",
    "russian",
    "korean",
    "french",
    "japanese",
    "portuguese",
    "turkish",
    "german",
    "arabic",
    "italian",
    "indonesian",
    "vietnamese",
    "dutch"
]

# set env constants
FILE_PATH_ERROR = "Invalid file path or file type: {config_path}. Must be a valid path to a JSON file."
JSON_LOAD_ERROR = "Failed to load JSON config file"
JSON_KEY_MISSING = "Missing required key: {key} in the config file."
TYPE_ERROR_MESSAGE = "Expected {key} to be of type {expected_type}, got {actual_type} instead."
PROJECT_NOT_SET = "Project ID is not set. Cannot check project access."
PROJECT_ACCESS_DENIED = "Access to project {project} denied."
PROJECT_CHECK_FAILURE = "Failed to verify access for project {project}: {exception}"

KEY_TO_TYPE_MAP = {
    "api_key": str,
    "auth_token": str,
    "team_id": int,
    "project_id": int
}

# Error Constants
FILE_PATH_EXTENSION_ERROR = "File path '{file_path}' does not have a valid extension"
WRONG_PATH_ERROR = "Please check the file path"
