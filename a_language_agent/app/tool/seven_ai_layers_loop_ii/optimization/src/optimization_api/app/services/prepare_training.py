import os, json
import os.path as osp
import shutil
import pandas as pd

from .config_template import DPO_TRAIN_CONFIG_TEMPLATE, INFERENCE_CONFIG_TEMPLATE
from ..utils import save_json, load_json, read_yml, save_yml, copy_file


def merge_corpora_info_llama_factory(
    corpora_info: list, llama_factory_root: str
) -> None:
    """
    Merges the provided corpora information into the llama_factory dataset.
    Parameters:
        corpora_info (list): List of dictionaries containing corpora information. Each dictionary should have 'name' and 'content' keys.
        llama_factory_root (str): Path to the root directory of the llama_factory.
    """
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
            "rejected": "rejected"
           }
        }

    save_json(dataset_info, dataset_info_path)

def generate_DPO_train_config(
    corpora_info: list,
    base_model_path: str,
    lora_output_dir: str,
    llama_factory_root: str,
    DPO_train_config_template: dict,
    output_name: str,
) -> None:
    
    """
    Generates the DPO training configuration file.
    Parameters:
        corpora_info (list): List of dictionaries containing corpora information. Each dictionary should have 'name' and 'content' keys.
        base_model_path (str): Path to the base model.
        lora_output_dir (str): Directory to save the LoRA output.
        llama_factory_root (str): Path to the root directory of the llama_factory.
        DPO_train_config_template (dict): Template dictionary for the DPO training configuration.
        output_name (str): Name to use for the output configuration file.
    """
    train_config_root = osp.join(llama_factory_root, "examples", "train_lora")
    output_train_config_path = osp.join(train_config_root, f"{output_name}.yaml")

    DPO_train_config_template["model_name_or_path"] = base_model_path
    DPO_train_config_template["output_dir"] = lora_output_dir
    DPO_train_config_template["dataset"] = [corpora["name"] for corpora in corpora_info]
    save_yml(DPO_train_config_template, output_train_config_path)


def generate_inference_config(
    base_model_path: str,
    lora_weights_path: str,
    llama_factory_root: str,
    inference_config_template: dict,
    output_name: str,
) -> None:
    """
    Generates the inference configuration file.
    Parameters:
        base_model_path (str): Path to the base model.
        lora_weights_path (str): Path to the LoRA weights.
        llama_factory_root (str): Path to the root directory of the llama_factory.
        inference_config_template (dict): Template dictionary for the inference configuration.
        output_name (str): Name to use for the output configuration file.
    """
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
    """
    Generates the training meta information file.
    Parameters:
        corpora_info (list): List of dictionaries containing corpora information. Each dictionary should have 'name' and 'content' keys.
        base_model_path (str): Path to the base model.
        lora_output_dir (str): Directory to save the LoRA output.
        llama_factory_root (str): Path to the root directory of the llama_factory.
        train_meta_info_root (str): Directory to save the training meta information.
        output_name (str): Name to use for the output configuration file.
    """
    train_meta_info = {
        "base_model_path": base_model_path,
        "lora_output_dir": lora_output_dir,
        "corpora": [corpora["name"] for corpora in corpora_info],
        "train_config_path": f"{llama_factory_root}/examples/train_lora/{output_name}.yaml",
        "inference_config_path": f"{llama_factory_root}/examples/inference/{output_name}.yaml",
    }

    output_train_meta_info_path = osp.join(train_meta_info_root, f"{output_name}.json")

    save_json(train_meta_info, output_train_meta_info_path)

def prepare_training(
    corpora_info: list,
    base_model_path: str,
    lora_output_dir: str,
    llama_factory_root: str,
    train_meta_info_root: str,
    output_name: str,
    DPO_train_config_template: dict = None,
    inference_config_template: dict = None,
) -> bool:
    """
    Prepares the training by generating necessary configuration files and meta information.
    Parameters:
        corpora_info (list): List of dictionaries containing corpora information. Each dictionary should have 'name' and 'content' keys.
        base_model_path (str): Path to the base model.
        lora_output_dir (str): Directory to save the LoRA output.
        llama_factory_root (str): Path to the root directory of the llama_factory.
        train_meta_info_root (str): Directory to save the training meta information.
        output_name (str): Name to use for the output configuration file.
        DPO_train_config_template (dict): Template dictionary for the DPO training configuration.
        inference_config_template (dict): Template dictionary for the inference configuration.
    Returns:
        bool: True if preparation is successful, False otherwise.
    """

    dpo_corpora_info= []

    #added contents: construct dpo-pair
    for dict_my in corpora_info:
        file_name = dict_my["content"]
        # file_name = dict_my["content"]

        # dpo_json=[]
        dpo_file=file_name.replace(".csv", ".json") # default processing format is csv, ans out json fomart training files

        try:
            df = pd.read_csv(file_name, sep=None, engine='python', encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_name, sep=None, engine='python', encoding='gbk')
        
        required_cols = ['ID', 'Score', 'Mechnism', "Question"]
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            raise ValueError(f"CSV missing column: {missing_cols}")
        
        # data
        id_counts = df['ID'].value_counts()
        abnormal_ids = id_counts[id_counts < 2]

        if not abnormal_ids.empty:
            print(f"warning: some examples repeat less than 2 times: {abnormal_ids.to_dict()}")
        
        # 2. group by ID，extract Mechnism with highest score and lowest score
        result_list = []
        for id_val, group in df.groupby('ID'):
            # reset index
            group = group.reset_index(drop=True)
            
            # find the smallest row 
            min_score_row = group[group['Score'] == group['Score'].min()].iloc[0]
            # find the largest row
            max_score_row = group[group['Score'] == group['Score'].max()].iloc[0]
            
            # merge result
            result_list.append(
                {
                "instruction": max_score_row["Question"],
                "input": "",
                "chosen": max_score_row["Mechnism"],
                "rejected": min_score_row["Mechnism"]
                }
            )
        
        
       
        json.dump(result_list*100, open(dpo_file, "w"), indent=2)
        
        dpo_corpora_info.append({       
            "name":  dpo_file.replace(".json", ""),
            "content" : dpo_file
        })

    if DPO_train_config_template is None:
        DPO_train_config_template = DPO_TRAIN_CONFIG_TEMPLATE.copy()

    if inference_config_template is None:
        inference_config_template = INFERENCE_CONFIG_TEMPLATE.copy()
    try:
        merge_corpora_info_llama_factory(dpo_corpora_info, llama_factory_root)
        item_lora_output_dir = osp.join(lora_output_dir, output_name)
        os.makedirs(item_lora_output_dir, exist_ok=True)

        generate_DPO_train_config(
            dpo_corpora_info,
            base_model_path,
            item_lora_output_dir,
            llama_factory_root,
            DPO_train_config_template,
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
