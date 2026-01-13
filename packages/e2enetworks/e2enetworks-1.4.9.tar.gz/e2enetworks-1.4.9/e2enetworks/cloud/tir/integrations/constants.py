# Payload constants
WANDB_USERNAME = "wandB_username"
WANDB_KEY = "wandB_key"
WANDB_PROJECT = "wandB_project_name"
INTEGRATION_DETAILS = "integration_details"
NAME = "name"
HUGGINGFACE_TOKEN = "hugging_face_token"
INTEGRATION_TYPE = "integration_type"

# Basic constants
HUGGING_FACE = "hugging_face"
WEIGHTS_BIASES = "weights_biases"
INTEGRATION_TYPES = [HUGGING_FACE, WEIGHTS_BIASES]

# Error constants
INTEGRATION_TYPE_ERROR = "Integration type '{given_type}' is invalid, it must be in {integration_types}"
WANDB_USERNAME_ERROR = "Please provide a Weights & Biases username."
WANDB_PROJECT_ERROR = "Please provide a Weights & Biases project name."
INTEGRATION_LIST_ERROR = "Unable to list Integrations."
SHOW_DETAILS_ERROR = "Unable to show Integration details."
