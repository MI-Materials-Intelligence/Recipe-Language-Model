import json
import os
import os.path as osp
import shutil

import pandas as pd

from .config_template import DPO_TRAIN_CONFIG_TEMPLATE, INFERENCE_CONFIG_TEMPLATE
from ..utils import copy_file, load_json, save_json, save_yml


def merge_corpora_info_llama_factory(
    corpora_info: list, llama_factory_root: str
) -> None:
    dataset_root = osp.join(llama_factory_root, "data")

    dataset_info_path = osp.join(dataset_root, "dataset_info.json")
    dataset_info_backup_path = dataset_info_path + ".backup"

    if not osp.exists(dataset_info_backup_path):
        copy_file(dataset_info_path, dataset_info_backup_path)
    dataset_info = load_json(dataset_info_path)

    for corpora_item in corpora_info:
        corpora_name = corpora_item["name"]
        corpora_content = corpora_item["content"]
        corpora_dst_file = osp.join(dataset_root, f"{corpora_name}.json")

        os.makedirs(os.path.dirname(corpora_dst_file), exist_ok=True)
        shutil.copyfile(corpora_content, corpora_dst_file)

        dataset_info[corpora_name.replace(".json", "")] = {
            "file_name": f"{corpora_name}.json",
            "ranking": True,
            "columns": {
                "prompt": "instruction",
                "query": "input",
                "chosen": "chosen",
                "rejected": "rejected",
            },
        }

    save_json(dataset_info, dataset_info_path)


def generate_dpo_train_config(
    corpora_info: list,
    base_model_path: str,
    lora_output_dir: str,
    llama_factory_root: str,
    dpo_train_config_template: dict,
    output_name: str,
) -> None:
    train_config_root = osp.join(llama_factory_root, "examples", "train_lora")
    output_train_config_path = osp.join(train_config_root, f"{output_name}.yaml")

    dpo_train_config_template["model_name_or_path"] = base_model_path
    dpo_train_config_template["output_dir"] = lora_output_dir
    dpo_train_config_template["dataset"] = [
        corpora["name"] for corpora in corpora_info
    ]
    save_yml(dpo_train_config_template, output_train_config_path)


def generate_inference_config(
    base_model_path: str,
    lora_weights_path: str,
    llama_factory_root: str,
    inference_config_template: dict,
    output_name: str,
) -> None:
    inference_config_root = osp.join(llama_factory_root, "examples", "inference")
    output_inference_config_path = osp.join(
        inference_config_root, f"{output_name}.yaml"
    )

    inference_config_template["model_name_or_path"] = base_model_path
    inference_config_template["adapter_name_or_path"] = lora_weights_path
    save_yml(inference_config_template, output_inference_config_path)


def generate_train_meta_info(
    corpora_info: list,
    base_model_path: str,
    lora_output_dir: str,
    llama_factory_root: str,
    train_meta_info_root: str,
    output_name: str,
) -> None:
    train_meta_info = {
        "base_model_path": base_model_path,
        "lora_output_dir": lora_output_dir,
        "corpora": [corpora["name"] for corpora in corpora_info],
        "train_config_path": f"{llama_factory_root}/examples/train_lora/{output_name}.yaml",
        "inference_config_path": f"{llama_factory_root}/examples/inference/{output_name}.yaml",
    }

    output_train_meta_info_path = osp.join(train_meta_info_root, f"{output_name}.json")

    save_json(train_meta_info, output_train_meta_info_path)


def build_dpo_corpus(corpora_info: list) -> list:
    dpo_corpora_info = []

    for corpus in corpora_info:
        file_name = corpus["content"]
        dpo_file = file_name.replace(".csv", ".json")

        try:
            df = pd.read_csv(file_name, sep=None, engine="python", encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(file_name, sep=None, engine="python", encoding="gbk")

        required_cols = ["ID", "Score", "Mechnism", "Question"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"CSV missing column: {missing_cols}")

        id_counts = df["ID"].value_counts()
        abnormal_ids = id_counts[id_counts < 2]
        if not abnormal_ids.empty:
            print(
                "warning: some examples repeat less than 2 times: "
                f"{abnormal_ids.to_dict()}"
            )

        result_list = []
        for _, group in df.groupby("ID"):
            group = group.reset_index(drop=True)
            min_score_row = group[group["Score"] == group["Score"].min()].iloc[0]
            max_score_row = group[group["Score"] == group["Score"].max()].iloc[0]

            result_list.append(
                {
                    "instruction": max_score_row["Question"],
                    "input": "",
                    "chosen": max_score_row["Mechnism"],
                    "rejected": min_score_row["Mechnism"],
                }
            )

        with open(dpo_file, "w", encoding="utf-8") as file_handle:
            json.dump(result_list * 100, file_handle, indent=2)

        dpo_corpora_info.append({
            "name": dpo_file.replace(".json", ""),
            "content": dpo_file,
        })

    return dpo_corpora_info


def prepare_training(
    corpora_info: list,
    base_model_path: str,
    lora_output_dir: str,
    llama_factory_root: str,
    train_meta_info_root: str,
    output_name: str,
    dpo_train_config_template: dict = None,
    inference_config_template: dict = None,
) -> bool:
    dpo_corpora_info = build_dpo_corpus(corpora_info)

    if dpo_train_config_template is None:
        dpo_train_config_template = DPO_TRAIN_CONFIG_TEMPLATE.copy()

    if inference_config_template is None:
        inference_config_template = INFERENCE_CONFIG_TEMPLATE.copy()
    try:
        merge_corpora_info_llama_factory(dpo_corpora_info, llama_factory_root)
        item_lora_output_dir = osp.join(lora_output_dir, output_name)
        os.makedirs(item_lora_output_dir, exist_ok=True)

        generate_dpo_train_config(
            dpo_corpora_info,
            base_model_path,
            item_lora_output_dir,
            llama_factory_root,
            dpo_train_config_template,
            output_name,
        )

        generate_inference_config(
            base_model_path,
            item_lora_output_dir,
            llama_factory_root,
            inference_config_template,
            output_name,
        )

        generate_train_meta_info(
            corpora_info,
            base_model_path,
            item_lora_output_dir,
            llama_factory_root,
            train_meta_info_root,
            output_name,
        )
        return True
    except Exception as e:
        print(f"Error in prepare_training: {e}")
        return False
