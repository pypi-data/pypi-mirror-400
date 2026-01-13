from prettytable import PrettyTable
from typing import Type
from e2enetworks.cloud.tir.finetuning.constants import (
    HUGGING_FACE, INVALID_DATASET,
    FINETUNING_HF_MODEL_ID_TO_IMAGE_MAPPING,
    CUSTOM_ENDPOINT_DETAILS, PLAN_NAME_INVALID,
    )
from e2enetworks.cloud.tir.skus import Plans


def get_supported_models_table(data):
    supported_models_table = PrettyTable()
    supported_models_table.field_names = ['Supported Fine-tuning Models']
    for model in data:
        supported_models_table.add_row([model.name])
    return supported_models_table


def get_finetunings_table(data):
    finetunings_table = PrettyTable()
    finetunings_table.field_names = ['Finetuning ID', 'Finetuning Name', 'SKU Name', 'Status']
    for item in data:
        finetunings_table.add_row([
            item.id,
            item.name,
            item.sku.name,
            item.status
        ])
    return finetunings_table


def get_sku_item_price_from_plan_name(plan_name, service, framework=None, committed_days=0):
    plans = Plans().list(service=service, framework=framework)
    plan_name_to_sku = {}
    gpu_skus = plans["GPU"]
    for sku in gpu_skus:
        for sku_item_price in sku["plans"]:
            if not sku["is_free"]:
                name = sku.get('name')
                committed_days = sku_item_price.get('committed_days')
                key = f'{name}_c{committed_days}'
                plan_name_to_sku[key] = sku_item_price['sku_item_price_id']
    if plan_name_to_sku.get(f'{plan_name}_c{committed_days}'):
        return plan_name_to_sku.get(f'{plan_name}_c{committed_days}')
    raise Exception(PLAN_NAME_INVALID.format(plan_name=plan_name))


def get_model_training_inputs(dataset, dataset_type, default_training_args, **training_args):
    return {
        **get_dataset_config(dataset, dataset_type),
        **{key: get_argument_from_training_args(key, training_args, type_, default, is_required)
            for key, (type_, default, is_required) in default_training_args.items()}
    }


def get_dataset_config(dataset, dataset_type):
    if dataset_type == HUGGING_FACE:
        return {"dataset_type": HUGGING_FACE,
                "dataset": dataset}
    dataset_sub_str = dataset.split('/')
    if len(dataset_sub_str) <= 1:
        raise Exception(INVALID_DATASET)
    object_name = dataset.replace(f"{dataset_sub_str[0]}/", '', 1)
    if not object_name:
        raise Exception("dataset invalid")
    return {"dataset_type": dataset_type,
            "dataset": f'{dataset_sub_str[0]}/{object_name}'}


def get_argument_from_training_args(argument_name, training_args, type_: Type, default="", is_required=False):
    """Get argument from training_args with a type check, default value, and required condition."""
    # Check if the argument is in training_args
    if argument_name in training_args:
        value = training_args[argument_name]
    elif is_required:
        raise ValueError(f"Required argument missing: {argument_name}")
    else:
        return default

    # Check type of the argument
    if not isinstance(value, type_):
        raise TypeError(f"Argument type is invalid: {argument_name}, valid type is {type_}.")

    return value


def get_finetuning_details(data):
    finished_at = data.run.finished_at if data.run else "-"
    finetuning_details = f"""
    Finetuning Details:
    -------------------
    Finetuning ID       : {data.id}
    Finetuning Name     : {data.name}
    Model Name          : {data.model_name}
    Dataset Name        : {data.training_inputs.dataset_name}
    Dataset Type        : {data.training_inputs.dataset_type}
    Training Type       : {data.training_type}
    Status              : {data.status}
    Created At          : {data.created_at}
    Finished At         : {finished_at}
    Huggingface ID      : {data.huggingface_integration_id}
    Description         : {data.description or "None"}
    SKU ID              : {data.sku.sku_id}
    SKU Name            : {data.sku.name}
    """
    return finetuning_details


def prepare_custom_endpoint_details(response, disk_size):
    image_name = FINETUNING_HF_MODEL_ID_TO_IMAGE_MAPPING.get(response.model_name)
    if image_name:
        CUSTOM_ENDPOINT_DETAILS["container"]["container_name"] = image_name
    CUSTOM_ENDPOINT_DETAILS["resource_details"]["disk_size"] = disk_size
    return CUSTOM_ENDPOINT_DETAILS
