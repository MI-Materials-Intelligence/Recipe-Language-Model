import csv
import json
import os
import sys
from functools import partial
from itertools import combinations, product
from multiprocessing import Pool, cpu_count
from typing import Any, Dict, List

import pandas as pd

# Ensure correct package path can be found in multi-process environment
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # Learning/src
grandparent_dir = os.path.dirname(parent_dir)  # Learning
if grandparent_dir not in sys.path:
    sys.path.insert(0, grandparent_dir)

from .perovskite_text_generator import generate_segmented_text, generate_text
from ..cleaning.utils import save_json

VALUE_FEATURES = [
    "Concentration PVK",  # concentration and processing
    "Spin Coating Speed PVK 1",
    "Spin Coating Time PVK 1",
    "Spin Coating Speed PVK 2",
    "Spin Coating Time PVK 2",
    "Antisolvent Volume",
    "Antisolvent Dropping Timing",
    "Annealed Temperature PVK",
    "Annealed Time PVK",
    "Concentration SAM 1",
    "Concentration SAM 2",
    "Concentration SAM 3",
    "Concentration Additive 1",
    "Concentration Additive 2",
    "Concentration Additive 3",
    "Concentration Passivator 1",
    "Concentration Passivator 2",
    "Concentration Passivator 3",
    "Spin Coating Speed Passivator",
    "Spin Coating Time Passivator",
    "Spin Coating Speed SAM",
    "Spin Coating Time SAM",
    "Annealed Temperature SAM",
    "Annealed Time SAM",
    "Passivator Dropping Timing",
    "Passivator Volume",
    "Annealed Temperature Passivator",
    "Annealed Time Passivator",
    "Concentration Passivator 4",
]

PERMITTED_FEATURE_TUPLE = [
    {"Formula Additive 1", "Concentration Additive 1"},
    {"Formula Additive 2", "Concentration Additive 2"},
    {"Formula Additive 3", "Concentration Additive 3"},
    {"Formula SAM 1", "Concentration SAM 1"},
    {"Formula SAM 2", "Concentration SAM 2"},
    {"Formula SAM 3", "Concentration SAM 3"},
    {
        "Spin Coating Speed SAM",
        "Spin Coating Time SAM",
        "Annealed Temperature SAM",
        "Annealed Time SAM",
    },
    {"Formula Passivator 1", "Concentration Passivator 1"},
    {"Formula Passivator 2", "Concentration Passivator 2"},
    {"Formula Passivator 3", "Concentration Passivator 3"},
    {"Formula Passivator 4", "Concentration Passivator 4"},
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
]

SINGLE_COATING_FEATURES = {
    "Spin Coating Speed SAM",
    "Spin Coating Time SAM",
    "Annealed Temperature SAM",
    "Annealed Time SAM",
}
FORMULA_COLUMN_SET = {
    "Formula Additive 1",
    "Formula Additive 2",
    "Formula Additive 3",
    "Formula SAM 1",
    "Formula SAM 2",
    "Formula SAM 3",
    "Formula Passivator 1",
    "Formula Passivator 2",
    "Formula Passivator 3",
    "Formula Passivator 4",
}

FEATURE_SET_DICT = {
    "PVK": {
        "Formula PVK",
        "Concentration PVK",
        "Spin Coating Speed PVK 1",
        "Spin Coating Time PVK 1",
        "Spin Coating Speed PVK 2",
        "Spin Coating Time PVK 2",
        "Antisolvent Volume",
        "Antisolvent Dropping Timing",
        "Annealed Temperature PVK",
        "Annealed Time PVK",
    },
    "SAM": {
        "Formula SAM 1",
        "Concentration SAM 1",
        "Formula SAM 2",
        "Concentration SAM 2",
        "Formula SAM 3",
        "Concentration SAM 3",
    },
    "Additive": {
        "Formula Additive 1",
        "Concentration Additive 1",
        "Formula Additive 2",
        "Concentration Additive 2",
        "Formula Additive 3",
        "Concentration Additive 3",
    },
    "Passivator": {
        "Formula Passivator 1",
        "Concentration Passivator 1",
        "Formula Passivator 2",
        "Concentration Passivator 2",
        "Formula Passivator 3",
        "Concentration Passivator 3",
        "Spin Coating Speed Passivator",
        "Spin Coating Time Passivator",
        "Passivator Dropping Timing",
        "Passivator Volume",
        "Annealed Temperature Passivator",
        "Annealed Time Passivator",
    },
    "Single_Coating": {
        "Spin Coating Speed SAM",
        "Spin Coating Time SAM",
        "Annealed Temperature SAM",
        "Annealed Time SAM",
    },
}

