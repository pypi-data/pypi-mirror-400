# Error Messages
COMMITTED_POLICY_REQUIRED_ERROR = "Committed policy is required when SKU item price does not match hourly rate."
INVALID_COMMITTED_POLICY_ERROR = "Committed policy must be one of: {}"
NEXT_SKU_ITEM_PRICE_ID_REQUIRED_ERROR = "Next SKU item price ID is required for committed policy."
IMAGE_VERSION_ID_REQUIRED_ERROR = "Image version ID is required for non-custom images."
CUSTOM_IMAGE_DETAILS_REQUIRED_ERROR = "Both registry_namespace_id and e2e_registry_image_url are required for custom images."
NOTEBOOK_ID_TYPE_ERROR = "notebook_id must be a valid integer value."
INVALID_NOTEBOOK_ID_TYPE_ERROR = "Notebook ID must be an integer."
INVALID_PLAN_NAME_TYPE_ERROR = "Plan name must be a string."
INVALID_SKU_ITEM_PRICE_ID_TYPE_ERROR = "SKU item price ID must be an integer."
INVALID_COMMITTED_POLICY_TYPE_ERROR = "Committed policy must be a string."
INVALID_ACTION = "Invalid actions, must be one of {actions}."
UPDATE_ACTION_ERROR = "'update' action requires either 'ssh_keys_to_add' or 'ssh_keys_to_remove'"
ENABLE_ACTION_ERROR = "'enable' action requires 'ssh_keys_to_add'"

# Keywords
AUTO_RENEW_STATUS = 'auto_renew'
AUTO_TERMINATE_STATUS = 'auto_terminate'
CONVERT_TO_HOURLY_BILLING = 'convert_to_hourly_billing'
SSH_ENABLE = "enable"
SSH_DISABLE = "disable"
SSH_UPDATE = "update"
FREE_USAGE = "free_usage"
PAID_USAGE = "paid_usage"

# Lists and Dicts
COMMITTED_POLICIES = [AUTO_RENEW_STATUS, AUTO_TERMINATE_STATUS, CONVERT_TO_HOURLY_BILLING]
AVAILABLE_ACTIONS = [SSH_ENABLE, SSH_DISABLE, SSH_UPDATE]
INSTANCE_TYPE = [FREE_USAGE, PAID_USAGE]
