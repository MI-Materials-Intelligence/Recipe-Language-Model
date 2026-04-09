from __future__ import annotations

import json
import os
import os.path as osp
import shutil
from copy import deepcopy
from typing import Any

from ..utils import load_json, save_json, save_yml

ALLOWED_DATASET_EXTS = {".json", ".jsonl", ".csv", ".parquet", ".arrow"}


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _file_ext(path: str) -> str:
    return osp.splitext(path)[1].lower()


def _peek_sample(file_path: str) -> dict[str, Any]:
    ext = _file_ext(file_path)
    if ext == ".jsonl":
        with open(file_path, "r", encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if line:
                    return json.loads(line)
        raise ValueError(f"Empty jsonl dataset: {file_path}")

    if ext == ".json":
        with open(file_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        if isinstance(data, list):
            if not data:
                raise ValueError(f"Empty json dataset: {file_path}")
            if not isinstance(data[0], dict):
                raise ValueError(f"Unsupported json sample type in {file_path}")
            return data[0]
        if isinstance(data, dict):
            return data
        raise ValueError(f"Unsupported json dataset structure in {file_path}")

    raise ValueError(
        f"Unsupported dataset file extension: {ext}. Supported: {sorted(ALLOWED_DATASET_EXTS)}"
    )


def _normalize_single_json_object_dataset(file_path: str) -> None:
    """Convert a single JSON object into a one-item list for local datasets."""
    if _file_ext(file_path) != ".json":
        return
    with open(file_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    if isinstance(data, dict):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([data], f, ensure_ascii=False, indent=2)


def infer_dataset_description(file_path: str) -> tuple[dict[str, Any], str]:
    """Infer dataset_info.json entry and training stage from dataset sample."""
    _normalize_single_json_object_dataset(file_path)
    sample = _peek_sample(file_path)
    file_name = osp.basename(file_path)

    # OpenAI-style chat format
    if "messages" in sample:
        return (
            {
                "file_name": file_name,
                "formatting": "sharegpt",
                "columns": {"messages": "messages"},
                "tags": {
                    "role_tag": "role",
                    "content_tag": "content",
                    "user_tag": "user",
                    "assistant_tag": "assistant",
                    "system_tag": "system",
                },
            },
            "sft",
        )

    # ShareGPT / tool-call style
    if "conversations" in sample:
        columns = {"messages": "conversations"}
        if "system" in sample:
            columns["system"] = "system"
        if "tools" in sample:
            columns["tools"] = "tools"
        if "images" in sample:
            columns["images"] = "images"
        if "videos" in sample:
            columns["videos"] = "videos"
        if "audios" in sample:
            columns["audios"] = "audios"
        return (
            {
                "file_name": file_name,
                "formatting": "sharegpt",
                "columns": columns,
            },
            "sft",
        )

    # Alpaca SFT style
    if "instruction" in sample or "output" in sample:
        columns = {"prompt": "instruction", "query": "input", "response": "output"}
        if "system" in sample:
            columns["system"] = "system"
        if "history" in sample:
            columns["history"] = "history"
        if "images" in sample:
            columns["images"] = "images"
        if "videos" in sample:
            columns["videos"] = "videos"
        if "audios" in sample:
            columns["audios"] = "audios"
        return ({"file_name": file_name, "columns": columns}, "sft")

    # Plain text PT style
    if "text" in sample and set(sample.keys()) <= {"text"}:
        return ({"file_name": file_name, "columns": {"prompt": "text"}}, "pt")

    raise ValueError(
        "Unsupported dataset format. Supported local datasets follow latest LLaMA-Factory docs: "
        "alpaca, sharegpt/openai, or pretraining text format."
    )


def build_local_dataset_dir(corpora_info: list[dict[str, str]], dataset_dir: str) -> tuple[list[str], str]:
    _ensure_dir(dataset_dir)
    dataset_info: dict[str, Any] = {}
    inferred_stages: set[str] = set()
    dataset_names: list[str] = []

    for item in corpora_info:
        dataset_name = item["name"]
        src_path = item["content"]
        ext = _file_ext(src_path)
        if ext not in ALLOWED_DATASET_EXTS:
            raise ValueError(
                f"Dataset {src_path} has unsupported extension {ext}. Supported: {sorted(ALLOWED_DATASET_EXTS)}"
            )

        dst_path = osp.join(dataset_dir, f"{dataset_name}{ext}")
        shutil.copyfile(src_path, dst_path)
        dataset_desc, stage = infer_dataset_description(dst_path)
        dataset_info[dataset_name] = dataset_desc
        inferred_stages.add(stage)
        dataset_names.append(dataset_name)

    if len(inferred_stages) != 1:
        raise ValueError(
            f"Mixed dataset stages are not supported in one job: {sorted(inferred_stages)}"
        )

    save_json(dataset_info, osp.join(dataset_dir, "dataset_info.json"))
    return dataset_names, inferred_stages.pop()


def generate_train_config(
    dataset_names: list[str],
    dataset_dir: str,
    base_model_path: str,
    lora_output_dir: str,
    llama_factory_root: str,
    train_config_template: dict,
    output_name: str,
) -> str:
    train_config_root = osp.join(llama_factory_root, "examples", "train_lora")
    _ensure_dir(train_config_root)
    output_train_config_path = osp.join(train_config_root, f"{output_name}.yaml")

    config = deepcopy(train_config_template)
    config["model_name_or_path"] = base_model_path
    config["output_dir"] = lora_output_dir
    config["dataset"] = ",".join(dataset_names)
    config["dataset_dir"] = dataset_dir
    save_yml(config, output_train_config_path)
    return output_train_config_path


def generate_inference_config(
    base_model_path: str,
    lora_weights_path: str,
    inference_config_template: dict,
    llama_factory_root: str,
    output_name: str,
) -> str:
    inference_config_root = osp.join(llama_factory_root, "examples", "inference")
    _ensure_dir(inference_config_root)
    output_inference_config_path = osp.join(inference_config_root, f"{output_name}.yaml")

    config = deepcopy(inference_config_template)
    config["model_name_or_path"] = base_model_path
    config["adapter_name_or_path"] = lora_weights_path
    save_yml(config, output_inference_config_path)
    return output_inference_config_path


def generate_merge_config(
    base_model_path: str,
    lora_weights_path: str,
    merged_weights_path: str,
    merge_lora_config_template: dict,
    llama_factory_root: str,
    output_name: str,
) -> str:
    merge_config_root = osp.join(llama_factory_root, "examples", "merge_lora")
    _ensure_dir(merge_config_root)
    output_merge_config_path = osp.join(merge_config_root, f"{output_name}.yaml")

    config = deepcopy(merge_lora_config_template)
    config["model_name_or_path"] = base_model_path
    config["adapter_name_or_path"] = lora_weights_path
    config["export_dir"] = merged_weights_path
    save_yml(config, output_merge_config_path)
    return output_merge_config_path


def generate_train_meta_info(
    corpora_info: list[dict[str, str]],
    base_model_path: str,
    lora_output_dir: str,
    dataset_dir: str,
    stage: str,
    train_meta_info_root: str,
    train_config_path: str,
    inference_config_path: str | None,
    merge_config_path: str | None,
    output_name: str,
) -> str:
    _ensure_dir(train_meta_info_root)
    train_meta_info = {
        "stage": stage,
        "base_model_path": base_model_path,
        "lora_output_dir": lora_output_dir,
        "dataset_dir": dataset_dir,
        "corpora": [corpora["name"] for corpora in corpora_info],
        "train_config_path": train_config_path,
        "inference_config_path": inference_config_path,
        "merge_config_path": merge_config_path,
    }
    output_train_meta_info_path = osp.join(train_meta_info_root, f"{output_name}.json")
    save_json(train_meta_info, output_train_meta_info_path)
    return output_train_meta_info_path


def read_train_meta_info(train_meta_info_root: str, item_name: str) -> dict[str, Any]:
    meta_path = osp.join(train_meta_info_root, f"{item_name}.json")
    if not osp.exists(meta_path):
        raise FileNotFoundError(f"Training meta info not found: {meta_path}")
    return load_json(meta_path)


def prepare_training(
    corpora_info: list[dict[str, str]],
    base_model_path: str,
    lora_output_dir: str,
    merged_output_dir: str,
    llama_factory_root: str,
    train_meta_info_root: str,
    dataset_workspace_root: str,
    output_name: str,
    sft_train_config_template: dict,
    pt_train_config_template: dict | None = None,
    merge_lora_config_template: dict | None = None,
    inference_config_template: dict | None = None,
) -> bool:
    try:
        item_dataset_dir = osp.join(dataset_workspace_root, output_name)
        dataset_names, stage = build_local_dataset_dir(corpora_info, item_dataset_dir)

        item_lora_output_dir = osp.join(lora_output_dir, output_name)
        _ensure_dir(item_lora_output_dir)

        merged_weights_output_dir = osp.join(merged_output_dir, output_name)
        _ensure_dir(merged_weights_output_dir)

        if stage == "sft":
            train_template = sft_train_config_template
        elif stage == "pt":
            if pt_train_config_template is None:
                raise ValueError("Current model template does not provide a pretraining config.")
            train_template = pt_train_config_template
        else:
            raise ValueError(f"Unsupported inferred stage: {stage}")

        train_config_path = generate_train_config(
            dataset_names=dataset_names,
            dataset_dir=item_dataset_dir,
            base_model_path=base_model_path,
            lora_output_dir=item_lora_output_dir,
            llama_factory_root=llama_factory_root,
            train_config_template=train_template,
            output_name=output_name,
        )

        inference_config_path = None
        merge_config_path = None

        if stage == "sft" and inference_config_template is not None:
            inference_config_path = generate_inference_config(
                base_model_path=base_model_path,
                lora_weights_path=item_lora_output_dir,
                inference_config_template=inference_config_template,
                llama_factory_root=llama_factory_root,
                output_name=output_name,
            )

        if stage == "sft" and merge_lora_config_template is not None:
            merge_config_path = generate_merge_config(
                base_model_path=base_model_path,
                lora_weights_path=item_lora_output_dir,
                merged_weights_path=merged_weights_output_dir,
                merge_lora_config_template=merge_lora_config_template,
                llama_factory_root=llama_factory_root,
                output_name=output_name,
            )

        generate_train_meta_info(
            corpora_info=corpora_info,
            base_model_path=base_model_path,
            lora_output_dir=item_lora_output_dir,
            dataset_dir=item_dataset_dir,
            stage=stage,
            train_meta_info_root=train_meta_info_root,
            train_config_path=train_config_path,
            inference_config_path=inference_config_path,
            merge_config_path=merge_config_path,
            output_name=output_name,
        )
        return True
    except Exception as e:
        print(f"Error in prepare_training: {e}")
        return False