IGNORED_FEATURES = [
    "date",
    "rank",
    "PCE",
    "FF",
    "Voc",
    "Jsc",
    "No",
    "No_x",
    "No_y",
    "area_px2",
    "mean_RGB",
    "VAR_RGB",
    "gray_mean",
    "gray_contrast",
    "mean_B",
    "mean_G",
    "mean_R",
    "var_B",
    "var_G",
    "var_R",
    "filename",
    "folder_date",
    "date.1",
    "defect_bright",
    "defect_dark",
    "defect_crack",
    "defect_total",
    "closest_color_name",
    "Nucleation Onset Time After Spin Coating",
    "Maximum PL Intensity",
    "Time to Peak PL Intensity After Nucleation",
    "max_column",
    r"10%decay_column",
    r"10%decay_value",
    r"10%slope",
    r"20%decay_column",
    r"20%decay_value",
    r"20%slope",
    r"30%decay_column",
    r"30%decay_value",
    r"30%slope",
    "file_location",
    "xrd_intensity_12.6",
    "xrd_fhwm_12.6",
    "xrd_intensity_4",
    "xrd_fhwm_4",
    "xrd_intensity_4_filename",
    "xrd_Stress",
    "xrd_Stress_filename_x",
    "xrd_intensity_5.3",
    "xrd_fhwm_5.3",
    "xrd_intensity_5.3_filename",
    "Unnamed: 90",
    "Unnamed: 91",
    "xrd_Stress_filename_y",
    "Cs",
    "MA",
    "FA",
    "Pb",
    "I",
    "Br",
    "formula",
    "Group_ID",
    "index",
    "Product",
    "Channel",
    "From",
]


def check_feature_set(features: list) -> str:
    input_feature_set = set(features)

    for feature_set_name, feature_set in FEATURE_SET_DICT.items():
        if input_feature_set.issubset(feature_set):
            return feature_set_name

    print(input_feature_set)
    raise


def check_trans_stage_feature(feature_columns, high_pce_features, low_pce_features):
    feature_column_set = set(feature_columns)
    if feature_column_set not in PERMITTED_FEATURE_TUPLE:
        return False

    if feature_column_set.issubset(SINGLE_COATING_FEATURES):
        return list(SINGLE_COATING_FEATURES)

    target_column = feature_column_set.intersection(FORMULA_COLUMN_SET).pop()

    if high_pce_features[target_column] == "" or low_pce_features[target_column] == "":
        return target_column
    else:
        return False


def save_matched_pairs_to_csv(
    matched_pairs: List[Dict[str, Any]],
    output_file: str = "matched_pairs_filtered.csv",
    exclude_prefix: str = "description_",
) -> None:
    """
    Save a list of matched pair dictionaries to a CSV file, excluding keys with a given prefix.

    Args:
        matched_pairs (List[Dict[str, Any]]):
            A list of dictionaries containing matched pair data.
        output_file (str):
            The path to the output CSV file. Defaults to 'matched_pairs_filtered.csv'.
        exclude_prefix (str):
            The prefix of keys to exclude from the output. Defaults to 'description_'.

    Returns:
        None

    Example:
        >>> matched_pairs = [
        ...     {
        ...         'date': '2025-07-21',
        ...         'index_1': 1,
        ...         'index_2': 2,
        ...         'diff_columns': ['FF', 'Voc'],
        ...         'description_2025-07-21_1': 'Sample description'
        ...     }
        ... ]
        >>> save_matched_pairs_to_csv(matched_pairs, "output.csv")
    """
    if not matched_pairs:
        print("Warning: matched_pairs is empty. No file will be written.")
        return

    # Filter out keys with the specified prefix
    filtered_pairs = []
    for pair in matched_pairs:
        filtered_pair = {
            k: (";".join(v) if isinstance(v, list) else v)
            for k, v in pair.items()
            if not k.startswith(exclude_prefix)
        }
        filtered_pairs.append(filtered_pair)

    # Get fieldnames from the first dictionary
    fieldnames = filtered_pairs[0].keys()

    # Write to CSV
    try:
        with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(filtered_pairs)
        print(f"CSV file successfully saved to: {output_file}")
    except Exception as e:
        print(f"Error writing CSV file: {e}")


