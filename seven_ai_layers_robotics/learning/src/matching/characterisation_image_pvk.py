from __future__ import annotations
def run_characterisation_image_pvk(
    *,
    seed: int | None = None,
    verbose: bool = True,
) -> None:
    """
    Run Characterisation Image PVK pipeline.

    Args:
        seed: Override random seed (optional).
        verbose: Print start / end logs.
        
    Returns:
        None
    """
    if verbose:
        print("▶ Running Characterisation Image PVK pipeline...")

    if seed is not None:
        import random
        import numpy as np
        random.seed(seed)
        np.random.seed(seed)

    main()

    if verbose:
        print("✅ Characterisation Image PVK pipeline finished.")

import sys
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import re
import csv
import mysql.connector
from mysql.connector import Error
import os


def export_table_to_csv_exclude_id(table_name: str, output_csv: str, mysql_config: dict) -> None:
    """Export MySQL table to CSV, excluding 'id' column, and safely handle output path.
    
    Args:
        table_name: Name of the MySQL table to export.
        output_csv: Output CSV file path.
        mysql_config: MySQL database configuration dictionary.
        
    Returns:
        None
    """
    # Safely create output directory (only when path is not empty)
    output_dir = os.path.dirname(output_csv)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute(f"SELECT * FROM `{table_name}`")
        rows = cursor.fetchall()

        if not rows:
            print(f"⚠️ Table `{table_name}` is empty.")
            # Get column names
            cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
            columns_info = cursor.fetchall()
            all_columns = [col['Field'] for col in columns_info]
        else:
            all_columns = list(rows[0].keys())

        # Exclude 'id' column (case insensitive)
        data_columns = [col for col in all_columns if col.lower() != 'id']

        with open(output_csv, "w", encoding="utf-8", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data_columns, extrasaction='ignore')
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

        row_count = len(rows) if rows else 0
        print(f"✅ Table `{table_name}` exported to `{output_csv}` ({row_count} rows, excluding 'id' column)")

    except Error as e:
        print(f"❌ Export failed: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# =========================
# Import configuration from config
# =========================
import sys
from pathlib import Path

# Add project root to Python path to find config module
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from config import config

MYSQL_CONFIG = {
    'host': config.learning_database.host,
    'port': config.learning_database.port,
    'user': config.learning_database.user,
    'password': config.learning_database.password,
    'database': config.learning_database.database,
    'charset': config.learning_database.charset,
}

# Replace with your actual table name
TABLE_NAME = "characterisation_image_pvk"  # ← e.g., the table you imported before
OUTPUT_CSV = "characterisation_image_pvk_db.csv"


# export_table_to_csv_exclude_id(TABLE_NAME, OUTPUT_CSV, MYSQL_CONFIG)

# Subsequent processing scripts can directly use:
INPUT_CSV = OUTPUT_CSV
# =========================
# CONFIG (edit here)
# =========================
OUTPUT_JSON = "characterisation_image_pvk/characterisation_image_pvk_pairs.json"
INDEX_COL = "index"                           # <-- your stable row id column
DATE_COL = "date"                        # <-- date column name (optional)

QUESTION = (
    "During the preparation of perovskite thin films, how do adjustments to perovskite composition concentration or "
    "process parameters affect the defect coverage ratio and grayscale intensity values obtained from image-based "
    "defect detection, thereby influencing the device performance parameters (PCE, Voc, Jsc, FF)?"
)

# --- Pair definition space ---
# We lock ALL formula + material concentration columns, and only allow "PROCESS_COLS" to be the differing column.
FORMULA_COLS_ALL = [
    "Formula PVK",
    "Formula SAM 1", "Formula SAM 2", "Formula SAM 3",
    "Formula Additive 1", "Formula Additive 2", "Formula Additive 3",
    "Formula Passivator 1", "Formula Passivator 2", "Formula Passivator 3",
]
MATERIAL_CONC_COLS_ALL = [
    "Concentration PVK",
    "Concentration SAM 1", "Concentration SAM 2", "Concentration SAM 3",
    "Concentration Additive 1", "Concentration Additive 2", "Concentration Additive 3",
    "Concentration Passivator 1", "Concentration Passivator 2", "Concentration Passivator 3",
]

# Process columns: the ONLY columns we allow to differ (missing cols will be ignored automatically)
PROCESS_COLS = [
    # perovskite spin/antisolvent/anneal
    "Spin Coating Speed PVK 1",
    "Spin Coating Time PVK 1",
    "Spin Coating Speed PVK 2",
    "Spin Coating Time PVK 2",
    "Antisolvent Dropping Timing",
    "Antisolvent Volume",
    "Annealed Temperature PVK",
    "Annealed Time PVK",
    # (optional) passivator process, if your table contains these
    "Spin Coating Speed Passivator",
    "Spin Coating Time Passivator",
    "Passivator Dropping Timing",
    "Passivator Volume",
    "Annealed Temperature Passivator",
    "Annealed Time Passivator",
]

# Build the "concentration space" = material concentrations + process columns
CONC_COLS_ALL = MATERIAL_CONC_COLS_ALL + PROCESS_COLS

# We do NOT need formula-mode pairs for Process (disable by ignoring all formula columns)
FORMULA_DIFF_IGNORE = list(FORMULA_COLS_ALL)

# In concentration-mode, material concentration columns must match but are not allowed to be "the differing column"
CONC_DIFF_IGNORE = list(MATERIAL_CONC_COLS_ALL)

# --- Filtering rule metrics (from your process_pairs_evaluation.py) ---
AREA_COL = "area_px2"
GRAY_COL = "gray_mean"
PCE_COL = "PCE"
METRIC_COLS = [AREA_COL, GRAY_COL, PCE_COL]


# Extra filter: keep only if target PCE >= this threshold
TARGET_PCE_MIN = 10.0
# Random seed for template sampling
SEED = 42

# Pair sources to export: for Process we only use "concentration"
# Change to {"formula", "concentration"} if you want both modes
PAIR_SOURCES = {"concentration"}

# If >0, randomly downsample filtered pairs (per source)
MAX_PAIRS_PER_SOURCE = 0

# Write intermediate debug CSV files next to OUTPUT_JSON
WRITE_DEBUG_CSV = True
# =========================
# END CONFIG
# =========================


# -------------------------
# 1) CSV I/O helpers
# -------------------------
def read_csv_auto(path: Path) -> pd.DataFrame:
    """Read CSV file with automatic encoding detection.
    
    Args:
        path: Path to the CSV file.
        
    Returns:
        Loaded DataFrame.
        
    Raises:
        RuntimeError: If file cannot be read with utf-8-sig/utf-8/gbk/GBK encodings.
    """
    last_err = None
    for enc in ("utf-8-sig", "utf-8", "gbk", "GBK"):
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Failed to read CSV with utf-8-sig/utf-8/gbk: {path}. Last error: {last_err}")


def strip_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace from all column names in DataFrame.
    
    Args:
        df: Input DataFrame.
        
    Returns:
        DataFrame with stripped column names.
    """
    df = df.copy()
    df.rename(columns=lambda c: str(c).strip(), inplace=True)
    return df


def ensure_index_col(df: pd.DataFrame, index_col: str) -> pd.DataFrame:
    """Ensure there is a stable ID column (index_col) and normalize it as string.
    - If index_col is missing, we fall back to the current DataFrame index (reset_index).
    - Empty IDs are dropped.
    """
    df = df.copy()
    if index_col not in df.columns:
        df = df.reset_index().rename(columns={"index": index_col})

    df[index_col] = df[index_col].astype("string").fillna("").str.strip()
    df = df[df[index_col] != ""].copy()
    return df

def normalize_series(s: pd.Series) -> pd.Series:
    """Normalize text cells without pandas.replace downcasting warnings."""
    s = s.astype("string").fillna("")
    s = s.str.strip()
    s = s.str.replace(r"\s+", " ", regex=True)
    s = s.mask(s.str.lower().eq("nan"), "")
    return s


def normalize_date(v: Any) -> str:
    """Normalize date to 'YYYYMMDD' string. Returns '' if missing/unparseable."""
    if v is None:
        return ""
    try:
        if pd.isna(v):
            return ""
    except Exception:
        pass
    s = str(v).strip()
    if s.lower() in ("", "n/a", "na", "none", "nan"):
        return ""
    digits = re.sub(r"\D", "", s)
    if len(digits) >= 8:
        return digits[:8]
    dt = pd.to_datetime(s, errors="coerce")
    if pd.isna(dt):
        return ""
    return dt.strftime("%Y%m%d")

# -------------------------
# 2) Pair mining (only 1 col differs)
# -------------------------
def count_pairs_differing_in_one_column(
    df_in: pd.DataFrame,
    cols_all: List[str],
    target_col: str,
    row_index_col: str = "_row_index",
) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Find all pairs where ONLY target_col differs and all other cols in cols_all are identical.
    Returns (n_pairs, records).
    """
    other_cols = [c for c in cols_all if c != target_col]
    if not other_cols:
        return 0, []

    # group by identical other_cols
    keys = df_in[other_cols].apply(lambda r: tuple(r.values.tolist()), axis=1)
    grouped = df_in.groupby(keys, dropna=False)

    records: List[Dict[str, Any]] = []
    for _, gdf in grouped:
        # Need at least 2 distinct values in target_col
        if gdf[target_col].nunique(dropna=False) <= 1:
            continue

        val_to_rows = {val: rows for val, rows in gdf.groupby(target_col)}
        values = list(val_to_rows.keys())
        for i in range(len(values)):
            for j in range(i + 1, len(values)):
                a = val_to_rows[values[i]]
                b = val_to_rows[values[j]]
                for _, row1 in a.iterrows():
                    for _, row2 in b.iterrows():
                        r1 = str(row1[row_index_col])
                        r2 = str(row2[row_index_col])
                        if r1 == r2:
                            continue
                        rr1, rr2 = (r1, r2) if str(r1) < str(r2) else (r2, r1)
                        records.append(
                            {
                                "differing_column": target_col,
                                "row1_index": rr1,
                                "row2_index": rr2,
                            }
                        )

    if not records:
        return 0, []
    recs_df = pd.DataFrame(records).drop_duplicates(subset=["differing_column", "row1_index", "row2_index"])
    return len(recs_df), recs_df.to_dict(orient="records")


def build_pairs(
    df_main: pd.DataFrame,
    index_col: str,
    formula_cols_all: List[str],
    conc_cols_all: List[str],
    formula_diff_ignore: List[str],
    conc_diff_ignore: List[str],
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Returns:
      pairs_formula_df (likely empty for Process),
      pairs_conc_df (Process pairs live here),
      summary dict
    """
    df = df_main.copy()

    fcols = [c for c in formula_cols_all if c in df.columns]
    ccols = [c for c in conc_cols_all if c in df.columns]

    cols_needed = list(dict.fromkeys([index_col] + fcols + ccols))
    df = df[cols_needed].copy()
    df["_row_index"] = df[index_col]

    for c in fcols + ccols:
        df[c] = normalize_series(df[c])

    # ---- formula pairs (disabled for Process by ignoring all formula cols) ----
    formula_diff_cols = [c for c in fcols if c not in set(formula_diff_ignore)]
    formula_records_all: List[Dict[str, Any]] = []
    formula_breakdown: List[Dict[str, Any]] = []
    for col in formula_diff_cols:
        cnt, recs = count_pairs_differing_in_one_column(df, fcols, col, row_index_col="_row_index")
        formula_breakdown.append({"column": col, "pairs": cnt})
        formula_records_all.extend(recs)
    pairs_formula_df = pd.DataFrame(formula_records_all)

    # ---- concentration pairs: formulas + concentrations must match, except 1 differing conc col (process col) ----
    conc_diff_cols = [c for c in ccols if c not in set(conc_diff_ignore)]
    cols_for_space = fcols + ccols

    conc_records_all: List[Dict[str, Any]] = []
    conc_breakdown: List[Dict[str, Any]] = []
    for col in conc_diff_cols:
        cnt, recs = count_pairs_differing_in_one_column(df, cols_for_space, col, row_index_col="_row_index")
        conc_breakdown.append({"column": col, "pairs": cnt})
        conc_records_all.extend(recs)
    pairs_conc_df = pd.DataFrame(conc_records_all)

    summary = {
        "n_rows_main": len(df_main),
        "existing_formula_cols": fcols,
        "existing_conc_cols": ccols,
        "formula_pairs": int(len(pairs_formula_df)),
        "concentration_pairs": int(len(pairs_conc_df)),
        "formula_breakdown": formula_breakdown,
        "concentration_breakdown": conc_breakdown,
    }
    return pairs_formula_df, pairs_conc_df, summary


# -------------------------
# 3) Pair filtering rule (Process / image metrics)
# -------------------------
def rule_image_case(row1: pd.Series, row2: pd.Series, area_col: str, gray_col: str, pce_col: str) -> Optional[str]:
    """
    Rule aligned with process_pairs_evaluation.py:
      Case row1:
        (area1 < area2) AND (gray1 > gray2) AND (pce1 < pce2)
      Case row2:
        (area2 < area1) AND (gray2 > gray1) AND (pce2 < pce1)

    Return "row1"/"row2" indicating which row satisfies the condition.
    """
    a1, g1, p1 = row1[area_col], row1[gray_col], row1[pce_col]
    a2, g2, p2 = row2[area_col], row2[gray_col], row2[pce_col]

    if any(pd.isna(v) for v in (a1, a2, g1, g2, p1, p2)):
        return None

    if (a1 < a2) and (g1 > g2) and (p1 < p2):
        return "row1"
    if (a2 < a1) and (g2 > g1) and (p2 < p1):
        return "row2"
    return None


def evaluate_pairs(
    pairs_df: pd.DataFrame,
    df_main: pd.DataFrame,
    index_col: str,
    metric_cols: List[str],
    area_col: str,
    gray_col: str,
    pce_col: str,
) -> pd.DataFrame:
    """
    Adds condition_case and filters to only condition_case != None.
    """
    if pairs_df is None or pairs_df.empty:
        return pairs_df.copy()

    missing_metrics = [c for c in metric_cols if c not in df_main.columns]
    if missing_metrics:
        raise ValueError(f"Main table missing required metric cols: {missing_metrics}")

    metrics_df = (
        df_main.drop_duplicates(subset=[index_col], keep="first")
        .set_index(index_col)[metric_cols]
        .apply(pd.to_numeric, errors="coerce")
    )

    res = pairs_df.copy()
    case_list = []
    for _, row in res.iterrows():
        r1 = str(row["row1_index"])
        r2 = str(row["row2_index"])
        if (r1 not in metrics_df.index) or (r2 not in metrics_df.index):
            case_list.append(None)
            continue
        s1 = metrics_df.loc[r1]
        s2 = metrics_df.loc[r2]
        case_list.append(rule_image_case(s1, s2, area_col=area_col, gray_col=gray_col, pce_col=pce_col))

    res["condition_case"] = case_list
    res = res[res["condition_case"].notna()].reset_index(drop=True)
    return res


# -------------------------
# 4) Text generation via templates_lib
# -------------------------
def import_templates_lib():
    script_dir = Path(__file__).parent.resolve()
    # 确保 matching 目录在 Python 路径中
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

    # 强制重新加载 templates_lib 模块（可选）
    import importlib
    try:
        import templates_lib
        importlib.reload(templates_lib)
    except ImportError:
        # 如果仍然失败，尝试直接添加 templates_lib 目录
        templates_lib_dir = script_dir / "templates_lib"
        if templates_lib_dir.exists() and str(templates_lib_dir) not in sys.path:
            sys.path.insert(0, str(templates_lib_dir))
        import templates_lib

    try:
        from templates_lib import (  # type: ignore
            prepared_phrases,
            intro_segments,
            perovskite_formula_segments,
            process_segments,
            antisolvent_segments,
            anneal_segments,
            instruction_templates,
            image_analysis_segments,
            pl_analysis_segments,
            xrd_analysis_segments_12,
            xrd_analysis_segments_stress,
            sam_formula_segments_single,
            sam_formula_segments_dual,
            sam_formula_segments_triple,
            additive_formula_segments_single,
            additive_formula_segments_dual,
            additive_formula_segments_triple,
            passivation_material_segments_single,
            passivation_material_segments_dual,
            passivation_material_segments_triple,
            passivation_spin_segments,
            passivation_drop_segments,
            passivation_anneal_segments,
        )
    except Exception as e:
        raise ImportError(
            "Cannot import templates_lib. Put templates_lib.py next to this script, or add it to PYTHONPATH. "
            f"Original error: {e}"
        )

    return {
        "prepared_phrases": prepared_phrases,
        "intro_segments": intro_segments,
        "perovskite_formula_segments": perovskite_formula_segments,
        "process_segments": process_segments,
        "antisolvent_segments": antisolvent_segments,
        "anneal_segments": anneal_segments,
        "instruction_templates": instruction_templates,
        "image_analysis_segments": image_analysis_segments,
        "pl_analysis_segments": pl_analysis_segments,
        "xrd_analysis_segments_12": xrd_analysis_segments_12,
        "xrd_analysis_segments_stress": xrd_analysis_segments_stress,
        "sam_formula_segments_single": sam_formula_segments_single,
        "sam_formula_segments_dual": sam_formula_segments_dual,
        "sam_formula_segments_triple": sam_formula_segments_triple,
        "additive_formula_segments_single": additive_formula_segments_single,
        "additive_formula_segments_dual": additive_formula_segments_dual,
        "additive_formula_segments_triple": additive_formula_segments_triple,
        "passivation_material_segments_single": passivation_material_segments_single,
        "passivation_material_segments_dual": passivation_material_segments_dual,
        "passivation_material_segments_triple": passivation_material_segments_triple,
        "passivation_spin_segments": passivation_spin_segments,
        "passivation_drop_segments": passivation_drop_segments,
        "passivation_anneal_segments": passivation_anneal_segments,
    }


def gv(row: pd.Series, col: str, default: str = "N/A") -> str:
    if col not in row.index:
        return default
    val = row[col]
    if pd.isna(val):
        return default
    return str(val)


def build_templates_for_row(row: pd.Series, T: Dict[str, Any]) -> Dict[str, str]:
    prepared_term = random.choice(T["prepared_phrases"])
    intro_template = random.choice(T["intro_segments"])
    perovskite_template = random.choice(T["perovskite_formula_segments"])
    process_template = random.choice(T["process_segments"])
    antisolvent_template = random.choice(T["antisolvent_segments"])
    anneal_template = random.choice(T["anneal_segments"])
    _ = random.choice(T["instruction_templates"])  # keep randomness consistent

    image_analysis_template = random.choice(T["image_analysis_segments"]) if T["image_analysis_segments"] else ""

    # NOTE: For Process dataset, you likely don't want PL/XRD in the text; keep them available but unused by default.
    pl_analysis_template = random.choice(T["pl_analysis_segments"]) if T["pl_analysis_segments"] else ""
    xrd_analysis_12 = random.choice(T["xrd_analysis_segments_12"]) if T["xrd_analysis_segments_12"] else ""
    xrd_analysis_stress = random.choice(T["xrd_analysis_segments_stress"]) if T["xrd_analysis_segments_stress"] else ""

    # SAM templates (optional)
    sam_formula_template = ""
    if gv(row, "Formula SAM 1") != "N/A":
        if gv(row, "Formula SAM 2") == "N/A" and gv(row, "Formula SAM 3") == "N/A":
            sam_formula_template = random.choice(T["sam_formula_segments_single"])
        elif gv(row, "Formula SAM 3") == "N/A":
            sam_formula_template = random.choice(T["sam_formula_segments_dual"])
        else:
            sam_formula_template = random.choice(T["sam_formula_segments_triple"])

    # Additive templates (optional)
    additive_formula_template = ""
    if gv(row, "Formula Additive 1") != "N/A":
        if gv(row, "Formula Additive 2") == "N/A" and gv(row, "Formula Additive 3") == "N/A":
            additive_formula_template = random.choice(T["additive_formula_segments_single"])
        elif gv(row, "Formula Additive 3") == "N/A":
            additive_formula_template = random.choice(T["additive_formula_segments_dual"])
        else:
            additive_formula_template = random.choice(T["additive_formula_segments_triple"])

    # Passivation templates (optional)
    passivation_material_template = ""
    passivation_spin_template = ""
    passivation_drop_template = ""
    passivation_anneal_template = ""
    if gv(row, "Formula Passivator 1") != "N/A":
        p2 = gv(row, "Formula Passivator 2")
        p3 = gv(row, "Formula Passivator 3")
        if p2 != "N/A" and p3 != "N/A":
            passivation_material_template = random.choice(T["passivation_material_segments_triple"])
        elif p2 != "N/A":
            passivation_material_template = random.choice(T["passivation_material_segments_dual"])
        else:
            passivation_material_template = random.choice(T["passivation_material_segments_single"])
        passivation_spin_template = random.choice(T["passivation_spin_segments"])
        passivation_drop_template = random.choice(T["passivation_drop_segments"])
        passivation_anneal_template = random.choice(T["passivation_anneal_segments"])

    return {
        "prepared_term": prepared_term,
        "intro": intro_template,
        "perovskite_formula": perovskite_template,
        "sam_formula": sam_formula_template,
        "additive_formula": additive_formula_template,
        "process": process_template,
        "antisolvent": antisolvent_template,
        "anneal": anneal_template,
        "passivation_material": passivation_material_template,
        "passivation_spin": passivation_spin_template,
        "passivation_drop": passivation_drop_template,
        "passivation_anneal": passivation_anneal_template,
        "image_analysis": image_analysis_template,
        # keep but not used by default:
        "pl_analysis": pl_analysis_template,
        "xrd_analysis_12": xrd_analysis_12,
        "xrd_analysis_stress": xrd_analysis_stress,
    }


def generate_output_text(row: pd.Series, templates: Dict[str, str]) -> str:
    parts: List[str] = []

    parts.append(
        templates["intro"].format(
            prepared_term=templates["prepared_term"],
            pce=gv(row, "PCE"),
            ff=gv(row, "FF"),
            voc=gv(row, "Voc"),
            jsc=gv(row, "Jsc"),
        )
    )

    parts.append(
        templates["perovskite_formula"].format(
            formula_pvk=gv(row, "Formula PVK"),
            concentration_pvk=gv(row, "Concentration PVK"),
        )
    )

    if templates.get("sam_formula"):
        parts.append(
            templates["sam_formula"].format(
                formula_sam1=gv(row, "Formula SAM 1"),
                concentration_sam1=gv(row, "Concentration SAM 1"),
                formula_sam2=gv(row, "Formula SAM 2"),
                concentration_sam2=gv(row, "Concentration SAM 2"),
                formula_sam3=gv(row, "Formula SAM 3"),
                concentration_sam3=gv(row, "Concentration SAM 3"),
            )
        )

    if templates.get("additive_formula"):
        parts.append(
            templates["additive_formula"].format(
                formula_add1=gv(row, "Formula Additive 1"),
                concentration_add1=gv(row, "Concentration Additive 1"),
                formula_add2=gv(row, "Formula Additive 2"),
                concentration_add2=gv(row, "Concentration Additive 2"),
                formula_add3=gv(row, "Formula Additive 3"),
                concentration_add3=gv(row, "Concentration Additive 3"),
            )
        )

    parts.append(
        templates["process"].format(
            spin1_speed=gv(row, "Spin Coating Speed PVK 1"),
            spin1_time=gv(row, "Spin Coating Time PVK 1"),
            spin2_speed=gv(row, "Spin Coating Speed PVK 2"),
            spin2_time=gv(row, "Spin Coating Time PVK 2"),
        )
    )

    parts.append(
        templates["antisolvent"].format(
            antisolvent_volume=gv(row, "Antisolvent Volume"),
            antisolvent_timing=gv(row, "Antisolvent Dropping Timing"),
        )
    )

    parts.append(
        templates["anneal"].format(
            anneal_temp=gv(row, "Annealed Temperature PVK"),
            anneal_time=gv(row, "Annealed Time PVK"),
        )
    )

    if templates.get("passivation_material"):
        parts.append(
            templates["passivation_material"].format(
                formula_passivator1=gv(row, "Formula Passivator 1"),
                concentration_passivator1=gv(row, "Concentration Passivator 1"),
                formula_passivator2=gv(row, "Formula Passivator 2"),
                concentration_passivator2=gv(row, "Concentration Passivator 2"),
                formula_passivator3=gv(row, "Formula Passivator 3"),
                concentration_passivator3=gv(row, "Concentration Passivator 3"),
            )
        )
        if templates.get("passivation_spin"):
            parts.append(
                templates["passivation_spin"].format(
                    spin_speed_passivator=gv(row, "Spin Coating Speed Passivator"),
                    spin_time_passivator=gv(row, "Spin Coating Time Passivator"),
                )
            )
        if templates.get("passivation_drop"):
            parts.append(
                templates["passivation_drop"].format(
                    passivator_timing=gv(row, "Passivator Dropping Timing"),
                    passivator_volume=gv(row, "Passivator Volume"),
                )
            )
        if templates.get("passivation_anneal"):
            parts.append(
                templates["passivation_anneal"].format(
                    anneal_temp_passivator=gv(row, "Annealed Temperature Passivator"),
                    anneal_time_passivator=gv(row, "Annealed Time Passivator"),
                )
            )

    # Image metrics segment (optional, if your table has them)
    if (AREA_COL in row.index) and (GRAY_COL in row.index):
        if gv(row, AREA_COL) != "N/A" and gv(row, GRAY_COL) != "N/A":
            parts.append(
                templates["image_analysis"].format(
                    coverage=gv(row, AREA_COL),
                    grayscale_value=gv(row, GRAY_COL),
                )
            )

    return " ".join([p for p in parts if p])


def row_to_text(row: pd.Series, T: Dict[str, Any]) -> str:
    templates = build_templates_for_row(row, T)
    return generate_output_text(row, templates)



def to_float(x: Any) -> float:
    """Robust float conversion; returns NaN if conversion fails."""
    try:
        if pd.isna(x):
            return float("nan")
    except Exception:
        pass
    try:
        s = str(x).strip()
        if s.lower() in ("", "n/a", "na", "none", "nan"):
            return float("nan")
        return float(s)
    except Exception:
        return float("nan")

def safe_colname(x: Any) -> str:
    if x is None:
        return ""
    s = str(x).strip()
    if s.lower() in ("", "n/a", "na", "none", "nan"):
        return ""
    return s


# -------------------------
# 5) End-to-end main
# -------------------------
def maybe_downsample(df: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
    if n <= 0 or df is None or df.empty or len(df) <= n:
        return df
    return df.sample(n=n, random_state=seed).reset_index(drop=True)


def main() -> None:
    random.seed(SEED)
    np.random.seed(SEED)

    # in_path = Path(INPUT_CSV)
    # out_path = Path(OUTPUT_JSON)
    # out_path.parent.mkdir(parents=True, exist_ok=True)
    script_dir = Path(__file__).parent.resolve()
    # 所有输出都到 data 目录（与 src 平级）
    output_dir = script_dir.parent.parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_csv = output_dir / OUTPUT_CSV

    # JSON 输出也到 data 目录
    json_output_dir = output_dir / "characterisation_image_pvk"
    json_output_dir.mkdir(parents=True, exist_ok=True)
    output_json = json_output_dir / "characterisation_image_pvk_pairs.json"

    export_table_to_csv_exclude_id(TABLE_NAME, output_csv, MYSQL_CONFIG)

    # ---- read main table ----
    df_main = read_csv_auto(output_csv)
    df_main = strip_columns(df_main)
    df_main = ensure_index_col(df_main, INDEX_COL)

    # ---- mine pairs ----
    pairs_formula_df, pairs_conc_df, summary = build_pairs(
        df_main=df_main,
        index_col=INDEX_COL,
        formula_cols_all=FORMULA_COLS_ALL,
        conc_cols_all=CONC_COLS_ALL,
        formula_diff_ignore=FORMULA_DIFF_IGNORE,
        conc_diff_ignore=CONC_DIFF_IGNORE,
    )

    # ---- filter by rule ----
    filtered_formula = pd.DataFrame()
    filtered_conc = pd.DataFrame()
    if "formula" in PAIR_SOURCES and not pairs_formula_df.empty:
        filtered_formula = evaluate_pairs(
            pairs_df=pairs_formula_df,
            df_main=df_main,
            index_col=INDEX_COL,
            metric_cols=METRIC_COLS,
            area_col=AREA_COL,
            gray_col=GRAY_COL,
            pce_col=PCE_COL,
        )
    if "concentration" in PAIR_SOURCES and not pairs_conc_df.empty:
        filtered_conc = evaluate_pairs(
            pairs_df=pairs_conc_df,
            df_main=df_main,
            index_col=INDEX_COL,
            metric_cols=METRIC_COLS,
            area_col=AREA_COL,
            gray_col=GRAY_COL,
            pce_col=PCE_COL,
        )

    # ---- optional downsample ----
    filtered_formula = maybe_downsample(filtered_formula, MAX_PAIRS_PER_SOURCE, SEED) if not filtered_formula.empty else filtered_formula
    filtered_conc = maybe_downsample(filtered_conc, MAX_PAIRS_PER_SOURCE, SEED) if not filtered_conc.empty else filtered_conc

    # ---- debug CSVs ----
    if WRITE_DEBUG_CSV:
        out_path = output_json
        debug_dir = output_dir / (output_dir.stem + "_debug")
        debug_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(summary["formula_breakdown"]).to_csv(debug_dir / "breakdown_formula.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(summary["concentration_breakdown"]).to_csv(debug_dir / "breakdown_concentration.csv", index=False, encoding="utf-8-sig")
        pairs_formula_df.to_csv(debug_dir / "pairs_formula_all.csv", index=False, encoding="utf-8-sig")
        pairs_conc_df.to_csv(debug_dir / "pairs_concentration_all.csv", index=False, encoding="utf-8-sig")
        if not filtered_formula.empty:
            filtered_formula.to_csv(debug_dir / "pairs_formula_filtered.csv", index=False, encoding="utf-8-sig")
        if not filtered_conc.empty:
            filtered_conc.to_csv(debug_dir / "pairs_concentration_filtered.csv", index=False, encoding="utf-8-sig")

    # ---- build JSON records ----
    T = import_templates_lib()
    data_idx = df_main.drop_duplicates(subset=[INDEX_COL], keep="first").fillna("N/A").set_index(INDEX_COL)

    all_records: List[Dict[str, Any]] = []

    def emit_from_pairs(src_name: str, pairs_df: pd.DataFrame) -> None:
        if pairs_df is None or pairs_df.empty:
            return

        for _, pr in pairs_df.iterrows():
            r1 = str(pr["row1_index"])
            r2 = str(pr["row2_index"])

            if r1 not in data_idx.index or r2 not in data_idx.index:
                continue

            # decide which row becomes "control" based on condition_case
            case = pr.get("condition_case", None)
            if case == "row2":
                ctrl_idx, tgt_idx = r2, r1
            else:
                ctrl_idx, tgt_idx = r1, r2

            row_control = data_idx.loc[ctrl_idx]
            row_target = data_idx.loc[tgt_idx]


            # Extra filter: target PCE must be >= TARGET_PCE_MIN
            target_pce = to_float(row_target.get(PCE_COL, float("nan")))
            if not (target_pce >= TARGET_PCE_MIN):
                continue
            control_text = row_to_text(row_control, T)
            target_text = row_to_text(row_target, T)

            # Process list from differing_column
            proc_name = safe_colname(pr.get("differing_column", ""))
            process_list = [proc_name] if proc_name else []

            record = {
                "question": QUESTION,
                "control": control_text,
                "target": target_text,
                "pair_source": src_name,
                "sample_id_1": str(ctrl_idx),
                "sample_id_2": str(tgt_idx),
                "sample_id_1_date": normalize_date(row_control.get(DATE_COL, "")),
                "sample_id_2_date": normalize_date(row_target.get(DATE_COL, "")),
                "Process": process_list,
            }
            all_records.append(record)

    if "formula" in PAIR_SOURCES and not filtered_formula.empty:
        emit_from_pairs("formula", filtered_formula)
    if "concentration" in PAIR_SOURCES and not filtered_conc.empty:
        emit_from_pairs("concentration", filtered_conc)

    # ---- write JSON ----
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)

    # ---- summary ----

    print("✅ Done.")
    print("Output JSON:", OUTPUT_JSON)
    print("Records:", summary["n_rows_main"])

    pass
if __name__ == "__main__":
    run_characterisation_image_pvk()
