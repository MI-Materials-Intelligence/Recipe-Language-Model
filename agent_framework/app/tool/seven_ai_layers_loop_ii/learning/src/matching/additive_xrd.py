from __future__ import annotations
def run_additive_xrd(
    *,
    seed: int | None = None,
    verbose: bool = True,
) -> None:
    """
    Run Image Process pipeline.

    Parameters
    ----------
    seed : int | None
        Override random seed (optional).
    verbose : bool
        Print start / end logs.
    """
    if verbose:
        print("▶ Running Additive XRD pipeline...")

    if seed is not None:
        import random
        import numpy as np
        random.seed(seed)
        np.random.seed(seed)

    main()

    if verbose:
        print("✅ Image Process pipeline finished.")
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


def export_table_to_csv_exclude_id(table_name, output_csv, mysql_config):
    """
    Export MySQL table to CSV, excluding 'id' column, and safely handle output path.
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
# Import configuration from app.config
# =========================
from app.config import config

MYSQL_CONFIG = {
    'host': config.learning_database.host,
    'port': config.learning_database.port,
    'user': config.learning_database.user,
    'password': config.learning_database.password,
    'database': config.learning_database.database,
    'charset': config.learning_database.charset,
}

# =========================
# CONFIG (edit here)
# =========================

# Replace with your actual table name
TABLE_NAME = "xrd_additives"  # ← e.g., the table you imported before
OUTPUT_CSV = "additives.csv"





INPUT_CSV = OUTPUT_CSV             # <-- your csv total table
OUTPUT_JSON = "XRD_additives/XRD_additives_pairs.json"         # <-- output json
INDEX_COL = "index"                         # <-- your stable row id column
DATE_COL = "date"                        # <-- date column name (optional)

QUESTION = (
    "How will the peak intensity and half width of the 12.6 ° characteristic peak of additives added to perovskite "
    "precursors to prepare thin films change in XRD characterization?"
)

# Pair definition space (for additives)
FORMULA_COLS = [
    "Formula PVK",
    "Formula Additive 1", "Formula Additive 2", "Formula Additive 3",
]
CONC_COLS = [
    "Concentration PVK",
    "Concentration Additive 1", "Concentration Additive 2", "Concentration Additive 3",
]

# In formula-mode, these columns must match but will not be counted as "the differing column"
FORMULA_DIFF_IGNORE = ["Formula PVK"]

# Metrics used by filtering rule
INTENSITY_COL = "xrd_intensity_12.6"
FWHM_COL = "xrd_fhwm_12.6"
PCE_COL = "PCE"
METRIC_COLS = [INTENSITY_COL, FWHM_COL, PCE_COL]

# Random seed for template sampling
SEED = 42

# Pair sources to export: choose any subset of {"formula", "concentration"}
PAIR_SOURCES = {"formula", "concentration"}

# If >0, randomly downsample the filtered pairs per source
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
    last_err = None
    for enc in ("utf-8-sig", "utf-8", "gbk"):
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Failed to read CSV with utf-8-sig/utf-8/gbk: {path}. Last error: {last_err}")


def strip_columns(df: pd.DataFrame) -> pd.DataFrame:
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
    other_cols = [c for c in cols_all if c != target_col]
    if not other_cols:
        return 0, []

    keys = df_in[other_cols].apply(lambda r: tuple(r.values.tolist()), axis=1)
    grouped = df_in.groupby(keys, dropna=False)

    records: List[Dict[str, Any]] = []
    for _, gdf in grouped:
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

                        # keep a canonical ordering for de-duplication
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
    formula_cols: List[str],
    conc_cols: List[str],
    formula_diff_ignore: List[str],
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    df = df_main.copy()

    fcols = [c for c in formula_cols if c in df.columns]
    ccols = [c for c in conc_cols if c in df.columns]

    cols_needed = list(dict.fromkeys([index_col] + fcols + ccols))
    df = df[cols_needed].copy()
    df["_row_index"] = df[index_col]

    for c in fcols + ccols:
        df[c] = normalize_series(df[c])

    # formula pairs: only 1 formula col differs (excluding ignore list)
    formula_diff_cols = [c for c in fcols if c not in set(formula_diff_ignore)]
    formula_records_all: List[Dict[str, Any]] = []
    formula_breakdown: List[Dict[str, Any]] = []

    for col in formula_diff_cols:
        cnt, recs = count_pairs_differing_in_one_column(df, fcols, col, row_index_col="_row_index")
        formula_breakdown.append({"column": col, "pairs": cnt})
        formula_records_all.extend(recs)

    pairs_formula_df = pd.DataFrame(formula_records_all)

    # concentration pairs: formulas same; only 1 conc col differs
    cols_for_space = fcols + ccols
    conc_records_all: List[Dict[str, Any]] = []
    conc_breakdown: List[Dict[str, Any]] = []

    for col in ccols:
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
# 3) Pair filtering rule
# -------------------------
def rule_xrd_better_but_pce_worse(
    row1: pd.Series, row2: pd.Series,
    intensity_col: str, fwhm_col: str, pce_col: str
) -> Optional[str]:
    """
    Keep pairs where:
      - One row has better XRD: higher intensity AND lower FWHM
      - but that row has worse PCE (lower)
    Return "row1" / "row2" indicating which row is "better XRD but worse PCE".
    """
    i1, f1, p1 = row1[intensity_col], row1[fwhm_col], row1[pce_col]
    i2, f2, p2 = row2[intensity_col], row2[fwhm_col], row2[pce_col]

    if any(pd.isna(v) for v in (i1, i2, f1, f2, p1, p2)):
        return None

    if (i1 > i2) and (f1 < f2) and (p1 < p2):
        return "row1"
    if (i2 > i1) and (f2 < f1) and (p2 < p1):
        return "row2"
    return None


def evaluate_pairs(
    pairs_df: pd.DataFrame,
    df_main: pd.DataFrame,
    index_col: str,
    metric_cols: List[str],
    intensity_col: str,
    fwhm_col: str,
    pce_col: str,
) -> pd.DataFrame:
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
        case = rule_xrd_better_but_pce_worse(
            s1, s2,
            intensity_col=intensity_col,
            fwhm_col=fwhm_col,
            pce_col=pce_col
        )
        case_list.append(case)

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

    xrd_analysis_12 = random.choice(T["xrd_analysis_segments_12"]) if T["xrd_analysis_segments_12"] else ""
    xrd_analysis_stress = random.choice(T["xrd_analysis_segments_stress"]) if T["xrd_analysis_segments_stress"] else ""

    # SAM templates
    sam_formula_template = ""
    if gv(row, "Formula SAM 1") != "N/A":
        if gv(row, "Formula SAM 2") == "N/A" and gv(row, "Formula SAM 3") == "N/A":
            sam_formula_template = random.choice(T["sam_formula_segments_single"])
        elif gv(row, "Formula SAM 3") == "N/A":
            sam_formula_template = random.choice(T["sam_formula_segments_dual"])
        else:
            sam_formula_template = random.choice(T["sam_formula_segments_triple"])

    # Additive templates
    additive_formula_template = ""
    if gv(row, "Formula Additive 1") != "N/A":
        if gv(row, "Formula Additive 2") == "N/A" and gv(row, "Formula Additive 3") == "N/A":
            additive_formula_template = random.choice(T["additive_formula_segments_single"])
        elif gv(row, "Formula Additive 3") == "N/A":
            additive_formula_template = random.choice(T["additive_formula_segments_dual"])
        else:
            additive_formula_template = random.choice(T["additive_formula_segments_triple"])

    # Passivation templates
    passivation_material_template = ""
    passivation_spin_template = ""
    passivation_drop_template = ""
    passivation_anneal_template = ""
    if gv(row, "Formula Passivator 1") != "N/A":
        if gv(row, "Formula Passivator 2") != "N/A" and gv(row, "Formula Passivator 3") != "N/A":
            passivation_material_template = random.choice(T["passivation_material_segments_triple"])
        elif gv(row, "Formula Passivator 2") != "N/A":
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

    # XRD 12.6° block
    if templates.get("xrd_analysis_12"):
        if gv(row, INTENSITY_COL) != "N/A" and gv(row, FWHM_COL) != "N/A":
            parts.append(
                templates["xrd_analysis_12"].format(
                    xrd_intensity_12=gv(row, INTENSITY_COL),
                    xrd_fhwm_12=gv(row, FWHM_COL),
                )
            )

    # XRD stress block
    if templates.get("xrd_analysis_stress"):
        if gv(row, "xrd_Stress") != "N/A":
            parts.append(
                templates["xrd_analysis_stress"].format(
                    xrd_intensity_4=gv(row, "xrd_intensity_4"),
                    xrd_Stress=gv(row, "xrd_Stress"),
                )
            )

    return " ".join([p for p in parts if p and str(p).strip()])


def row_to_text(row: pd.Series, T: Dict[str, Any]) -> str:
    templates = build_templates_for_row(row, T)
    return generate_output_text(row, templates)


# -------------------------
# 5) Additive list extraction
# -------------------------
def _normalize_material(x: Any) -> Optional[str]:
    if x is None:
        return None
    s = str(x).strip()
    if s.lower() in ("", "n/a", "na", "none", "nan"):
        return None
    return s


def _collect_materials(row: pd.Series, cols: List[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for c in cols:
        if c not in row.index:
            continue
        name = _normalize_material(row[c])
        if name and name not in seen:
            seen.add(name)
            out.append(name)
    return out


def ordered_union(a: List[str], b: List[str]) -> List[str]:
    seen, out = set(), []
    for lst in (a, b):
        for x in lst:
            if x not in seen:
                seen.add(x)
                out.append(x)
    return out


# -------------------------
# 6) Build JSON records (保持你要求的格式)
# -------------------------
def pairs_to_records(
    pairs_df: pd.DataFrame,
    df_indexed: pd.DataFrame,
    T: Dict[str, Any],
    question_text: str,
    pair_source: str,
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for _, pr in pairs_df.iterrows():
        r1 = str(pr["row1_index"])
        r2 = str(pr["row2_index"])
        if (r1 not in df_indexed.index) or (r2 not in df_indexed.index):
            continue

        # control = "better XRD but worse PCE" row
        case = pr.get("condition_case", None)
        if case == "row2":
            ctrl_idx, tgt_idx = r2, r1
        else:
            ctrl_idx, tgt_idx = r1, r2

        row_ctrl = df_indexed.loc[ctrl_idx]
        row_tgt = df_indexed.loc[tgt_idx]

        control_text = row_to_text(row_ctrl, T)
        target_text = row_to_text(row_tgt, T)

        ctrl_add = _collect_materials(row_ctrl, ["Formula Additive 1", "Formula Additive 2", "Formula Additive 3"])
        tgt_add = _collect_materials(row_tgt, ["Formula Additive 1", "Formula Additive 2", "Formula Additive 3"])

        rec = {
            "question": question_text,
            "control": control_text,
            "target": target_text,
            "pair_source": pair_source,
            "sample_id_1": str(ctrl_idx),
            "sample_id_2": str(tgt_idx),
            "sample_id_1_date": normalize_date(row_ctrl.get(DATE_COL, "")),
            "sample_id_2_date": normalize_date(row_tgt.get(DATE_COL, "")),
            "Additive": ordered_union(ctrl_add, tgt_add),
        }
        records.append(rec)
    return records


# -------------------------
# 7) Run
# -------------------------
def main() -> None:
    random.seed(SEED)
    np.random.seed(SEED)


    script_dir = Path(__file__).parent.resolve()

    output_dir = script_dir.parent.parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_csv = output_dir / OUTPUT_CSV


    json_output_dir = output_dir / "XRD_additives"
    json_output_dir.mkdir(parents=True, exist_ok=True)
    output_json = json_output_dir / "additive_xrd_pairs.json"

    export_table_to_csv_exclude_id(TABLE_NAME, output_csv, MYSQL_CONFIG)


    # input_csv = Path(INPUT_CSV)
    # output_json = Path(OUTPUT_JSON)
    # output_json.parent.mkdir(parents=True, exist_ok=True)

    df = read_csv_auto(output_csv)
    df = strip_columns(df)
    df = ensure_index_col(df, INDEX_COL)

    pairs_formula, pairs_conc, _ = build_pairs(
        df_main=df,
        index_col=INDEX_COL,
        formula_cols=FORMULA_COLS,
        conc_cols=CONC_COLS,
        formula_diff_ignore=FORMULA_DIFF_IGNORE,
    )

    pairs_formula_f = evaluate_pairs(
        pairs_df=pairs_formula, df_main=df, index_col=INDEX_COL,
        metric_cols=METRIC_COLS,
        intensity_col=INTENSITY_COL, fwhm_col=FWHM_COL, pce_col=PCE_COL,
    )
    pairs_conc_f = evaluate_pairs(
        pairs_df=pairs_conc, df_main=df, index_col=INDEX_COL,
        metric_cols=METRIC_COLS,
        intensity_col=INTENSITY_COL, fwhm_col=FWHM_COL, pce_col=PCE_COL,
    )

    def _sample(d: pd.DataFrame) -> pd.DataFrame:
        if MAX_PAIRS_PER_SOURCE and MAX_PAIRS_PER_SOURCE > 0 and len(d) > MAX_PAIRS_PER_SOURCE:
            return d.sample(n=MAX_PAIRS_PER_SOURCE, random_state=SEED).reset_index(drop=True)
        return d

    pairs_formula_f = _sample(pairs_formula_f)
    pairs_conc_f = _sample(pairs_conc_f)

    T = import_templates_lib()
    df_indexed = df.drop_duplicates(subset=[INDEX_COL], keep="first").fillna("N/A").set_index(INDEX_COL)

    records: List[Dict[str, Any]] = []
    if "formula" in PAIR_SOURCES:
        records.extend(pairs_to_records(pairs_formula_f, df_indexed, T, QUESTION, "formula"))
    if "concentration" in PAIR_SOURCES:
        records.extend(pairs_to_records(pairs_conc_f, df_indexed, T, QUESTION, "concentration"))

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    if WRITE_DEBUG_CSV:
        stem = output_json.with_suffix("")
        pairs_formula.to_csv(stem.as_posix() + "_pairs_formula_raw.csv", index=False, encoding="utf-8-sig")
        pairs_conc.to_csv(stem.as_posix() + "_pairs_conc_raw.csv", index=False, encoding="utf-8-sig")
        pairs_formula_f.to_csv(stem.as_posix() + "_pairs_formula_filtered.csv", index=False, encoding="utf-8-sig")
        pairs_conc_f.to_csv(stem.as_posix() + "_pairs_conc_filtered.csv", index=False, encoding="utf-8-sig")

    print("✅ Done.")
    print("Output JSON:", output_json)
    print("Records:", len(records))


if __name__ == "__main__":
    run_additive_xrd()