def process_date(i, dates, grouped, n, output_dir, only_formula=True):
    json_filename = os.path.join(output_dir, f"{dates[i].date()}.json")
    if os.path.exists(json_filename):
        print(f"skip: {json_filename}")
        return
    # try:
    current_date_group = (
        grouped.get_group(dates[i])
        .sort_values(by="PCE", ascending=False)
        .reset_index(drop=True)
        .reset_index()
    )

    current_date = pd.to_datetime(dates[i])

    print(current_date_group.columns)

    if only_formula:
        feature_columns = [
            col for col in current_date_group.columns if col not in IGNORED_FEATURES
        ]
    else:
        feature_columns = [
            col
            for col in current_date_group.columns
            if not (col in IGNORED_FEATURES or col in VALUE_FEATURES)
        ]
    print(feature_columns)

    window_dates = dates[max(0, i - n + 1) : i + 1]
    window_group = pd.concat(
        [
            grouped.get_group(d)
            .sort_values(by="PCE", ascending=False)
            .reset_index(drop=True)
            .reset_index()
            for d in window_dates
        ],
        ignore_index=True,
    )
    matched_pairs = get_single_var_pair(
        current_date_group, window_group, feature_columns, current_date
    )

    save_json(matched_pairs, json_filename)
    print(f"saved: {json_filename}")


def get_data(exp_data_path):
    df = pd.read_csv(exp_data_path, encoding="gbk")
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d", errors="coerce")


    # object_cols = df.select_dtypes(include=["object"]).columns
    # df[object_cols] = df[object_cols].fillna("")
    df.fillna("", inplace=True)

    df["Formula PVK"] = df["formula"]
    df = df.drop(columns=["formula"])

    print(len(df))
    grouped = df.groupby(("date"))
    return grouped


