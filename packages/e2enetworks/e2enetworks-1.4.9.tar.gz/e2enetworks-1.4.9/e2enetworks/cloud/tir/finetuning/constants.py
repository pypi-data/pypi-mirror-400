HUGGING_FACE = "huggingface"
EOS_BUCKET = "eos-bucket"
DATASET_TYPES_LIST = [HUGGING_FACE, EOS_BUCKET]

LLAMA2_7B_HF_MODEL_ID = 'meta-llama/Llama-2-7b-hf'
LLAMA3_8B_HF_MODEL_ID = 'meta-llama/Meta-Llama-3-8B'
LLAMA3_8B_INST_HF_MODEL_ID = 'meta-llama/Meta-Llama-3-8B-Instruct'
MISTRAL_7B_HF_MODEL_ID = 'mistralai/Mistral-7B-v0.1'
MISTRAL_7B_INST_HF_MODEL_ID = 'mistralai/Mistral-7B-Instruct-v0.2'
MISTRAL_8X7B_HF_MODEL_ID = 'mistralai/Mixtral-8x7B-v0.1'
GEMMA_7B_HF_MODEL_ID = 'google/gemma-7b'
GEMMA_7B_INST_HF_MODEL_ID = 'google/gemma-7b-it'
STABLE_DIFFUSION_2_HF_MODEL_ID = 'stabilityai/stable-diffusion-2-1'
STABLE_DIFFUSION_XL_HF_MODEL_ID = 'stabilityai/stable-diffusion-xl-base-1.0'

TEXT_MODELS_LIST = [
   LLAMA2_7B_HF_MODEL_ID, LLAMA3_8B_HF_MODEL_ID, LLAMA3_8B_INST_HF_MODEL_ID,
   MISTRAL_7B_HF_MODEL_ID, MISTRAL_7B_INST_HF_MODEL_ID, MISTRAL_8X7B_HF_MODEL_ID,
   GEMMA_7B_HF_MODEL_ID, GEMMA_7B_INST_HF_MODEL_ID,
   ]
IMAGE_MODELS_LIST = [
   STABLE_DIFFUSION_2_HF_MODEL_ID,
   STABLE_DIFFUSION_XL_HF_MODEL_ID,
   ]
COMBINED_MODELS_LIST = TEXT_MODELS_LIST + IMAGE_MODELS_LIST
PIPELINE = "pipeline"
INVALID_DATASET = "Invalid dataset"
PLAN_NAME_ERROR = "plan_name is should be a string"
DEFAULT_TEXT_TRAINING_ARGS = {
    "validation_split_ratio": (float, 0.1, False),
    "target_dataset_field": (str, 'text', False),
    "gradient_accumulation_steps": (int, 1, False),
    "context_length": (int, 512, False),
    "learning_rate": (float, 0.0000141, False),
    "epochs": (int, 3, False),
    "stop_training_when": (str, "epoch_count", False),
    "max_steps": (int, -1, False),
    "batch_size": (int, 4, False),
    "peft_lora_alpha": (int, 16, False),
    "peft_lora_r": (int, 64, False),
    "save_strategy": (str, "no", False),
    "task": (str, "Instruction-Finetuning", False),
    "prompt_configuration": (str, "", False),
    "save_steps": (int, 10, False),
    "limit_training_records_count": (int, -1, False),
    "limit_eval_records_count": (int, -1, False),
    "source_repository_type": (str, "base_model", False),
    "source_model_repo_info": (str, "", False),
    "source_model_path": (str, "", False),
    "save_total_limit": (int, 10, False),
    "lora_dropout": (float, 0.05, False),
    "lora_bias": (str, "none", False),
    "load_in_4bit": (bool, False, False),
    "bnb_4bit_compute_dtype": (str, "bfloat16", False),
    "bnb_4bit_quant_type": (str, "fp4", False),
    "bnb_4bit_use_double_quant": (bool, False, False),
}
DEFAULT_IMAGE_TRAINING_ARGS = {
    "gradient_accumulation_steps": (int, 1, False),
    "learning_rate": (float, 0.0000141, False),
    "epochs": (int, 3, False),
    "stop_training_when": (str, "epoch_count", False),
    "max_steps": (int, -1, False),
    "batch_size": (int, 4, False),
    "peft_lora_alpha": (int, 16, False),
    "peft_lora_r": (int, 64, False),
    "save_strategy": (str, "no", False),
    "task": (str, "Instruction-Finetuning", False),
    "save_steps": (int, 10, False),
    "limit_training_records_count": (int, -1, False),
    "source_repository_type": (str, "base_model", False),
    "source_model_repo_info": (str, "", False),
    "source_model_path": (str, "", False),
    "save_total_limit": (int, 10, False),
    "image_column": (str, "image", False),
    "caption_column": (str, "text", False),
    "validation_prompt": (str, "A photo of a man with green eyes", False),
    "num_validation_images": (int, 2, False),
    "train_batch_size": (int, 1, False),
    "load_in_8bit": (bool, False, False),
    "mixed_precision": (str, "no", False),
    "checkpointing_steps": (int, 500, False),
    "checkpoints_total_limit": (int, 10, False)
}
INVALID_MODEL_NAME = f"Model name must be in {COMBINED_MODELS_LIST}"
SUPPORTED_MODELS_NOT_FOUND = "Failed to fetch supported models"
FAILED_TO_SHOW_FINETUNINGS = "Failed to fetch finetuning details"
CUSTOM_ENDPOINT_DETAILS = {
    "service_port": False,
    "metric_port": False,
    "container": {
        "container_name": "vllm/vllm-openai:latest",
        "container_type": "public",
        "private_image_details": {},
        "advance_config": {
            "image_pull_policy": "Always",
            "is_readiness_probe_enabled": False,
            "is_liveness_probe_enabled": False,
            "readiness_probe": {
                "protocol": "http",
                "initial_delay_seconds": 10,
                "success_threshold": 1,
                "failure_threshold": 3,
                "port": 8080,
                "period_seconds": 10,
                "timeout_seconds": 10,
                "path": "/metrics",
                "grpc_service": "",
                "commands": ""
            },
            "liveness_probe": {
                "protocol": "http",
                "initial_delay_seconds": 10,
                "success_threshold": 1,
                "failure_threshold": 3,
                "port": 8080,
                "period_seconds": 10,
                "timeout_seconds": 10,
                "path": "/metrics",
                "grpc_service": "",
                "commands": ""
            }
        }
    },
    "resource_details": {
        "disk_size": 120,
        "mount_path": "",
        "env_variables": [
            {
                "key": "HF_HOME",
                "value": "/mnt/models",
                "required": True,
                "disabled": {
                    "key": True,
                    "value": True
                }
            }
        ]
    },
    "public_ip": "no"
}
DETAILED_INFO = {
    "commands": "",
    "args": "",
    "hugging_face_id": "",
    "tokenizer": "",
    "server_version": "",
    "world_size": 1,
    "error_log": True,
    "info_log": True,
    "warning_log": True,
    "log_verbose_level": 1,
    "model_serve_type": ""
}
FINETUNING_MODEL_PATH = "final/"
FINETUNED = "finetuned"

