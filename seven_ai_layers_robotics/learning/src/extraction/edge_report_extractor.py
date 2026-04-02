# -*- coding: utf-8 -*-
"""
Edge Report Data Cleaning and Deduplication Extractor
Responsible for exporting data from database, performing outlier filtering and deduplication, and writing back to database
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from sqlalchemy import create_engine, text


class EdgeReportExtractor:
    """Edge Report Data Extractor - Handles data cleaning, deduplication and write-back."""

    def __init__(self, db_config: Dict[str, Any]):
        """Initialize extractor.
        
        Args:
            db_config: Database configuration dictionary.
        """
        self.db_config = db_config
        self.db_uri = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}?charset=utf8mb4"

        # Parameter columns (business unique formula + process)
        self.param_cols = [
            "Formula PVK", "Concentration PVK",
            "Formula Additive 1", "Concentration Additive 1",
            "Formula Additive 2", "Concentration Additive 2",
            "Formula Additive 3", "Concentration Additive 3",
            "Formula SAM 1", "Concentration SAM 1",
            "Formula SAM 2", "Concentration SAM 2",
            "Formula SAM 3", "Concentration SAM 3",
            "Spin Coating Speed SAM", "Spin Coating Time SAM",
            "Annealed Temperature SAM", "Annealed Time SAM",
            "Spin Coating Speed PVK 1", "Spin Coating Time PVK 1",
            "Spin Coating Speed PVK 2", "Spin Coating Time PVK 2",
            "Antisolvent Dropping Timing", "Antisolvent Volume",
            "Annealed Temperature PVK", "Annealed Time PVK",
            "Formula Passivator 1", "Concentration Passivator 1",
            "Formula Passivator 2", "Concentration Passivator 2",
            "Formula Passivator 3", "Concentration Passivator 3",
            "Formula Passivator 4", "Concentration Passivator 4",
            "Spin Coating Speed Passivator", "Spin Coating Time Passivator",
            "Passivator Dropping Timing", "Passivator Volume",
            "Annealed Temperature Passivator", "Annealed Time Passivator",
        ]

        # Metric columns
        self.metric_cols = ["PCE", "FF", "Voc", "Jsc"]

        # All write columns
        self.all_write_cols = ["No"] + self.param_cols + self.metric_cols

        # No segmentation dynamic thresholds (strict inequality)
        self.no_segments = [
            # (no_lo, no_hi, pce_lo, pce_hi, ff_lo, ff_hi, voc_lo, voc_hi, jsc_lo, jsc_hi)
            (0,     7680,  10, 18,    50, 90,    0.9, 1.15,  15, 24),
            (7681,  32960, 10, 23.5,  50, 90,    0.9, 1.19,  15, 25.5),
            (32961, 42420, 10, 25.56, 50, 90,    0.9, 1.19,  15, 26.5),
            (42421, 50764, 10, 27,    50, 90,    0.9, 1.22,  15, 26.7),
        ]

    def _assert_columns(self, df: pd.DataFrame, required_cols: List[str]) -> None:
        """Check if DataFrame contains all required columns.
        
        Args:
            df: Input DataFrame to validate.
            required_cols: List of required column names.
            
        Raises:
            ValueError: If any required columns are missing.
        """
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def _coerce_numeric_inplace(self, df: pd.DataFrame) -> None:
        """Convert No and metric columns to numeric, invalid values become NaN.
        
        Args:
            df: Input DataFrame to convert in-place.
        """
        df["No"] = pd.to_numeric(df["No"], errors="coerce")
        for c in self.metric_cols:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    def _filter_by_no_segments(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Dynamic outlier removal by No segments (vectorized implementation)
        - No, PCE, FF, Voc, Jsc must be non-empty and valid numeric values
        - Then filter by segment thresholds
        """
        self._assert_columns(df, ["No"] + self.metric_cols)

        df = df.copy()
        self._coerce_numeric_inplace(df)

        df = df.dropna(subset=["No"] + self.metric_cols)
        if df.empty:
            return df

        no = df["No"]
        pce, ff, voc, jsc = df["PCE"], df["FF"], df["Voc"], df["Jsc"]

        masks = []
        for (nlo, nhi, p_lo, p_hi, ff_lo, ff_hi, v_lo, v_hi, j_lo, j_hi) in self.no_segments:
            seg = (
                (no >= nlo) & (no <= nhi) &
                (pce > p_lo) & (pce < p_hi) &
                (ff > ff_lo) & (ff < ff_hi) &
                (voc > v_lo) & (voc < v_hi) &
                (jsc > j_lo) & (jsc < j_hi)
            )
            masks.append(seg)

        mask_all = masks[0]
        for m in masks[1:]:
            mask_all = mask_all | m

        return df.loc[mask_all].copy()

    def clean_and_dedup_keep_max_pce(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and deduplicate data, keeping rows with maximum PCE.
        
        Processing steps:
            1. Remove outliers by No segments
            2. Deduplication by PARAM_COLS (keep max PCE)
            3. Remove outliers again (to prevent idxmax boundary issues)
            4. Restore original order
        
        Args:
            df: Input DataFrame to clean and deduplicate.
            
        Returns:
            Cleaned and deduplicated DataFrame.
        """
        self._assert_columns(df, self.all_write_cols)

        df = df.copy()
        df["_orig_idx"] = range(len(df))

        n0 = len(df)

        # 1) 去异常
        df = self._filter_by_no_segments(df)
        n1 = len(df)
        if df.empty:
            print(f"⚠️ After outlier removal is empty: {n0} → {n1}")
            return df.drop(columns=["_orig_idx"], errors="ignore")

        # 2) Deduplication: Group by parameter columns, keep max PCE
        idx = df.groupby(self.param_cols, dropna=False)["PCE"].idxmax()
        df = df.loc[idx].copy()
        n2 = len(df)

        # 3) Remove outliers again
        df = self._filter_by_no_segments(df)
        n3 = len(df)
        if df.empty:
            print(f"⚠️ After deduplication then outlier removal is empty: {n2} → {n3}")
            return df.drop(columns=["_orig_idx"], errors="ignore")

        # 4) Restore original order
        df = df.sort_values("_orig_idx").drop(columns=["_orig_idx"])

        print(f"✅ Cleaning Statistics: Original {n0} → After outlier removal {n1} → After deduplication {n2} → After second outlier removal {n3}")
        return df

    def export_table_to_csv(self, src_table: str, output_csv: str) -> pd.DataFrame:
        """
        Export table from database to CSV
        :param src_table: Source table name
        :param output_csv: Output CSV path
        :return: DataFrame
        """
        engine = create_engine(self.db_uri)
        df = pd.read_sql(f"SELECT * FROM `{src_table}`;", con=engine)
        df.to_csv(output_csv, index=False, encoding="utf-8-sig")
        print(f"✅ Exported {len(df)} rows → {output_csv}")
        return df

    def process_csv(self, input_csv: str, output_dir: str) -> pd.DataFrame:
        """
        Process CSV file: cleaning + deduplication → output CSV
        :param input_csv: Input CSV path
        :param output_dir: Output directory
        :return: Processed DataFrame
        """
        df = pd.read_csv(input_csv, encoding="utf-8-sig")

        df_out = self.clean_and_dedup_keep_max_pce(df)

        Path(output_dir).mkdir(exist_ok=True)
        out_filename = f"data_clean_dedup_{len(df_out)}rows.csv"
        out_path = Path(output_dir) / out_filename
        df_out.to_csv(out_path, index=False, encoding="utf-8-sig")

        print(f"✅ Cleaning completed: {out_path}")
        return df_out

    @staticmethod
    def to_param(col: str) -> str:
        """Convert database column name to bind parameter name for SQLAlchemy.
        
        Args:
            col: Database column name.
            
        Returns:
            Bind parameter name with 'p_' prefix and underscores replaced.
        """
        return "p_" + col.replace(" ", "_").replace("-", "_")

    def upsert_to_target_table(self, df: pd.DataFrame, target_table: str) -> None:
        """
        UPSERT full fields write-back to target table
        :param df: DataFrame to write
        :param target_table: Target table name
        """
        self._assert_columns(df, self.all_write_cols)

        df_write = df[self.all_write_cols].copy()

        param_map = {col: self.to_param(col) for col in self.all_write_cols}

        insert_cols = ", ".join(f"`{c}`" for c in self.all_write_cols)
        value_cols = ", ".join(f":{param_map[c]}" for c in self.all_write_cols)

        update_cols = ", ".join(
            f"`{c}` = VALUES(`{c}`)" for c in (self.param_cols + self.metric_cols)
        )

        sql = text(f"""
        INSERT INTO `{target_table}` ({insert_cols})
        VALUES ({value_cols})
        ON DUPLICATE KEY UPDATE
            {update_cols}
        """)

        records = []
        for _, row in df_write.iterrows():
            rec = {}
            for col in self.all_write_cols:
                val = row[col]
                if pd.isna(val):
                    val = None
                rec[param_map[col]] = val
            records.append(rec)

        engine = create_engine(self.db_uri)
        with engine.begin() as conn:
            conn.execute(sql, records)

        print(f"✅ Successfully UPSERTed full fields {len(records)} rows → `{target_table}`")

    def extract_and_process(self, src_table: str, target_table: str,
                           output_dir: str = "data") -> bool:
        """
        Execute complete extraction, cleaning and write-back workflow
        :param src_table: Source table name
        :param target_table: Target table name
        :param output_dir: Output directory (default: data)
        :return: True if successful, raises Exception on failure
        """
        try:
            # Step 1: DB → CSV (save to output directory)
            Path(output_dir).mkdir(exist_ok=True)
            raw_csv = Path(output_dir) / f"{src_table}_from_db.csv"
            df_raw = self.export_table_to_csv(src_table, str(raw_csv))

            # Step 2: Cleaning + Deduplication → output CSV
            df_clean = self.process_csv(raw_csv, output_dir)

            # Step 3: UPSERT write-back
            self.upsert_to_target_table(df_clean, target_table)

            return True

        except Exception as e:
            print(f"❌ Processing failed: {e}")
            raise e