def get_single_var_pair(group1, group2, feature_columns, exp_date):
    matched_pairs = []

    pair_indices = []

    for i, j in product(group1.iterrows(), group2.iterrows()):
        row_i_full = i[1]
        row_j_full = j[1]
        #  ensure index i has a larger PCE
        if row_i_full["PCE"] < row_j_full["PCE"]:
            high_pce_full, low_pce_full = row_j_full, row_i_full  # swap
        elif row_i_full["PCE"] > row_j_full["PCE"]:
            high_pce_full, low_pce_full = row_i_full, row_j_full
        elif row_i_full["PCE"] == row_j_full["PCE"]:
            continue

        if high_pce_full["PCE"] - low_pce_full["PCE"] < 0.5:
            continue

        if "index" in feature_columns:
            feature_columns.remove("index")

        high_pce = high_pce_full[feature_columns]
        low_pce = low_pce_full[feature_columns]

        unequal_mask = high_pce != low_pce
        diff_count = unequal_mask.sum()

        diff_features = [
            feature
            for feature, feature_mask in zip(feature_columns, unequal_mask)
            if feature_mask
        ]

        if diff_count in [1, 2, 4, 8]:
            if diff_count in [1, 2] and "Concentration SAM 1" in diff_features:
                print(diff_features)
            if diff_count in [2, 4, 8]:

                permit_single_var = check_trans_stage_feature(
                    diff_features, high_pce, low_pce
                )
                if not permit_single_var:
                    continue
            else:
                permit_single_var = diff_features[0]

            if (
                "Formula Passivator 4" in diff_features
                or "Concentration Passivator 4" in diff_features
            ):
                continue

            diff_part = check_feature_set(diff_features)
            des1 = generate_segmented_text(high_pce_full)
            des2 = generate_segmented_text(low_pce_full)

            full_desc1 = generate_text(high_pce_full)
            full_desc2 = generate_text(low_pce_full)

            high_pce_no = high_pce_full["No"]
            low_pce_no = low_pce_full["No"]

            if not high_pce_no or not low_pce_no:
                continue

            pair_index = (
                "SampleID_"
                + str(int(low_pce_no))
                + "-"
                + "SampleID_"
                + str(int(high_pce_no))
            )

            if pair_index not in pair_indices:
                pair_indices.append(pair_index)
            else:
                continue

            difference_desc_list = []

            for column in diff_features:
                low_desc = low_pce_full[column] if low_pce_full[column] else "NULL"
                high_desc = high_pce_full[column] if high_pce_full[column] else "NULL"
                difference_desc_list.append(f"{column}: {low_desc}->{high_desc}")
            difference_desc = "| ".join(difference_desc_list)
            high_pce_exp_date = high_pce_full["date"].date()
            high_pce_full = high_pce_full.drop("date")
            matched_pairs.append(
                {
                    "date": str(exp_date.date()),
                    "pair_index": pair_index,
                    "target_device_sample_date": str(high_pce_exp_date),
                    "control_device_sample_date": str(low_pce_full["date"].date()),
                    "target_device_sample_id": int(high_pce_no),  # index in date
                    "control_device_sample_id": int(low_pce_no),  # index in date
                    "target_device_group_id": int(high_pce_full["Group_ID"]),
                    "control_device_group_id": int(low_pce_full["Group_ID"]),
                    "diff_count": int(diff_count),
                    "diff_columns": [
                        col
                        for col, unequal in zip(feature_columns, unequal_mask)
                        if unequal
                    ],
                    "valid_diff_columns": permit_single_var,
                    "target_device_desc": des1,
                    "control_device_desc": des2,
                    "target_device_desc_full": full_desc1,
                    "control_device_desc_full": full_desc2,
                    "diff_part": diff_part,
                    "FF_Change": f"{low_pce_full['FF']}->{high_pce_full['FF']}",
                    "Voc_Change": f"{low_pce_full['Voc']}->{high_pce_full['Voc']}",
                    "Jsc_Change": f"{low_pce_full['Jsc']}->{high_pce_full['Jsc']}",
                    "PCE_Change": f"{low_pce_full['PCE']}->{high_pce_full['PCE']}",
                    "PCE_Change_Value": float(
                        high_pce_full["PCE"] - low_pce_full["PCE"]
                    ),
                    "Diff_Desc": difference_desc,
                    **high_pce_full,
                }
            )

    return matched_pairs


def fp_process(fp_data_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    grouped = get_data(fp_data_path)
    dates = sorted(grouped.groups.keys())

    only_formula = True

    n = 300  # size of sliding window

    process_func = partial(
        process_date,
        dates=dates,
        grouped=grouped,
        n=n,
        output_dir=output_dir,
        only_formula=only_formula,
    )

    with Pool(processes=5) as pool:
        pool.map(process_func, range(len(dates)))


def formula_process(formula_data_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    grouped = get_data(formula_data_path)
    dates = sorted(grouped.groups.keys())

    only_formula = False

    n = 300  # size of sliding window

    process_func = partial(
        process_date,
        dates=dates,
        grouped=grouped,
        n=n,
        output_dir=output_dir,
        only_formula=only_formula,
    )

    with Pool(processes=5) as pool:
        pool.map(process_func, range(len(dates)))


def generate_single_var(
    fp_data_path, formula_data_path, fp_output_dir, formula_output_dir
):
    formula_process(formula_data_path, formula_output_dir)
    fp_process(fp_data_path, fp_output_dir)


