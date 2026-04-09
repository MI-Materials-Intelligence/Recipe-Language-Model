from __future__ import annotations

from copy import deepcopy


def _base_train_template(*, stage: str, template: str, enable_thinking=None) -> dict:
    config = {
        # model
        "model_name_or_path": None,
        "trust_remote_code": True,
        # method
        "stage": stage,
        "do_train": True,
        "finetuning_type": "lora",
        "lora_rank": 8,
        "lora_target": "all",
        # dataset
        "dataset": None,
        "dataset_dir": None,
        "template": template,
        "cutoff_len": 2048,
        "max_samples": 100000,
        "overwrite_cache": True,
        "preprocessing_num_workers": 16,
        "dataloader_num_workers": 4,
        # output
        "output_dir": None,
        "logging_steps": 10,
        "save_steps": 500,
        "plot_loss": True,
        "overwrite_output_dir": True,
        "save_only_model": False,
        "report_to": "none",
        # train
        "per_device_train_batch_size": 1,
        "gradient_accumulation_steps": 8,
        "learning_rate": 1.0e-4,
        "num_train_epochs": 3.0,
        "lr_scheduler_type": "cosine",
        "warmup_ratio": 0.1,
        "bf16": True,
        "ddp_timeout": 180000000,
        "resume_from_checkpoint": None,
    }
    if enable_thinking is not None:
        config["enable_thinking"] = enable_thinking
    return config


QWEN3_SFT_TRAIN_CONFIG_TEMPLATE = _base_train_template(
    stage="sft",
    template="qwen3_nothink",
    enable_thinking=False,
)

QWEN3_PT_TRAIN_CONFIG_TEMPLATE = _base_train_template(
    stage="pt",
    template="qwen3_nothink",
    enable_thinking=False,
)

QWEN3_INFERENCE_CONFIG_TEMPLATE = {
    "model_name_or_path": None,
    "adapter_name_or_path": None,
    "template": "qwen3_nothink",
    "infer_backend": "huggingface",  # choices: [huggingface, vllm]
    "trust_remote_code": True,
    "enable_thinking": False,
}

QWEN3_MERGE_LORA_CONFIG_TEMPLATE = {
    "model_name_or_path": None,
    "adapter_name_or_path": None,
    "template": "qwen3_nothink",
    "finetuning_type": "lora",
    "trust_remote_code": True,
    "export_dir": None,
    "export_size": 5,
    "export_device": "cpu",  # choices: [cpu, auto]
    "export_legacy_format": False,
}

DEEPSEEK3_SFT_TRAIN_CONFIG_TEMPLATE = _base_train_template(
    stage="sft",
    template="deepseek3",
)

DEEPSEEK3_PT_TRAIN_CONFIG_TEMPLATE = _base_train_template(
    stage="pt",
    template="deepseek3",
)

DEEPSEEK3_INFERENCE_CONFIG_TEMPLATE = {
    "model_name_or_path": None,
    "adapter_name_or_path": None,
    "template": "deepseek3",
    "infer_backend": "huggingface",
    "trust_remote_code": True,
}

DEEPSEEK3_MERGE_LORA_CONFIG_TEMPLATE = {
    "model_name_or_path": None,
    "adapter_name_or_path": None,
    "template": "deepseek3",
    "finetuning_type": "lora",
    "trust_remote_code": True,
    "export_dir": None,
    "export_size": 5,
    "export_device": "cpu",
    "export_legacy_format": False,
}


AVAILABLE_TEMPLATES = {
    "deepseek3": {
        "sft_train_template": DEEPSEEK3_SFT_TRAIN_CONFIG_TEMPLATE,
        "pt_train_template": DEEPSEEK3_PT_TRAIN_CONFIG_TEMPLATE,
        "inference_template": DEEPSEEK3_INFERENCE_CONFIG_TEMPLATE,
        "merge_template": DEEPSEEK3_MERGE_LORA_CONFIG_TEMPLATE,
    },
    "qwen3": {
        "sft_train_template": QWEN3_SFT_TRAIN_CONFIG_TEMPLATE,
        "pt_train_template": QWEN3_PT_TRAIN_CONFIG_TEMPLATE,
        "inference_template": QWEN3_INFERENCE_CONFIG_TEMPLATE,
        "merge_template": QWEN3_MERGE_LORA_CONFIG_TEMPLATE,
    },
}


def clone_template(template_name: str, template_kind: str) -> dict | None:
    template = AVAILABLE_TEMPLATES.get(template_name, {}).get(template_kind)
    return deepcopy(template) if template is not None else None
