DPO_TRAIN_CONFIG_TEMPLATE = {
    ### model
    "model_name_or_path": None,
    ### method
    "stage": "dpo",
    "do_train": True,
    "finetuning_type": "lora",
    "lora_target": "all",
    "lora_rank": 8,
    "deepspeed": "examples/deepspeed/ds_z3_config.json",
    # "lora_target": "q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj",
    # "lora_rank": 32,
    # "lora_alpha": 64,
    # "lora_dropout": 0.05,
    # "deepspeed": "examples/deepspeed/ds_z2_config.json",
    "template": "qwen3",

    ### dataset
    "dataset": None,
    "cutoff_len": 4096,
    "max_samples": 10000000000,
    "overwrite_cache": True,
    "preprocessing_num_workers": 32,
    ### output
    "output_dir": None,
    "logging_steps": 1000,
    "save_steps": 100,
    "plot_loss": True,
    "overwrite_output_dir": True,
    ### train
    "per_device_train_batch_size": 1,
    "gradient_accumulation_steps": 8,
    "learning_rate": 2.0e-5,
    "num_train_epochs": 8.0,
    "lr_scheduler_type": "cosine",
    "warmup_ratio": 0.1,
    "bf16": True,
    "ddp_timeout": 180000000,
    
    # ### eval
    # "val_size": 0.1,
    # "per_device_eval_batch_size": 1,
    # "eval_strategy": "steps",
    # "eval_steps": 200,
}

INFERENCE_CONFIG_TEMPLATE = {
    "model_name_or_path": None,
    "adapter_name_or_path": None,
    "template": "qwen3",
    "finetuning_type": "lora",
}
