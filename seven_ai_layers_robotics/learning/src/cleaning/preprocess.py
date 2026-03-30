import os
import os.path as osp
from typing import Optional

import pandas as pd

PVK_ELE_COLUMNS = ["Cs", "MA", "FA", "Pb", "I", "Br"]
FORMULA_COLUMNS = [
    "Formula Additive 1",
    "Formula Additive 2",
    "Formula Additive 3",
    "Formula SAM 1",
    "Formula SAM 2",
    "Formula SAM 3",
    "Formula Passivator 1",
    "Formula Passivator 2",
    "Formula Passivator 3",
    "formula",
]

FP_COLUMNS = [
    "Formula Additive 1",
    "Formula Additive 2",
    "Formula Additive 3",
    "Concentration Additive 1",
    "Concentration Additive 2",
    "Concentration Additive 3",
    "Formula SAM 1",
    "Formula SAM 2",
    "Formula SAM 3",
    "Concentration SAM 1",
    "Concentration SAM 2",
    "Concentration SAM 3",
    "Formula Passivator 1",
    "Formula Passivator 2",
    "Formula Passivator 3",
    "Concentration Passivator 1",
    "Concentration Passivator 2",
    "Concentration Passivator 3",
    "Spin Coating Speed PVK 1",
    "Spin Coating Time PVK 1",
    "Spin Coating Speed PVK 2",
    "Spin Coating Time PVK 2",
    "Antisolvent Dropping Timing",
    "Antisolvent Volume",
    "Annealed Temperature PVK",
    "Annealed Time PVK",
    "Spin Coating Speed Passivator",
    "Spin Coating Time Passivator",
    "Passivator Dropping Timing",
    "Passivator Volume",
    "Annealed Temperature Passivator",
    "Annealed Time Passivator",
    "formula",
    "Concentration PVK",
]


def save_dataframe_to_csv(
    df: pd.DataFrame,
    file_path: str,
    index: bool = False,
    encoding: str = "utf-8",
    sep: str = ",",
    na_rep: Optional[str] = None,
) -> None:
    """
    Save a pandas DataFrame to a CSV file.

    Parameters:
        df (pd.DataFrame): The DataFrame to save.
        file_path (str): The path (including filename) where the CSV will be saved.
        index (bool): Whether to write row names (index). Default is False.
        encoding (str): File encoding. Default is 'utf-8'.
        sep (str): Delimiter to use. Default is ','.
        na_rep (Optional[str]): Missing data representation. Default is None.

    Raises:
        ValueError: If the input DataFrame is empty.
        IOError: If there is an error writing the file.
    """
    if df.empty:
        raise ValueError("The input DataFrame is empty and cannot be saved.")

    try:
        df.to_csv(file_path, index=index, encoding=encoding, sep=sep, na_rep=na_rep)
    except Exception as e:
        raise IOError(f"Failed to save DataFrame to CSV: {e}")


def format_number(element, num):
    if num == 0:
        return ""  # 不保留该元素
    if element == "Pb" and num == 1:
        return "Pb"  # Pb1 → Pb
    if num == int(num):
        return f"{element}{int(num)}"  # 如 I1 → I1
    else:
        return f"{element}{str(num).rstrip('0').rstrip('.')}"  # 如 Cs0.05 → Cs0.05


def generate_dedup_data(data_path):
    # df = pd.read_excel(data_path)
    df = pd.read_csv(data_path)
    df = df.fillna("NA")

    df["formula"] = df.apply(
        lambda row: "".join([format_number(col, row[col]) for col in PVK_ELE_COLUMNS]),
        axis=1,
    )

    df[("Group_ID")] = df.groupby(FORMULA_COLUMNS).ngroup()

    df_with_group_id = df.copy()

    df_sorted = df.sort_values(by="PCE", ascending=False)

    df_dedup = df_sorted.drop_duplicates(subset=FP_COLUMNS, keep="first").copy()

    df_formula_dedup = df_dedup.drop_duplicates(
        subset=FORMULA_COLUMNS, keep="first"
    ).copy()

    return df_formula_dedup, df_dedup, df_with_group_id


def preprocess(
    src_file: str, formula_dedup_path: str, fp_dedup_path: str, no_dedup_path: str
):
    df_formula_dedup, df_fp_dedup, df_with_group_id = generate_dedup_data(src_file)

    if not osp.exists(osp.dirname(formula_dedup_path)):
        os.makedirs(osp.dirname(formula_dedup_path), exist_ok=True)

    print(len(df_formula_dedup))
    print(len(df_fp_dedup))
    print(len(df_with_group_id))

    save_dataframe_to_csv(df_formula_dedup, formula_dedup_path)
    save_dataframe_to_csv(df_fp_dedup, fp_dedup_path)
    save_dataframe_to_csv(df_with_group_id, no_dedup_path)


def main():
    src_path = "/data/sunyao/Workspace/Projects/Reasoning/data/src/latest_50764/re_formula_remove_abnormal.csv"
    save_root = "/data/sunyao/Workspace/Projects/Reasoning/data/src/latest_50764/"

    df_formula_dedup, df_fp_dedup, df_with_group_id = generate_dedup_data(src_path)
    if not osp.exists(save_root):
        os.makedirs(save_root, exist_ok=True)

    formula_dedup_path = osp.join(save_root, "formula_dedup_remove_abnormal.csv")
    fp_dedup_path = osp.join(save_root, "fp_dedup_remove_abnormal.csv")
    no_dedup_path = osp.join(save_root, "reformula_with_group_id.csv")

    print(len(df_formula_dedup))
    print(len(df_fp_dedup))
    print(len(df_with_group_id))

    save_dataframe_to_csv(df_formula_dedup, formula_dedup_path)
    save_dataframe_to_csv(df_fp_dedup, fp_dedup_path)
    save_dataframe_to_csv(df_with_group_id, no_dedup_path)


if __name__ == "__main__":
    main()
