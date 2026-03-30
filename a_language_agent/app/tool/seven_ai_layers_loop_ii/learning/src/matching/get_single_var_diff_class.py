import os
import os.path as osp
import random
from functools import lru_cache
from typing import List, Tuple
import os
import os.path as osp
import re
from ..cleaning.utils import read_json, save_json

CONCENTRATION_COLUMN = [
    "Concentration PVK",
    "Concentration Additive 1",
    "Concentration Additive 2",
    "Concentration Additive 3",
    "Concentration SAM 1",
    "Concentration SAM 2",
    "Concentration SAM 3",
    "Concentration Passivator 1",
    "Concentration Passivator 2",
    "Concentration Passivator 3",
    "Concentration Passivator 4",
]

COLUMN_RELATION = [
    [
        {"Concentration PVK"},
        "Formula PVK",
        "Formula PVK",
    ],
    [{"Concentration Additive 1"}, "Formula Additive 1", "Formula Additive 1"],
    [{"Concentration Additive 2"}, "Formula Additive 2", "Formula Additive 2"],
    [{"Concentration Additive 3"}, "Formula Additive 3", "Formula Additive 3"],
    [{"Concentration SAM 1"}, "Formula SAM 1", "Formula SAM 1"],
    [{"Concentration SAM 2"}, "Formula SAM 2", "Formula SAM 2"],
    [{"Concentration SAM 3"}, "Formula SAM 3", "Formula SAM 3"],
    [{"Concentration Passivator 1"}, "Formula Passivator 1", "Formula Passivator 1"],
    [{"Concentration Passivator 2"}, "Formula Passivator 2", "Formula Passivator 2"],
    [{"Concentration Passivator 3"}, "Formula Passivator 3", "Formula Passivator 3"],
    [{"Concentration Passivator 4"}, "Formula Passivator 4", "Formula Passivator 4"],
    [
        {"Formula Additive 1", "Concentration Additive 1"},
        "Formula Additive 1",
        "Formula Additive 1",
    ],
    [
        {"Formula Additive 2", "Concentration Additive 2"},
        "Formula Additive 2",
        "Formula Additive 2",
    ],
    [
        {"Formula Additive 3", "Concentration Additive 3"},
        "Formula Additive 3",
        "Formula Additive 3",
    ],
    [{"Formula SAM 1", "Concentration SAM 1"}, "Formula SAM 1", "Formula SAM 1"],
    [{"Formula SAM 2", "Concentration SAM 2"}, "Formula SAM 2", "Formula SAM 2"],
    [{"Formula SAM 3", "Concentration SAM 3"}, "Formula SAM 3", "Formula SAM 3"],
    [
        {"Formula Passivator 4", "Concentration Passivator 4"},
        "Formula Passivator 4",
        "Formula Passivator 4",
    ],
    [
        {"Formula Passivator 2", "Concentration Passivator 2"},
        "Formula Passivator 2",
        "Formula Passivator 2",
    ],
    [
        {"Formula Passivator 3", "Concentration Passivator 3"},
        "Formula Passivator 3",
        "Formula Passivator 3",
    ],
    [
        {
            "Formula Passivator 1",
            "Concentration Passivator 1",
            "Spin Coating Speed Passivator",
            "Spin Coating Time Passivator",
            "Passivator Dropping Timing",
            "Passivator Volume",
            "Annealed Temperature Passivator",
            "Annealed Time Passivator",
        },
        "Formula Passivator 1",
        "Formula Passivator 1",
    ],
    [
        {
            "Spin Coating Speed SAM",
            "Spin Coating Time SAM",
            " Annealed Temprature SAM",
            "Annealed Time SAM",
        },
        "Spin Coating Speed SAM",
        "Single Coating",
    ],
    # TODO: Consider single coating
]


VALUE_COLUMN = [
    "Concentration PVK",
    "Concentration Additive 1",
    "Concentration Additive 2",
    "Concentration Additive 3",
    "Concentration SAM 1",
    "Concentration SAM 2",
    "Concentration SAM 3",
    "Concentration Passivator 1",
    "Concentration Passivator 2",
    "Concentration Passivator 3",
    "Concentration Passivator 4",
    "Spin Coating Speed Passivator",
    "Spin Coating Time Passivator",
    "Passivator Dropping Timing",
    "Passivator Volume",
    "Annealed Temperature Passivator",
    "Annealed Time Passivator",
    "Spin Coating Speed PVK 1",
    "Spin Coating Speed PVK 2",
    "Spin Coating Time PVK 1",
    "Spin Coating Time PVK 2",
    "Antisolvent Volume",
    "Antisolvent Dropping Timing",
    "Annealed Temperature PVK",
    "Annealed Time PVK",
    "Spin Coating Speed SAM",
    "Spin Coating Time SAM",
    "Annealed Temperature SAM",
    "Annealed Time SAM",
]