FINETUNED_VLLM_OPENAI_IMAGE = 'vllm/vllm-openai:latest'
FINETUNED_MISTRAL_8X7B_INFERENCE_IMAGE = 'registry.e2enetworks.net/aimle2e/finetuned-mixtral8x7b-server:v1'
FINETUNED_STABLE_DIFFUSION_2_INFERENCE_IMAGE = 'registry.e2enetworks.net/aimle2e/finetuned-stable-diff-2:v1'
FINETUNED_STABLE_DIFFUSION_XL_INFERENCE_IMAGE = 'registry.e2enetworks.net/aimle2e/finetuned-stable-diff-sdxl:v1'

FINETUNING_HF_MODEL_ID_TO_IMAGE_MAPPING = {
    MISTRAL_8X7B_HF_MODEL_ID: FINETUNED_MISTRAL_8X7B_INFERENCE_IMAGE,
    STABLE_DIFFUSION_2_HF_MODEL_ID: FINETUNED_STABLE_DIFFUSION_2_INFERENCE_IMAGE,
    STABLE_DIFFUSION_XL_HF_MODEL_ID: FINETUNED_STABLE_DIFFUSION_XL_INFERENCE_IMAGE,
    LLAMA2_7B_HF_MODEL_ID: FINETUNED_VLLM_OPENAI_IMAGE,
    LLAMA3_8B_HF_MODEL_ID: FINETUNED_VLLM_OPENAI_IMAGE,
    LLAMA3_8B_INST_HF_MODEL_ID: FINETUNED_VLLM_OPENAI_IMAGE,
    MISTRAL_7B_HF_MODEL_ID: FINETUNED_VLLM_OPENAI_IMAGE,
    MISTRAL_7B_INST_HF_MODEL_ID: FINETUNED_VLLM_OPENAI_IMAGE,
    GEMMA_7B_HF_MODEL_ID: FINETUNED_VLLM_OPENAI_IMAGE,
    GEMMA_7B_INST_HF_MODEL_ID: FINETUNED_VLLM_OPENAI_IMAGE,
}
DEFAULT_FINETUNING_MODEL = LLAMA2_7B_HF_MODEL_ID
SUCCEEDED = 'Succeeded'
FINETUNING_NOT_SUCCEEDED = "Finetuning is not succeeded, it is in {status} state"
MODEL_ID_NOT_FOUND = "Model id not found for finetuning id {finetuning_id}"
PLAN_NAME_INVALID = "Plan name {plan_name} is invalid"
POD_NOT_FOUND = "No pods found for fine-tuning {finetuning_id}"
DATASET_TYPE_ERROR = "dataset_type must be either 'huggingface' or 'eos-bucket'"
