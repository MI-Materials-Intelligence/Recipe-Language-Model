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
    """Format chemical element number representation.
    
    Args:
        element: Chemical element symbol (e.g., 'Pb', 'Cs').
        num: Numeric value for the element.
    
    Returns:
        Formatted string representation of element with number.
    """
    if num == 0:
        return ""
    if element == "Pb" and num == 1:
        return "Pb"
    if num == int(num):
        return f"{element}{int(num)}"
    return f"{element}{str(num).rstrip('0').rstrip('.')}"


def generate_dedup_data(data_path):
    """Generate deduplicated data from input CSV file.
    
    Args:
        data_path: Path to the input CSV file.
    
    Returns:
        Tuple of three DataFrames:
            - df_formula_dedup: Deduplicated by formula columns
            - df_dedup: Deduplicated by full process columns
            - df_with_group_id: Original data with group IDs
    """
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
) -> None:
    """Preprocess data: remove abnormalities and perform deduplication.
    
    Args:
        src_file: Path to source CSV file.
        formula_dedup_path: Output path for formula-deduplicated CSV.
        fp_dedup_path: Output path for full-process-deduplicated CSV.
        no_dedup_path: Output path for non-deduplicated CSV with group IDs.
    
    Returns:
        None
    """
    df_formula_dedup, df_fp_dedup, df_with_group_id = generate_dedup_data(src_file)

    if not osp.exists(osp.dirname(formula_dedup_path)):
        os.makedirs(osp.dirname(formula_dedup_path), exist_ok=True)

    print(len(df_formula_dedup))
    print(len(df_fp_dedup))
    print(len(df_with_group_id))

    save_dataframe_to_csv(df_formula_dedup, formula_dedup_path)
    save_dataframe_to_csv(df_fp_dedup, fp_dedup_path)
    save_dataframe_to_csv(df_with_group_id, no_dedup_path)