@lru_cache(maxsize=1)
def get_predefined_relation() -> Tuple[List, List]:
    different_column_list = []
    concern_column_list = []
    class_list = []

    for different_columns, concern_column, class_name in COLUMN_RELATION:
        different_columns = list(different_columns)
        different_columns.sort()
        different_column_list.append(different_columns)
        concern_column_list.append(concern_column)
        class_list.append(class_name)
    return different_column_list, concern_column_list, class_list


def process_single_data(data: dict):
    low_pce_sample_id = f"{data['control_device_sample_id']},control device"
    high_pce_sample_id = f"{data['target_device_sample_id']},target device"

    result = {
        "Meta Info": {
            "Analysis_Type": "-".join(data["diff_columns"]),
            "Sample_ID_1": low_pce_sample_id,
            "Sample_ID_1_date": data["control_device_sample_date"],
            "Sample_ID_1_Group_ID": data["control_device_group_id"],
            "Sample_ID_2": high_pce_sample_id,
            "Sample_ID_2_date": data["target_device_sample_date"],
            "Sample_ID_2_Group_ID": data["target_device_group_id"],
            "Expert": "",
        },
        "Input": {
            "control_device_fabrication": data["control_device_desc_full"],
            "control_device_characterization": "",
            "target_device_fabrication": data["target_device_desc_full"],
            "target_device_characterization": "",
            "diff_part": data["valid_diff_columns"],
        },
        "Output": {"expert_explanation": {"Voc": "", "Jsc": "", "FF": "", "PCE": ""}},
    }

    return result


def parse_equipment_value(change_desc: str):
    if "->" not in change_desc:
        return None
    control_device_value, target_device_value = change_desc.split("->", 1)
    return float(control_device_value), float(target_device_value)


def parse_difference_desc(difference_desc: str):
    low_pce_full = {}
    high_pce_full = {}

    if not difference_desc.strip():
        return low_pce_full, high_pce_full

    # split different columns
    changes = [item.strip() for item in difference_desc.split("|") if item.strip()]

    for change in changes:
        if "->" not in change or ":" not in change:
            continue  # skip wrong format

        # split field and value
        field_part, value_part = change.split(":", 1)
        old_value, new_value = value_part.split("->", 1)

        field = field_part.strip()
        low_value = None if old_value.strip() == "NULL" else old_value.strip()
        high_value = None if new_value.strip() == "NULL" else new_value.strip()

        low_pce_full[field] = low_value
        high_pce_full[field] = high_value

    return low_pce_full, high_pce_full


def get_target_field_desc(
    low_pce_full: dict,
    high_pce_full: dict,
    target_field: str,
    need_full_desc: bool = False,
) -> str:
    low_pce_value = low_pce_full[target_field]
    high_pce_value = high_pce_full[target_field]

    if target_field in VALUE_COLUMN:
        if low_pce_value < high_pce_value:
            desc = f"Increasing"
            reverse_desc = f"Decreasing"
        elif low_pce_value > high_pce_value:
            desc = f"Decreasing"
            reverse_desc = f"Increasing"
        else:
            raise
    else:
        if low_pce_value is None and high_pce_value is not None:
            if not need_full_desc:
                desc = f"Adding"
                reverse_desc = f"Removing"
            else:
                desc = f"Adding {high_pce_value}"
                reverse_desc = f"Removing {high_pce_value}"
        elif low_pce_value is not None and high_pce_value is None:
            if not need_full_desc:
                desc = f"Removing"
                reverse_desc = f"Adding"
            else:
                desc = f"Removing {low_pce_value}"
                reverse_desc = f"Adding {low_pce_value}"

        else:
            desc = f"{low_pce_value} -> {high_pce_value}"
            reverse_desc = f"{high_pce_value} -> {low_pce_value}"

    return desc, reverse_desc


def get_meta_info(data: dict):

    data_different_columns = data["diff_columns"]
    data_different_columns.sort()
    diff_item = data["Diff_Desc"]
    low_pce_full, high_pce_full = parse_difference_desc(diff_item)
    different_column_list, concern_column_list, class_list = get_predefined_relation()

    if data_different_columns in different_column_list:
        index = different_column_list.index(data_different_columns)
        concern_column = concern_column_list[index]
        meta_class_name = class_list[index]
    else:
        concern_column = data_different_columns[0]
        meta_class_name = data_different_columns[0]

    if (
        len(data_different_columns) == 1
        and data_different_columns[0] in CONCENTRATION_COLUMN
    ):
        desc, reverse_desc = get_target_field_desc(
            low_pce_full, high_pce_full, data_different_columns[0]
        )
        concern_column_value = data[concern_column]
        diff_class = concern_column_value + ": " + desc
        reverse_diff_class = concern_column_value + ": " + reverse_desc
    elif len(data_different_columns) >= 2:
        desc, reverse_desc = get_target_field_desc(
            low_pce_full, high_pce_full, concern_column
        )
        if desc == "Removing":
            concern_column_value = low_pce_full[concern_column]
        else:
            concern_column_value = high_pce_full[concern_column]
        diff_class = concern_column_value + ": " + desc
        reverse_diff_class = concern_column_value + ": " + reverse_desc
    else:
        desc, reverse_desc = get_target_field_desc(
            low_pce_full, high_pce_full, concern_column, need_full_desc=True
        )
        diff_class = desc
        reverse_diff_class = reverse_desc

    if diff_class == reverse_diff_class:
        raise f"diff_class and reverse_diff_class are same: {reverse_diff_class}"
    return data_different_columns, meta_class_name, diff_class, reverse_diff_class


