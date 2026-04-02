import os
import os.path as osp
from typing import List, Optional

import pandas as pd

from ..cleaning.utils import read_json, save_json


def get_all_json_files(directory: str, recursive: bool = True) -> List[str]:
    """
    Get a list of all .json files in the specified directory.

    Args:
        directory (str): The path to the directory to search in.
        recursive (bool): Whether to search subdirectories recursively. Default is True.

    Returns:
        List[str]: A list of full paths to .json files.
    """
    json_files = []

    if recursive:
        # Walk through directory tree
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(".json"):
                    full_path = os.path.join(root, file)
                    json_files.append(full_path)
    else:
        # List files in the top-level directory only
        for file in os.listdir(directory):
            full_path = os.path.join(directory, file)
            if os.path.isfile(full_path) and file.lower().endswith(".json"):
                json_files.append(full_path)

    return json_files


def process_single_data(data: dict, single_var_id: int) -> dict:
    """Process single data item with unique identifier.
    
    Args:
        data: Dictionary containing matched pair information.
        single_var_id: Unique identifier for this single variable pair.
        
    Returns:
        Structured dictionary with Meta Info, Input, and Output sections.
    """
    low_pce_identifier = f"Sample_{data['index_low_PCE_date']}_{data['index_low_PCE']}"
    high_pce_identifier = (
        f"Sample_{data['index_high_PCE_date']}_{data['index_high_PCE']}"
    )
    result = {
        "Meta Info": {
            "low_pce_sample": low_pce_identifier,
            "high_pce_sample": high_pce_identifier,
            "single_var_id": single_var_id,
            "diff_columns": data["diff_columns"],
        },
        "Input": {
            "low_pce_sample": {
                "PVK": data["low_PCE_desc"]["PVK"],
                "SAM": data["low_PCE_desc"]["SAM"],
                "Additive": data["low_PCE_desc"]["Additive"],
                "Passivator": data["low_PCE_desc"]["Passivator"],
            },
            "high_pce_sample": {
                "PVK": data["high_PCE_desc"]["PVK"],
                "SAM": data["high_PCE_desc"]["SAM"],
                "Additive": data["high_PCE_desc"]["Additive"],
                "Passivator": data["high_PCE_desc"]["Passivator"],
            },
            "diff_part": {
                "low_pce_sample": data["low_PCE_desc"][data["diff_part"]],
                "high_pce_sample": data["high_PCE_desc"][data["diff_part"]],
            },
        },
        "Output": {
            "metrics": {
                "low_pce_sample": data["low_PCE_desc"]["Metrics"],
                "high_pce_sample": data["high_PCE_desc"]["Metrics"],
            },
            "expert_explanation": "",
        },
    }

    return result


def reorg_data(data: list) -> dict:
    """Reorganize data list into dictionary grouped by difference columns.
    
    Args:
        data: List of dictionaries containing matched pair data.
        
    Returns:
        Dictionary organized by difference column sets.
    """
    total_diff_items = {}
    counter = 0
    avaiable_diff_columns = []
    for d in data:
        d_diff_columns = set(d["diff_columns"])

        if d_diff_columns in avaiable_diff_columns:

            for diff_id, diff_values in total_diff_items.items():
                if d_diff_columns == diff_values["diff_columns"]:
                    diff_values["single_var_pair_items"].append(d)
        else:
            total_diff_items[counter] = {
                "diff_columns": d_diff_columns,
                "single_var_pair_items": [d],
            }
            counter += 1
            avaiable_diff_columns.append(d_diff_columns)

    return total_diff_items


def process_tasks(
    total_diff_items: dict, experts: List[str], total_tasks_num: int
) -> dict:
    task_counter = 0
    average_task_num = int(total_tasks_num / len(experts)) + 1

    experts_tasks = {}
    current_expert_index = 0
    current_expert = experts[current_expert_index]
    experts_tasks[current_expert] = []
    overall_tasks = []
    for _, diff_items in total_diff_items.items():
        for diff_item in diff_items["single_var_pair_items"]:
            experts_tasks[current_expert].append(
                process_single_data(diff_item, task_counter)
            )
            diff_item["single_var_id"] = task_counter
            diff_item["expert"] = current_expert
            overall_tasks.append(diff_item)

            task_counter += 1

            if task_counter % average_task_num == 0:
                current_expert_index += 1
                current_expert = experts[current_expert_index]
                experts_tasks[current_expert] = []

    return experts_tasks, overall_tasks


def process_tasks_simple(total_diff_items: dict) -> dict:

    overall_tasks = []
    for _, diff_items in total_diff_items.items():
        for diff_item in diff_items["single_var_pair_items"]:

            overall_tasks.append(diff_item)

    return overall_tasks


def save_expert_files(save_root: str, expert_tasks: dict):
    counter = 1
    for i, (expert, e_task) in enumerate(expert_tasks.items()):
        save_path = osp.join(save_root, f"{i+1}.json")
        task = {"expert": expert, "tasks": e_task}
        save_json(task, save_path)


def merge_json_files(file_paths: List[str], output_root: Optional[str] = None) -> dict:
    """
    Merge multiple json files with the same header into a single DataFrame.

    Parameters:
        file_paths (List[str]): A list of paths to the json files to be merged.
        output_root (Optional[str]): If provided, the merged data will be saved to this path as a json file.

    Returns:
        dict: A DataFrame containing the merged data from all input json files.

    Raises:
        FileNotFoundError: If any file in file_paths does not exist.
        ValueError: If the json files do not have matching headers.
    """
    if not file_paths:
        raise ValueError("No file paths provided.")

    overall_data = []
    for i, file_path in enumerate(file_paths):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_data = read_json(file_path)
        overall_data += file_data

    total_diff_items = reorg_data(overall_data)
    overall_tasks = process_tasks_simple(total_diff_items)

    save_json(overall_tasks, osp.join(output_root, "overall_tasks.json"))

    # save_expert_files(output_root, expert_tasks)


def merge_results(formula_root: str, fp_root: str):
    formula_src_root = osp.join(formula_root, "date")
    formula_json_files = get_all_json_files(formula_src_root)
    merge_json_files(formula_json_files, formula_root)

    fp_src_root = osp.join(fp_root, "date")
    fp_json_files = get_all_json_files(fp_src_root)
    merge_json_files(fp_json_files, fp_root)