def remove_conflict_in_columns(diff_classes: dict):
    valid_result = {}

    for class_name in diff_classes.keys():
        reverse_class_name = diff_classes[class_name]["reverse_diff_class"]
        if reverse_class_name in diff_classes:
            reverse_class_max_pce = diff_classes[reverse_class_name]["max_PCE"]
            class_max_pce = diff_classes[class_name]["max_PCE"]
            if reverse_class_max_pce > class_max_pce:
                valid_result[reverse_class_name] = diff_classes[reverse_class_name]
            elif class_max_pce > reverse_class_max_pce:
                valid_result[class_name] = diff_classes[class_name]
            else:
                raise f"Same PCE appear for conflict pair <{class_name}-{diff_classes[class_name]['max_PCE_sample_id']}, {reverse_class_name}-{diff_classes[reverse_class_name]['max_PCE_sample_id']}>"
        else:
            valid_result[class_name] = diff_classes[class_name]

    return valid_result


def remove_conflict(data_dict: dict):
    valid_result = {}

    for diff_columns, diff_classes in data_dict.items():
        valid_result[diff_columns] = remove_conflict_in_columns(diff_classes)

    return valid_result


def process_data(data_list: list):
    result = {}

    for d in data_list:
        data_diff_columns, meta_class_name, diff_class, reverse_diff_class = (
            get_meta_info(d)
        )
        joint_diff_columns = "-".join(data_diff_columns)

        if meta_class_name not in result:
            result[meta_class_name] = {}

        if diff_class not in result[meta_class_name]:
            result[meta_class_name][diff_class] = {
                "max_PCE": 0.0,
                "max_PCE_sample_id": None,
                "reverse_diff_class": reverse_diff_class,
                "data": {},
            }

        control_device_pce, target_device_pce = parse_equipment_value(d["PCE_Change"])

        if target_device_pce > result[meta_class_name][diff_class]["max_PCE"]:
            result[meta_class_name][diff_class]["max_PCE"] = target_device_pce
            result[meta_class_name][diff_class]["max_PCE_sample_id"] = d[
                "target_device_sample_id"
            ]

        result[meta_class_name][diff_class]["data"][d["pair_index"]] = (
            process_single_data(d)
        )

    return result


def get_middle_ten(sorted_list: List[int]) -> List[int]:
    """
    Extract the middle 10 elements from a sorted list.

    If the list has fewer than 10 elements, return the entire list.
    If the list has an even number of elements, the middle 10 are centered around the center.

    Parameters:
        sorted_list (List[int]): A list of sorted integers.

    Returns:
        List[int]: A list containing the middle 10 elements.
    """
    n = len(sorted_list)

    if n <= 10:
        return sorted_list.copy()

    mid = n // 2
    start = max(0, mid - 5)
    end = start + 10

    # Adjust if slicing goes out of bounds
    if end > n:
        end = n
        start = end - 10

    return sorted_list[start:end]


def save_data(data: dict, save_root: str):
    count = 0
    for joint_diff_columns, content in data.items():
   
        if os.name == 'nt':
            joint_diff_columns = sanitize_filename_for_windows(joint_diff_columns)

        joint_diff_columns_save_root = osp.join(save_root, joint_diff_columns)
        os.makedirs(joint_diff_columns_save_root, exist_ok=True)

        for diff_class, data_info in content.items():
  
            filename = f"{diff_class}.json"
            if os.name == 'nt':
                filename = sanitize_filename_for_windows(filename)

            save_path = osp.join(joint_diff_columns_save_root, filename)
            save_json(data_info, save_path)

def sanitize_filename_for_windows(name: str) -> str:
    """仅在 Windows 下需要的安全化函数"""
    # 替换 Windows 非法字符：< > : " | ? * \ /
    safe_name = re.sub(r'[<>:"|?*\\/]', '_', name)
    safe_name = safe_name.strip(' .')
    return safe_name if safe_name else "unnamed"

def get_single_var_diff_class(formula_data_root, fp_data_root):
    formula_data_path = osp.join(formula_data_root, "overall_tasks.json")
    fp_data_path = osp.join(fp_data_root, "overall_tasks.json")
    formula_save_root = osp.join(formula_data_root, "tasks")
    fp_save_root = osp.join(fp_data_root, "tasks")
    formula_data_list = read_json(formula_data_path)
    formula_result = process_data(formula_data_list)
    save_data(formula_result, formula_save_root)

    fp_data_list = read_json(fp_data_path)
    fp_result = process_data(fp_data_list)
    save_data(fp_result, fp_save_root)


